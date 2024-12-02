package com.apflu.alliancesim.event;

import java.util.List;
import java.util.Optional;

public abstract class GameEvent {
    protected final EventSession session;
    protected final List<GameEventOption> options;

    public GameEvent(EventSession session, GameEventOption... options) {
        this.session = session;
        this.options = List.of(options);
    }

    public GameEvent(EventSession session, List<GameEventOption> options) {
        this.session = session;
        this.options = options;
    }

    public abstract String getText();
    public abstract String getDescription();

    /**
     * 默认所有事件都需要手动触发。override此方法来在进行自动判断时加入。
     * @return true: 满足自动判定条件
     */
    public boolean isEligible() {
        return false;
    }

    /**
     * 在事件加入pending list的那一刻执行。
     */
    public void before() {}

    /**
     * 在玩家主动去选择处理这项事件时执行。一般而言，是为玩家展示事件描述，没有实际影响。
     */
    public void immediate() {}

    /**
     * 在事件从pending list移除后执行。override时应当执行父类的此方法，除非另有需求。
     */
    public void after() {
        // 某些事件可能有不同的trigger！
        Optional.ofNullable(session.getEventLine())
                .ifPresent(eventLine -> eventLine.triggerNext(session.getEventLineSource()));
    }
    public void timeout() {}

    public EventSession getSession() {
        return session;
    }

    public List<GameEventOption> getOptions() {
        return options;
    }
}
