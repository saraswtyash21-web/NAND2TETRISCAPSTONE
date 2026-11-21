# Nand2Tetris Capstone Report

**Student roll number:** 2501730421  
**Personal parameter:** K = 21  
**Project:** Hack CPU, memory system, assembler, and key-controlled screen output

## 1. Objective and personal parameter

This capstone implements the Hack computer core in HDL, a two-pass assembler, and a keyboard-driven screen demonstration. The parameter is 2501730421 mod 100 = 21. Since K mod 3 = 0, the selected assembler feature records predefined symbols, labels, and variables with their addresses in `symbols.txt`.

## 2. HDL design

`CPU.hdl` combines the ALU, A and D registers, and program counter. A-instructions load the A register with the instruction value; C-instructions can load A and/or D from the ALU. The instruction a-bit selects A or M as the ALU y-input. The CPU exposes the ALU result on `outM`, asserts `writeM` only for a C-instruction that selects M, and outputs the A-register address on `addressM`. The PC increments normally, loads A for a true C-instruction jump, and clears on reset.

`Memory.hdl` decodes the 15-bit address. RAM16K handles addresses 0-16383; Screen handles the screen-mapped range beginning at 16384; Keyboard supplies a read-only mapped value. `Computer.hdl` connects ROM32K, CPU, and Memory.

## 3. Assembler and Box program

`assembler.py` performs two passes: it records labels at ROM instruction addresses, then emits 16-bit instructions and allocates unresolved variables starting at RAM[16]. It supports standard predefined symbols and rejects malformed instructions and duplicate symbols. `symbols.txt` lists resolved addresses. `SymbolDemo` resolves its label to ROM 2 and variable to RAM 16. `Box.asm` assembles to 62 instructions in `Box.hack`.

The program polls KBD (24576). A nonzero key paints the rectangle black; zero clears it. The box is 32 pixels wide and 20 scanlines high, starting on row 21. Each Hack screen word stores 16 horizontal pixels, so it writes two adjacent words per scanline. The first word is `SCREEN + 21 × 32 = 17056`; the loop advances 32 words per row for rows 21-40. R12 holds the screen pointer and R13 the row count.

## 4. Mistake fixed and validation

**Mistake fixed:** The first CPU test failed because the jump bits were connected to the DMux8Way selector in reverse significance, so conditional jumps could choose the wrong condition. I corrected the selector order so instruction[2], instruction[1], and instruction[0] map to selector bits 0, 1, and 2, then reran `CPU.tst`; the simulator reported that its output matched the compare file. A geometry correction also accounts for 16 pixels per screen word: the 32-pixel rectangle writes two words per row starting at 17056.

All five official Project 5 tests passed in the Web IDE with the success message that output matched the compare file: `CPU.tst`, `Memory.tst`, `ComputerAdd.tst`, `ComputerMax.tst`, and `ComputerRect.tst`. The ComputerMax result was observed as a successful comparison, but its screenshot was not available as a local file for this package. The initial failing CPU screenshot and the corrected pass screenshot are retained.

The CPU Emulator recording shows the box while H is held (character code 72) and a cleared screen after release (character code 0). Those visual checks are separate from the official test scripts.
