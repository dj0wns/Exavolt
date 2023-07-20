
## CONSTANTS
CodeDestination=0x800032b0
JumpInsertion=0x8019abf4
Mask=0x00ffffff
ForwardJump=0x4800
BackwardJump=0x4b00


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


#Store current value in load register
mfspr r30, LR
#get pointer to start of code
bl END

## code to be injected

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
# read byte count
or r3, r22, r22 # file handle
li r4, 0x4
or r5, r21, r21 #int buffer
li r6, 0
li r7, 0
call ffile_Read

#compare return to see if there is data
cmpwi r3, 0
# branch if read failed (<0 response)
ble NO_MORE_CODES

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
#addi r7, r7, 4 # add 4 for last instruction
add r7, r5, r7 #add byte length to offset
jump r7, r6

# now read bytes into buffer
or r3, r22, r22 # file handle
lwz r4, 0(r21) # byte length
# r5 already where it needs to go
li r6, 0
li r7, 0
call ffile_Read

b LOOP_START

NO_MORE_CODES:
# close file
or r3, r22, r22 # file handle
call ffile_Close

# fix link register
mtspr LR, r15
# fix register state, r3, r4, r5 and r7 need to be persisted
li r3, 1
or r4, r14, r14
or r5, r16, r16
or r7, r17, r17

# copied code
lwz r0, 0x44(r1)

## end of code being injected

END:
mflr r3 # r3 is initial pointer
bl LENGTH
LENGTH:
mflr r4 # r4 is length... +12 i believe?
sub r4, r4, r3 # subtract base
subi r4, r4, 0x8 # subtract extra commands

mtctr r4 # set counter variable

lis r5, CodeDestination@h # set up destination ptr
ori r5, r5, CodeDestination@l
lis r4, JumpInsertion@h # set up where the code will jump here
ori r4, r4, JumpInsertion@l

# set up jump to code, this is for dancing titans
# start is greater than destination so subtract
lis r6, BackwardJump

# calc jump distance
sub r7, r5, r4 # for backward jump
lis r9, Mask@h # mask for back jump
ori r9, r9, Mask@l
and r7, r7, r9 # apply mask

mfctr r8 # get length of code to fixup the jump
add r8, r8, r5 # add to offset
subi r8, r8, 4 # go to the line after the initial jump!
sub r8, r4, r8 # subtract offset now


or r6, r6, r7
stw r6, 0(r4) # store jump command to injection

# start loop
LOOP:
lbz r4, 0(r3)
stb r4, 0(r5)
addi r3, r3, 1
addi r5, r5, 1
bdnz LOOP

# now add proper jumps
# these jumps are for titan code not code injector
lis r6, ForwardJump
or r6, r6, r8
stw r6, 0(r5) # return to main code... code

# Restore link register
mtspr LR, r30

# copied code
li r14, 0
