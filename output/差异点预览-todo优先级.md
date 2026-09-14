# 差异点预览报告：todo.py 优先级与排序支持

## 1. 变更规模

| 指标 | 值 |
|------|-----|
| 修改文件 | `todo.py`（+44/-8 行） |
| 新增文件 | `tests/test_todo_pipeline.py`（22 测试用例） |
| 新增目录 | `tests/`、`docs/rfc/0001-todo-priority/` |

## 2. 文件清单

| 文件 | 状态 | 说明 |
|------|------|------|
| `todo.py` | 修改 | 新增优先级字段 + --priority 解析 + --sorted 排序 |
| `tests/test_todo_pipeline.py` | 新增 | 22 个 unittest 用例 |
| `docs/rfc/0001-todo-priority/design.md` | 新增 | 设计文档（已评审通过） |
| `docs/rfc/0001-todo-priority/requirements.md` | 新增 | 需求文档 |
| `docs/rfc/0001-todo-priority/rfc.md` | 新增 | RFC 文档 |

## 3. 重点差异点

| # | 设计承诺 | 落地文件 | 实现方式 |
|---|---------|---------|---------|
| 1 | add --priority high/mid/low | `todo.py` L39-52 `parse_priority()` | 提取 `--priority` 参数，非法值硬拦截 |
| 2 | 缺省优先级 mid | `todo.py` L40 `return rest, "mid"` | `--priority` 不存在时默认返回 mid |
| 3 | list --sorted 高→中→低 | `todo.py` L65-68 | `sorted(view, key=lambda pair: order[pair[1]["priority"]])` |
| 4 | 编号恒为存储序 | `todo.py` L66 `enumerate(items, 1)` | `list --sorted` 的编号是存储序，done 直接对应 |
| 5 | 旧数据兼容 | `todo.py` L18-20 `it.setdefault("priority", "mid")` | load 时自动补缺省值 |
| 6 | 非法值拦截不污染数据 | `todo.py` L45-47 | 写入前 `sys.exit(1)`，数据文件不变 |

## 4. 测试结果

全部 **22 个测试通过**：

```
TestZeroRegression (5)  ... ok  # 零回归
TestPriorityAdd (7)     ... ok  # FR-1/FR-4
TestSortedView (7)      ... ok  # FR-2/FR-3
TestLegacyCompat (3)    ... ok  # FR-5
```

## 5. 未覆盖项

无。设计文档中所有功能需求（FR-1~FR-5）均已覆盖。

## 6. 交付件完成情况

| 交付件 | 状态 | 路径 |
|--------|------|------|
| 实现代码 (todo.py) | ✅ | `todo.py` |
| 测试套件 | ✅ | `tests/test_todo_pipeline.py` |
| 设计文档 | ✅ | `docs/rfc/0001-todo-priority/design.md` |
