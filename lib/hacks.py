# gecko code for extended heap
HEAP_SIZE = 0x0218bbbb # update if we extend heap further
EXTENDED_HEAP = [
  0x042185d0, 0x3c600218,
  0x042185e0, 0x3943bbbb,
]

HACKS = {
  "extended_heap" : EXTENDED_HEAP,
}
