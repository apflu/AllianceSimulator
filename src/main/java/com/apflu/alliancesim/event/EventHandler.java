package com.apflu.alliancesim.event;

import com.apflu.alliancesim.player.Alliance;

import java.util.List;

public class EventHandler {
    public static final EventHandler INSTANCE = new EventHandler();

    public void triggerEvent(GameEvent event, Alliance target, Object source) {
        // TODO
        event.before();

        // 没有选项的事件默认为隐藏事件，不加入队列，立刻解决。
        // 如果只是需要玩家确认的事件，也需要加入一个选项。
        if (event.getOptions().isEmpty()) {
            event.pending();
            event.after();
        }
    }

    public void triggerEventLine(GameEventLine event, Alliance target, Object source) {
        // TODO
    }

    public List<GameEvent> getPendingEvents(Alliance alliance) {
        // TODO
        return null;
    }

    public List<GameEventLine> getActiveEventLines(Alliance alliance) {
        // TODO
        return null;
    }
}
