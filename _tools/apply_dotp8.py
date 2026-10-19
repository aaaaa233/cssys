import io, os, sys

DEC = "/mnt/smartssd/wlx/cssys/gem5/src/arch/riscv/isa/decoder.isa"
BLK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dotp8_block.txt")

with io.open(DEC, encoding="utf-8") as fh:
    src = fh.read()

if "dotp8" in src:
    print("already patched, nothing to do")
    sys.exit(0)

with io.open(BLK, encoding="utf-8") as fh:
    block = fh.read()

anchor = "        0x03: decode FUNCT3 {\n            format FenceOp {"
n = src.count(anchor)
if n != 1:
    print("ERROR: anchor found %d times, expected 1" % n)
    sys.exit(1)

src = src.replace(anchor, block + anchor)

with io.open(DEC, "w", encoding="utf-8") as fh:
    fh.write(src)
print("patched OK")
