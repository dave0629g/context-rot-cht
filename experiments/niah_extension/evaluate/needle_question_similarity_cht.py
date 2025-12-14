import argparse
import os
import sys
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
import requests

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# 設定支援中文的字體（與 visualize_cht.py 類似）
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Microsoft JhengHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def _normalize_text_for_ngrams(s: str) -> str:
    return "".join(str(s).split())


def _char_ngrams(s: str, n: int = 2) -> List[str]:
    s = _normalize_text_for_ngrams(s)
    if n <= 0:
        return []
    if len(s) < n:
        return [s] if s else []
    return [s[i : i + n] for i in range(len(s) - n + 1)]


def jaccard_similarity(a: str, b: str, ngram: int = 2) -> float:
    A = set(_char_ngrams(a, ngram))
    B = set(_char_ngrams(b, ngram))
    if not A and not B:
        return 1.0
    if not A or not B:
        return 0.0
    return float(len(A & B) / len(A | B))


def ollama_embed(
    base_url: str,
    model: str,
    text: str,
    timeout: int = 60,
) -> List[float]:
    """Call Ollama /api/embeddings and return embedding vector."""
    base_url = base_url.rstrip("/")
    url = f"{base_url}/api/embeddings"
    payload = {"model": model, "prompt": text}
    r = requests.post(url, json=payload, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    emb = data.get("embedding")
    if not isinstance(emb, list) or not emb:
        raise ValueError(f"Ollama embeddings 回傳格式不符：{data}")
    return [float(x) for x in emb]


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    denom = (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))
    if denom == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / denom)


def add_similarity_column(
    df: pd.DataFrame,
    method: str,
    question_col: str,
    answer_col: str,
    ollama_base_url: Optional[str] = None,
    ollama_embed_model: Optional[str] = None,
    jaccard_ngram: int = 2,
) -> pd.DataFrame:
    if question_col not in df.columns or answer_col not in df.columns:
        raise ValueError(f"CSV 必須包含欄位：{question_col}, {answer_col}")

    out = df.copy()

    if method == "jaccard":
        out["needle_question_similarity"] = [
            jaccard_similarity(q, a, ngram=jaccard_ngram)
            for q, a in zip(out[question_col].astype(str), out[answer_col].astype(str))
        ]
        return out

    if method != "ollama":
        raise ValueError(f"未知 similarity method: {method}")

    if not ollama_base_url:
        raise ValueError("使用 ollama 相似度時必須提供 --ollama-base-url 或設定 $OLLAMA_BASE_URL")
    if not ollama_embed_model:
        raise ValueError("使用 ollama 相似度時必須提供 --ollama-embed-model（例如 nomic-embed-text）")

    # 針對重複文本做快取（question 常常重複、answer 也可能重複）
    cache: Dict[Tuple[str, str], np.ndarray] = {}

    def get_emb(kind: str, text: str) -> np.ndarray:
        key = (kind, text)
        if key in cache:
            return cache[key]
        vec = np.asarray(ollama_embed(ollama_base_url, ollama_embed_model, text), dtype=np.float32)
        cache[key] = vec
        return vec

    sims: List[float] = []
    for q, a in zip(out[question_col].astype(str), out[answer_col].astype(str)):
        qv = get_emb("q", q)
        av = get_emb("a", a)
        sims.append(cosine_similarity(qv, av))

    out["needle_question_similarity"] = sims
    return out


