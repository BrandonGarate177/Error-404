    ADDI $r2, $r0, 1
    ADD $r1, $r2, $r0
    JUMP L3
    ADDI $r3, $r0, 3
    MOD $r4, $r1, $r3
    ADDI $r5, $r0, 0
    BEQ $r4, $r5, L13
    ADDI $r6, $r0, 5
    MOD $r7, $r1, $r6
    ADDI $r8, $r0, 0
    BEQ $r7, $r8, L14
L13:
    JUMP L47
L14:
    ADDI $r6, $r0, 70
    PANIC $r6
    ADDI $r6, $r0, 105
    PANIC $r6
    ADDI $r6, $r0, 122
    PANIC $r6
    ADDI $r6, $r0, 122
    PANIC $r6
    ADDI $r6, $r0, 66
    PANIC $r6
    ADDI $r6, $r0, 117
    PANIC $r6
    ADDI $r6, $r0, 122
    PANIC $r6
    ADDI $r6, $r0, 122
    PANIC $r6
    ADDI $r6, $r0, 70
    PANIC $r6
    ADDI $r6, $r0, 105
    PANIC $r6
    ADDI $r6, $r0, 122
    PANIC $r6
    ADDI $r6, $r0, 122
    PANIC $r6
    ADDI $r6, $r0, 66
    PANIC $r6
    ADDI $r6, $r0, 117
    PANIC $r6
    ADDI $r6, $r0, 122
    PANIC $r6
    ADDI $r6, $r0, 122
    PANIC $r6
