#!/usr/bin/env python3
"""Two-pass assembler for the Nand2Tetris Hack ISA.

Usage: python3 assembler.py Box.asm [output.hack]
The symbol report is written beside the source as symbols.txt.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEST = {"": "000", "M": "001", "D": "010", "MD": "011",
        "A": "100", "AM": "101", "AD": "110", "AMD": "111"}
JUMP = {"": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
        "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"}
COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "!D": "0001101", "!A": "0110001",
    "-D": "0001111", "-A": "0110011", "D+1": "0011111", "A+1": "0110111",
    "D-1": "0001110", "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
    "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
    "M": "1110000", "!M": "1110001", "-M": "1110011", "M+1": "1110111",
    "M-1": "1110010", "D+M": "1000010", "D-M": "1010011", "M-D": "1000111",
    "D&M": "1000000", "D|M": "1010101",
}
PREDEFINED = {"SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
              **{f"R{i}": i for i in range(16)}, "SCREEN": 16384, "KBD": 24576}
SYMBOL_RE = re.compile(r"^[A-Za-z_.$:][A-Za-z0-9_.$:]*$")


def clean_lines(text: str):
    for line_no, original in enumerate(text.splitlines(), 1):
        line = original.split("//", 1)[0]
        line = "".join(line.split())
        if line:
            yield line_no, line


def assemble(source: Path, output: Path, symbols_path: Path) -> None:
    lines = list(clean_lines(source.read_text(encoding="utf-8")))
    symbols = dict(PREDEFINED)
    labels = {}
    instructions = []
    rom = 0
    for line_no, line in lines:
        if line.startswith("("):
            if not line.endswith(")") or line.count("(") != 1:
                raise ValueError(f"line {line_no}: malformed label {line!r}")
            name = line[1:-1]
            if not SYMBOL_RE.fullmatch(name):
                raise ValueError(f"line {line_no}: invalid symbol {name!r}")
            if name in symbols or name in labels:
                raise ValueError(f"line {line_no}: duplicate or reserved symbol {name!r}")
            if rom > 32767:
                raise ValueError(f"line {line_no}: label lies beyond ROM32K")
            labels[name] = rom
        else:
            if line.startswith("(") or line.endswith(")"):
                raise ValueError(f"line {line_no}: malformed label {line!r}")
            instructions.append((line_no, line))
            rom += 1
    symbols.update(labels)

    next_variable = 16
    machine = []
    variables = {}
    for line_no, line in instructions:
        if line.startswith("@"):
            token = line[1:]
            if token.isdecimal():
                value = int(token)
                if value > 32767:
                    raise ValueError(f"line {line_no}: A-instruction value exceeds 32767")
            else:
                if not SYMBOL_RE.fullmatch(token):
                    raise ValueError(f"line {line_no}: invalid symbol {token!r}")
                if token not in symbols:
                    if next_variable > 16383:
                        raise ValueError(f"line {line_no}: variable RAM space exhausted")
                    symbols[token] = next_variable
                    variables[token] = next_variable
                    next_variable += 1
                value = symbols[token]
            machine.append(f"{value:016b}")
            continue
        if line.count(";") > 1 or line.count("=") > 1:
            raise ValueError(f"line {line_no}: malformed C-instruction {line!r}")
        left, sep, jump = line.partition(";")
        if sep and jump not in JUMP:
            raise ValueError(f"line {line_no}: unknown jump mnemonic {jump!r}")
        dest, eq, comp = left.partition("=")
        if not eq:
            comp, dest = left, ""
        if comp not in COMP:
            raise ValueError(f"line {line_no}: unknown comp mnemonic {comp!r}")
        if dest not in DEST:
            raise ValueError(f"line {line_no}: unknown destination {dest!r}")
        machine.append("111" + COMP[comp] + DEST[dest] + JUMP[jump])

    output.write_text("\n".join(machine) + "\n", encoding="ascii")
    report = ["# Hack assembler symbols", "# kind\tname\taddress"]
    report.extend(f"predefined\t{name}\t{address}" for name, address in sorted(PREDEFINED.items(), key=lambda x: (x[1], x[0])))
    report.extend(f"label\t{name}\t{address}" for name, address in sorted(labels.items(), key=lambda x: (x[1], x[0])))
    report.extend(f"variable\t{name}\t{address}" for name, address in sorted(variables.items(), key=lambda x: (x[1], x[0])))
    symbols_path.write_text("\n".join(report) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", nargs="?", type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve() if args.output else source.with_suffix(".hack")
    symbols_path = source.with_name("symbols.txt")
    try:
        assemble(source, output, symbols_path)
    except (OSError, ValueError) as exc:
        print(f"assembler: {exc}", file=sys.stderr)
        return 1
    print(f"Assembled {source.name}: {len(output.read_text().splitlines())} instructions -> {output.name}")
    print(f"Symbol table -> {symbols_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
