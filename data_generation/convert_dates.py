#!/usr/bin/env python3
"""
日期重算脚本 - llm_wiki 数据集生成工具

用法：
    python convert_dates.py [--config config.yaml] [--dry-run]

流程：
    1. 读取 config.yaml 中的 anchor_date 和 project_start
    2. 计算所有 date_N（project_start + N 天）
    3. 遍历 data_template/ 目录，将所有 {{date_N}} 替换为实际日期
    4. 重命名文件名中的日期部分
    5. 输出到 output/ 目录（不修改原始 data_template/）

示例：
    # 默认用法（anchor_date = config.yaml 中的值）
    python convert_dates.py

    # 模拟运行（不改文件，只显示会改什么）
    python convert_dates.py --dry-run

    # 指定 config 文件路径
    python convert_dates.py --config /path/to/config.yaml
"""

import os
import re
import shutil
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import yaml

# 默认配置
DEFAULT_CONFIG = "config.yaml"
DEFAULT_TEMPLATE_DIR = "data_template"
DEFAULT_OUTPUT_DIR = "output"


def parse_args():
    parser = argparse.ArgumentParser(description="重算数据集中的日期占位符")
    parser.add_argument(
        "--config", "-c",
        default=DEFAULT_CONFIG,
        help=f"配置文件路径（默认：{DEFAULT_CONFIG}）"
    )
    parser.add_argument(
        "--template-dir", "-t",
        default=DEFAULT_TEMPLATE_DIR,
        help=f"模板数据目录（默认：{DEFAULT_TEMPLATE_DIR}）"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=DEFAULT_OUTPUT_DIR,
        help=f"输出目录（默认：{DEFAULT_OUTPUT_DIR}）"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="模拟运行：只显示会改什么，不实际修改文件"
    )
    return parser.parse_args()


def load_config(config_path: str) -> dict:
    """加载配置文件"""
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


def calculate_dates(config: dict) -> dict:
    """
    根据 anchor_date 和 project_start 计算所有 date_N 对应的绝对日期

    date_N 的定义：project_start 开始第 N 天
    例如 project_start = 2026-03-16：
      date_0   = project_start + 0 天 = 2026-03-16
      date_7   = project_start + 7 天 = 2026-03-23
      date_42  = project_start + 42 天 = anchor_date 当天（2026-04-28）
    """
    anchor_date_str = config["anchor_date"]
    project_start_str = config["project_start"]

    anchor_date = datetime.strptime(anchor_date_str, "%Y-%m-%d")
    project_start = datetime.strptime(project_start_str, "%Y-%m-%d")

    # 计算从 project_start 到 anchor_date 的总天数
    total_days = (anchor_date - project_start).days

    # 扫描所有模板文件，找出最大的 date_N
    template_path = Path("data_template")
    max_date_n = total_days
    if template_path.exists():
        for item in template_path.rglob("*.txt"):
            try:
                content = item.read_text(encoding="utf-8")
                for m in re.findall(r"\{\{date_(\d+)\}\}", content):
                    max_date_n = max(max_date_n, int(m))
            except Exception:
                pass

    # 预先计算所有可能用到的 date_N
    # 从 date_0 到 date_{max_date_n}，每一天都要
    all_dates = {}
    for n in range(0, max_date_n + 1):
        key = f"date_{n}"
        date_val = project_start + timedelta(days=n)
        all_dates[key] = date_val.strftime("%Y-%m-%d")

    return all_dates


def process_content(content: str, date_map: dict) -> str:
    """将内容中的 {{date_N}} 替换为实际日期"""
    for key, value in date_map.items():
        placeholder = f"{{{{{key}}}}}"
        content = content.replace(placeholder, value)
    return content


