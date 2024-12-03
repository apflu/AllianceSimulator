package com.apflu.alliancesim.event;

public interface QuitListener extends Listener {
    @Override
    default String getName() {
        return "quit";
    }
}
