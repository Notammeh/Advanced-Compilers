    def test_fallthrough_between_labeled_blocks(self):
        # A block that doesn't end in a terminator should fall through to the next block.
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
        # First block has no label; it should be named b0 and fall through to the next labeled block.
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
        # Small graph to sanity-check BFS distances from entry.
        from cfg import get_path_lengths  # local import to avoid unused if not present
        cfg = {
            "start": ["x", "y"],
            "x": ["z"],
            "y": ["z"],
            "z": [],
        }
        dist = get_path_lengths(cfg, "start")
        self.assertEqual(dist, {"start": 0, "x": 1, "y": 1, "z": 2})
