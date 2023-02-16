# gecko code for extended heap
HEAP_SIZE = 0x0218bbbb # update if we extend heap further
EXTENDED_HEAP = [
  0x04218060, 0x3c600220, # double heap from 17.5 mb to 34 mb
  0x04218070, 0x39430000, # remove trailing zeroes for chillin
  0x0421807c, 0x3cc000a0, # double fast mem to 10 MB from 5
  #0x04218078, 0x3cc00140, # double audo streaming space to 20 MB
  # possible exe offsets:
  0x04323c20, 0x3c600080,
  0x04345224, 0x3ca00080,
  0x0434d10c, 0x3e600080,

]

HACKS = {
  "extended_heap" : EXTENDED_HEAP,
}
