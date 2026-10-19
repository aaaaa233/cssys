/*
 * cssys_rp.cc —— 实验三参考解答
 * 放置位置：gem5/src/mem/cache/replacement_policies/cssys_rp.cc
 */

#include "mem/cache/replacement_policies/cssys_rp.hh"

#include <cassert>
#include <memory>

#include "params/CssysRP.hh"
#include "sim/cur_tick.hh"

namespace gem5
{

namespace replacement_policy
{

Cssys::Cssys(const Params &p)
  : Base(p), evictMru(p.evict_mru), cssysStats(this)
{
}

Cssys::CssysStats::CssysStats(statistics::Group *parent)
  : statistics::Group(parent),
    ADD_STAT(insertions, statistics::units::Count::get(),
             "块被装进本级 Cache 的次数"),
    ADD_STAT(touches, statistics::units::Count::get(),
             "本级 Cache 命中导致的 touch 次数"),
    ADD_STAT(victimizations, statistics::units::Count::get(),
             "挑选牺牲者的次数"),
    ADD_STAT(deadOnArrival, statistics::units::Count::get(),
             "被踢掉时一次都没命中过的块数"),
    ADD_STAT(victimRefSum, statistics::units::Count::get(),
             "所有牺牲者的命中次数之和"),
    ADD_STAT(firstTouchDelaySum, statistics::units::Tick::get(),
             "插入到首次命中的间隔之和"),
    ADD_STAT(firstTouchCount, statistics::units::Count::get(),
             "首次命中的样本数"),
    ADD_STAT(refsPerInsertion, statistics::units::Rate<
             statistics::units::Count, statistics::units::Count>::get(),
             "★ 平均每个块从装入到踢出被访问多少次"),
    ADD_STAT(deadFraction, statistics::units::Ratio::get(),
             "白装的块占被踢块的比例"),
    ADD_STAT(avgFirstTouchDelay, statistics::units::Tick::get(),
             "★ 插入之后过多久被第一次访问")
{
    refsPerInsertion = touches / insertions;
    deadFraction = deadOnArrival / victimizations;
    avgFirstTouchDelay = firstTouchDelaySum / firstTouchCount;
}

void
Cssys::invalidate(const std::shared_ptr<ReplacementData>& replacement_data)
{
    std::shared_ptr<CssysReplData> d =
        std::static_pointer_cast<CssysReplData>(replacement_data);
    // 时间戳清 0 = "这一路是空的"。getVictim 里对 0 做了特判，
    // 所以不管是 LRU 口径还是 MRU 口径，空的路都会被优先选中。
    d->lastTouchTick = Tick(0);
    d->refCount = 0;
}

void
Cssys::touch(const std::shared_ptr<ReplacementData>& replacement_data) const
{
    std::shared_ptr<CssysReplData> d =
        std::static_pointer_cast<CssysReplData>(replacement_data);

    if (d->refCount == 0) {
        // 第一次命中。这个间隔就是"插入位置策略的赌注能活多久"。
        cssysStats.firstTouchDelaySum += curTick() - d->insertTick;
        cssysStats.firstTouchCount++;
    }
    d->refCount++;
    d->lastTouchTick = curTick();
    cssysStats.touches++;
}

void
Cssys::reset(const std::shared_ptr<ReplacementData>& replacement_data) const
{
    std::shared_ptr<CssysReplData> d =
        std::static_pointer_cast<CssysReplData>(replacement_data);
    d->lastTouchTick = curTick();
    d->insertTick = curTick();
    d->refCount = 0;
    cssysStats.insertions++;
}

ReplaceableEntry*
Cssys::getVictim(const ReplacementCandidates& candidates) const
{
    assert(candidates.size() > 0);

    ReplaceableEntry* victim = candidates[0];
    for (const auto& candidate : candidates) {
        std::shared_ptr<CssysReplData> c =
            std::static_pointer_cast<CssysReplData>(
                candidate->replacementData);

        // 空的路一律优先。别漏了这一条：如果只把下面的 '<' 改成 '>'，
        // 空路的时间戳是 0（最小），在"找最大值"的循环里永远选不中，
        // Cache 会一直只用其中一路，结果和 gem5 自带的 MRURP 对不上。
        if (c->lastTouchTick == 0) {
            victim = candidate;
            break;
        }

        Tick v = std::static_pointer_cast<CssysReplData>(
            victim->replacementData)->lastTouchTick;

        // ★★ 整个实验的核心就是这一个比较符 ★★
        //   '<' : 挑时间戳最小的 = 最久没用的  -> LRU
        //   '>' : 挑时间戳最大的 = 最近用过的  -> MRU
        bool better = evictMru ? (c->lastTouchTick > v)
                               : (c->lastTouchTick < v);
        if (better) {
            victim = candidate;
        }
    }

    // 统计这个牺牲者活着的时候被用了几次
    std::shared_ptr<CssysReplData> vd =
        std::static_pointer_cast<CssysReplData>(victim->replacementData);
    if (vd->lastTouchTick != 0) {   // 空的路不算"被替换"
        cssysStats.victimizations++;
        cssysStats.victimRefSum += vd->refCount;
        if (vd->refCount == 0) {
            cssysStats.deadOnArrival++;
        }
    }

    return victim;
}

std::shared_ptr<ReplacementData>
Cssys::instantiateEntry()
{
    return std::shared_ptr<ReplacementData>(new CssysReplData());
}

} // namespace replacement_policy
} // namespace gem5
