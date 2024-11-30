package com.apflu.alliancesim.events;

public interface QuitListener extends Listener {
    void onQuit();

    @Override
    default String getName() {
        return "quit";
    }
}
