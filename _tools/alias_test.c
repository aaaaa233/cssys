#include <stdint.h>

#ifdef USE_MAY_ALIAS
typedef int64_t i64_a __attribute__((may_alias));
#else
typedef int64_t i64_a;
#endif

#define DOTP8(acc, va, vb)                                                     \
  asm volatile(".insn r 0x0b, 0, 0, %0, %1, %2" : "+r"(acc) : "r"(va), "r"(vb))

__attribute__((noinline)) int32_t dot_i8(const int8_t *a, const int8_t *b,
                                         int n) {
  const i64_a *pa = (const i64_a *)a;
  const i64_a *pb = (const i64_a *)b;
  int64_t acc = 0;
  for (int i = 0; i < n / 8; i++)
    DOTP8(acc, pa[i], pb[i]);
  return (int32_t)acc;
}
