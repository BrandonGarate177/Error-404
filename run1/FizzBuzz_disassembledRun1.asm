    ADDI $r1, $r0, 1
    ADDI $r9, $r0, 15
L2:
    ADDI $r2, $r0, 3
    MOD $r3, $r1, $r2
    ADDI $r2, $r0, 5
    MOD $r4, $r1, $r2
    BEQ $r3, $r0, L9
    BEQ $r4, $r0, L17
    JUMP L22
L9:
    BEQ $r4, $r0, L11
    JUMP L14
L11:
    ADDI $r6, $r0, 100
    PANIC $r6
    JUMP L20
L14:
    ADDI $r6, $r0, 101
    PANIC $r6
    JUMP L20
L17:
    ADDI $r6, $r0, 102
    PANIC $r6
    JUMP L20
L20:
    ADDI $r1, $r1, 1
    BNE $r1, $r9, L2
