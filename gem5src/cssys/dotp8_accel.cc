#include "cssys/dotp8_accel.hh"

#include <algorithm>
#include <cstring>

#include "base/trace.hh"
#include "debug/Dotp8Accel.hh"
#include "mem/packet_access.hh"
#include "mem/page_table.hh"
#include "mem/port_proxy.hh"
#include "sim/process.hh"

namespace gem5
{

Dotp8Accel::Dotp8Accel(const Params &p)
    : ClockedObject(p),
      cpuPort(p.name + ".cpu_side", this),
      memPort(p.name + ".mem_side", this),
      sys(p.system),
      requestorId(p.system->getRequestorId(this)),
      pioAddr(p.pio_addr),
      pioSize(p.pio_size),
      pe(p.pe),
      maxOutstanding(p.outstanding),
      startLatency(p.start_latency),
      respEvent([this] { sendQueuedResp(); }, name() + ".resp"),
      computeEvent([this] { computeTick(); }, name() + ".compute"),
      startEvent([this] { issueFetches(); }, name() + ".start"),
      stats(this)
{
}

void
Dotp8Accel::init()
{
    ClockedObject::init();
    /* 主动向 membus 报告"MMIO 这段地址归我管"。
       不报的话 membus 的 gotAllAddrRanges 永远为假，第一次功能访问就断言失败。 */
    if (cpuPort.isConnected())
        cpuPort.sendRangeChange();
}

void
Dotp8Accel::startup()
{
    /* SE 模式没有操作系统，也就没人替我们建立 MMIO 映射。
       加速器自己往被测进程的页表里插一条：虚地址 == 物理地址，
       并且标成 uncacheable —— 不标的话，写 GO 会停在 L1 里出不去，
       读 STATUS 会一直命中 L1 拿到旧值。
       （RISC-V 的 SE 模式默认不认这个标志位，需要打一个 tlb.cc 的补丁，
         见 _tools/apply_lab6.py。） */
    Process *p = sys->threads[0]->getProcessPtr();
    p->map(pioAddr, pioAddr, pioSize, /*cacheable=*/false);
    inform("%s: MMIO 寄存器已映射到 %#x（%d 字节，uncacheable）",
           name(), pioAddr, (int)pioSize);
}

Port &
Dotp8Accel::getPort(const std::string &if_name, PortID idx)
{
    if (if_name == "cpu_side")
        return cpuPort;
    if (if_name == "mem_side")
        return memPort;
    return ClockedObject::getPort(if_name, idx);
}

/* ===================================================================== *
 * 地址翻译与功能访问
 * ===================================================================== */

bool
Dotp8Accel::translate(Addr vaddr, Addr &paddr) const
{
    auto *tc = sys->threads[0];
    Process *proc = tc->getProcessPtr();
    return proc->pTable->translate(vaddr, paddr);
}

/* 功能访问必须按页切开：相邻虚页的物理页不一定相邻 */
void
Dotp8Accel::readMem(Addr vaddr, void *buf, size_t len)
{
    PortProxy proxy(memPort, sys->cacheLineSize());
    uint8_t *out = static_cast<uint8_t *>(buf);
    const Addr pgSize = 4096;
    while (len) {
        Addr off = vaddr & (pgSize - 1);
        size_t chunk = std::min<size_t>(len, pgSize - off);
        Addr pa = 0;
        panic_if(!translate(vaddr, pa),
                 "dotp8 accel: 虚地址 %#x 没有映射", vaddr);
        proxy.readBlobPhys(pa, 0, out, chunk);
        vaddr += chunk; out += chunk; len -= chunk;
    }
}

void
Dotp8Accel::writeMem(Addr vaddr, const void *buf, size_t len)
{
    PortProxy proxy(memPort, sys->cacheLineSize());
    const uint8_t *in = static_cast<const uint8_t *>(buf);
    const Addr pgSize = 4096;
    while (len) {
        Addr off = vaddr & (pgSize - 1);
        size_t chunk = std::min<size_t>(len, pgSize - off);
        Addr pa = 0;
        panic_if(!translate(vaddr, pa),
                 "dotp8 accel: 虚地址 %#x 没有映射", vaddr);
        proxy.writeBlobPhys(pa, 0, in, chunk);
        vaddr += chunk; in += chunk; len -= chunk;
    }
}

void
Dotp8Accel::computeFunctional()
{
    std::vector<int8_t> a((size_t)rows * dimN), b((size_t)batch * dimN);
    readMem(regB, b.data(), (size_t)batch * dimN);
    readMem(regA, a.data(), (size_t)rows * dimN);

    /* out[s][r] = sum_i A[r][i] * B[s][i] —— batch 个样本共用同一份 A。
       这一条就是本次实验的关键：A 只搬一遍，算了 batch 倍的乘加。 */
    results.assign((size_t)rows * batch, 0);
    for (uint32_t s = 0; s < batch; ++s) {
        const int8_t *vec = b.data() + (size_t)s * dimN;
        for (uint32_t r = 0; r < rows; ++r) {
            int32_t acc = 0;
            const int8_t *row = a.data() + (size_t)r * dimN;
            for (uint32_t i = 0; i < dimN; ++i)
                acc += (int32_t)row[i] * (int32_t)vec[i];
            results[(size_t)s * rows + r] = acc;
        }
    }
}

/* ===================================================================== *
 * 命令处理
 * ===================================================================== */

void
Dotp8Accel::startJob()
{
    panic_if(busy, "dotp8 accel: 上一条命令还没做完就又下了一条");
    panic_if(rows == 0 || dimN == 0, "dotp8 accel: rows/n 还没写就 GO");

    /* 先把结果算对（不占时间），时序由下面那套真实访存流水决定 */
    computeFunctional();

    busy = true;
    jobStartTick = curTick();
    segs[0] = {regB, (uint64_t)batch * dimN};
    segs[1] = {regA, (uint64_t)rows * dimN};
    curSeg = 0;
    segOff = 0;
    bytesRequested = 0;
    bytesTotal = segs[0].len + segs[1].len;
    bytesArrived = 0;
    macsTotal = (uint64_t)rows * dimN * batch;
    macsDone = 0;
    inFlight = 0;
    stats.jobs++;

    DPRINTF(Dotp8Accel, "GO: rows=%u n=%u batch=%u bytes=%llu macs=%llu\n",
            rows, dimN, batch, bytesTotal, macsTotal);

    schedule(startEvent, clockEdge(startLatency));
}

/* ===================================================================== *
 * 取数流水
 * ===================================================================== */

void
Dotp8Accel::issueFetches()
{
    const Addr line = sys->cacheLineSize();

    while (inFlight < maxOutstanding && bytesRequested < bytesTotal &&
           !memPort.isBlocked()) {
        /* 跳到下一段 */
        while (curSeg < 2 && segOff >= segs[curSeg].len) {
            ++curSeg;
            segOff = 0;
        }
        if (curSeg >= 2)
            break;

        Addr va = segs[curSeg].va + segOff;
        /* 对齐到 Cache 块：一次请求不跨块，也不跨页 */
        Addr lineOff = va & (line - 1);
        uint64_t chunk = std::min<uint64_t>(line - lineOff,
                                            segs[curSeg].len - segOff);
        Addr pa = 0;
        panic_if(!translate(va, pa), "dotp8 accel: 虚地址 %#x 没有映射", va);

        RequestPtr req = std::make_shared<Request>(pa, chunk, 0, requestorId);
        PacketPtr pkt = new Packet(req, MemCmd::ReadReq);
        pkt->allocate();

        segOff += chunk;
        bytesRequested += chunk;
        ++inFlight;
        stats.lineReads++;
        stats.bytesRead += chunk;

        memPort.sendPacket(pkt);
    }
}

void
Dotp8Accel::handleFetchResp(PacketPtr pkt)
{
    bytesArrived += pkt->getSize();
    --inFlight;
    delete pkt;

    if (!computeEvent.scheduled() && busy)
        schedule(computeEvent, clockEdge(Cycles(1)));
    issueFetches();
}

/* ===================================================================== *
 * 计算流水：每周期最多 pe 次乘加，且不能算还没到的数据
 * ===================================================================== */

void
Dotp8Accel::computeTick()
{
    if (!busy)
        return;

    /* B 的 batch*n 个字节先到；之后每到 1 字节 A，就多出 batch 次可做的乘加
       ——A 的一行被 batch 个样本共用，这正是 batch 能省带宽的原因。 */
    const int64_t bBytes = (int64_t)batch * dimN;
    int64_t avail = ((int64_t)bytesArrived - bBytes) * (int64_t)batch
                    - (int64_t)macsDone;
    if (avail < 0)
        avail = 0;

    uint64_t step = std::min<uint64_t>(pe, (uint64_t)avail);
    macsDone += step;
    stats.macs += step;
    stats.busyCycles++;
    if (step < pe)
        stats.stallCycles++;

    if (macsDone >= macsTotal) {
        finish();
        return;
    }
    schedule(computeEvent, clockEdge(Cycles(1)));
}

void
Dotp8Accel::finish()
{
    /* 结果写回内存。用功能访问，会正确地把 CPU Cache 里的旧副本处理掉 */
    writeMem(regOut, results.data(), results.size() * sizeof(int32_t));

    stats.jobCycles += (curTick() - jobStartTick) / clockPeriod();
    busy = false;
    DPRINTF(Dotp8Accel, "done: %llu ticks\n", curTick() - jobStartTick);

    if (pendingStatus) {
        PacketPtr pkt = pendingStatus;
        pendingStatus = nullptr;
        pkt->makeResponse();
        pkt->setLE<uint64_t>(0);
        queueResp(pkt);
    }
}

/* ===================================================================== *
 * MMIO
 * ===================================================================== */

void
Dotp8Accel::queueResp(PacketPtr pkt)
{
    respQueue.push_back(pkt);
    if (!respEvent.scheduled())
        schedule(respEvent, clockEdge(Cycles(1)));
}

void
Dotp8Accel::sendQueuedResp()
{
    if (respQueue.empty())
        return;
    PacketPtr pkt = respQueue.front();
    respQueue.erase(respQueue.begin());
    cpuPort.sendPacket(pkt);
    if (!respQueue.empty() && !respEvent.scheduled())
        schedule(respEvent, clockEdge(Cycles(1)));
}

bool
Dotp8Accel::handleTimingReq(PacketPtr pkt)
{
    Addr off = pkt->getAddr() - pioAddr;

    if (pkt->isWrite()) {
        uint64_t val = pkt->getLE<uint64_t>();
        switch (off) {
          case ACC_REG_A:    regA = val; break;
          case ACC_REG_B:    regB = val; break;
          case ACC_REG_OUT:  regOut = val; break;
          case ACC_REG_DIMS: rows = val >> 32; dimN = val & 0xffffffffu; break;
          case ACC_REG_BATCH: batch = val ? val : 1; break;
          case ACC_REG_GO:   startJob(); break;
          default:
            panic("dotp8 accel: 写了一个不存在的寄存器 offset=%#x", off);
        }
        pkt->makeResponse();
        queueResp(pkt);
        return true;
    }

    if (pkt->isRead()) {
        if (off == ACC_REG_STATUS) {
            if (busy) {
                /* ★ 这就是"等加速器算完"：这条 load 一直挂在这里不回复，
                   CPU 的 LSQ 里那一项就一直不能提交。 */
                panic_if(pendingStatus, "dotp8 accel: 两个 STATUS 读同时挂起");
                pendingStatus = pkt;
                return true;
            }
            pkt->makeResponse();
            pkt->setLE<uint64_t>(0);
            queueResp(pkt);
            return true;
        }
        pkt->makeResponse();
        pkt->setLE<uint64_t>(0);
        queueResp(pkt);
        return true;
    }

    panic("dotp8 accel: 不认识的 MMIO 命令 %s", pkt->cmdString());
}

/* ===================================================================== *
 * 端口样板代码
 * ===================================================================== */

AddrRangeList
Dotp8Accel::CpuSidePort::getAddrRanges() const
{
    AddrRangeList ranges;
    ranges.push_back(AddrRange(owner->pioAddr, owner->pioAddr + owner->pioSize));
    return ranges;
}

void
Dotp8Accel::CpuSidePort::sendPacket(PacketPtr pkt)
{
    panic_if(blockedPacket != nullptr, "应该先检查是否阻塞再发包");
    if (!sendTimingResp(pkt))
        blockedPacket = pkt;
}

void
Dotp8Accel::CpuSidePort::trySendRetry()
{
    if (needRetry && blockedPacket == nullptr) {
        needRetry = false;
        sendRetryReq();
    }
}

Tick
Dotp8Accel::CpuSidePort::recvAtomic(PacketPtr pkt)
{
    /* atomic 模式只用于功能验证(--cpu atomic)，直接原地完成 */
    Addr off = pkt->getAddr() - owner->pioAddr;
    if (pkt->isWrite()) {
        uint64_t val = pkt->getLE<uint64_t>();
        switch (off) {
          case ACC_REG_A:    owner->regA = val; break;
          case ACC_REG_B:    owner->regB = val; break;
          case ACC_REG_OUT:  owner->regOut = val; break;
          case ACC_REG_DIMS:
            owner->rows = val >> 32; owner->dimN = val & 0xffffffffu; break;
          case ACC_REG_BATCH:
            owner->batch = val ? val : 1; break;
          case ACC_REG_GO:
            owner->computeFunctional();
            owner->writeMem(owner->regOut, owner->results.data(),
                            owner->results.size() * sizeof(int32_t));
            owner->stats.jobs++;
            break;
          default: panic("dotp8 accel(atomic): 未知寄存器 %#x", off);
        }
    } else {
        pkt->setLE<uint64_t>(0);
    }
    pkt->makeResponse();
    return 1;
}

void
Dotp8Accel::CpuSidePort::recvFunctional(PacketPtr pkt)
{
    if (pkt->isRead())
        pkt->setLE<uint64_t>(0);
    if (pkt->needsResponse())
        pkt->makeResponse();
}

bool
Dotp8Accel::CpuSidePort::recvTimingReq(PacketPtr pkt)
{
    if (blockedPacket != nullptr) {
        needRetry = true;
        return false;
    }
    return owner->handleTimingReq(pkt);
}

void
Dotp8Accel::CpuSidePort::recvRespRetry()
{
    panic_if(blockedPacket == nullptr, "没有被阻塞的包却收到重试");
    PacketPtr pkt = blockedPacket;
    blockedPacket = nullptr;
    sendPacket(pkt);
    if (blockedPacket == nullptr)
        owner->sendQueuedResp();
}

void
Dotp8Accel::MemSidePort::sendPacket(PacketPtr pkt)
{
    panic_if(blockedPacket != nullptr, "应该先检查是否阻塞再发包");
    if (!sendTimingReq(pkt))
        blockedPacket = pkt;
}

bool
Dotp8Accel::MemSidePort::recvTimingResp(PacketPtr pkt)
{
    owner->handleFetchResp(pkt);
    return true;
}

void
Dotp8Accel::MemSidePort::recvReqRetry()
{
    panic_if(blockedPacket == nullptr, "没有被阻塞的包却收到重试");
    PacketPtr pkt = blockedPacket;
    blockedPacket = nullptr;
    sendPacket(pkt);
    if (blockedPacket == nullptr)
        owner->issueFetches();
}

void
Dotp8Accel::MemSidePort::recvRangeChange()
{
    /* 什么都不用做：我们的 MMIO 地址是固定的，不随下游变化。
       （这里如果照抄 SimpleMemobj 转发给 cpuPort，会和 membus 形成
         "你等我报范围、我等你报范围"的死循环。） */
}

/* ===================================================================== *
 * 统计
 * ===================================================================== */

Dotp8Accel::AccelStats::AccelStats(statistics::Group *parent)
    : statistics::Group(parent),
      ADD_STAT(jobs, statistics::units::Count::get(), "收到的命令次数"),
      ADD_STAT(macs, statistics::units::Count::get(), "累计乘加次数"),
      ADD_STAT(bytesRead, statistics::units::Byte::get(),
               "加速器自己搬进来的字节数"),
      ADD_STAT(lineReads, statistics::units::Count::get(),
               "加速器发出的访存请求个数"),
      ADD_STAT(jobCycles, statistics::units::Cycle::get(),
               "从 GO 到结果写回的总周期数(含启动开销和第一次访存延迟)"),
      ADD_STAT(busyCycles, statistics::units::Cycle::get(),
               "计算流水实际运转的周期数"),
      ADD_STAT(stallCycles, statistics::units::Cycle::get(),
               "算力空转(数据没到)的周期数"),
      ADD_STAT(bytesPerCycle, statistics::units::Rate<
                   statistics::units::Byte, statistics::units::Cycle>::get(),
               "加速器实测带宽(字节/周期)"),
      ADD_STAT(macsPerCycle, statistics::units::Rate<
                   statistics::units::Count, statistics::units::Cycle>::get(),
               "实测算力(乘加/周期)——和 pe 比就知道算力有没有喂饱"),
      ADD_STAT(macsPerByte, statistics::units::Rate<
                   statistics::units::Count, statistics::units::Byte>::get(),
               "算术强度(乘加/字节)——roofline 的横坐标")
{
    bytesPerCycle = bytesRead / jobCycles;
    macsPerCycle = macs / jobCycles;
    macsPerByte = macs / bytesRead;
}

} // namespace gem5
