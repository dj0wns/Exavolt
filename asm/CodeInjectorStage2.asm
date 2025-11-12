
################################################################################
# This is the primary assembly code loader in exavolt. It uses a type indicator
# to determine how it should handle the code.
# Expected Binary Formay:
# First 4 bytes are the type:
#   - Type 0x0: C2 code
#     | 4 Bytes     | 4 Bytes           | N Bytes        |
#     | Code Length | Insertion Address | Assembled Code |
#   - Type 0x1: C2 code with custom return address
#     | 4 Bytes     | 4 Bytes           | 4 Bytes        | N Bytes        |
#     | Code Length | Insertion Address | Return address | Assembled Code |
#   - Type 0x2: C2 code that gets executed immediately, and is never linked, will live on as an inaccessible fragment in memory.
#     | 4 Bytes     | N Bytes        |
#     | Code Length | Assembled Code |
################################################################################

## FOR IMMEDIATE EXECUTION CODE: DON't USE THE FOLLOWING REGISTERS ##
## r14, r15, r16, r17, r18, r19, r21, r22

##

## Inject at 0x8029e468

## CONSTANTS
Mask=0x01ffffff
ForwardJump=0x4800
BackwardJump=0x4a00


fmem_AllocAndZero=0x80288c60
ffile_Open=0x80285a40
ffile_Read=0x80285efc
ffile_Close=0x80285b8c
## CONSTANTS

## MACROS
.macro call addr #cool call macro from minty for constant references to functions
  lis r12,  \addr@h
  ori r12, r12, \addr@l
  mtlr r12
  blrl
.endm

# uses r12, r3, r4
.macro jump from to #to simplify code used for adding jump statements for injections, from and to are registers
  cmpw \from, \to
  blt 36
  ## BACKWARD JUMP ##
  sub r12, \to, \from # get delta
  lis r3, Mask@h #create mask
  ori r3, r3, Mask@l
  lis r4, BackwardJump # start command
  and r12, r12, r3 #mask delta
  or r4, r4, r12 #combine delta with command
  stw r4, 0(\from)
  b 0x14 # jump to end, no labels in macros

  ## FORWARD JUMP ##
  sub r12, \to, \from # get delta
  lis r4, ForwardJump # start command
  or r4, r4, r12 #combine delta with command
  stw r4, 0(\from)
.endm
## MACROS

# Store current value in load register
mfspr r15, LR
# fix register state, r3 = 1, r4, r5 and r7 need to be persisted
or r14, r4, r4
or r16, r5, r5
or r17, r7, r7

bl ENDSTRING
# pointer to file name
.string "codes.bin\0\0"
ENDSTRING:
mflr r3 #file name string

li r4, 1 #Sequential read
li r5, 0 #dont bypass master file
li r6, 1 #unknown
call ffile_Open
or r22, r3, r3 #save file handle in r9

bl TYPE_BUFFER
or r0, r0, r0 #for storing int read from file
TYPE_BUFFER:
mflr r18 # size buffer

bl SIZE_BUFFER
or r0, r0, r0 #for storing int read from file
SIZE_BUFFER:
mflr r21 # size buffer

bl ADDRESS_BUFFER
or r0, r0, r0 #for storing address read from file
ADDRESS_BUFFER:
mflr r19 #address buffer


# now read from file while we can
LOOP_START:
# read and ignore type information
or r3, r22, r22 # file handle
li r4, 0x4
or r5, r18, r18 #int buffer
li r6, 0
li r7, 0
call ffile_Read

#compare return to see if there is data
cmpwi r3, 0
# branch if read failed (<0 response)
ble NO_MORE_CODES

# now figure out what type of code
lwz r3, 0(r18)
cmpwi r3, 0 # STANDARD CODE
beq STANDARD_CODE
cmpwi r3, 1 # Custom return value code
beq CUSTOM_RETURN_CODE
cmpwi r3, 2 # Instantly executed code
beq INSTANT_EXECUTE_CODE

#no codes should exist here so it probably crashes... lmao

STANDARD_CODE:
# read byte count
or r3, r22, r22 # file handle
li r4, 0x4
or r5, r21, r21 #int buffer
li r6, 0
li r7, 0
call ffile_Read

