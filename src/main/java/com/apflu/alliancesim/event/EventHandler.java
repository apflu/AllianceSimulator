package com.apflu.alliancesim.event;

import com.apflu.alliancesim.player.Alliance;

import java.util.*;

public class EventHandler {
    public static final EventHandler INSTANCE = new EventHandler();
    private final Map<String, GameEvent> globalEventPool = new HashMap<String, GameEvent>();

    private final List<GameEventLine> eventLines = new ArrayList<>(); // 事件队列

    public void recordEventLine(GameEventLine eventLine) {
        if(eventLine != null) {
            eventLines.add(eventLine);
        }
    }

    public void registerEvent(GameEvent event) {
        // TODO
    }

    public boolean checkEligible(GameEvent event, Alliance alliance) {
        // TODO
        return false;
    }

    /**
     * 检查所有全局事件池里的事件，并将符合条件的加入此玩家的事件池。<br>
     * 频繁使用可能有性能问题。
     * @param alliance 玩家
     */
    public void checkAllEligible(Alliance alliance) {
        // TODO
    }

    /**
     * 无视条件，直接将事件加入此玩家的事件池
     * @param event 对象
     * @param alliance 玩家
     */
    public void setEligible(GameEvent event, Alliance alliance) {
        // TODO
    }

    public void triggerEvent(GameEvent event, Alliance target, Object source) {
        // TODO
        event.before();

        // 没有选项的事件默认为隐藏事件，不加入队列，立刻解决。
        // 如果只是需要玩家确认的事件，也需要加入一个选项。
        if (event.getOptions().isEmpty()) {
            event.immediate();
            event.after();
        }
    }

    /**
     * 触发事件链的下一个事件。
     * @param eventLine 事件链
     * @param target 目标
     * @param source 来源
     */
    public void triggerEventLine(GameEventLine eventLine, Alliance target, Object source) {
        if (eventLine != null && source != null) {
            EventSession eventSession = new EventSession(null, source, eventLine, source);
            eventLine.triggerNext(source);
            // log or handle the event session as needed
        }
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

    public Map<String, GameEvent> getGlobalEventPool() {
        return Map.copyOf(globalEventPool);
    }
}
