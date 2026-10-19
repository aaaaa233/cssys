/*
 * 实验六：dotp8 矩阵-向量加速器
 *
 * 它做的事情和实验五那条 dotp8 指令完全一样——int8 乘加——但边界移动了：
 *   实验五：CPU 用 load 把数据搬进寄存器，再用一条指令算 8 次乘加
 *   实验六：CPU 只下一条命令，加速器自己去内存里把 98 KB 权重取回来算完
 *
 * 一次命令算完一整层：out[r] = sum_i A[r*n+i] * B[i]，r = 0..rows-1
 *
 * ---------------------------------------------------------------------------
 * 建模上的一个诚实声明（参考解答里要讲给学生听）：
 *
 * **功能和时序是分开算的。** 收到 GO 时用功能访问(functional)把结果一次算好
 * 并写回内存；同时启动一套真实的、带时序的访存流水去搬同样多的数据。
 * 周期数完全由后者决定，功能那一路不占时间。
 *
 * 这样做的理由：让"结果对不对"和"要花多少时间"互不干扰，
 * 学生改时序模型的时候不会把 checksum 改坏。
 * 代价是：我们隐含假设了一个**完美的地址翻译**（真实系统里那是 IOMMU，
 * 是一笔真实开销）。这一条要在报告里作为模型局限写出来。
 * ---------------------------------------------------------------------------
 */
#ifndef __CSSYS_DOTP8_ACCEL_HH__
#define __CSSYS_DOTP8_ACCEL_HH__

#include <cstdint>
#include <vector>

#include "base/statistics.hh"
#include "base/types.hh"
#include "mem/packet.hh"
#include "mem/port.hh"
#include "params/Dotp8Accel.hh"
#include "sim/clocked_object.hh"
#include "sim/eventq.hh"
#include "sim/system.hh"

namespace gem5
{

/* MMIO 寄存器（相对 pio_addr 的字节偏移），每个 8 字节 */
enum Dotp8AccelReg
{
    ACC_REG_A      = 0x00,  /* W: 矩阵 A 的虚地址 */
    ACC_REG_B      = 0x08,  /* W: 向量/矩阵 B 的虚地址 */
    ACC_REG_OUT    = 0x10,  /* W: int32 结果数组的虚地址 */
    ACC_REG_DIMS   = 0x18,  /* W: (rows << 32) | n */
    ACC_REG_GO     = 0x20,  /* W: 写任意值即启动 */
    ACC_REG_STATUS = 0x28,  /* R: 阻塞读，算完才返回 */
    ACC_REG_BATCH  = 0x30,  /* W: 一次算几个样本，0/不写 = 1 */
};

class Dotp8Accel : public ClockedObject
{
  private:
    /* ------------------------------------------------------------------
     * CPU 侧：MMIO 寄存器端口
     * ------------------------------------------------------------------ */
    class CpuSidePort : public ResponsePort
    {
      private:
        Dotp8Accel *owner;
        bool needRetry;
        PacketPtr blockedPacket;

      public:
        CpuSidePort(const std::string &name, Dotp8Accel *owner)
            : ResponsePort(name), owner(owner), needRetry(false),
              blockedPacket(nullptr)
        {}

        AddrRangeList getAddrRanges() const override;
        void sendPacket(PacketPtr pkt);
        void trySendRetry();
        bool isBlocked() const { return blockedPacket != nullptr; }

      protected:
        Tick recvAtomic(PacketPtr pkt) override;
        void recvFunctional(PacketPtr pkt) override;
        bool recvTimingReq(PacketPtr pkt) override;
        void recvRespRetry() override;
    };

    /* ------------------------------------------------------------------
     * 内存侧：加速器自己的取数端口
     * ------------------------------------------------------------------ */
    class MemSidePort : public RequestPort
    {
      private:
        Dotp8Accel *owner;
        PacketPtr blockedPacket;

      public:
        MemSidePort(const std::string &name, Dotp8Accel *owner)
            : RequestPort(name), owner(owner), blockedPacket(nullptr)
        {}

