package com.apflu.alliancesim.game.equipment;

import com.apflu.alliancesim.events.InvalidSpaceTargetException;
import com.apflu.alliancesim.game.SpaceObject;
import com.apflu.alliancesim.util.Validator;
import com.apflu.alliancesim.util.Validators;
import com.apflu.alliancesim.gameschedule.Scheduler;
import org.jetbrains.annotations.Nullable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * 一个<b>主动模块</b>，或称为<b>主动装备</b>，代表它可以被主动启用以制造一些特定的效果。<br>
 * 例如，对敌人造成伤害、或回复自身的护盾等。<br>
 * 一般而言，主动装备还会有附带的开销，例如电量、或特定燃料之类的消耗品。
 */
public abstract class ShipActiveModule extends ShipModule {
    private static final Logger logger = LoggerFactory.getLogger(ShipActiveModule.class);
    private final float interval;

    protected ShipActiveModule(float interval) {
        this.interval = interval;
    }

    public abstract void onCycleStart(SpaceObject target);
    public abstract void onCycleEnd(SpaceObject target);

    public void use(SpaceObject target) throws InvalidSpaceTargetException {
        Validator<SpaceObject> validator = Validators.Any;
        use(target, validator, logger);
    }

    public float getInterval() {
        return interval;
    }

    /**
     * 对目标启用这件装备。如果装备的启用无需目标，那么传入null。对于自我维修的装备，传入其owner。
     * @param target 目标
     * @param validator 验证器；一般一种特定装备的验证器都一样，可以在类里找到。
     * @param logger 来源logger；通常可以在来源的class里找到。
     * @throws InvalidSpaceTargetException 如果目标不能被这个主动装备指向；这个Exception必须被处理。
     */
    protected void use(@Nullable SpaceObject target, Validator<SpaceObject> validator, Logger logger)
            throws InvalidSpaceTargetException {
        if (target != null && !validator.validate(target)) {
            logger.debug("{} is not a valid {}, thus it's not activated.", target, validator.getName());
            throw new InvalidSpaceTargetException(target, validator.getName());
        }

        // 将启用的主动装备提交给计时器；表现为，在读秒开始时执行onCycleStart，然后在结束时执行onCycleEnd。
        Scheduler.INSTANCE.registerModule(this, target);
    }
}