def process_filename(filename: str, date_map: dict, original_project_start: str, new_anchor_date: str) -> str:
    """
    处理文件名中的日期占位符

    文件名格式可能是：
      email_{{date_0}}_Poky_项目启动通知.txt
      im_{{date_7}}_向量数据库选型讨论.txt

    需要把 {{date_N}} 替换为实际日期，并格式化成像 "2026-03-16" 这样的日期
    """
    # 匹配文件名中的日期模式
    # 原始格式：{{date_N}}  → 替换为 YYYY-MM-DD
    for key, value in date_map.items():
        placeholder = f"{{{{{key}}}}}"
        if placeholder in filename:
            return filename.replace(placeholder, value)

    # 也处理没有占位符但有原始日期的文件名
    # 原始 anchor_date = 2026-04-28 时写死的日期，替换为新的 anchor_date
    if original_project_start in filename:
        # 计算新旧 anchor_date 之间的偏移
        orig_anchor = datetime.strptime("2026-04-28", "%Y-%m-%d")
        new_anchor = datetime.strptime(new_anchor_date, "%Y-%m-%d")
        return filename

    return filename


def copy_and_process_template(template_dir: str, output_dir: str, date_map: dict, config: dict, dry_run: bool):
    """
    遍历模板目录，处理每个文件，输出到 output 目录
    """
    template_path = Path(template_dir)
    output_path = Path(output_dir)

    if not dry_run:
        if output_path.exists():
            shutil.rmtree(output_path)
        output_path.mkdir(parents=True)

    original_anchor = "2026-04-28"  # 写死在模板里的原始 anchor_date

    files_processed = []
    files_created = []

    for root, dirs, files in os.walk(template_path):
        # 计算相对路径
        rel_dir = Path(root).relative_to(template_path)

        if not dry_run:
            (output_path / rel_dir).mkdir(parents=True, exist_ok=True)

        for filename in files:
            template_file = Path(root) / filename

            # 处理文件名中的日期占位符
            new_filename = process_filename(filename, date_map, original_anchor, config["anchor_date"])

            # 读取文件内容
            with open(template_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 替换内容中的日期占位符
            new_content = process_content(content, date_map)

            if dry_run:
                # 干跑：只显示变化
                if new_filename != filename:
                    files_processed.append(f"  重命名：{filename} → {new_filename}")
                if new_content != content:
                    files_processed.append(f"  内容变化：{new_filename}")
            else:
                # 写入输出目录
                output_file = output_path / rel_dir / new_filename
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(new_content)
                files_created.append(str(output_file.relative_to(output_path)))

    return files_processed, files_created


def generate_phase_output(template_dir: str, output_dir_base: str, date_map: dict, config: dict, dry_run: bool):
    """
    按 phase 分批输出到 output/{phase_name}/ 目录（保留原始目录结构）
    """
    template_path = Path(template_dir)
    output_path_base = Path(output_dir_base)

    original_anchor = "2026-04-28"

    all_phase_dirs = []

    # 遍历 phase_* 子目录
    for item in sorted(template_path.iterdir()):
        if not item.is_dir() or not item.name.startswith("phase_"):
            continue

        phase_name = item.name
        phase_output = output_path_base / phase_name

        if not dry_run:
            phase_output.mkdir(parents=True, exist_ok=True)

        files_created = []

        for root, dirs, files in os.walk(item):
            # rel_dir 是相对于 phase 目录本身的路径（如 phase_m1/email/）
            # output 时直接用 phase_output / rel_dir，不需要再乘以 phase_name
            rel_dir = Path(root).relative_to(item)

            if not dry_run:
                phase_output.mkdir(parents=True, exist_ok=True)

            for filename in files:
                template_file = Path(root) / filename

                new_filename = process_filename(filename, date_map, original_anchor, config["anchor_date"])

                with open(template_file, "r", encoding="utf-8") as f:
                    content = f.read()

                new_content = process_content(content, date_map)

                if dry_run:
                    pass
                else:
                    output_file = phase_output / new_filename
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    files_created.append(str(output_file.relative_to(phase_output)))

        all_phase_dirs.append((phase_name, phase_output if not dry_run else None, files_created if not dry_run else []))

    return all_phase_dirs


def generate_sources_output(output_dir_base: str, dry_run: bool):
    """
    生成 llm_wiki 可直接导入的 sources 目录结构：
    output/{phase}/sources/  — 所有文件平铺在一个目录，文件名含日期
    用户直接 copy整个 sources/ 目录到 llm_wiki 的 raw/sources/ 即可导入
    """
    output_path_base = Path(output_dir_base)

    for item in sorted(output_path_base.iterdir()):
        if not item.is_dir() or not item.name.startswith("phase_"):
            continue

        sources_dir = item / "sources"
        if not dry_run:
            sources_dir.mkdir(parents=True, exist_ok=True)

        # 收集所有文件（跳过 sources 自身和 manifest）
        files_to_copy = []
        for root, dirs, filenames in os.walk(item):
            # 跳过 sources 目录本身
            if "sources" in Path(root).parts:
                continue
            for filename in filenames:
                if filename == "manifest.txt":
                    continue
                files_to_copy.append(Path(root) / filename)

        if dry_run:
            print(f"  {item.name}/sources/ → {len(files_to_copy)} files")
        else:
            for f in files_to_copy:
                # 去掉 phase_mX/ 前缀，直接放到 sources/ 下
                # 比如 phase_m1/email/email_2026-03-16_xxx.txt → sources/email_2026-03-16_xxx.txt
                # 但不同 phase 可能有同名文件（如 manifest.txt 跳过），所以按 phase 子目录组织
                # 更简单做法：保留原始目录结构在 sources 下
                pass

            # 简化：把所有文件平铺到 sources/，文件名本身已含日期不会冲突
            for f in files_to_copy:
                rel = f.relative_to(item)
                dest = sources_dir / rel.name
                shutil.copy2(f, dest)

    return not dry_run


def main():
    args = parse_args()

    # 加载配置
    if not os.path.exists(args.config):
        print(f"错误：配置文件 {args.config} 不存在")
        return 1

    config = load_config(args.config)

    anchor_date = config["anchor_date"]
    project_start = config["project_start"]

    print("=" * 60)
    print("llm_wiki 数据集日期重算工具")
    print("=" * 60)
    print(f"配置文件：{args.config}")
    print(f"模板目录：{args.template_dir}")
    print(f"输出目录：{args.output_dir}")
    print()
    print(f"anchor_date（demo当天）：{anchor_date}")
    print(f"project_start（项目开始）：{project_start}")

    # 计算日期映射
    date_map = calculate_dates(config)

    print()
    print("日期映射：")
    for key in sorted(date_map.keys(), key=lambda k: int(k.split("_")[1])):
        print(f"  {key} → {date_map[key]}")

    print()

    if args.dry_run:
        print("【干跑模式】不做实际修改，只显示会变化的内容")
        print()
        files_processed, _ = copy_and_process_template(
            args.template_dir, args.output_dir, date_map, config, dry_run=True
        )
        # generate_phase_output 也需要干跑
        for item in sorted(Path(args.template_dir).iterdir()):
            if not item.is_dir() or not item.name.startswith("phase_"):
                continue
            print(f"  {item.name}/")
            _ = generate_phase_output(args.template_dir, args.output_dir, date_map, config, dry_run=True)
        # generate_sources_output 也干跑
        print()
    else:
        print("【执行模式】开始处理文件...")
        print()

        # 全量输出
        print(f"生成全量数据集到 {args.output_dir}/...")
        _, _ = copy_and_process_template(
            args.template_dir, args.output_dir, date_map, config, dry_run=False
        )
        print(f"  ✓ 全量数据集已生成")

        # 分 phase 输出
        print(f"按 phase 分批生成...")
        all_phase_dirs = generate_phase_output(args.template_dir, args.output_dir, date_map, config, dry_run=False)
        for phase_name, phase_output, _ in all_phase_dirs:
            print(f"  ✓ {phase_name}/ 已生成")

        print()
        print("=" * 60)
        print("完成！")
        print(f"全量数据：{args.output_dir}/")
        for phase_name, _, _ in all_phase_dirs:
            print(f"分批数据：{args.output_dir}/{phase_name}/")
        print()
        print("下一步：")
        print("  将 output/{phase}/ 下的文件导入 llm_wiki（New Project → Import）")
        print("=" * 60)

    return 0


if __name__ == "__main__":
    exit(main())