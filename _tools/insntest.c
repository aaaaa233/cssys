#include <stdint.h>

/* Probe 1: R-type custom-0 (opcode 0x0b), rd read-modify-write. */
int64_t mac(int64_t acc, int64_t a, int64_t b) {
  asm volatile(".insn r 0x0b, 0, 0, %0, %1, %2" : "+r"(acc) : "r"(a), "r"(b));
  return acc;
}

/* Probe 2: same but with a nonzero funct7, to check the encoding lands right. */
int64_t mac2(int64_t acc, int64_t a, int64_t b) {
  asm volatile(".insn r 0x0b, 1, 3, %0, %1, %2" : "+r"(acc) : "r"(a), "r"(b));
  return acc;
}

/* Probe 3: the shape the lab actually needs -- unaligned-safe 8-byte gather
   from an int8_t* and accumulate in a loop. */
int32_t dot8(const signed char *a, const signed char *b, int n) {
  int64_t acc = 0;
  for (int i = 0; i < n; i += 8) {
    int64_t va, vb;
    __builtin_memcpy(&va, a + i, 8);
    __builtin_memcpy(&vb, b + i, 8);
    asm volatile(".insn r 0x0b, 0, 0, %0, %1, %2" : "+r"(acc) : "r"(va), "r"(vb));
  }
  return (int32_t)acc;
}
