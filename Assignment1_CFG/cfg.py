import json
import sys
from collections import deque

TERMINATORS = ("jmp", "br", "ret")


def generate_cfg(bril_program):
    """
    Generate a CFG for the first function in a Bril program.

    Args:
        bril_program (dict): Parsed Bril program.
    Returns:
        dict | None: CFG for the first function, or None if not found.
    """
    if (
        not bril_program
        or "functions" not in bril_program
        or not bril_program["functions"]
    ):
        return None

    func = bril_program["functions"][0]
    blocks = form_blocks(func["instrs"])
    name2block = block_map(blocks)
    return get_cfg(name2block)


def form_blocks(body):
    """
    Split a list of instructions into basic blocks.

    A new block begins at each label and after each terminator instruction.
    Empty blocks are not returned.

    Args:
        body (list[dict]): Bril instruction list.

    Returns:
        list[list[dict]]: Sequence of basic blocks (labels kept inline).
    """
    blocks = []
    cur_block = []

    for instr in body:
        # If we encounter a label, start a new block at the label.
        if "label" in instr:
            if cur_block:
                blocks.append(cur_block)
            cur_block = [instr]
            continue

        # Otherwise it’s a normal instruction — append it.
        cur_block.append(instr)

        # If it’s a terminator, close the current block.
        if instr.get("op") in TERMINATORS:
            blocks.append(cur_block)
            cur_block = []

    if cur_block:
        blocks.append(cur_block)

    # Filter out any accidental empties.
    return [b for b in blocks if b]


def block_map(blocks):
    """
    Assign names to basic blocks.

    - If a block begins with a label, use that label as the block's name and
      remove the label from the block body.
    - Otherwise generate a name: b{index}.

    Args:
        blocks (list[list[dict]]): Blocks as produced by form_blocks.

    Returns:
        dict[str, list[dict]]: name -> block body (no label dicts inside).
    """
    out = {}
    for idx, block in enumerate(blocks):
        if not block:
            continue

        first = block[0]
        if "label" in first:
            name = first["label"]
            body = block[1:]
        else:
            name = f"b{idx}"
            body = block

        out[name] = body
    return out


def get_cfg(name2block):
    """
    Compute the successor list for each block.

    Control flow rules:
      - 'jmp labels: [L]'  -> succs = labels
      - 'br labels: [T,F]' -> succs = labels (two-way)
      - 'ret'              -> succs = []
      - otherwise          -> fall-through to the next block in insertion order
    """
    out = {}
    names = list(name2block.keys())

    for i, (name, block) in enumerate(name2block.items()):
        if not block:
            out[name] = []
            continue

        last = block[-1]
        op = last.get("op")

        if op in ("jmp", "br"):
            succ = last.get("labels", []) or []
        elif op == "ret":
            succ = []
        else:
            # Fall-through if there is a subsequent block
            succ = [names[i + 1]] if i + 1 < len(names) else []

        out[name] = succ

    return out


def get_path_lengths(cfg, entry):
    """
    Compute shortest path lengths (in edges) from *entry* to reachable nodes.

    Args:
        cfg (dict[str, list[str]]): Block successor map.
        entry (str): Entry block name.

    Returns:
        dict[str, int]: node -> distance (in edges) from entry.
    """
    if entry is None or entry not in cfg:
        return {}

    dist = {entry: 0}
    q = deque([entry])

    while q:
        u = q.popleft()
        for v in cfg.get(u, []):
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist
