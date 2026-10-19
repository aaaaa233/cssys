#include <stdint.h>

typedef int64_t i64_a __attribute__((may_alias));

/* Variant A: plain cast through a may_alias typedef (assumes 8-byte alignment). */
int32_t dotA(const signed char *a, const signed char *b, int n) {
  int64_t acc = 0;
  const i64_a *pa = (const i64_a *)a;
  const i64_a *pb = (const i64_a *)b;
  for (int i = 0; i < n / 8; i++) {
    int64_t va = pa[i], vb = pb[i];
    asm volatile(".insn r 0x0b, 0, 0, %0, %1, %2" : "+r"(acc) : "r"(va), "r"(vb));
  }
  return (int32_t)acc;
}

/* Variant B: feed the memory operands straight in, no temporaries. */
int32_t dotB(const signed char *a, const signed char *b, int n) {
  int64_t acc = 0;
  const i64_a *pa = (const i64_a *)a;
  const i64_a *pb = (const i64_a *)b;
  for (int i = 0; i < n / 8; i++)
    asm volatile(".insn r 0x0b, 0, 0, %0, %1, %2"
                 : "+r"(acc) : "r"(pa[i]), "r"(pb[i]));
  return (int32_t)acc;
}

/* Baseline scalar, for instruction-count comparison. */
int32_t dotS(const signed char *a, const signed char *b, int n) {
  int32_t acc = 0;
  for (int i = 0; i < n; i++)
    acc += (int32_t)a[i] * (int32_t)b[i];
  return acc;
}
