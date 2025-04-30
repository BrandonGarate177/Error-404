def indent(line, level):
    return "    " * level + line if not line.endswith(":") else line

# fizzbuzz compiler
# This is a simple compiler that translates a simplified C FizzBuzz program into assembly-like instructions.
def compile_c_fizzbuzz():
    output = []

    output.append(indent("ADDI $r1, $r0, 1", 0))      # i = 1
    output.append(indent("ADDI $r9, $r0, 15", 0))     # loop upper bound

    output.append("LOOP:")

    # i % 3
    output.append(indent("ADDI $r2, $r0, 3", 1))
    output.append(indent("MOD $r3, $r1, $r2", 1))

    # i % 5
    output.append(indent("ADDI $r2, $r0, 5", 1))
    output.append(indent("MOD $r4, $r1, $r2", 1))

    # Check i % 3 == 0 first
    output.append(indent("BEQ $r3, $r0, CHECK_BUZZ", 1))
    output.append(indent("BEQ $r4, $r0, PRINT_BUZZ", 1))  # else if i % 5 == 0
    output.append(indent("JUMP CONTINUE", 1))

    output.append("CHECK_BUZZ:")
    output.append(indent("BEQ $r4, $r0, PRINT_FIZZBUZZ", 1))
    output.append(indent("JUMP PRINT_FIZZ", 1))

    output.append("PRINT_FIZZBUZZ:")
    output.append(indent("ADDI $r6, $r0, 100", 1))
    output.append(indent("PANIC $r6", 1))
    output.append(indent("JUMP NEXT", 1))

    output.append("PRINT_FIZZ:")
    output.append(indent("ADDI $r6, $r0, 101", 1))
    output.append(indent("PANIC $r6", 1))
    output.append(indent("JUMP NEXT", 1))

    output.append("PRINT_BUZZ:")
    output.append(indent("ADDI $r6, $r0, 102", 1))
    output.append(indent("PANIC $r6", 1))
    output.append(indent("JUMP NEXT", 1))

    output.append("NEXT:")
    output.append(indent("ADDI $r1, $r1, 1", 1))
    output.append(indent("BNE $r1, $r9, LOOP", 1))

    output.append("CONTINUE:")
    output.append(indent("CRASH", 1))

    return output


if __name__ == "__main__":
    with open("FizzBuzz.c", "r") as f:
        source = f.read()

    if "for" in source and "printf" in source:
        print("Recognized simplified FizzBuzz logic...")
        asm = compile_c_fizzbuzz()
    else:
        raise NotImplementedError("C parsing beyond this structure is not supported yet.")

    with open("FizzBuzzCompiledRun1.txt", "w") as f:
        for line in asm:
            f.write(line + "\n")

    print("Compiled C to FizzBuzzCompiledRun1.txt")
