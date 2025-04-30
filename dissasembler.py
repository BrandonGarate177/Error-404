from instructions import INSTRUCTIONS

# Reverse register map
REVERSE_REGISTER_MAP = {
    "00000": "$r0", "00001": "$r1", "00010": "$r2", "00011": "$r3",
    "00100": "$r4", "00101": "$r5", "00110": "$r6", "00111": "$r7",
    "01000": "$r8", "01001": "$r9", "01010": "$ip", "01011": "$sp",
    "01100": "$err", "01101": "$ex", "01110": "$dbg"
}

# Build reverse opcode and funct maps
OPCODE_MAP = {}
FUNCT_MAP = {}

for name, info in INSTRUCTIONS.items():
    if info["type"] == "R":
        FUNCT_MAP[(info["opcode"], info["funct"])] = name
    else:
        OPCODE_MAP[info["opcode"]] = name


def decode_r_type(binary):
    opcode = binary[:6]
    rs = binary[6:11]
    rt = binary[11:16]
    rd = binary[16:21]
    shamt = binary[21:26]
    funct = binary[26:32]

    instr = FUNCT_MAP.get((opcode, funct), f"UNKNOWN_R({opcode}_{funct})")

    if instr in ["CRASH", "FREEZE", "TRACE", "BREAKPT"]:
        return f"{instr}"
    elif instr in ["PANIC", "FORK"]:
        return f"{instr} {REVERSE_REGISTER_MAP[rs]}"
    elif instr == "NULL":
        return f"{instr} {REVERSE_REGISTER_MAP[rd]}"
    else:
        return f"{instr} {REVERSE_REGISTER_MAP[rd]}, {REVERSE_REGISTER_MAP[rs]}, {REVERSE_REGISTER_MAP[rt]}"


def decode_i_type(binary, pc):
    opcode = binary[:6]
    rs = binary[6:11]
    rt = binary[11:16]
    imm = binary[16:32]

    instr = OPCODE_MAP.get(opcode, f"UNKNOWN_I({opcode})")

    imm_val = int(imm, 2)
    if imm[0] == "1":  # handle negative two's complement
        imm_val -= (1 << 16)

    if instr in ["BEQ", "BNE", "404"]:
        return f"{instr} {REVERSE_REGISTER_MAP[rs]}, {REVERSE_REGISTER_MAP[rt]}, {imm_val}"
    elif instr == "ADDI":
        return f"{instr} {REVERSE_REGISTER_MAP[rt]}, {REVERSE_REGISTER_MAP[rs]}, {imm_val}"
    elif instr in ["LW", "SW"]:
        return f"{instr} {REVERSE_REGISTER_MAP[rt]}, {imm_val}({REVERSE_REGISTER_MAP[rs]})"
    elif instr == "GLITCH":
        return f"{instr} {REVERSE_REGISTER_MAP[rs]}, {REVERSE_REGISTER_MAP[rt]}"
    else:
        return f"{instr} ???"


def decode_j_type(binary):
    opcode = binary[:6]
    addr = int(binary[6:], 2)
    instr = OPCODE_MAP.get(opcode, f"UNKNOWN_J({opcode})")
    return f"{instr} {addr}"


def disassemble_binary(binary_lines):
    output = []

    for pc, line in enumerate(binary_lines):
        line = line.strip()
        if len(line) != 32:
            continue

        opcode = line[:6]
        instr = OPCODE_MAP.get(opcode)
        inst_type = INSTRUCTIONS[instr]["type"] if instr in INSTRUCTIONS else None

        if (opcode, line[26:32]) in FUNCT_MAP: # panic instruction not showing up 
            asm = decode_r_type(line)
        elif opcode == "000000" or (instr and inst_type == "R"):
            asm = decode_r_type(line)
        elif instr and inst_type == "J":
            asm = decode_j_type(line)
        elif instr and inst_type == "I":
            asm = decode_i_type(line, pc)
        else:
            asm = f"UNKNOWN_OPCODE({opcode})"

        indented = "    " + asm if not asm.endswith(":") else asm
        output.append(indented)

    return output


