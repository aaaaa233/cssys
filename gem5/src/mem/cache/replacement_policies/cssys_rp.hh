/*
 * cssys_rp.hh —— 实验三参考解答：自己动手写的 Cache 替换策略
 *
 * 这个文件是从 gem5 自带的 lru_rp.hh 复制过来改的。相对 LRU 加了两样东西：
 *
 *   1) 一个 SimObject 参数 evict_mru，用来在"踢最久没用的(LRU)"和
 *      "踢最近用过的(MRU)"之间切换。任务 2 只要改 getVictim 里的一个
 *      比较符就够了，这里做成参数只是为了少编译一次。
 *
 *   2) 一组统计量，专门回答任务 3 的问题：
 *      "为什么 LIP/BIP/RRIP 这些论文里很有名的策略，放进 L1 完全没有效果？"
 *      核心指标是 refsPerInsertion —— 一个块从被装进来到被踢出去，
 *      平均被访问了多少次。这个数在 L1 上是 126，在 L2 上是 1。
 *
 * 放置位置：gem5/src/mem/cache/replacement_policies/cssys_rp.hh
 */

#ifndef __MEM_CACHE_REPLACEMENT_POLICIES_CSSYS_RP_HH__
#define __MEM_CACHE_REPLACEMENT_POLICIES_CSSYS_RP_HH__

#include "base/statistics.hh"
#include "base/stats/group.hh"
#include "base/types.hh"
#include "mem/cache/replacement_policies/base.hh"

namespace gem5
{

struct CssysRPParams;

namespace replacement_policy
{

class Cssys : public Base
{
  protected:
    /**
     * 每个 Cache 块挂一份。lastTouchTick 是 LRU/MRU 排序用的时间戳；
     * 另外两个字段纯粹是为了统计，真实硬件里不会有。
     */
    struct CssysReplData : ReplacementData
    {
        /** 最后一次访问的时刻。0 表示这一路是空的（无效）。 */
        Tick lastTouchTick;
        /** 被装进来的时刻。 */
        Tick insertTick;
        /** 装进来之后被命中了几次。 */
        uint64_t refCount;

        CssysReplData() : lastTouchTick(0), insertTick(0), refCount(0) {}
    };

    /** true = 踢最近用过的(MRU)；false = 踢最久没用的(LRU)。 */
    const bool evictMru;

    /**
     * 这些统计量是这次实验的主要产出。注意 touch()/reset()/getVictim()
     * 在基类里都是 const 方法，所以统计对象必须声明成 mutable，
     * 否则编译不过——这本身就是一次"读懂编译错误"的练习。
     */
    struct CssysStats : public statistics::Group
    {
        CssysStats(statistics::Group *parent);

        /** reset() 被调用的次数 = 有多少个块被装进这一级 Cache。 */
        statistics::Scalar insertions;
        /** touch() 被调用的次数 = 有多少次命中落在这一级。 */
        statistics::Scalar touches;
        /** getVictim() 被调用的次数 = 有多少次需要挑一个牺牲者。 */
        statistics::Scalar victimizations;
        /** 被踢掉时一次都没被命中过的块（装进来就白装了）。 */
        statistics::Scalar deadOnArrival;
        /** 所有牺牲者的命中次数之和。 */
        statistics::Scalar victimRefSum;
        /** 从"装进来"到"第一次被命中"的时间间隔之和（tick）。 */
        statistics::Scalar firstTouchDelaySum;
        /** 上面这个和一共累加了多少次。 */
        statistics::Scalar firstTouchCount;

        /** ★ 平均每装进来一个块，它被访问多少次。 */
        statistics::Formula refsPerInsertion;
        /** 白装的块占比。 */
        statistics::Formula deadFraction;
        /** ★ 插入之后过多久就被第一次访问（tick）。 */
        statistics::Formula avgFirstTouchDelay;
    };
    mutable CssysStats cssysStats;

  public:
    typedef CssysRPParams Params;
    Cssys(const Params &p);
    ~Cssys() = default;

    void invalidate(const std::shared_ptr<ReplacementData>&
        replacement_data) override;
    void touch(const std::shared_ptr<ReplacementData>&
        replacement_data) const override;
    void reset(const std::shared_ptr<ReplacementData>&
        replacement_data) const override;
    ReplaceableEntry* getVictim(
        const ReplacementCandidates& candidates) const override;
    std::shared_ptr<ReplacementData> instantiateEntry() override;
};

} // namespace replacement_policy
} // namespace gem5

#endif // __MEM_CACHE_REPLACEMENT_POLICIES_CSSYS_RP_HH__
