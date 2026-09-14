# -*- coding: utf-8 -*-
"""todo.py 优先级特性 · 流水线测试套件（RFC-0001 / FR-1~FR-5）

纯标准库 unittest；每用例在独立临时目录复制运行 todo.py，互不污染。
约定：正例/负例/变体三种玩法；含确定性证据（两次运行逐字节一致）与零回归对照。
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TODO_SRC = Path(__file__).resolve().parent.parent / "todo.py"


class TodoCase(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="todo_test_"))
        self.todo = self.dir / "todo.py"
        shutil.copy(TODO_SRC, self.todo)
        self.store = self.dir / "todo.json"

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def run_cli(self, *args):
        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        p = subprocess.run([sys.executable, str(self.todo), *args],
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace", cwd=self.dir, timeout=30, env=env)
        return p.returncode, (p.stdout or "") + (p.stderr or "")

    def seed(self, items):
        self.store.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")


class TestZeroRegression(TodoCase):
    """FR 边界：不带新参数时行为与改造前逐字一致"""

    def test_add_plain_message(self):
        rc, out = self.run_cli("add", "写周报")
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), "已添加: 写周报")
        data = json.loads(self.store.read_text(encoding="utf-8"))
        self.assertEqual(data[0]["text"], "写周报")
        self.assertFalse(data[0]["done"])

    def test_list_insertion_order(self):
        self.run_cli("add", "甲")
        self.run_cli("add", "乙")
        rc, out = self.run_cli("list")
        self.assertEqual(out, "[ ] 1. 甲\n[ ] 2. 乙\n")

    def test_done_by_number(self):
        self.run_cli("add", "甲")
        rc, out = self.run_cli("done", "1")
        self.assertEqual(out.strip(), "已完成: 甲")
        self.assertTrue(json.loads(self.store.read_text(encoding="utf-8"))[0]["done"])

    def test_unknown_command_exit1(self):
        rc, out = self.run_cli("nope")
        self.assertEqual(rc, 1)
        self.assertIn("未知命令或参数不足", out)

    def test_empty_store_list_no_output(self):
        rc, out = self.run_cli("list")
        self.assertEqual((rc, out), (0, ""))


class TestPriorityAdd(TodoCase):
    """FR-1/FR-4：add --priority 与写入前硬拦截"""

    def test_add_with_priority(self):
        rc, _ = self.run_cli("add", "交房租", "--priority", "high")
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(self.store.read_text(encoding="utf-8"))[0]["priority"], "high")

    def test_add_priority_before_text(self):
        self.run_cli("add", "--priority", "low", "买菜")
        d = json.loads(self.store.read_text(encoding="utf-8"))
        self.assertEqual((d[0]["text"], d[0]["priority"]), ("买菜", "low"))

    def test_default_mid(self):
        self.run_cli("add", "无标记")
        self.assertEqual(json.loads(self.store.read_text(encoding="utf-8"))[0]["priority"], "mid")

    def test_invalid_value_intercepted(self):
        self.run_cli("add", "基线条目")
        snapshot = self.store.read_text(encoding="utf-8")
        rc, out = self.run_cli("add", "坏", "--priority", "urgent")
        self.assertEqual(rc, 1)
        self.assertIn("非法优先级", out)
        self.assertEqual(self.store.read_text(encoding="utf-8"), snapshot, "非法值不得污染数据文件")

    def test_missing_value_intercepted(self):
        rc, out = self.run_cli("add", "坏", "--priority")
        self.assertEqual(rc, 1)
        self.assertIn("需要取值", out)

    def test_duplicate_flag_intercepted(self):
        rc, out = self.run_cli("add", "x", "--priority", "high", "--priority", "low")
        self.assertEqual(rc, 1)

    def test_strict_spelling_rejects_abbrev(self):
        """决策点3裁决：严格全拼，h/m/l 必须被拒"""
        rc, _ = self.run_cli("add", "x", "--priority", "h")
        self.assertEqual(rc, 1)


class TestSortedView(TodoCase):
    """FR-2/FR-3：确定性排序、稳定、标记与编号（决策点1/4）"""

    def _six(self):
        for text, pri in [("甲", "low"), ("乙", "high"), ("丙", "mid"),
                          ("丁", "high"), ("戊", "low"), ("己", "mid")]:
            self.run_cli("add", text, "--priority", pri)

    def test_sorted_high_mid_low(self):
        self._six()
        rc, out = self.run_cli("list", "--sorted")
        texts = [line.split(". ")[1].split(" [")[0] for line in out.strip().splitlines()]
        self.assertEqual(texts, ["乙", "丁", "丙", "己", "甲", "戊"])

    def test_same_priority_keeps_insertion_order(self):
        self._six()
        rc, out = self.run_cli("list", "--sorted")
        nums = [line.split("] ")[1].split(".")[0] for line in out.strip().splitlines()]
        self.assertEqual(nums, ["2", "4", "3", "6", "1", "5"])

    def test_shows_priority_mark(self):
        self.run_cli("add", "重要", "--priority", "high")
        rc, out = self.run_cli("list", "--sorted")
        self.assertIn("[高]", out)

    def test_plain_list_no_mark(self):
        self.run_cli("add", "重要", "--priority", "high")
        rc, out = self.run_cli("list")
        self.assertNotIn("[高]", out)

    def test_numbers_match_storage_for_done(self):
        """决策点4：--sorted 显示存储编号，done 用所见编号操作同一条目"""
        self.run_cli("add", "甲", "--priority", "low")
        self.run_cli("add", "乙", "--priority", "high")
        rc, out = self.run_cli("list", "--sorted")
        first = out.splitlines()[0]
        self.assertTrue(first.endswith("乙 [高]") and " 2. " in first)
        self.run_cli("done", "2")
        d = json.loads(self.store.read_text(encoding="utf-8"))
        self.assertTrue(d[1]["done"])
        self.assertFalse(d[0]["done"])

    def test_determinism_two_runs_identical(self):
        """FR-3 确定性证据：乱序写入，两次 --sorted 输出逐字节一致"""
        for t, p in [("a", "mid"), ("b", "high"), ("c", "low"), ("d", "mid"), ("e", "high")]:
            self.run_cli("add", t, "--priority", p)
        _, o1 = self.run_cli("list", "--sorted")
        _, o2 = self.run_cli("list", "--sorted")
        self.assertEqual(o1, o2)

    def test_empty_sorted_ok(self):
        rc, out = self.run_cli("list", "--sorted")
        self.assertEqual((rc, out), (0, ""))


class TestLegacyCompat(TodoCase):
    """FR-5：旧数据（无 priority 字段）读入补 mid"""

    def test_legacy_list_and_done_work(self):
        self.seed([{"text": "旧甲", "done": False}, {"text": "旧乙", "done": True}])
        rc, out = self.run_cli("list")
        self.assertEqual(out, "[ ] 1. 旧甲\n[x] 2. 旧乙\n")
        rc, out = self.run_cli("done", "1")
        self.assertEqual(rc, 0)

    def test_legacy_sorted_treated_as_mid(self):
        self.seed([{"text": "旧", "done": False}])
        self.run_cli("add", "新高", "--priority", "high")
        rc, out = self.run_cli("list", "--sorted")
        self.assertTrue(out.splitlines()[0].endswith("新高 [高]"))
        self.assertIn("[中]", out.splitlines()[1])

    def test_legacy_mixed_no_crash(self):
        self.seed([{"text": "无字段", "done": False},
                   {"text": "有字段", "done": False, "priority": "low"}])
        rc, _ = self.run_cli("list", "--sorted")
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