def identify_and_inject_labels(binary_lines):
    from instructions import INSTRUCTIONS

    # Reverse register map
    REVERSE_REGISTER_MAP = {
        "00000": "$r0", "00001": "$r1", "00010": "$r2", "00011": "$r3",
        "00100": "$r4", "00101": "$r5", "00110": "$r6", "00111": "$r7",
        "01000": "$r8", "01001": "$r9", "01010": "$ip", "01011": "$sp",
        "01100": "$err", "01101": "$ex", "01110": "$dbg"
    }

    # Build maps
    OPCODE_MAP = {}
    FUNCT_MAP = {}
    for name, info in INSTRUCTIONS.items():
        if info["type"] == "R":
            FUNCT_MAP[(info["opcode"], info["funct"])] = name
        else:
            OPCODE_MAP[info["opcode"]] = name

    label_targets = set()

    # Pass 1: detect branch and jump targets
    for pc, binary in enumerate(binary_lines):
        binary = binary.strip()
        if len(binary) != 32:
            continue
        opcode = binary[:6]
        instr = OPCODE_MAP.get(opcode)

        if instr in ["BEQ", "BNE", "404"]:
            imm = binary[16:32]
            offset = int(imm, 2)
            if imm[0] == '1':
                offset -= (1 << 16)
            label_pc = pc + 1 + offset
            label_targets.add(label_pc)

        elif instr == "JUMP":
            addr = int(binary[6:], 2)
            label_targets.add(addr)

    # Label mapping
    label_map = {pc: f"L{pc}" for pc in sorted(label_targets)}

    # Pass 2: decode with labels
    output = []
    for pc, binary in enumerate(binary_lines):
        binary = binary.strip()
        if len(binary) != 32:
            continue
        opcode = binary[:6]
        instr = OPCODE_MAP.get(opcode)
        inst_type = INSTRUCTIONS[instr]["type"] if instr in INSTRUCTIONS else None

        # Inject label
        if pc in label_map:
            output.append(f"{label_map[pc]}:")

        # Decode R-type
        if (opcode, binary[26:32]) in FUNCT_MAP:
            name = FUNCT_MAP[(opcode, binary[26:32])]
            rs = binary[6:11]
            rt = binary[11:16]
            rd = binary[16:21]
            if name in ["CRASH", "FREEZE", "TRACE", "BREAKPT"]:
                output.append(f"    {name}")
            elif name in ["PANIC", "FORK"]:
                output.append(f"    {name} {REVERSE_REGISTER_MAP[rs]}")
            elif name == "NULL":
                output.append(f"    {name} {REVERSE_REGISTER_MAP[rd]}")
            else:
                output.append(f"    {name} {REVERSE_REGISTER_MAP[rd]}, {REVERSE_REGISTER_MAP[rs]}, {REVERSE_REGISTER_MAP[rt]}")

        # Decode I-type
        elif instr in ["BEQ", "BNE", "404"]:
            rs = REVERSE_REGISTER_MAP[binary[6:11]]
            rt = REVERSE_REGISTER_MAP[binary[11:16]]
            imm = binary[16:32]
            offset = int(imm, 2)
            if imm[0] == '1':
                offset -= (1 << 16)
            target = pc + 1 + offset
            label = label_map.get(target, str(offset))
            output.append(f"    {instr} {rs}, {rt}, {label}")

        elif instr == "ADDI":
            rs = REVERSE_REGISTER_MAP[binary[6:11]]
            rt = REVERSE_REGISTER_MAP[binary[11:16]]
            imm = int(binary[16:], 2)
            if binary[16] == '1':
                imm -= (1 << 16)
            output.append(f"    ADDI {rt}, {rs}, {imm}")

        elif instr in ["LW", "SW"]:
            rs = REVERSE_REGISTER_MAP[binary[6:11]]
            rt = REVERSE_REGISTER_MAP[binary[11:16]]
            imm = int(binary[16:], 2)
            if binary[16] == '1':
                imm -= (1 << 16)
            output.append(f"    {instr} {rt}, {imm}({rs})")

        elif instr == "GLITCH":
            rs = REVERSE_REGISTER_MAP[binary[6:11]]
            rt = REVERSE_REGISTER_MAP[binary[11:16]]
            output.append(f"    GLITCH {rs}, {rt}")

        # Decode JUMP
        elif instr == "JUMP":
            addr = int(binary[6:], 2)
            label = label_map.get(addr, str(addr))
            output.append(f"    JUMP {label}")

        else:
            output.append(f"    UNKNOWN_OPCODE({opcode})")

    return output





if __name__ == "__main__":
    with open("FizzBuzzAssembledRun1.bin", "r") as f:
        binary_lines = f.readlines()

    labeled_output = identify_and_inject_labels(binary_lines)

    with open("FizzBuzz_disassembledRun1.asm", "w") as f:
        for line in labeled_output:
            f.write(line + "\n")

    print("Disassembled with labels toFizzBuzz_disassembledRun1.asm")
