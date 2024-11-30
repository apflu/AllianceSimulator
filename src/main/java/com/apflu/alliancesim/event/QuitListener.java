package com.apflu.alliancesim.event;

public interface QuitListener extends Listener {
    void onQuit();

    @Override
    default String getName() {
        return "quit";
    }
}
