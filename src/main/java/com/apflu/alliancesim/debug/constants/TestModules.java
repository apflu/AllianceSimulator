package com.apflu.alliancesim.debug.constants;

import com.apflu.alliancesim.game.equipment.MiningEquipment;
import com.apflu.alliancesim.game.equipment.Weapon;

public final class TestModules {
    public static final MiningEquipment CivilianMiner =
            new MiningEquipment(6, 10, 10000, 0);

    public static final Weapon CivilianGatlingRailgun =
            new Weapon(5, 2, 4800, 2000);
}
