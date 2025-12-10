import argparse
import sys
import os
import glob
import random
import tiktoken
import pandas as pd
from tqdm import tqdm


def load_text_files(haystack_folder: str) -> list[str]:
    """載入指定資料夾中的所有 .txt 文件"""
    txt_files = glob.glob(os.path.join(haystack_folder, "*.txt"))
    if not txt_files:
        raise ValueError(f"在 {haystack_folder} 中找不到 .txt 文件")

    texts = []
    for file_path in txt_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            texts.append(f.read().strip())

    print(f"已從 {haystack_folder} 載入 {len(texts)} 個文字檔案")
    return texts


def split_chinese_sentences(text: str) -> list[str]:
    """
    將繁體中文文本按句子分割
    中文句子結束符號：。！？；
    """
    import re
    # 使用中文句號、驚嘆號、問號、分號來分句
    sentences = re.split(r'([。！？；])', text)

    # 重新組合句子和標點符號
    result = []
    for i in range(0, len(sentences)-1, 2):
        if i+1 < len(sentences):
            sentence = sentences[i].strip() + sentences[i+1]
            if sentence.strip():
                result.append(sentence)

    # 處理最後一個可能沒有標點的句子
    if len(sentences) % 2 == 1 and sentences[-1].strip():
        result.append(sentences[-1].strip())

    return result


def build_haystack_sequential(texts: list[str], target_tokens: int, tokenizer) -> str:
    """依序組建 haystack，直到達到目標 token 數量"""
    haystack = ""
    text_index = 0

    while len(tokenizer.encode(haystack)) < target_tokens:
        next_text = texts[text_index % len(texts)]
        test_haystack = haystack + next_text + "\n\n"

        test_tokens = len(tokenizer.encode(test_haystack))
        if test_tokens > target_tokens:
            current_tokens = len(tokenizer.encode(haystack))
            remaining_tokens = target_tokens - current_tokens

            if remaining_tokens > 0:
                text_tokens = tokenizer.encode(next_text + "\n\n")
                truncated_tokens = text_tokens[:remaining_tokens]
                haystack += tokenizer.decode(truncated_tokens)
            break
        else:
            haystack = test_haystack

        text_index += 1

    return haystack


def build_haystack_shuffled(texts: list[str], target_tokens: int, tokenizer) -> str:
    """
    隨機打亂句子順序來組建 haystack
    針對繁體中文使用中文句子分割
    """
    all_chunks = []
    for text in texts:
        sentences = split_chinese_sentences(text)
        for sentence in sentences:
            if sentence.strip():
                all_chunks.append({
                    'text': sentence,
                    'token_count': len(tokenizer.encode(sentence))
                })

    available_chunks = all_chunks.copy()
    random.shuffle(available_chunks)

    context_parts = []
    current_tokens = 0
    chunk_index = 0

    while current_tokens < target_tokens:
        if chunk_index >= len(available_chunks):
            random.shuffle(available_chunks)
            chunk_index = 0

        chunk = available_chunks[chunk_index]
        chunk_text = chunk['text']
        chunk_tokens = chunk.get('token_count', len(tokenizer.encode(chunk_text)))

        if current_tokens + chunk_tokens > target_tokens:
            if current_tokens > 0:
                break
            tokens_needed = target_tokens
            chunk_tokens_list = tokenizer.encode(chunk_text)
            truncated_tokens = chunk_tokens_list[:tokens_needed]
            chunk_text = tokenizer.decode(truncated_tokens)
            current_tokens = tokens_needed
            context_parts.append(chunk_text)
            break

        context_parts.append(chunk_text)
        current_tokens += chunk_tokens
        chunk_index += 1

    # 繁體中文不需要額外空格分隔
    return "".join(context_parts)


def insert_needle_at_depth(haystack: str, needle: str, depth_percent: float, tokenizer) -> str:
    """
    在指定深度位置插入 needle
    針對繁體中文，在句子邊界處插入
    """
    haystack_tokens = tokenizer.encode(haystack)
    needle_tokens = tokenizer.encode(needle)

    if depth_percent == 100:
        new_tokens = haystack_tokens + needle_tokens
    elif depth_percent == 0:
        new_tokens = needle_tokens + haystack_tokens
    else:
        insertion_point = int(len(haystack_tokens) * (depth_percent / 100))

        # 尋找最近的中文句子結束符號
        # 取得可能的句子結束符號的 token
        sentence_end_chars = ['。', '！', '？', '；']
        sentence_end_tokens = set()
        for char in sentence_end_chars:
            sentence_end_tokens.update(tokenizer.encode(char))

        # 往前找到最近的句子結束符號
        search_point = insertion_point
        while search_point > 0 and haystack_tokens[search_point - 1] not in sentence_end_tokens:
            search_point -= 1

        # 如果找到句子結束符號，使用該位置；否則使用原始位置
        if search_point > 0:
            insertion_point = search_point

        new_tokens = haystack_tokens[:insertion_point] + needle_tokens + haystack_tokens[insertion_point:]

    return tokenizer.decode(new_tokens)


