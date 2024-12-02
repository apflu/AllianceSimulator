package com.apflu.alliancesim.game.space;

import com.apflu.alliancesim.game.geography.ImportantSpaceObject;
import com.apflu.alliancesim.game.SpaceObject;
import com.apflu.alliancesim.game.equipment.ShipModule;
import com.apflu.alliancesim.game.ship.ShipType;

import java.util.ArrayList;
import java.util.List;

public class SpaceShip extends SpaceObject implements ShipType, ImportantSpaceObject {
    private final List<ShipModule> moduleList;

    public SpaceShip() {
        this.moduleList = new ArrayList<>();
    }

    public SpaceShip(List<ShipModule> moduleList) {
        this.moduleList = moduleList;
    }

    public static SpaceShip of(int id) {
        return new SpaceShip(); // TODO
    }

    /**
     * 船只将会尝试用所有有效的武器攻击目标。如果该武器无法攻击该目标，那么此武器则不会启用。
     * @param target 任意目标
     */
    public void attack(SpaceObject target) {
        // TODO
    }

    /**
     * 受到伤害时，船只应当削减护盾、装甲，最后是结构值。如果结构值归零，那么舰船将会被判定为死亡。
     * @param amount 伤害量
     */
    @Override
    public void onDamageTaken(SpaceObject source, int amount) {
        // TODO
    }


    public List<ShipModule> getModuleList() {
        return new ArrayList<>(moduleList);
    }

    public boolean isCapitalShip() {
        // TODO
        return false;
    }

    public boolean isSuperCapitalShip() {
        // TODO
        return false;
    }
}