        void sendPacket(PacketPtr pkt);
        bool isBlocked() const { return blockedPacket != nullptr; }

      protected:
        bool recvTimingResp(PacketPtr pkt) override;
        void recvReqRetry() override;
        void recvRangeChange() override;
    };

    CpuSidePort cpuPort;
    MemSidePort memPort;

    System *sys;
    RequestorID requestorId;

    const Addr pioAddr;
    const Addr pioSize;
    const unsigned pe;           /* 每周期乘加次数 */
    const unsigned maxOutstanding;
    const Cycles startLatency;

    /* --- 命令寄存器 --- */
    Addr regA = 0, regB = 0, regOut = 0;
    uint32_t rows = 0, dimN = 0, batch = 1;

    /* --- 运行状态 --- */
    bool busy = false;
    PacketPtr pendingStatus = nullptr; /* 挂起的 STATUS 读，算完再回它 */

    Addr fetchVA = 0;        /* 下一个要取的虚地址 */
    Addr fetchEndVA = 0;     /* 取到这里为止 */
    uint64_t bytesArrived = 0;
    uint64_t macsTotal = 0;
    uint64_t macsDone = 0;
    unsigned inFlight = 0;

    void issueFetches();
    void computeTick();
    void finish();
    void startJob();

    /* 一次性把结果算对（功能通路，不占时间） */
    void computeFunctional();
    std::vector<int32_t> results;

    /* 取数计划：先取 B(n 字节)，再流式取 A(rows*n 字节) */
    struct Segment { Addr va; uint64_t len; };
    Segment segs[2];
    int curSeg = 0;
    uint64_t segOff = 0;
    uint64_t bytesRequested = 0, bytesTotal = 0;

    std::vector<PacketPtr> respQueue;
    void sendQueuedResp();
    void queueResp(PacketPtr pkt);
    EventFunctionWrapper respEvent;
    bool translate(Addr vaddr, Addr &paddr) const;
    void readMem(Addr vaddr, void *buf, size_t len);
    void writeMem(Addr vaddr, const void *buf, size_t len);

    EventFunctionWrapper computeEvent;
    EventFunctionWrapper startEvent;

    struct AccelStats : public statistics::Group
    {
        AccelStats(statistics::Group *parent);
        statistics::Scalar jobs;        /* 收到多少次命令 */
        statistics::Scalar macs;        /* 一共算了多少次乘加 */
        statistics::Scalar bytesRead;   /* 加速器自己搬了多少字节 */
        statistics::Scalar lineReads;   /* 发了多少个访存请求 */
        statistics::Scalar jobCycles;   /* 从 GO 到写回结果的总周期 */
        statistics::Scalar busyCycles;  /* 计算流水跑了多少周期 */
        statistics::Scalar stallCycles; /* 数据没到、算力空转的周期 */
        /* 下面三个是 roofline 的三个坐标，直接从 stats.txt 里读 */
        statistics::Formula bytesPerCycle;  /* 实测带宽 */
        statistics::Formula macsPerCycle;   /* 实测算力利用率 */
        statistics::Formula macsPerByte;    /* 算术强度：batch 一提它就涨 */
    } stats;

    Tick jobStartTick = 0;

  public:
    PARAMS(Dotp8Accel);
    Dotp8Accel(const Params &p);

    /* 告诉总线"这段地址归我管"。必须在 init() 里主动报一次：
       总线要等所有下游端口都报完地址范围才肯干活，我们不报就死锁。 */
    void init() override;

    /* 把自己的 MMIO 寄存器映射进被测进程的地址空间。
       真实系统里这是设备驱动 mmap 干的事，SE 模式没有内核，只好自己来。 */
    void startup() override;

    Port &getPort(const std::string &if_name,
                  PortID idx = InvalidPortID) override;

    /* 被端口回调 */
    Tick handleMmioRead(PacketPtr pkt);
    Tick handleMmioWrite(PacketPtr pkt);
    bool handleTimingReq(PacketPtr pkt);
    void handleFetchResp(PacketPtr pkt);
};

} // namespace gem5

#endif // __CSSYS_DOTP8_ACCEL_HH__
