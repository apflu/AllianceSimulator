package com.apflu.alliancesim.event;

public interface SaveListener extends Listener {
    void onSave();

    @Override
    default String getName() {
        return "save";
    }
}
