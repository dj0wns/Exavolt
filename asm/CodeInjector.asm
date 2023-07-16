.include "/home/dj0wns/Programming/MetalArmsModLoader/lib/pyiiasmh/__includes.s"
.set INJECTADDR, 0x80000000

#Store current value in load register
mfspr r31, LR
#get pointer to start of code
bl END
# code to be injected
lwz r0,0x3f8(r3)
addic r0, r0, 1
cmpwi r0, 60
blt less60
cmpwi r0, 180
blt less120
greater:
li r0, 0x0
stw r0,0x3f8(r3)
stw r0,0x8dc(r3)
b finish
less120:
stw r0,0x3f8(r3)
li r0, 0x1
stw r0,0x8dc(r3)
b finish
less60:
stw r0,0x3f8(r3)
li r0, 0x0
stw r0,0x8dc(r3)
b finish
finish:
cmpwi r0, 0x0
# end of code being injected
END:
mflr r3 # r3 is initial pointer
bl LENGTH
LENGTH:
mflr r4 # r4 is length... +12 i believe?
sub r4, r4, r3 # subtract base
subi r4, r4, 0x8 # subtract extra commands
mtctr r4 # set counter variable
lis r5, 0x8000 # set up destination ptr
ori r5, r5, 0x32b0
lis r4, 0x8008 # set up where the code will jump here
ori r4, r4, 0x9250
# set up jump to code, this is for dancing titans
# start is greater than destination so subtract
lis r6, 0x4b00
# calc jump distance
sub r7, r5, r4 # for backward jump
lis r9, 0x00ff # mask for back jump
ori r9, r9, 0xffff
and r7, r7, r9 # apply mask
mfctr r8 # get length of code to fixup the jump
add r8, r8, r5 # add to offset
subi r8, r8, 4 # go to the line after the initial jump!
sub r8, r4, r8 # subtract offset now
or r6, r6, r7
stw r6, 0(r4) # store jump command to injection
#TODO ^^^ SEEMS CORRECT
# start loop
LOOP:
lbz r4, 0(r3)
stb r4, 0(r5)
addi r3, r3, 1
addi r5, r5, 1
bdnz LOOP
# now add proper jumps
# these jumps are for titan code not code injector
lis r6, 0x4800
or r6, r6, r8
stw r6, 0(r5) # return to main code... code
#TODO ^^^ THIS JUMP SEEMS WRONG
# Restore link register
mtspr LR, r31
# copied code
li r14,0