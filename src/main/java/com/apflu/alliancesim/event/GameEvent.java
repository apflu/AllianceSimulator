package com.apflu.alliancesim.event;

import java.util.List;

public abstract class GameEvent {
    protected final EventSession session;
    private final List<GameEventOption> options;

    public GameEvent(EventSession session, GameEventOption... options) {
        this.session = session;
        this.options = List.of(options);
    }

    public GameEvent(EventSession session, List<GameEventOption> options) {
        this.session = session;
        this.options = options;
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
        session.getEventLine().triggerNext(session.getTriggerSource());
    }
    public void timeout() {}

    public EventSession getSession() {
        return session;
    }

    public List<GameEventOption> getOptions() {
        return options;
    }
}
