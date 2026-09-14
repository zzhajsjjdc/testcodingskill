# RFC-0001：todo.py 优先级与排序支持

## 概述

给极简待办 CLI（todo.py）增加优先级字段（high/mid/low），支持按优先级排序展示，同时保持零回归兼容。

## 现状与缺口

当前 `todo.py` 的 `list` 只按录入顺序展示，重要事项会被淹没。`items` 存储为 `{"text": ..., "done": bool}`，无优先级字段。详见 `需求文档-todo优先级.md`。

## 方案要点

### 数据模型
```python
{"text": "交房租", "done": False, "priority": "high"}
```

### 命令变更
- `python todo.py add <文本> --priority high|mid|low` — 添加时指定优先级，缺省 mid
- `python todo.py list` — 保持原行为（零回归）
- `python todo.py list --sorted` — 按 高→中→低 排序，显示优先级标记
- `python todo.py done <编号>` — 不变

### 兼容性
旧 `todo.json` 无 `priority` 字段时，读入自动补 `"mid"`。

### 确定性
排序算法稳定（Python `sorted` 默认稳定），相同数据两次输出一致。

## 竞品对比

| 产品 | 优先级方式 | 本项目差异 |
|------|-----------|-----------|
| todo.txt | 字母 A/B/C | 本项目用全拼 high/mid/low，更直观 |
| taskwarrior | 数字 P1-P5 | 本项目三档更简单，单文件零依赖 |

## 技术边界

- 优先级非法值写入前硬拦截，不污染 `todo.json`
- `--sorted` 视图编号为存储序编号，与 `done` 命令可直接对应

## 里程碑

- M0：种子代码注入 ✅
- M1：RFC 提交（本 Issue）
- M2：设计评审
- M3：开发与 PR 合并
