import pandas as pd
import json
from pathlib import Path
from core.processor import StreamableRAGComparisonProcessor
from core.json_generator import JSONGenerator
from utils.excel_generator import (
    create_model_evaluation_excel,
    create_empty_evaluation_template,
)
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


def main():
    """主函数入口"""
    with open("config/models_config.json", "r", encoding="utf-8") as f:
        config_data = json.load(f)

    thread_count = config_data.get("thread_count", 16)
    main_multithreaded(thread_count=thread_count)


def main_multithreaded(thread_count: int = 16):
    """多线程版本的主函数"""
    with open("config/models_config.json", "r", encoding="utf-8") as f:
        models = json.load(f)["models"]

    df = pd.read_excel("骨科病例.xlsx")

    required_columns = ["问题1", "问题2", "问题3"]
    if not all(col in df.columns for col in required_columns):
        print("错误：Excel 文件中缺少必要的问题列")
        return

    all_results = []
    case_lock = threading.Lock()
    completed = [0]

    def process_single_case(indexed_row):
        idx, (row_idx, row) = indexed_row
        thread_processor = StreamableRAGComparisonProcessor(thread_safe=True)
        case_results = thread_processor.process_case(row, idx + 1)

        with case_lock:
            all_results.extend(case_results)
            completed[0] += 1
            print(f"进度：{completed[0]}/{len(df)}")

    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        tasks = [
            (idx, (row_idx, row))
            for idx, (row_idx, row) in enumerate(df.iterrows())
        ]
        future_to_task = {
            executor.submit(process_single_case, task): task for task in tasks
        }

        for future in as_completed(future_to_task):
            future.result()

    Path("PDFs").mkdir(exist_ok=True)
    JSONGenerator.generate_json_output(all_results, "评估结果.json")
    create_model_evaluation_excel(all_results, "模型评分.xlsx")
    create_empty_evaluation_template(all_results, "人工评分.xlsx")

    print(f"\n✓ 处理完成！生成 {len(all_results)} 个结果项")


if __name__ == "__main__":
    main()
