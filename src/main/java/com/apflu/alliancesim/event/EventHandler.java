package com.apflu.alliancesim.event;

import com.apflu.alliancesim.player.Alliance;

import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class EventHandler {
    public static final EventHandler INSTANCE = new EventHandler();
    private final Map<String, GameEvent> globalEventPool = new HashMap<String, GameEvent>();

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

    public Map<String, GameEvent> getGlobalEventPool() {
        return Map.copyOf(globalEventPool);
    }
}