def make_similarity_heatmap(
    df: pd.DataFrame,
    output_path: str,
    title: str,
    length_col: str = "approximate_input_length",
    judge_col: str = "llm_judge_output",
    sim_col: str = "needle_question_similarity",
    sim_bins: int = 10,
    aggregate_depth: bool = True,
    depth_value: Optional[float] = None,
    depth_col: str = "needle_depth",
    figsize: Tuple[int, int] = (12, 6),
) -> None:
    if length_col not in df.columns:
        raise ValueError(f"缺少欄位：{length_col}")
    if judge_col not in df.columns:
        raise ValueError(f"缺少欄位：{judge_col}")
    if sim_col not in df.columns:
        raise ValueError(f"缺少欄位：{sim_col}")

    plot_df = df.copy()

    if depth_value is not None:
        if depth_col not in plot_df.columns:
            raise ValueError(f"指定 --depth 但 CSV 缺少欄位：{depth_col}")
        plot_df = plot_df[plot_df[depth_col] == depth_value]

    # judge 轉成 0/1
    plot_df["accuracy"] = plot_df[judge_col].apply(lambda x: 1 if str(x).strip().lower() == "true" else 0)

    # 相似度分箱（0..1）
    # 若 cosine 可能略超界，先 clip
    plot_df[sim_col] = pd.to_numeric(plot_df[sim_col], errors="coerce").clip(lower=-1.0, upper=1.0)
    # 把 [-1,1] 映射到 [0,1] 以便直覺呈現（也更接近一般「相似度」圖表習慣）
    plot_df["sim_01"] = (plot_df[sim_col] + 1.0) / 2.0

    # 分箱標籤用區間中點
    bins = np.linspace(0.0, 1.0, sim_bins + 1)
    mids = (bins[:-1] + bins[1:]) / 2.0
    plot_df["sim_bin"] = pd.cut(plot_df["sim_01"], bins=bins, include_lowest=True, labels=[f"{m:.2f}" for m in mids])

    # 依需求是否把 depth 平均掉
    group_cols = [length_col, "sim_bin"]
    if not aggregate_depth and depth_col in plot_df.columns:
        group_cols.insert(1, depth_col)

    grouped = plot_df.groupby(group_cols)["accuracy"].mean().reset_index()

    if not aggregate_depth and depth_col in grouped.columns:
        # 有 depth 的話：輸出多張（每個 depth 一張）
        depths = sorted(grouped[depth_col].unique())
        n = len(depths)
        fig, axes = plt.subplots(1, n, figsize=(max(figsize[0], 4 * n), figsize[1]), squeeze=False)
        for i, d in enumerate(depths):
            sub = grouped[grouped[depth_col] == d]
            pivot = sub.pivot(index=length_col, columns="sim_bin", values="accuracy")
            pivot = pivot.sort_index(axis=0).reindex(sorted(pivot.columns, key=lambda s: float(s)), axis=1)

            ax = axes[0][i]
            im = ax.imshow(pivot.values, aspect="auto", vmin=0, vmax=1, origin="lower")
            ax.set_title(f"{title}\nDepth={d}%")
            ax.set_xlabel("Needle-Question 相似度（分箱中點）")
            ax.set_ylabel("輸入長度（tokens）")
            ax.set_xticks(range(len(pivot.columns)))
            ax.set_xticklabels(list(pivot.columns), rotation=45, ha="right")
            ax.set_yticks(range(len(pivot.index)))
            ax.set_yticklabels([str(int(x)) for x in pivot.index])

        fig.colorbar(im, ax=axes.ravel().tolist(), fraction=0.02, pad=0.02, label="Accuracy")
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close()
        return

    pivot = grouped.pivot(index=length_col, columns="sim_bin", values="accuracy")
    pivot = pivot.sort_index(axis=0).reindex(sorted(pivot.columns, key=lambda s: float(s)), axis=1)

    plt.figure(figsize=figsize)
    im = plt.imshow(pivot.values, aspect="auto", vmin=0, vmax=1, origin="lower")
    plt.colorbar(im, fraction=0.03, pad=0.02, label="Accuracy")

    plt.title(title)
    plt.xlabel("Needle-Question 相似度（分箱中點；0=低, 1=高）")
    plt.ylabel("輸入長度（tokens）")

    plt.xticks(range(len(pivot.columns)), list(pivot.columns), rotation=45, ha="right")
    plt.yticks(range(len(pivot.index)), [str(int(x)) for x in pivot.index])

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="將 NIAH 結果加上 needle-question 相似度，並產生相似度×長度熱圖")

    parser.add_argument("--input-csv", type=str, required=True, help="輸入 CSV（建議用 *_evaluated.csv）")
    parser.add_argument("--output-csv", type=str, default=None, help="輸出（加上 similarity 欄位）CSV 路徑（可選）")
    parser.add_argument("--output-png", type=str, required=True, help="輸出熱圖 PNG 路徑")
    parser.add_argument("--title", type=str, default="NIAH: Accuracy vs Needle-Question Similarity", help="圖標題")

    parser.add_argument("--similarity-method", type=str, default="ollama", choices=["ollama", "jaccard"], help="相似度計算方法")

    default_ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    parser.add_argument("--ollama-base-url", type=str, default=default_ollama_base_url, help="Ollama base URL（預設：$OLLAMA_BASE_URL 或 http://localhost:11434）")
    parser.add_argument("--ollama-embed-model", type=str, default=os.getenv("OLLAMA_EMBED_MODEL", ""), help="Ollama embeddings model（例如 nomic-embed-text）。也可用環境變數 $OLLAMA_EMBED_MODEL")

    parser.add_argument("--question-column", type=str, default="question", help="question 欄位名")
    parser.add_argument("--answer-column", type=str, default="answer", help="needle/answer 欄位名")

    parser.add_argument("--sim-bins", type=int, default=10, help="相似度分箱數（預設 10）")
    parser.add_argument("--jaccard-ngram", type=int, default=2, help="Jaccard 字元 n-gram（預設 2）")

    parser.set_defaults(aggregate_depth=True)
    parser.add_argument(
        "--no-aggregate-depth",
        action="store_false",
        dest="aggregate_depth",
        help="不要把不同 needle_depth 平均；改成每個 depth 各畫一張（多子圖）",
    )
    parser.add_argument("--depth", type=float, default=None, help="只畫特定 needle_depth（例如 50）。未指定則使用全部")

    args = parser.parse_args()

    try:
        df = pd.read_csv(args.input_csv)

        df2 = add_similarity_column(
            df,
            method=args.similarity_method,
            question_col=args.question_column,
            answer_col=args.answer_column,
            ollama_base_url=args.ollama_base_url if args.similarity_method == "ollama" else None,
            ollama_embed_model=args.ollama_embed_model if args.similarity_method == "ollama" else None,
            jaccard_ngram=args.jaccard_ngram,
        )

        if args.output_csv:
            df2.to_csv(args.output_csv, index=False)

        make_similarity_heatmap(
            df2,
            output_path=args.output_png,
            title=args.title,
            sim_bins=args.sim_bins,
            aggregate_depth=args.aggregate_depth,
            depth_value=args.depth,
        )

        print("完成！")
        if args.output_csv:
            print(f"已輸出 CSV：{args.output_csv}")
        print(f"已輸出 PNG：{args.output_png}")

    except Exception as e:
        print(f"錯誤：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
