from df import Analysis

class ReachingDefinitions(Analysis):
    def direction(self):
        # Forward analysis
        return "forward"

    def top(self, blocks):
        # Start with empty sets everywhere
        return {b: set() for b in blocks}

    def meet(self, sets):
        # Union of all predecessor OUT sets
        result = set()
        for s in sets:
            result |= s
        return result

    def transfer(self, block, in_set):
        """
        OUT[b] = GEN[b] ∪ (IN[b] - KILL[b])
        """
        gen, kill = set(), set()
        for i, instr in enumerate(block):
            if "dest" in instr:  # definition
                v = instr["dest"]
                # Treat each def as a unique (var, block, index)
                d = (v, id(block), i)
                gen.add(d)
                # KILL = all other defs of v (we can't know globally here,
                # so in practice you'd precompute def sites per var)
                kill |= {d2 for d2 in in_set if d2[0] == v}
        return (in_set - kill) | gen


if __name__ == "__main__":
    import sys, json
    from df import run_df

    prog = json.load(sys.stdin)
    analysis = ReachingDefinitions()
    result = run_df(prog, analysis)

    # Pretty-print results
    for func, ins_outs in result.items():
        print(f"Function {func}:")
        for label, (ins, outs) in ins_outs.items():
            print(f"  Block {label}:")
            print(f"    IN : {ins}")
            print(f"    OUT: {outs}")
