#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""todo.py —— 极简待办清单 CLI（练习仓种子代码）

现状能力：add 添加 / list 按录入顺序展示 / done 勾选完成
已知局限：不支持优先级，list 无法区分轻重缓急（留待 RFC 改进）
"""
import json
import sys
from pathlib import Path

STORE = Path(__file__).with_name("todo.json")


def load():
    if STORE.exists():
        return json.loads(STORE.read_text(encoding="utf-8"))
    return []


def save(items):
    STORE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    args = sys.argv[1:]
    if not args:
        print("用法: python todo.py add <文本> | list | done <编号>")
        return
    cmd, *rest = args
    items = load()
    if cmd == "add" and rest:
        items.append({"text": " ".join(rest), "done": False})
        save(items)
        print("已添加:", " ".join(rest))
    elif cmd == "list":
        for i, it in enumerate(items, 1):
            mark = "x" if it["done"] else " "
            print(f"[{mark}] {i}. {it['text']}")
    elif cmd == "done" and rest and rest[0].isdigit():
        n = int(rest[0]) - 1
        if 0 <= n < len(items):
            items[n]["done"] = True
            save(items)
            print("已完成:", items[n]["text"])
            return
        print("编号不存在")
        sys.exit(1)
    else:
        print("未知命令或参数不足")
        sys.exit(1)


if __name__ == "__main__":
    main()
