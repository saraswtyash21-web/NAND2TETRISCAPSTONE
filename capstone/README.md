# Nand2Tetris Capstone — Roll No. 2501730421

## Personal parameter

`K = 2501730421 mod 100 = 21`, and `21 mod 3 = 0`. The selected assembler feature is the labels-and-variables symbol table: `assembler.py` writes each predefined symbol, label, and variable with its address to `symbols.txt`.

## Contents

- `CPU.hdl`, `Memory.hdl`, `Computer.hdl` — Project 5 chips.
- `assembler.py` — two-pass Hack assembler; emits a `.hack` file and `symbols.txt` beside its input.
- `Box.asm`, `Box.hack` — key-controlled rectangle program and machine code.
- `symbols.txt`, `examples/` — generated symbol table and a small symbol resolution demonstration.
- `CPU.tst/.cmp`, `Memory.tst/.cmp`, `ComputerAdd.tst/.cmp`, `ComputerMax.tst/.cmp`, `ComputerRect.tst/.cmp`, and test machine-code inputs — official Project 5 assets.
- `Report.md`, `Report.docx`, `Report.pdf` — final four-page report.
- `screenshots/` — genuine simulator and emulator evidence, including the initial CPU failure, corrected CPU pass, other available passing test results, and Box key-held/key-released states.

## Box behavior

The program polls `KBD` (address 24576). A nonzero key value paints a 32-pixel-wide, 20-row-high black rectangle starting at row 21. A zero value clears it. Each Hack screen word stores 16 horizontal pixels, so the program writes two adjacent words on each of 20 scanlines. The first word address is `SCREEN + 21 × 32 = 17056`; rows 21 through 40 are covered.

## Assemble

From this directory run:

```sh
python3 assembler.py Box.asm
```

This regenerates `Box.hack` and `symbols.txt`. To choose a different output file, pass it as the second argument.

## Validation

`CPU.tst`, `Memory.tst`, `ComputerAdd.tst`, `ComputerMax.tst`, and `ComputerRect.tst` all completed successfully in the Nand2Tetris Web IDE; each reported that the output file matched its compare file. The ComputerMax result was observed as a successful comparison, but its screenshot was not available as a local file for this package. The CPU Emulator recording showed the rectangle with H held (character code 72) and the cleared screen after release (character code 0). See `Report.pdf` and `screenshots/` for details and evidence.
