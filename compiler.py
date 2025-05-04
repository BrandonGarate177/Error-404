t_register = 1
variables = {}
memory_address = 5000
label_counter = 0

def set_variable_register(var_name):
    global t_register, memory_address
    reg = f"$r{t_register}"
    t_register += 1
    variables[var_name] = {"register": reg, "address": memory_address}
    memory_address += 4
    return reg

def get_variable_register(var_name):
    return variables[var_name]["register"] if var_name in variables else "ERROR"

def get_next_label(prefix="L"):
    global label_counter
    label = f"{prefix}{label_counter}"
    label_counter += 1
    return label

def indent(line, level=1):
    return "    " * level + line

def compile_assignment_immediate(var, val):
    reg = get_variable_register(var)
    return f"ADDI {reg}, $r0, {val}"

def compile_assignment_variable(dest, src):
    src_reg = get_variable_register(src)
    dest_reg = get_variable_register(dest)
    return f"ADD {dest_reg}, {src_reg}, $r0"

def compile_printf(string):
    output = []
    for char in string:
        ascii_val = ord(char)
        output.append(indent(f"ADDI $r6, $r0, {ascii_val}"))
        output.append(indent("PANIC $r6"))
    return output

def compile_file(filename):
    output = []
    with open(filename, "r") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip().rstrip(";")

        if line.startswith("int "):
            _, var_expr = line.split("int ")
            if "=" in var_expr:
                var, val = var_expr.split("=")
                var = var.strip()
                val = val.strip()
                set_variable_register(var)
                output.append(compile_assignment_immediate(var, val))
            else:
                var = var_expr.strip()
                set_variable_register(var)

        elif line.startswith("for"):
            # Parse: for (int i = 1; i <= 15; i++)
            loop_var = "i"
            set_variable_register(loop_var)
            output.append(indent(f"ADDI {get_variable_register(loop_var)}, $r0, 1", 0))

            loop_start = get_next_label("LOOP")
            loop_end = get_next_label("END")

            # Set upper bound
            upper_reg = f"$r{t_register}"
            output.append(indent(f"ADDI {upper_reg}, $r0, 15", 0))

            output.append(f"{loop_start}:")

            # Check loop condition i <= 15
            temp = f"$r{t_register+1}"
            output.append(indent(f"SUB {temp}, {get_variable_register(loop_var)}, {upper_reg}"))
            output.append(indent(f"BLT $r0, {temp}, {loop_end}"))  # i > 15 → exit loop

            i += 1
            while "}" not in lines[i]:
                inner_line = lines[i].strip().rstrip(";")

                if "i % 3 == 0 && i % 5 == 0" in inner_line:
                    # MOD i, 3 and MOD i, 5
                    mod3 = f"$r{t_register+2}"
                    mod5 = f"$r{t_register+3}"
                    three = f"$r{t_register+4}"
                    five = f"$r{t_register+5}"
                    zero = f"$r{t_register+6}"
                    output.append(indent(f"ADDI {three}, $r0, 3"))
                    output.append(indent(f"ADDI {five}, $r0, 5"))
                    output.append(indent(f"MOD {mod3}, {get_variable_register('i')}, {three}"))
                    output.append(indent(f"MOD {mod5}, {get_variable_register('i')}, {five}"))
                    output.append(indent(f"ADDI {zero}, $r0, 0"))
                    skip = get_next_label("SKIP_IF")
                    output.append(indent(f"BNE {mod3}, {zero}, {skip}"))
                    output.append(indent(f"BNE {mod5}, {zero}, {skip}"))
                    output += compile_printf("FizzBuzz")
                    output.append(f"{skip}:")
                elif "i % 3 == 0" in inner_line:
                    mod3 = f"$r{t_register+2}"
                    three = f"$r{t_register+4}"
                    zero = f"$r{t_register+6}"
                    output.append(indent(f"ADDI {three}, $r0, 3"))
                    output.append(indent(f"MOD {mod3}, {get_variable_register('i')}, {three}"))
                    output.append(indent(f"ADDI {zero}, $r0, 0"))
                    skip = get_next_label("SKIP_IF")
                    output.append(indent(f"BNE {mod3}, {zero}, {skip}"))
                    output += compile_printf("Fizz")
                    output.append(f"{skip}:")
                elif "i % 5 == 0" in inner_line:
                    mod5 = f"$r{t_register+3}"
                    five = f"$r{t_register+5}"
                    zero = f"$r{t_register+6}"
                    output.append(indent(f"ADDI {five}, $r0, 5"))
                    output.append(indent(f"MOD {mod5}, {get_variable_register('i')}, {five}"))
                    output.append(indent(f"ADDI {zero}, $r0, 0"))
                    skip = get_next_label("SKIP_IF")
                    output.append(indent(f"BNE {mod5}, {zero}, {skip}"))
                    output += compile_printf("Buzz")
                    output.append(f"{skip}:")
                i += 1

            # Increment i and loop back
            output.append(indent(f"ADDI {get_variable_register('i')}, {get_variable_register('i')}, 1"))
            output.append(indent(f"JUMP {loop_start}"))
            output.append(f"{loop_end}:")

        elif "=" in line:
            var, val = line.split("=")
            var = var.strip()
            val = val.strip()
            if val.isdigit():
                output.append(compile_assignment_immediate(var, val))
            else:
                output.append(compile_assignment_variable(var, val))
        i += 1
    return output

if __name__ == "__main__":
    compiled = compile_file("FizzBuzz.c")
    with open("output.asm", "w") as f:
        for line in compiled:
            f.write(line + "\n")
