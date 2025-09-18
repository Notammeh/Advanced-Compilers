"""
Test cases for CFG generator
"""
import unittest
from cfg import generate_cfg

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
                        {"op": "ret"}
                    ]
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
                        {"op": "ret"}
                    ]
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
                        {"op": "ret"}
                    ]
                }
            ]
        }
        cfg = generate_cfg(bril_program)
        self.assertEqual(cfg, {"start": ["then", "else"], "then": [], "else": []})

if __name__ == "__main__":
    unittest.main()
