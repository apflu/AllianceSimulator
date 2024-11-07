package com.apflu.alliancesim.logging;

import org.slf4j.Marker;
import org.slf4j.MarkerFactory;

public final class LogMarkers {
    public static final Marker PLAYER_COMMAND = MarkerFactory.getMarker("PLAYER_COMMAND");
    public static final Marker MINING = MarkerFactory.getMarker("MINING");
    public static final Marker COMBAT = MarkerFactory.getMarker("COMBAT");
}
