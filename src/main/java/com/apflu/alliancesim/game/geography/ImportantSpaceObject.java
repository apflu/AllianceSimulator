package com.apflu.alliancesim.game.geography;

public interface ImportantSpaceObject {
    default Location onCreate() {
        return LocationManager.INSTANCE.register(this);
    }
    default void onDestroy() {
        LocationManager.INSTANCE.markDestroyed(this);
    }
}
