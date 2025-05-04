INSTRUCTIONS = {
    # R-Type Instructions
    "ADD":     {"type": "R", "opcode": "000000", "funct": "100000"},
    "SUB":     {"type": "R", "opcode": "000000", "funct": "100010"},
    "MUL":     {"type": "R", "opcode": "000000", "funct": "011000"},
    "DIV":     {"type": "R", "opcode": "000000", "funct": "011010"},
    "MOD":     {"type": "R", "opcode": "000000", "funct": "011011"},
    
    "CRASH":   {"type": "R", "opcode": "010010", "funct": "000000"},
    "PANIC":   {"type": "R", "opcode": "010100", "funct": "000001"},
    "FREEZE":  {"type": "R", "opcode": "010101", "funct": "000000"},
    "NULL":    {"type": "R", "opcode": "010110", "funct": "000001"},
    "TRACE":   {"type": "R", "opcode": "010111", "funct": "000000"},
    "FORK":    {"type": "R", "opcode": "011000", "funct": "000001"},
    "BREAKPT": {"type": "R", "opcode": "011010", "funct": "000000"},

    # I-Type Instructions
    "ADDI":    {"type": "I", "opcode": "001000"},
    "BEQ":     {"type": "I", "opcode": "000100"},
    "BNE":     {"type": "I", "opcode": "000101"},
    "LW":      {"type": "I", "opcode": "100011"},
    "SW":      {"type": "I", "opcode": "101011"},
    "BLT":     {"type": "I", "opcode": "000110"},  
    
    "404":     {"type": "I", "opcode": "010001"},  # Branch if R2 == -1
    "GLITCH":  {"type": "I", "opcode": "011001"},  # Randomly swap R1 and R2

    # J-Type Instructions
    "REBOOT":  {"type": "J", "opcode": "010011"},
    "JUMP": {"type": "J", "opcode": "000010"},  # Classic MIPS-style jump

}


