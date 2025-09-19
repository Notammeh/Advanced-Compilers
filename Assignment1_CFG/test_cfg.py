"""Test cases for CFG generator and analysis helpers."""

import os
import sys
import unittest
sys.path.insert(0, os.path.dirname(__file__))

from cfg import (
    generate_cfg,
    get_path_lengths,
    reverse_postorder,
    find_back_edges,
    is_reducible,
)

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
@@ -39,27 +49,74 @@ class TestCFG(unittest.TestCase):
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

class TestCFGAnalysis(unittest.TestCase):
    def test_get_path_lengths(self):
        cfg = {
            "entry": ["left", "right"],
            "left": ["exit"],
            "right": ["exit"],
            "exit": [],
            "dead": ["dead"],
        }

        distances = get_path_lengths(cfg, "entry")
        self.assertEqual(distances, {"entry": 0, "left": 1, "right": 1, "exit": 2})

    def test_reverse_postorder_linear(self):
        cfg = {"entry": ["mid"], "mid": ["exit"], "exit": []}
        self.assertEqual(reverse_postorder(cfg, "entry"), ["entry", "mid", "exit"])

    def test_find_back_edges_simple_loop(self):
        cfg = {
            "entry": ["loop"],
            "loop": ["entry", "exit"],
            "exit": [],
        }

        back_edges = find_back_edges(cfg, "entry")
        self.assertEqual(back_edges, [("loop", "entry")])

    def test_is_reducible_simple_loop(self):
        cfg = {
            "entry": ["loop"],
            "loop": ["entry", "exit"],
            "exit": [],
        }

        self.assertTrue(is_reducible(cfg, "entry"))

    def test_is_reducible_irreducible_graph(self):
        cfg = {
            "A": ["B", "D"],
            "B": ["C"],
            "C": ["D"],
            "D": ["B", "E"],
            "E": [],
        }

        self.assertFalse(is_reducible(cfg, "A"))

if __name__ == "__main__":
    unittest.main()
