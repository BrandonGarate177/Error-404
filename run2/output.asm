ADDI $r1, $r0, 1
ADDI $r2, $r0, 15
LOOP0:
    SUB $r3, $r1, $r2
    BLT $r0, $r3, END1
    ADDI $r6, $r0, 3
    ADDI $r7, $r0, 5
    MOD $r4, $r1, $r6
    MOD $r5, $r1, $r7
    ADDI $r8, $r0, 0
    BNE $r4, $r8, SKIP_IF2
    BNE $r5, $r8, SKIP_IF2
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
SKIP_IF2:
    ADDI $r6, $r0, 3
    MOD $r4, $r1, $r6
    ADDI $r8, $r0, 0
    BNE $r4, $r8, SKIP_IF3
    ADDI $r6, $r0, 70
    PANIC $r6
    ADDI $r6, $r0, 105
    PANIC $r6
    ADDI $r6, $r0, 122
    PANIC $r6
    ADDI $r6, $r0, 122
    PANIC $r6
SKIP_IF3:
    ADDI $r7, $r0, 5
    MOD $r5, $r1, $r7
    ADDI $r8, $r0, 0
    BNE $r5, $r8, SKIP_IF4
    ADDI $r6, $r0, 66
    PANIC $r6
    ADDI $r6, $r0, 117
    PANIC $r6
    ADDI $r6, $r0, 122
    PANIC $r6
    ADDI $r6, $r0, 122
    PANIC $r6
SKIP_IF4:
    ADDI $r1, $r1, 1
    JUMP LOOP0
END1:
