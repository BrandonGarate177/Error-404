from instructions import INSTRUCTIONS  # importing the instruction set

# REGISTERS
REGISTER_MAP = {
    "$r0": "00000", "$r1": "00001", "$r2": "00010", "$r3": "00011",
    "$r4": "00100", "$r5": "00101", "$r6": "00110", "$r7": "00111",
    "$r8": "01000", "$r9": "01001", "$ip": "01010", "$sp": "01011",
    "$err": "01100", "$ex": "01101", "$dbg": "01110"
}


## MAIN ASSEMBLER
def assemble_line(line, labels=None, current_idx=None):
    parts = line.strip().split()
    if not parts:
        return None

    instr = parts[0].upper()
    info = INSTRUCTIONS.get(instr)
    if not info:
        raise ValueError(f"Unknown instruction: {instr}")

    instr_type = info["type"]

    if instr_type == "R":
        return assemble_r_type(instr, parts[1:], info)
    elif instr_type == "I":
        return assemble_i_type(instr, parts[1:], info)
    elif instr_type == "J":
        return assemble_j_type(parts[1:], info, labels, current_idx)
    else:
        raise ValueError(f"Unsupported instruction type: {instr_type}")


## R TYPE INSTRUCTIONS
def assemble_r_type(instr, operands, info):
    operands = [op.strip(",") for op in operands]
    opcode = info["opcode"]
    funct = info["funct"]

    if instr in ["CRASH", "FREEZE", "TRACE", "BREAKPT"]:
        return f"{opcode}000000000000000000000{funct}"

    if instr in ["PANIC", "FORK"]:
        rs = REGISTER_MAP[operands[0]]
        return f"{opcode}{rs}000000000000000{funct}"

    if instr == "NULL":
        rd = REGISTER_MAP[operands[0]]
        return f"{opcode}000000000{rd}000000{funct}"

    # Format: INSTR rd, rs, rt
    rd, rs, rt = [REGISTER_MAP[r.strip(',')] for r in operands]
    shamt = "00000"
    return f"{opcode}{rs}{rt}{rd}{shamt}{funct}"


## I TYPE INSTRUCTIONS
def assemble_i_type(instr, operands, info):
    operands = [op.strip(",") for op in operands]
    opcode = info["opcode"]

    if instr == "404":
        rs = REGISTER_MAP[operands[0]]
        rt = REGISTER_MAP[operands[1]]
        offset_val = int(operands[2])
        offset = format(offset_val & 0xFFFF, '016b')  # support 2's complement
        return f"{opcode}{rs}{rt}{offset}"

    if instr == "GLITCH":
        rs = REGISTER_MAP[operands[0]]
        rt = REGISTER_MAP[operands[1]]
        imm = "0" * 16
        return f"{opcode}{rs}{rt}{imm}"

    if instr in ["BEQ", "BNE"]:
        rs = REGISTER_MAP[operands[0]]
        rt = REGISTER_MAP[operands[1]]
        offset_val = int(operands[2])
        offset = format(offset_val & 0xFFFF, '016b')  # support 2's complement
        return f"{opcode}{rs}{rt}{offset}"

    if instr == "ADDI":
        rs = REGISTER_MAP[operands[1]]
        rt = REGISTER_MAP[operands[0]]
        imm = format(int(operands[2]), '016b')
        return f"{opcode}{rs}{rt}{imm}"

    if instr in ["LW", "SW"]:
        rt = REGISTER_MAP[operands[0]]
        offset, base = operands[1].split('(')
        offset = format(int(offset), '016b')
        rs = REGISTER_MAP[base.strip(')')]
        return f"{opcode}{rs}{rt}{offset}"


## J TYPE INSTRUCTIONS
def assemble_j_type(operands, info, labels=None, current_idx=None):
    opcode = info["opcode"]
    target = operands[0].strip(",")

    if labels and target in labels:
        addr = labels[target]
    else:
        try:
            addr = int(target)
        except ValueError:
            raise ValueError(f"Invalid jump target: {target}")

    return f"{opcode}{format(addr, '026b')}"


## LABELS
def resolve_labels(lines):
    labels = {}
    instruction_lines = []
    pc = 0  # instruction counter

    for line in lines:
        clean = line.strip()
        if not clean or clean.startswith("#"):
            continue
        if clean.endswith(":"):
            label = clean[:-1]
            labels[label] = pc
        else:
            instruction_lines.append(clean)
            pc += 1

    return labels, instruction_lines


## ASSEMBLER
def assemble_program(lines):
    output = []
    labels, instructions = resolve_labels(lines)

    for idx, line in enumerate(instructions):
        try:
            parts = line.split()
            instr_name = parts[0].upper()

            # Replace label operands for I-type branches
            if instr_name in ["BEQ", "BNE", "BLT", "404"] and len(parts) > 1 and parts[-1] in labels:
                label = parts[-1]
                offset = labels[label] - (idx + 1)
                parts[-1] = str(offset)
                line = " ".join(parts)

            binary = assemble_line(line, labels=labels, current_idx=idx)
            if binary:
                output.append(binary)

        except Exception as e:
            print(f"Error on line: {line.strip()}")
            raise e

    return output


### USAGE
if __name__ == "__main__":
    import sys

    input_file = "output.asm"
    output_file = "output.bin"

    with open(input_file, "r") as f:
        lines = f.readlines()

    try:
        binary_output = assemble_program(lines)
    except ValueError as e:
        print(f"Assembly failed: {e}")
        sys.exit(1)

    with open(output_file, "w") as f:
        for b in binary_output:
            f.write(b + "\n")

    print(f"Assembled to {output_file}")
