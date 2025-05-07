# CS 240 Project, SDSU
## FEAT's: 
- Create custom MIPS inspired instructions (Error-404 ASM),
- Create a compiler to Complie C -> Error 404 ASM,
- Create an Assembler, ERROR-404 ASM -> Machine Code,
- Create a Dissasembler, Machine Code -> ERROR-404 ASM

### Instruction Sheet for ERROR 404 ASM: 
[Error_404_Instruction_Sheet.pdf](https://github.com/user-attachments/files/20093991/Error_404_Instruction_Sheet.2.pdf)


## All of our test runs, and example C programs have been saved in designated seperate folder. (ie pipiline folders)

## Error 404 Pipeline: 
#### 1. C code snippets: 
  - There are three simple C programs {C_programs/}
#### 2. intructions.py: 
  - This contains a nested dictionary,

The outer dictionary, INSTRUCTIONS, contains keys for each of our custom instrucitons, each indicating the type of instruction, their opp code(s)
- EX;  "404":     {"type": "I", "opcode": "010001"}

#### 3. Compiler.py
The custom compiler that:
- Parses basic C constructs (e.g., for, if, mod)
- Allocates virtual registers
- Outputs Error-404 ASM instructions
- Output is saved as a .asm file, simulating what would be passed to the assembler.

#### 4. Assembler.py 
- Reads .asm files and converts each instruction into its corresponding 32-bit binary format based on the INSTRUCTIONS map
- Output is a .bin file with 1 line per machine instruction.

#### 5. Dissasembler.py
- Takes the .bin machine code and reconstructs the original Error-404 ASM.


## HOW TO RUN: 
``` python
# Compile C to Error-404 ASM
python compiler.py C_programs/fizzbuzz.c > output.asm

# Assemble Error-404 ASM to machine code
python assembler.py output.asm > output.bin

# Disassemble machine code back to ASM
python disassembler.py output.bin > output_disassembled.asm
```

### Contributors: 
- Brandon Garate 
- Cristian Olea Pacheco
