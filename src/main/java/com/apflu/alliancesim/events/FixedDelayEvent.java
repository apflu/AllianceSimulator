package com.apflu.alliancesim.events;

import com.apflu.alliancesim.event.EventSession;
import com.apflu.alliancesim.event.GameEvent;
import com.apflu.alliancesim.gameschedule.Scheduler;
import kotlin.Unit;

/**
 * 一个空事件，用于等待一段固定时间。
 * 常用于事件链。
 */
public class FixedDelayEvent extends GameEvent {


    private final long delay;

    public FixedDelayEvent(EventSession session, long delay) {
        super(session);
        this.delay = delay;
    }

    @Override
    public void after() {
        Scheduler.INSTANCE.delay(delay, () -> {
            this.after();
            return Unit.INSTANCE;
        });
    }
}
