# Reaching_Definitions.py
# Works with bril/examples/df.py where Analysis is constructed as:
# Analysis(forward: bool, init: Callable, merge: Callable, transfer: Callable)

from typing import Dict, Set, Tuple, List
import sys, json

# These are the helpers you copied from the Bril repo.
from df import Analysis, run_df
from form_blocks import form_blocks
from cfg import block_map
# util imported by cfg/form_blocks is already in your folder.

# A "definition" ID -> (var, block_label, instr_index)
DefId = Tuple[str, str, int]

def collect_all_defs(func) -> Dict[str, Set[DefId]]:
    """
    Map: var -> set of all def IDs across the function.
    """
    all_defs: Dict[str, Set[DefId]] = {}
    # Build basic blocks (labels -> list of instructions)
    blocks = block_map(form_blocks(func["instrs"]))
    for blabel, binstrs in blocks.items():
        for i, instr in enumerate(binstrs):
            dest = instr.get("dest")
            if dest is not None:
                d: DefId = (dest, blabel, i)
                all_defs.setdefault(dest, set()).add(d)
    return all_defs

def build_gen_kill(func):
    """
    Compute GEN and KILL per block.
    GEN[b]: defs created in b (unique per assignment)
    KILL[b]: all other defs of the same vars defined in b
    """
    blocks = block_map(form_blocks(func["instrs"]))
    all_defs = collect_all_defs(func)

    GEN: Dict[str, Set[DefId]] = {b: set() for b in blocks}
    KILL: Dict[str, Set[DefId]] = {b: set() for b in blocks}

    for blabel, binstrs in blocks.items():
        # Which variables are (re)defined in this block, and at what indices
        for i, instr in enumerate(binstrs):
            dest = instr.get("dest")
            if dest is None:
                continue
            d_here: DefId = (dest, blabel, i)
            GEN[blabel].add(d_here)
            # kill all other defs of dest across the function
            KILL[blabel] |= (all_defs.get(dest, set()) - {d_here})

    return blocks, GEN, KILL

def make_rd_analysis(func):
    """
    Return an Analysis instance configured for Reaching Definitions on `func`.
    """

    blocks, GEN, KILL = build_gen_kill(func)

    # --- init: initial fact for each block label
    def init() -> Dict[str, Set[DefId]]:
        # For RD (may, forward), boundary is IN[entry]=∅ and others start at ∅ too.
        return {blabel: set() for blabel in blocks.keys()}

    # --- merge: meet over preds (union for may analysis)
    def merge(facts: List[Set[DefId]]) -> Set[DefId]:
        out: Set[DefId] = set()
        for s in facts:
            out |= s
        return out

    # --- transfer: OUT[b] = GEN[b] ∪ (IN[b] − KILL[b])
    def transfer(blabel: str, in_fact: Set[DefId]) -> Set[DefId]:
        return GEN[blabel] | (in_fact - KILL[blabel])

    # forward=True (this is a forward analysis)
    return Analysis(True, init, merge, transfer)

def main():
    prog = json.load(sys.stdin)

    # Run RD on each function in the program (typical driver pattern in df.py)
    results = {}
    for func in prog.get("functions", []):
        name = func["name"]
        analysis = make_rd_analysis(func)
        ins_o_
