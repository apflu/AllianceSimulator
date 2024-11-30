package com.apflu.alliancesim.events;

public interface SaveListener extends Listener {
    void onSave();

    @Override
    default String getName() {
        return "save";
    }
}
