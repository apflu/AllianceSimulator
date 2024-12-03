package com.apflu.alliancesim.event;

public interface ServerTickListener extends Listener {
    @Override
    default String getName() {
        return "servertick";
    }
}
