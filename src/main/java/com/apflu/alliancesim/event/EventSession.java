package com.apflu.alliancesim.event;

import com.apflu.alliancesim.player.Alliance;

public class EventSession {
    private final Alliance alliance;
    private final Object triggerSource;
    private final GameEventLine eventLine;
    private final Object eventLineSource;

    public EventSession(Alliance alliance, Object triggerSource, GameEventLine eventLine, Object eventLineSource) {
        this.alliance = alliance;
        this.triggerSource = triggerSource;
        this.eventLine = eventLine;
        this.eventLineSource = eventLineSource;
    }
    public Alliance getAlliance() {
        return alliance;
    }

    public Object getTriggerSource() {
        return triggerSource;
    }

    public GameEventLine getEventLine() {
        return eventLine;
    }

    public Object getEventLineSource() {
        return eventLineSource;
    }
}
