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
@@ -55,37 +56,139 @@ def block_map(blocks):
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

def get_path_lengths(cfg, entry):
    """Compute shortest path lengths (in edges) from *entry* to reachable nodes."""
    if entry is None:
        return {}

    distances = {entry: 0}
    queue = deque([entry])

    while queue:
        node = queue.popleft()
        for succ in cfg.get(node, []):
            if succ not in distances:
                distances[succ] = distances[node] + 1
                queue.append(succ)

    return distances

def reverse_postorder(cfg, entry):
    """Return the reverse postorder of nodes reachable from *entry*."""
    if entry is None:
        return []

    visited = set()
    postorder = []

    def dfs(node):
        visited.add(node)
        for succ in cfg.get(node, []):
            if succ not in visited:
                dfs(succ)
        postorder.append(node)

    dfs(entry)
    return list(reversed(postorder))

def find_back_edges(cfg, entry):
    """Identify back edges using a DFS rooted at *entry*."""
    if entry is None:
        return []

    back_edges = []
    color = {}

    def dfs(node):
        color[node] = "gray"
        for succ in cfg.get(node, []):
            state = color.get(succ)
            if state is None:
                dfs(succ)
            elif state == "gray":
                back_edges.append((node, succ))
        color[node] = "black"

    dfs(entry)
    return back_edges

def is_reducible(cfg, entry):
    """Return True if the CFG rooted at *entry* is reducible."""
    if entry is None:
        return True

    reachable = set(get_path_lengths(cfg, entry).keys())
    if not reachable:
        return True

    preds = {node: set() for node in reachable}
    for node in reachable:
        for succ in cfg.get(node, []):
            if succ in reachable:
                preds[succ].add(node)

    dom = {node: set(reachable) for node in reachable}
    dom[entry] = {entry}

    changed = True
    while changed:
        changed = False
        for node in reachable:
            if node == entry:
                continue

            pred_nodes = preds[node]
            if pred_nodes:
                pred_doms = [dom[pred] for pred in pred_nodes]
                new_dom = set(pred_doms[0])
                for dom_set in pred_doms[1:]:
                    new_dom &= dom_set
            else:
                new_dom = set()

            new_dom.add(node)

            if new_dom != dom[node]:
                dom[node] = new_dom
                changed = True

    for tail, head in find_back_edges(cfg, entry):
        if tail in reachable and head in reachable and head not in dom[tail]:
            return False

    return True

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
