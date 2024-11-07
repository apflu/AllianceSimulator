package com.apflu.alliancesim.game.equipment;

import com.apflu.alliancesim.game.Item;
import com.apflu.alliancesim.game.SpaceObject;

public abstract class ShipModule extends Item {
    /*
     * 装配需求 fitting
     */
    public int Usage_CPU;
    public int Usage_Powergrid;

    protected SpaceObject owner; // TODO

    protected ShipModule() {
        super(0); // TODO: 临时解决方案。
    }
}
