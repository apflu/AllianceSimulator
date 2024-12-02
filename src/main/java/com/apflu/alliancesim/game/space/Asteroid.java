package com.apflu.alliancesim.game.space;

import com.apflu.alliancesim.game.Material;
import com.apflu.alliancesim.game.SpaceObject;
import com.apflu.alliancesim.game.equipment.ShipModule;
import com.apflu.alliancesim.game.geography.ImportantSpaceObject;
import com.apflu.alliancesim.game.geography.Location;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * 一个<b>小行星</b>是可被开采的对象，例如矿石、冰矿、气云。<br>
 * 其显著特点是拥有替代血条的体积属性。当体积耗尽时，小行星将会“死亡”并消失。
 */
public class Asteroid extends SpaceObject implements ImportantSpaceObject {
    private int volume;
    private Material type;

    public Asteroid(int volume, Material type, com.apflu.alliancesim.game.geography.Location location) {
        this.volume = volume;
        this.type = type;
        Location = location;
    }

    public void reduceVolume(int amount) {
        volume -= amount;
        if (this.volume <= 0) {
            onDestroy(); // 通知LocationManager��在的地点销��可能性
        }
    }

    public int getVolume() {
        return volume;
    }

    private static final Logger logger = LoggerFactory.getLogger(Asteroid.class);

    // 里面还剩多少矿
    private int hpRemain; // TODO: 追踪血量，且在初始化时设定为其最大血量

    public final Location Location;

    public Asteroid() {
        super.invulnerable = true; // 小行星不使用血量属性
        Location = onCreate(); // 通知LocationManager并获得其所在的地点
    }

    /**
     * 会返回小行星的种类，也就是说构成它的矿物是什么；开采它的时候将会把对应种类的矿物加入船舱。
     * @return 原材料
     */
    public Material getType() {
        // TODO
        return type;
    }

    public void recordDamage(int amount) {
        hpRemain -= amount;
        logger.info("Asteroid of type {} took {} damage, {} volume remaining.", type, amount, volume);
    }

    /**
     * 小行星受到伤害时（被开采）会损失体积。如果体积耗尽，小行星将会死亡。<br>
     * 这里不涉及到将开采到的矿物加入船舱的动作。矿物的获得应在采矿枪的对应方法处理。
     * @param amount 伤害
     */
    public void takeDamage(int amount, ShipModule source) {
        reduceVolume(amount);
        recordDamage(amount);
        onDamageTaken(source.getOwner(), amount);
    }

    @Override
    public void onDamageTaken(SpaceObject source, int amount) {
        if (true) { // TODO: 如果血量耗尽
            onDestroy(); // 通知LocationManager潜在的地点销毁可能性
        }

        logger.trace("Asteroid taking {} damage from {}, {} remaining.", amount, source, hpRemain);
    }
}