# read address
or r3, r22, r22 # file handle
li r4, 0x4
or r5, r19, r19 # address buffer
li r6, 0
li r7, 0
call ffile_Read

# declare memory for code
lis r3, 0x8049 #class address for fmem i guess
ori r3, r3, 0xf2f0
lwz r4, 0(r21) # byte length
addi r4, r4, 0x4 # we are doing long jumps so add in space to long jump
li r5, 4 #alignment maybe?
call fmem_AllocAndZero
or r5, r3, r3 #move new code buffer to proper arg position and save for macro

# create jumps
# from start
lwz r6, 0(r19)
jump r6, r5
# after end
addi r6, r6, 4
lwz r7, 0(r21) # byte length
add r7, r5, r7 #add byte length to offset
jump r7, r6

# clear the instruction cache for the block
icbi 0, r5

# now read bytes into buffer
or r3, r22, r22 # file handle
lwz r4, 0(r21) # byte length
# r5 already where it needs to go
li r6, 0
li r7, 0
call ffile_Read

b LOOP_START

CUSTOM_RETURN_CODE:
# read byte count
or r3, r22, r22 # file handle
li r4, 0x4
or r5, r21, r21 #int buffer
li r6, 0
li r7, 0
call ffile_Read

# read address
or r3, r22, r22 # file handle
li r4, 0x4
or r5, r19, r19 # address buffer
li r6, 0
li r7, 0
call ffile_Read

# read return address
or r3, r22, r22 # file handle
li r4, 0x4
or r5, r18, r18 # address buffer
li r6, 0
li r7, 0
call ffile_Read

# declare memory for code
lis r3, 0x8049 #class address for fmem i guess
ori r3, r3, 0xf2f0
lwz r4, 0(r21) # byte length
addi r4, r4, 0x4 # we are doing long jumps so add in space to long jump
li r5, 4 #alignment maybe?
call fmem_AllocAndZero
or r5, r3, r3 #move new code buffer to proper arg position and save for macro

# create jumps
# from start
lwz r6, 0(r19)
jump r6, r5

#after end
lwz r6, 0(r18)
lwz r7, 0(r21) # byte length
add r7, r5, r7 #add byte length to offset
jump r7, r6

# clear the instruction cache for the block
icbi 0, r5

# now read bytes into buffer
or r3, r22, r22 # file handle
lwz r4, 0(r21) # byte length
# r5 already where it needs to go
li r6, 0
li r7, 0
call ffile_Read

b LOOP_START

INSTANT_EXECUTE_CODE:
# read byte count
or r3, r22, r22 # file handle
li r4, 0x4
or r5, r21, r21 #int buffer
li r6, 0
li r7, 0
call ffile_Read

# declare memory for code
lis r3, 0x8049 #class address for fmem i guess
ori r3, r3, 0xf2f0
lwz r4, 0(r21) # byte length
addi r4, r4, 0x4 # we are doing long jumps so add in space to long jump
li r5, 4 #alignment maybe?
call fmem_AllocAndZero
or r5, r3, r3 #move new code buffer to proper arg position and save for macro
or r23, r3, r3 # Save code buffer for later.

## Use a branch and link to get the current code position in the LR
bl AUTORUN_LINK_LABEL

AUTORUN_LINK_LABEL:
mflr r4
## now need to add an offset to represent the amount of code executed 
addi r4, r4, AUTORUN_RETURN_LOCATION - AUTORUN_LINK_LABEL

# Now update jump register to return!
lwz r7, 0(r21) # byte length
add r7, r5, r7 #add byte length to offset
jump r7, r4

# now read bytes into buffer
or r3, r22, r22 # file handle
lwz r4, 0(r21) # byte length
# r5 already where it needs to go
li r6, 0
li r7, 0
call ffile_Read

# clear the instruction cache for the block before making the jump.
icbi 0, r23
isync

# Execute code
mtlr r23
blr

AUTORUN_RETURN_LOCATION:

b LOOP_START

NO_MORE_CODES:
# close file
or r3, r22, r22 # file handle
call ffile_Close

# fix link register
mtspr LR, r15
# fix register state, r3, r4, r5 and r7 need to be persisted
or r4, r14, r14
or r5, r16, r16
or r7, r17, r17

# overwritten opcodes to replace
cmplwi r29, 0x0
