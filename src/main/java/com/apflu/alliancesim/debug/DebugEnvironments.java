package com.apflu.alliancesim.debug;

import com.apflu.alliancesim.debug.constants.TestMinerals;
import com.apflu.alliancesim.debug.constants.TestShips;
import com.apflu.alliancesim.util.AsteroidBuilder;
import com.apflu.alliancesim.util.SpaceshipBuilder;

public final class DebugEnvironments {
    public static final AsteroidBuilder DebugMiningSiteBuilder = new AsteroidBuilder()
            .setType(TestMinerals.Veldspar)
            .setAmount(1_000_000_000);

    public static final SpaceshipBuilder DebugMiningSpaceshipBuilder = new SpaceshipBuilder()
            .setShip(TestShips.Ibis)
            .fitModule();
}
