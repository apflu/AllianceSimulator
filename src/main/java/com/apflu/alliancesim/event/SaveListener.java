package com.apflu.alliancesim.event;

public interface SaveListener extends Listener {
    @Override
    default String getName() {
        return "save";
    }
}
