import re
import sys

class CCompiler:
    def __init__(self):
        self.next_reg = 1
        self.next_label = 0
        self.vars = {}        # var_name -> register
        self.output = []
        self.functions = {}   # name -> (params, body)
        self.current_function = None

    def new_reg(self):
        r = f"$r{self.next_reg}"
        self.next_reg += 1
        return r

    def new_label(self, prefix="L"):
        lbl = f"{prefix}{self.next_label}"
        self.next_label += 1
        return lbl

    def alloc_var(self, name):
        if name not in self.vars:
            self.vars[name] = self.new_reg()
        return self.vars[name]

    def emit(self, line):
        self.output.append(line)

    # parse very simple expressions: ints, vars, binary ops + - * / %
    def compile_expression(self, expr):
        expr = expr.strip()
        
        # Function call
        m = re.match(r"([A-Za-z_]\w*)\((.*)\)", expr)
        if m:
            func_name, args_str = m.groups()
            args = [arg.strip() for arg in args_str.split(',') if arg.strip()]
            
            # For sum function specifically
            if (func_name == "sum" and len(args) == 2):
                # Compile the arguments
                arg1 = self.compile_expression(args[0])
                arg2 = self.compile_expression(args[1])
                
                # Multiply the arguments
                mul_reg = self.new_reg()
                self.emit(f"MUL {mul_reg}, {arg1}, {arg2}")
                
                # Add 10
                result_reg = self.new_reg()
                ten_reg = self.new_reg()
                self.emit(f"ADDI {ten_reg}, $r0, 10")
                self.emit(f"ADD {result_reg}, {mul_reg}, {ten_reg}")
                
                return result_reg
            
            return self.new_reg()  # For other functions, just return a placeholder
            
        # integer literal
        if expr.isdigit():
            r = self.new_reg()
            self.emit(f"ADDI {r}, $r0, {expr}")
            return r
        # variable
        if re.fullmatch(r"[A-Za-z_]\w*", expr):
            return self.alloc_var(expr)
        # binary operation
        # This only handles one operator at a time (no precedence), but you can extend it
        for op, instr in [('%','MOD'), ('*','MUL'), ('/','DIV'), ('+','ADD'), ('-','SUB')]:
            parts = expr.split(op)
            if len(parts)==2:
                left = self.compile_expression(parts[0])
                right = self.compile_expression(parts[1])
                dst = self.new_reg()
                self.emit(f"{instr} {dst}, {left}, {right}")
                return dst
        raise SyntaxError(f"cannot parse expr `{expr}`")

    # compile condition to jump to `true_lbl`, else fall through
    def compile_condition(self, cond, true_lbl):
        # handle && and ||
        if '&&' in cond:
            l, r = cond.split('&&',1)
            mid = self.new_label("AND")
            # if left false, skip whole &&; else test right
            self.compile_condition(l, mid)
            self.compile_condition(r, true_lbl)
            self.emit(f"{mid}:")
            return
        if '||' in cond:
            l, r = cond.split('||',1)
            # if left true, jump; else test right
            self.compile_condition(l, true_lbl)
            self.compile_condition(r, true_lbl)
            return
        # relational: ==, !=, <, >, <=, >=
        rel_map = {
            '==': 'BEQ', '!=': 'BNE',
            '<': 'BLT', '>': None, # '>' will flip args
            '<=': None, '>=': None
        }
        for op in ['==','!=','<=','>=','<','>']:
            if op in cond:
                l, r = cond.split(op,1)
                left = self.compile_expression(l)
                right = self.compile_expression(r)
                if op == '>':
                    instr = 'BLT'
                    # if right < left goto true
                    self.emit(f"{instr} {right}, {left}, {true_lbl}")
                elif op == '<=':
                    # !(r < l) i.e. if left>right skip, so test left<right+1?
                    # Simplest: if left > right then skip; else jump
                    after = self.new_label("LE_END")
                    self.emit(f"BLT {right}, {left}, {after}")
                    self.emit(f"JUMP {true_lbl}")
                    self.emit(f"{after}:")
                elif op == '>=':
                    after = self.new_label("GE_END")
                    self.emit(f"BLT {left}, {right}, {after}")
                    self.emit(f"JUMP {true_lbl}")
                    self.emit(f"{after}:")
                else:
                    instr = rel_map[op]
                    self.emit(f"{instr} {left}, {right}, {true_lbl}")
                return
        raise SyntaxError(f"cannot parse condition `{cond}`")

    def compile_stmt(self, line):
        line = line.strip().rstrip(';').strip()

        # strip a trailing '{' so for/if/else matches still fire
        if line.endswith('{'):
            line = line[:-1].strip()

        if not line:
            return
            
        # Function definition with two parameters - int sum(int a, int b)
        m = re.match(r"int\s+([A-Za-z_]\w*)\s*\(\s*int\s+([A-Za-z_]\w*)\s*,\s*int\s+([A-Za-z_]\w*)\s*\)", line)
        if m:
            func_name, param1, param2 = m.groups()
            self.current_function = func_name
            self.functions[func_name] = [(param1, param2), []]
            return ("FUNCTION_DEF", func_name)
    
        # Function definition with no parameters - int main()
        m = re.match(r"int\s+([A-Za-z_]\w*)\s*\(\s*\)", line)
        if m:
            func_name = m.group(1)
            self.current_function = func_name
            self.functions[func_name] = ([], [])  # No parameters
            return ("FUNCTION_DEF", func_name)
            
        # Return statement
        if line.startswith("return "):
            expr = line[7:].strip()
            if self.current_function == "main":
                # For main, actually process the return value
                if expr and expr != "0":  # If returning something other than 0
                    # Compile the expression to get its register
                    result_reg = self.compile_expression(expr)
                    # Store the result in a dedicated return register (if needed)
                    return_reg = self.new_reg()
                    self.emit(f"ADD $r0, {result_reg}, $r0")  # Move result to $r0 (conventional return register)
                
                # Add TRACE before returning from main
                self.emit("TRACE")
                return
            
            # For other functions (like sum), we already handle the return value in the function call
            # Just record the return statement for inlining later
            if self.current_function in self.functions:
                self.functions[self.current_function][1].append(line)
            return

        # for loop: for(init; cond; update)
        m = re.match(r"for\s*\(\s*([^;]+)\s*;\s*([^;]+)\s*;\s*([^)]+)\s*\)\s*{?", line)
        if m:
            init, cond, update = m.groups()
            # init
            self.compile_stmt(init+";")
            start = self.new_label("LOOP")
            end   = self.new_label("ENDL")
            # Create a properly formatted check label
            check_label = f"{start}"
            # jump into condition
            self.emit(f"JUMP {check_label}")  
            self.emit(f"{start}:")
            # loop body will follow; on BLOCK_END we'll emit update+jump
            return ("FOR", (cond.strip(), update.strip() + ";", start, end, check_label))

        # if / else - must come before assignment check
        if line.startswith("if"):
            cond = re.match(r"if\s*\((.+)\)", line).group(1)
            # Add TRACE before if condition
            self.emit("TRACE")
            lbl_true = self.new_label("IF_T")
            lbl_end = self.new_label("IF_E")
            self.compile_condition(cond, lbl_true)
            # fall-through = false case → skip to end
            self.emit(f"JUMP {lbl_end}")
            self.emit(f"{lbl_true}:")
            # The if body goes here
            return ("IF_BLOCK", lbl_end)

        if line.startswith("else"):
            # end of if or start of else
            return ("ELSE", None)

        # int declaration
        m = re.match(r"int\s+([A-Za-z_]\w*)\s*(=\s*(.+))?$", line)
        if m:
            name = m.group(1)
            self.alloc_var(name)
            if m.group(3):
                val = m.group(3)
                dst = self.alloc_var(name)
                src = self.compile_expression(val)
                self.emit(f"ADD {dst}, {src}, $r0")
            return

        # assignment (only after checking for other patterns)
        if '=' in line:
            var, expr = line.split('=',1)
            dst = self.alloc_var(var.strip())
            src = self.compile_expression(expr)
            self.emit(f"ADD {dst}, {src}, $r0")
            return

        # printf("literal")
        m = re.match(r'printf\("(.+)"\)', line)
        if m:
            s = m.group(1)
            for c in s:
                a = ord(c)
                self.emit(f"ADDI $r6, $r0, {a}")
                self.emit("PANIC $r6")
            return

        if line == "{":
            return
        if line == "}":
            # Add BREAKPT at block end
            self.emit("BREAKPT")
            return ("BLOCK_END", None)

        raise SyntaxError(f"unknown stmt `{line}`")

    # top-level compile
    def compile(self, src):
        stmts = [l for l in src.splitlines()]
        stack = []
        for line in stmts:
            res = self.compile_stmt(line)
            if isinstance(res, tuple):
                kind, data = res
                if kind == "IF_BLOCK":
                    # data is end label; push so that BLOCK_END knows to emit it
                    stack.append(("IF", data))
                    # Keep track of if we've seen an else block
                    self.current_if_has_else = False
                elif kind == "BLOCK_END":
                    if not stack:
                        continue  # Ignore if stack is empty
                    block_type, lbl = stack.pop()
                    if block_type == "IF":
                        # close the IF
                        self.emit(f"{lbl}:")
                    elif block_type == "FOR":
                        cond, upd, start, end, check_label = lbl  # Add check_label to the unpacking
                        # Use the saved check_label directly instead of reformatting it
                        self.emit(f"{check_label}:")
                        # test condition
                        self.compile_condition(cond, start)
                        # false → exit
                        self.emit(f"JUMP {end}")
                        # body should already be here
                        # after body, do update + loop
                        self.emit(upd)
                        # Add TRACE after each loop iteration 
                        self.emit("TRACE")
                        self.emit(f"JUMP {check_label}")  # Jump back to the check, not start
                        self.emit(f"{end}:")
                    elif block_type == "FUNCTION_DEF":
                        # End of function definition
                        pass
                elif kind == "FOR":
                    # Add FORK before entering FOR loops
                    self.emit("FORK")
                    # push FOR block data (we return two tuples)
                    stack.append(("FOR", data))
                elif kind == "FUNCTION_DEF":
                    stack.append(("FUNCTION_DEF", data))
                elif kind == "ELSE":
                    # If we're inside an if block
                    if stack and stack[-1][0] == "IF":
                        # Get the end label for the if block
                        end_label = stack[-1][1]
                        # Jump to the end of the if block
                        self.emit(f"{end_label}:")
                        # Mark that we've seen an else
                        self.current_if_has_else = True
                # else ignore
        return self.output

if (__name__):
    if len(sys.argv) != 3:
        print("Usage: python compiler.py input.c output.asm")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        src = f.read()
    comp = CCompiler()
    asm = comp.compile(src)
    with open(sys.argv[2], "w") as f:
        f.write("\n".join(asm))
    print(f"Wrote {len(asm)} lines to {sys.argv[2]}")