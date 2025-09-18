# Advanced-Compilers
Special Topics 2025

## How to clone this repo

```bash
git clone <https://github.com/Notammeh/Advanced-Compilers.git>
cd Advanced-Compilers
```

## How cfg.py works
- `cfg.py` reads a Bril program in JSON format from standard input.
- It prints the control flow graph (CFG) for each function.

Example usage:
```bash
python3 Assignment1_CFG/cfg.py < bril_program.json
```

## How to test cfg.py
- Run the test file using Python's unittest:

```bash
python3 -m unittest Assignment1_CFG/test_cfg.py
```
