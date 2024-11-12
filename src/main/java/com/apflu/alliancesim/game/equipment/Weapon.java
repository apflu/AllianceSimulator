package com.apflu.alliancesim.game.equipment;

import com.apflu.alliancesim.events.InvalidSpaceTargetException;
import com.apflu.alliancesim.game.SpaceObject;
import com.apflu.alliancesim.logging.LogMarkers;
import com.apflu.alliancesim.util.Validator;
import com.apflu.alliancesim.util.Validators;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Weapon extends ShipActiveModule implements ShipModuleRepeatable {
    private final int WeaponDamage;
    private final float RateOfFire;
    private int RangeOptimal; // 暂时没用
    private int RangeFalloff; // 暂时没用

    private static final Logger logger = LoggerFactory.getLogger(Weapon.class);

    // 临时用的构造函数
    public Weapon(int weaponDamage, float rateOfFire) {
        super(rateOfFire);
        WeaponDamage = weaponDamage;
        RateOfFire = rateOfFire;
    }

    public Weapon(int weaponDamage, float rateOfFire, int rangeOptimal, int rangeFalloff) {
        super(rateOfFire);
        WeaponDamage = weaponDamage;
        RateOfFire = rateOfFire;
        RangeOptimal = rangeOptimal;
        RangeFalloff = rangeFalloff;
    }
    public int getWeaponDamage() {
        return WeaponDamage;
    }

    @Override
    public void onCycleStart(SpaceObject target) {


        // 计算伤害
        int finalDamage = 0;
        // TODO

        // 对敌方造成伤害

        // 最后记录log
        logger.info(LogMarkers.COMBAT, "{} attacked {} with {}, dealing {} damage.", owner, target, this, finalDamage);
    }

    @Override
    public void onCycleEnd(SpaceObject target) {
        // 空的，普通武器没有攻击结束后的效果
    }

    public float getDPS() {
        return WeaponDamage * (1 / RateOfFire);
    }

    @Override
    public void use(SpaceObject target) throws InvalidSpaceTargetException {
        Validator<SpaceObject> validator = Validators.Attackable;
        use(target, validator, logger);
    }

    @Override
    public boolean getRepeat() {
        return true; // TODO
    }
}
