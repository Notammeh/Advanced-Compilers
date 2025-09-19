import json
import sys

TERMINATORS = ("jmp", "br", "ret")

def generate_cfg(bril_program):
    """
    Generate a CFG for the first function in a Bril program.
    Args:
        bril_program (dict): Parsed Bril program.
    Returns:
        dict: CFG representation for the first function, or None if not found.
    """
    if not bril_program or "functions" not in bril_program or not bril_program["functions"]:
        return None
    func = bril_program["functions"][0]
    name2block = block_map(form_blocks(func["instrs"]))
    return get_cfg(name2block)

def form_blocks(body):
    """Split a list of instructions into basic blocks.

    A new block begins at each label and after each terminator
    instruction. Empty blocks are not yielded.
    """
    cur_block = []
    for instr in body:
        if "op" in instr:  # actual instruction
            cur_block.append(instr)
            # End the current block at a terminator
            if instr["op"] in TERMINATORS:
                yield cur_block
                cur_block = []
        else:
            # instr is a label. End the current block if it has any contents.
            if cur_block:
                yield cur_block
            # start a new block beginning with this label
            cur_block = [instr]
    # yield the final block if it’s non-empty
    if cur_block:
        yield cur_block

def block_map(blocks):
    """Map block names to their instruction lists.

    Anonymous blocks get names like b0, b1, etc. If a block
    starts with a label, the label becomes the block name and
    is removed from the block body.
    """
    out = {}
    for block in blocks:
        if "label" in block[0]:
            name = block[0]["label"]
            block = block[1:]
        else:
            name = f"b{len(out)}"
        out[name] = block
    return out

def get_cfg(name2block):
    """Compute the successor mapping for each block."""
    out = {}
    names = list(name2block.keys())
    for i, (name, block) in enumerate(name2block.items()):
        if not block:
            out[name] = []
            continue
        last = block[-1]
        if "op" in last and last["op"] in ("jmp", "br"):
            succ = last.get("labels", [])
        elif "op" in last and last["op"] == "ret":
            succ = []
        else:
            # Fall-through to the next block if not terminated
            succ = [names[i + 1]] if i + 1 < len(names) else []
        out[name] = succ
    return out

def mycfg():
    """CLI entry point: read Bril JSON on stdin and print CFGs."""
    prog = json.load(sys.stdin)
    for func in prog["functions"]:
        name2block = block_map(form_blocks(func["instrs"]))
        cfg = get_cfg(name2block)
        print(f"CFG for function {func['name']}:")
        for block, succ in cfg.items():
            print(f"  {block} -> {succ}")

if __name__ == "__main__":
    mycfg()
