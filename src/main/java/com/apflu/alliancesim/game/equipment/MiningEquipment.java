package com.apflu.alliancesim.game.equipment;

import com.apflu.alliancesim.events.InvalidSpaceTargetException;
import com.apflu.alliancesim.game.SpaceObject;
import com.apflu.alliancesim.game.space.Asteroid;
import com.apflu.alliancesim.logging.LogMarkers;
import com.apflu.alliancesim.util.Validator;
import com.apflu.alliancesim.util.Validators;
import org.jetbrains.annotations.NotNull;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * <b>采矿装备</b>是一种特殊的武器，只能对矿石生效。<br>
 * 不同的是，采矿装备对矿石的体积造成伤害，而非血量。
 */
public class MiningEquipment extends Weapon {

    private static final Logger logger = LoggerFactory.getLogger(MiningEquipment.class);

    public MiningEquipment(int weaponDamage, float rateOfFire, int rangeOptimal, int rangeFalloff) {
        super(weaponDamage, rateOfFire, rangeOptimal, rangeFalloff);
    }

    @Override
    public void onCycleStart(SpaceObject target) {

        Asteroid targetAsteroid = (Asteroid) target;

        // 最后记录挖矿事件
        logger.info(LogMarkers.MINING, "started mining.");
    }

    /**
     * 一般而言，挖矿装备在一个cycle结束的时候才会处理。<br>
     * 例如，对矿石造成伤害；添加矿石到船只货仓等，都在此时处理。
     * @param target 目标；由于验证过必定是小行星，所以直接进行类型强制转换。
     */
    @Override
    public void onCycleEnd(SpaceObject target) {
        Asteroid targetAsteroid = (Asteroid) target;
        // TODO
        // 计算伤害
        int finalDamage = 0;

        // 对矿石造成体积伤害

        // 添加矿石到船只货仓

        // 最后记录挖矿事件完成
        logger.info(LogMarkers.MINING, "{} finished mining {} for {} units.",
                owner, targetAsteroid.getType(), finalDamage);
    }

    @Override
    public void use(SpaceObject target) throws InvalidSpaceTargetException {
        Validator<SpaceObject> validator = Validators.Mineable;
        use(target, validator, logger);
    }
}
