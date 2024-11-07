package com.apflu.alliancesim.game.ship;

import com.apflu.alliancesim.game.Item;
import com.apflu.alliancesim.game.space.SpaceShip;

public class ItemShip extends Item {
    protected ItemShip(int id) {
        super(id);
    }

    public static ItemShip of(SpaceShip ship) {
        return new ItemShip(0); // TODO
    }

    public static ItemShip of(int id) {
        return new ItemShip(id); // TODO
    }
}
