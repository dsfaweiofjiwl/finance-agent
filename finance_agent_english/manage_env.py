#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Key 管理工具
功能：
1. 查看当前配置的API Key（掩码显示，保护隐私）
2. 一键清除所有API Key（保留文件结构，清空值）
3. 交互式引导替换单个或全部API Key
"""

import os
import sys
from dotenv import load_dotenv


def parse_env_file(path: str) -> dict:
    """解析.env文件"""
    env_vars = {}
    if not os.path.exists(path):
        return env_vars

    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()

    return env_vars


def save_env_file(path: str, env_vars: dict) -> None:
    """保存.env文件"""
    # 先读取原始文件，保留注释和格式
    original_lines = []
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            original_lines = f.readlines()

    # 更新变量
    new_lines = []
    for line in original_lines:
        line = line.rstrip('\n')
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            new_lines.append(line)
            continue
        if '=' in stripped:
            key = stripped.split('=', 1)[0].strip()
            if key in env_vars:
                new_lines.append(f"{key}={env_vars[key]}")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines) + '\n')


def mask_key(key: str) -> str:
    """掩码显示API Key，只显示前4后4位"""
    if len(key) <= 8:
        return '*' * len(key)
    return key[:4] + '*' * (len(key) - 8) + key[-4:]


def print_current_env(env_vars: dict) -> None:
    """打印当前环境变量（掩码）"""
    print("\n📋 当前配置的API Key:")
    print("-" * 50)
    api_keys = [k for k in env_vars if any(x in k.upper() for x in ['API_KEY', 'SECRET', 'TOKEN'])]
    if not api_keys:
        print("  (无已配置的API Key)\n")
        return

    for k in sorted(api_keys):
        value = env_vars[k]
        if value:
            print(f"  {k:20s} : {mask_key(value)}")
        else:
            print(f"  {k:20s} : (空)")
    print("-" * 50)
    print()


def clear_all_api_keys(env_vars: dict) -> None:
    """清空所有API Key"""
    api_keys = [k for k in env_vars if any(x in k.upper() for x in ['API_KEY', 'SECRET', 'TOKEN'])]
    for k in api_keys:
        env_vars[k] = ''
    print(f"✅ 已清空 {len(api_keys)} 个API Key")


def interactive_replace(env_vars: dict) -> None:
    """交互式替换API Key"""
    api_keys = [k for k in env_vars if any(x in k.upper() for x in ['API_KEY', 'SECRET', 'TOKEN'])]

    if not api_keys:
        print("❌ 没有找到API Key配置项")
        return

    print(f"找到 {len(api_keys)} 个API Key配置项:")
    for i, k in enumerate(api_keys, 1):
        current = env_vars[k]
        if current:
            print(f"  {i}. {k} : {mask_key(current)}")
        else:
            print(f"  {i}. {k} : (空)")

    print("\n请输入要修改的编号（多个用空格分隔，输入'all'修改全部，输入'q'取消）:")
    choice = input("> ").strip()

    if choice.lower() == 'q':
        print("👋 取消修改")
        return

    selected = []
    if choice.lower() == 'all':
        selected = api_keys
    else:
        try:
            indexes = [int(x) - 1 for x in choice.split()]
            selected = [api_keys[i] for i in indexes if 0 <= i < len(api_keys)]
        except ValueError:
            print("❌ 输入格式错误")
            return

    for k in selected:
        current = env_vars[k]
        if current:
            print(f"\n当前 {k}: {mask_key(current)}")
        print(f"请输入新的 {k} 值（输入'empty'清空，输入'q'跳过）:")
        new_val = input("> ").strip()
        if new_val.lower() == 'q':
            continue
        elif new_val.lower() == 'empty':
            env_vars[k] = ''
            print(f"✅ 已清空 {k}")
        else:
            env_vars[k] = new_val
            print(f"✅ 已更新 {k}")


def main():
    env_path = os.path.join(os.path.dirname(__file__), '.env')

    if not os.path.exists(env_path):
        print(f"❌ 文件不存在: {env_path}")
        print("   请先复制 .env.example 到 .env 再配置")
        sys.exit(1)

    env_vars = parse_env_file(env_path)
    print_current_env(env_vars)

    print("请选择操作:")
    print("  1. 🧹  一键清除所有API Key（保留配置项，清空值）")
    print("  2. ✏️  交互式替换API Key")
    print("  3. 🚪  退出")

    choice = input("> ").strip()

    if choice == '1':
        confirm = input("⚠️  确认要清除所有API Key吗？这会清空所有值，确认请输入'y': ").strip().lower()
        if confirm == 'y':
            clear_all_api_keys(env_vars)
            save_env_file(env_path, env_vars)
            print("✅ 操作完成！所有API Key已清空")
            print_current_env(env_vars)
        else:
            print("👋 已取消")

    elif choice == '2':
        interactive_replace(env_vars)
        save_env_file(env_path, env_vars)
        print("\n✅ 修改已保存")
        print_current_env(env_vars)

    elif choice == '3':
        print("👋 再见")
        sys.exit(0)

    else:
        print("❌ 无效选择")


if __name__ == "__main__":
    main()
