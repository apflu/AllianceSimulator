package com.apflu.alliancesim.events;

import com.apflu.alliancesim.event.EventSession;
import com.apflu.alliancesim.event.GameEvent;
import com.apflu.alliancesim.gameschedule.Scheduler;
import kotlin.Unit;

import java.util.Random;

/**
 * 一个空事件，用于等待一段随机时间。
 * 常用于事件链。
 */
public class MTTHEvent extends GameEvent {
    private final long meanTime;
    private final Random random = new Random();

    public MTTHEvent(EventSession session, long meanTime) {
        super(session);
        this.meanTime = meanTime;
    }
    // 实际上，群星本体已经在弃用MTTH。
    // 名字留作纪念意义。

    @Override
    public String getText() {
        return "";
    }

    @Override
    public String getDescription() {
        return "";
    }

    @Override
    public void after() {
        long delay = generateGaussianDelay(meanTime);
        Scheduler.INSTANCE.delay(delay, () -> {
            this.after();
            return Unit.INSTANCE;
        });
    }

    private long generateGaussianDelay(long mean) {
        double gaussian = random.nextGaussian();
        double stddev = mean * 0.15; // 15%的标准差（假定的）
        return Math.max(0,(long) (mean + stddev * gaussian));
    }
}
