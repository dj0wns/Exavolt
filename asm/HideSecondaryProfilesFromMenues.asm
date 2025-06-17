###########################################################
# Because this is a highly professional project and we care so
# much about our end users, we hide the extra profiles from the
# menu so they don't accidentally click or delete them.
###########################################################

## Inject at 0x802bf6e0

## CONSTANTS
CARD_CLOSE=0x8032a3e8
CONTINUE_LOOP=0x802bf75c

## MACROS
.macro call addr #cool call macro from minty for constant references to functions
  lis r12,  \addr@h
  ori r12, r12, \addr@l
  mtlr r12
  blrl
.endm

addi r5, r1, 0x1c # Start of file name pointer

li r4, 0 # loop counter

SAVE_FILE_NAME_LOOP:
  lbzu r7, 0(r5)
  cmpwi r7, 126 # Search for the tilde
  beq INVALID_SAVE
  addi r5, r5, 1
  addi r4, r4, 1
  cmpwi r4, 24 # Arbitrary max name length
  bne SAVE_FILE_NAME_LOOP

VALID_SAVE:
  b END

INVALID_SAVE:
  # Need to close the card and result the loop, don't exit normally
  addi r3, r1, 0x8
  call CARD_CLOSE

  # Use the count register to continue loop
  lis r12, CONTINUE_LOOP@h
  ori r12, r12, CONTINUE_LOOP@l
  mtctr r12
  bctr


END:

# command we are replacing!!!
li r3, 0x0
cmpwi r3, 0x0

