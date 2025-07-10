###########################################################
# Because this is a highly professional project and we care so
# much about our end users, we hide the extra profiles from the
# menu so they don't accidentally click or delete them.
###########################################################

## Inject at 0x802be3f0


## MACROS
.macro call addr
  lis r12,  \addr@h
  ori r12, r12, \addr@l
  mtlr r12
  blrl
.endm

addi r5, r1, 0x8 # Start of file name pointer

li r6, 0 # loop counter

SAVE_FILE_NAME_LOOP:
  lbzu r12, 0(r5)
  cmpwi r12, 126 # Search for the tilde
  beq INVALID_SAVE
  addi r5, r5, 1
  addi r6, r6, 1
  cmpwi r6, 24 # Arbitrary max name length
  bne SAVE_FILE_NAME_LOOP

VALID_SAVE:
  addi r0, r3, 0x1 # valid account so increment counter
  b END

INVALID_SAVE:
  or r0, r3, r3 # just move the register ezpz

END:

# command we are replacing!!!
# No need to replace any commands, we do it only in the valid case.

