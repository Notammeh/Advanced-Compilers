from df import Analysis, run_df

def _union(sets):
    out = set()
    for s in sets:
        out |= s
    return out

def _rd_transfer(block, in_set):
    """
    OUT[b] = GEN[b] ∪ (IN[b] − KILL[b])
    - GEN[b]: defs created in b as unique ids like "var@<blockid>:<idx>"
    - KILL[b]∩IN: any defs in IN whose var is redefined in b
    We only need to subtract kills that are actually in IN.
    """
    # Collect variables defined in this block and build GEN
    block_id = id(block)
    def_vars = set()
    gen = set()
    for i, instr in enumerate(block):
        dest = instr.get("dest")
        if dest is not None:
            def_vars.add(dest)
            gen.add(f"{dest}@{block_id}:{i}")

    # From IN, drop any defs whose var is redefined here
    # We encoded def-ids as "var@..." so var is the prefix up to '@'
    kill_from_in = {d for d in in_set if d.split("@", 1)[0] in def_vars}

    return gen | (in_set - kill_from_in)

def main():
    import sys, json
    prog = json.load(sys.stdin)

    # Build the Analysis tuple for RD:
    # - forward = True
    # - init    = empty set
    # - merge   = union over predecessor OUTs
    # - transfer= _rd_transfer
    rd = Analysis(
        True,           # forward
        set(),          # init (bottom)
        _union,         # merge (may)
        _rd_transfer,   # transfer
    )

    # Let df.py do the CFG and the printing
    run_df(prog, rd)

if __name__ == "__main__":
    main()