def insert_distractors_randomly(haystack: str, distractors: list[str]) -> str:
    """
    隨機插入干擾句子
    針對繁體中文使用中文句子分割
    """
    if not distractors:
        return haystack

    sentences = split_chinese_sentences(haystack)
    if len(sentences) < 2:
        return haystack

    result_sentences = sentences.copy()

    for distractor in distractors:
        if len(result_sentences) > 1:
            insert_pos = random.randint(1, len(result_sentences) - 1)
            # 確保干擾句子有適當的結尾標點
            if not distractor.endswith(('。', '！', '？', '；')):
                distractor = distractor + '。'
            result_sentences.insert(insert_pos, distractor)

    # 繁體中文不需要額外分隔符
    return "".join(result_sentences)


def create_niah_prompt(haystack_with_needle: str, retrieval_question: str) -> str:
    """創建 NIAH 提示，使用繁體中文指示"""
    system_template = f"""你是一個有幫助的 AI 助手，負責回答使用者的問題。請保持回答簡短直接。

    <document_content>
    {haystack_with_needle}
    <document_content>

    這是使用者的問題：
    <question>
    {retrieval_question}
    <question>

    不要提供文件以外的資訊，也不要重複你的發現。
    助手：以下是文件中最相關的資訊：
    """

    return system_template


def create_haystacks(haystack_folder: str, needle: str, shuffled: bool, output_folder: str,
                    question: str, distractors: list[str] = None):
    """創建 NIAH 測試用的 haystacks"""
    os.makedirs(output_folder, exist_ok=True)
    tokenizer = tiktoken.get_encoding("o200k_base")

    texts = load_text_files(haystack_folder)

    input_lengths = [500, 1_000, 5_000, 10_000, 50_000, 100_000, 500_000, 900_000]
    depths = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

    sample_prompt = create_niah_prompt("SAMPLE_CONTEXT", question)
    overhead_tokens = len(tokenizer.encode(sample_prompt.replace("SAMPLE_CONTEXT", "")))

    results = []

    mode_text = "隨機打亂" if shuffled else "順序排列"
    print(f"正在創建{mode_text}的提示...")
    if distractors:
        print(f"將添加 {len(distractors)} 個干擾句子到 haystacks 中")

    for input_length in tqdm(input_lengths, desc="處理輸入長度"):
        needle_tokens = len(tokenizer.encode(needle))
        available_context_tokens = input_length - overhead_tokens - needle_tokens

        if available_context_tokens <= 100:
            print(f"跳過輸入長度 {input_length} - 空間不足以容納 needle 和 overhead")
            continue

        if shuffled:
            base_haystack = build_haystack_shuffled(texts, available_context_tokens, tokenizer)
        else:
            base_haystack = build_haystack_sequential(texts, available_context_tokens, tokenizer)

        for depth in depths:
            haystack_with_distractors = insert_distractors_randomly(base_haystack, distractors)
            haystack_with_needle = insert_needle_at_depth(haystack_with_distractors, needle, depth, tokenizer)

            full_prompt = create_niah_prompt(haystack_with_needle, question)

            actual_tokens = len(tokenizer.encode(full_prompt))

            results.append({
                'token_count': actual_tokens,
                'approximate_input_length': input_length,
                'needle_depth': depth,
                'prompt': full_prompt,
                'question': question,
                'answer': needle
            })

    results_df = pd.DataFrame(results)
    mode = "shuffled" if shuffled else "sequential"
    distractor_suffix = "_with_distractors" if distractors else ""
    output_path = os.path.join(output_folder, f"niah_prompts_cht_{mode}{distractor_suffix}.csv")
    results_df.to_csv(output_path, index=False)

    print(f"已創建 {len(results)} 個 NIAH 提示")
    print(f"結果已儲存至 {output_path}")

    return results_df


def main():
    parser = argparse.ArgumentParser(description='創建繁體中文 NIAH 測試提示')

    parser.add_argument('--haystack-folder', type=str, required=True,
                       help='包含 .txt 文件的資料夾，作為 haystack 內容來源')
    parser.add_argument('--needle', type=str, required=True,
                       help='要插入到 haystack 中的 needle 文字')
    parser.add_argument('--question', type=str, required=True,
                       help='關於 needle 的問題')
    parser.add_argument('--shuffled', action='store_true',
                       help='使用隨機打亂模式（隨機排列句子順序）')
    parser.add_argument('--output-folder', type=str, required=True,
                       help='生成 CSV 文件的輸出資料夾')
    parser.add_argument('--distractors', type=str, nargs='*', default=None,
                       help='可選的干擾句子，將隨機插入到 haystacks 中')

    args = parser.parse_args()

    try:
        if not os.path.exists(args.haystack_folder):
            raise ValueError(f"Haystack 資料夾不存在：{args.haystack_folder}")

        if not args.needle.strip():
            raise ValueError("Needle 不能為空")

        if not args.question.strip():
            raise ValueError("問題不能為空")

        distractors = [d.strip() for d in args.distractors if d.strip()] if args.distractors else None

        create_haystacks(
            haystack_folder=args.haystack_folder,
            needle=args.needle,
            shuffled=args.shuffled,
            output_folder=args.output_folder,
            question=args.question,
            distractors=distractors
        )

    except Exception as e:
        print(f"錯誤：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
