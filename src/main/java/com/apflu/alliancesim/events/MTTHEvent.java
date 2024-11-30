package com.apflu.alliancesim.events;

import com.apflu.alliancesim.event.EventSession;
import com.apflu.alliancesim.event.GameEvent;

/**
 * 一个空事件，用于等待一段随机时间。
 * 常用于事件链。
 */
public class MTTHEvent extends GameEvent {
    // 实际上，群星本体已经在弃用MTTH。
    // 名字留作纪念意义。
    public MTTHEvent(EventSession session) {
        super(session);
    }
}
