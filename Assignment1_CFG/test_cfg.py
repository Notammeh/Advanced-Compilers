import unittest
from cfg import generate_cfg, get_path_lengths


class TestCFG(unittest.TestCase):
    def test_empty_program(self):
        bril_program = {}
        cfg = generate_cfg(bril_program)
        self.assertIsNone(cfg)

    def test_single_block_ret(self):
        bril_program = {
            "functions": [
                {
                    "name": "main",
                    "instrs": [
                        {"op": "const", "dest": "x", "type": "int", "value": 1},
                        {"op": "ret"},
                    ],
                }
            ]
        }
        cfg = generate_cfg(bril_program)
        self.assertEqual(cfg, {"b0": []})

    def test_two_blocks_jmp(self):
        bril_program = {
            "functions": [
                {
                    "name": "main",
                    "instrs": [
                        {"label": "entry"},
                        {"op": "jmp", "labels": ["exit"]},
                        {"label": "exit"},
                        {"op": "ret"},
                    ],
                }
            ]
        }
        cfg = generate_cfg(bril_program)
        self.assertEqual(cfg, {"entry": ["exit"], "exit": []})

    def test_branch(self):
        bril_program = {
            "functions": [
                {
                    "name": "main",
                    "instrs": [
                        {"label": "start"},
                        {"op": "br", "args": ["cond"], "labels": ["then", "else"]},
                        {"label": "then"},
                        {"op": "ret"},
                        {"label": "else"},
                        {"op": "ret"},
                    ],
                }
            ]
        }
        cfg = generate_cfg(bril_program)
        self.assertEqual(cfg, {"start": ["then", "else"], "then": [], "else": []})

    # ---------- Extra edge-case tests ----------

    def test_fallthrough_between_labeled_blocks(self):
        # A block that doesn't end in a terminator should fall through.
        bril_program = {
            "functions": [
                {
                    "name": "main",
                    "instrs": [
                        {"label": "A"},
                        {"op": "const", "dest": "x", "type": "int", "value": 1},
                        {"label": "B"},
                        {"op": "ret"},
                    ],
                }
            ]
        }
        cfg = generate_cfg(bril_program)
        self.assertEqual(cfg, {"A": ["B"], "B": []})

    def test_unlabeled_then_labeled_fallthrough(self):
        # First block has no label; it should be named b0 and fall through.
        bril_program = {
            "functions": [
                {
                    "name": "main",
                    "instrs": [
                        {"op": "const", "dest": "x", "type": "int", "value": 1},
                        {"op": "const", "dest": "y", "type": "int", "value": 2},
                        {"label": "L"},
                        {"op": "ret"},
                    ],
                }
            ]
        }
        cfg = generate_cfg(bril_program)
        self.assertEqual(cfg, {"b0": ["L"], "L": []})

    def test_jmp_bypasses_middle_block(self):
        # A jmp should ignore fall-through and jump directly to its target.
        bril_program = {
            "functions": [
                {
                    "name": "main",
                    "instrs": [
                        {"label": "entry"},
                        {"op": "jmp", "labels": ["C"]},
                        {"label": "B"},
                        {"op": "ret"},
                        {"label": "C"},
                        {"op": "ret"},
                    ],
                }
            ]
        }
        cfg = generate_cfg(bril_program)
        self.assertEqual(cfg, {"entry": ["C"], "B": [], "C": []})

    def test_path_lengths_basic(self):
        # Sanity-check BFS distances from entry.
        cfg = {
            "start": ["x", "y"],
            "x": ["z"],
            "y": ["z"],
            "z": [],
        }
        dist = get_path_lengths(cfg, "start")
        self.assertEqual(dist, {"start": 0, "x": 1, "y": 1, "z": 2})


if __name__ == "__main__":
    unittest.main(verbosity=2)
