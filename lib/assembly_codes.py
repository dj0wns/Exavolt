

HEADERS = r"""
## Function pointers
fnew=0x8028fa88
BotGlitchConstructor=0x80023b6c
BotGlitchCreate=0x80023dfc

##

## MACROS
.macro call addr
  lis r12,  \addr@h
  ori r12, r12, \addr@l
  mtlr r12
  blrl
.endm
##

"""

# Simplified version of the code found in the disass
# ignoring most if checks
SPAWN_AS_GLITCH =r"""

li r3, 0xdf8
li r4, 0x8
call fnew

or r4, r3, r3
call BotGlitchConstructor

or r4, r3, r3
mulli r0, r31, 0x24c8
lis r3, 0x8048
addi r3, r3, 0x1af8
add r3, r3, r0
stw r4, 0x18d8(r3)
lwz r3, 0x18d8(r3)

lis r4, 0x803b
or r7, r30, r30
subi r5, r4, 0x2320
addi r6, r1, 0x8
addi r8, r5, 0x6e
or r4, r31, r31
li r5, 0x0
call BotGlitchCreate

"""
