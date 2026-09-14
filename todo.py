#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""todo.py —— 极简待办清单 CLI

能力：add 添加（可选 --priority high|mid|low，缺省 mid）
      list 展示（可选 --sorted：按 高→中→低 稳定排序并显示优先级标记；编号恒为存储序）
      done 勾选完成（按存储序编号）
"""
import json
import sys
from pathlib import Path

STORE = Path(__file__).with_name("todo.json")

PRIORITY_KEYS = {"high": "高", "mid": "中", "low": "低"}


def load():
    if STORE.exists():
        items = json.loads(STORE.read_text(encoding="utf-8"))
        for it in items:
            it.setdefault("priority", "mid")
        return items
    return []


def save(items):
    STORE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_priority(rest):
    """从参数列表提取可选 --priority <值>，返回 (文本tokens, 优先级)。非法值写入前硬拦截。"""
    if "--priority" not in rest:
        return rest, "mid"
    idx = rest.index("--priority")
    if idx + 1 >= len(rest):
        print("错误: --priority 需要取值 high/mid/low")
        sys.exit(1)
    val = rest[idx + 1]
    if val not in PRIORITY_KEYS:
        print(f"错误: 非法优先级 {val!r}，可选值: high/mid/low（严格全拼）")
        sys.exit(1)
    if "--priority" in rest[idx + 2:]:
        print("错误: --priority 只能出现一次")
        sys.exit(1)
    return rest[:idx] + rest[idx + 2:], val


def main():
    args = sys.argv[1:]
    if not args:
        print("用法: python todo.py add <文本> | list | done <编号>")
        return
    cmd, *rest = args
    items = load()
    if cmd == "add":
        rest, priority = parse_priority(rest)
        if not rest:
            print("未知命令或参数不足")
            sys.exit(1)
        items.append({"text": " ".join(rest), "done": False, "priority": priority})
        save(items)
        print("已添加:", " ".join(rest))
    elif cmd == "list":
        sorted_mode = "--sorted" in rest
        view = list(enumerate(items, 1))
        if sorted_mode:
            order = {"high": 0, "mid": 1, "low": 2}
            view = sorted(view, key=lambda pair: order[pair[1]["priority"]])
        for no, it in view:
            mark = "x" if it["done"] else " "
            line = f"[{mark}] {no}. {it['text']}"
            if sorted_mode:
                line += f" [{PRIORITY_KEYS[it['priority']]}]"
            print(line)
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
