	.section .text
	.global start
	.global main

.org 0x00000000
start:
	/* set stack pointer */
	lui sp,(16*1024)>>12

	/* jump to main C code */
	jal ra,main

	/* trap */
	ebreak

.org 0x00000020
irq: 
    j irq

