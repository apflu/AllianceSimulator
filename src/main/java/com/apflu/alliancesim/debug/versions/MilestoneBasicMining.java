package com.apflu.alliancesim.debug.versions;

import ch.qos.logback.classic.LoggerContext;
import ch.qos.logback.core.util.StatusPrinter2;
import com.apflu.alliancesim.debug.DebugEnvironments;
import com.apflu.alliancesim.debug.constants.TestModules;
import com.apflu.alliancesim.debug.constants.TestSolarSystems;
import com.apflu.alliancesim.game.geography.Location;
import com.apflu.alliancesim.game.geography.Universe;
import com.apflu.alliancesim.game.space.SpaceShip;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * 这是一个最基础的版本实现。
 * 如果这个示例得以成功运行，代表游戏向可以游玩的方向迈出了第一步。
 * TODO: Move to test section after it's marked as done.
 */
public final class MilestoneBasicMining {
    private static final Logger logger = LoggerFactory.getLogger(MilestoneBasicMining.class);

    public static void main(String[] args) {
        logger.debug("Running MilestoneBasicMining 1...");
        System.out.println();

        // 输出测试信息，用来debug logger本身。
        LoggerContext lc = (LoggerContext) LoggerFactory.getILoggerFactory();
        new StatusPrinter2().print(lc);
        logger.debug("finished logger config output.");

        Universe.INSTANCE.register(TestSolarSystems.NewCaldari); // 将测试用的星系添加到宇宙里

        Location miningSiteLocation = DebugEnvironments.DebugMiningSiteBuilder // 获取制作采矿区域的builder
                .setSolarSystem(TestSolarSystems.NewCaldari) // 预计地点设置为刚刚创建的测试星系
                .build(); // 根据刚才提供的信息实际创建采矿区域，里面包含一个富含矿石的小行星

        SpaceShip testShip = DebugEnvironments.DebugMiningSpaceshipBuilder // 获取builder
                .setLocation(miningSiteLocation) // 设置预计生成的位置到刚才创建的采矿区域
                // 使即将生成的飞船装配有一个民用采矿器，以及民用轨道炮
                .fitModule(TestModules.CivilianMiner, TestModules.CivilianGatlingRailgun)
                .build(); // 生成

        // 攻击里面的第一个关键物件；也就是刚刚创建的那块矿
        testShip.attack(miningSiteLocation.getImportantList().get(0));

        System.out.println("test");
    }
}
