package com.apflu.alliancesim.game.geography;

import java.util.List;

/**
 * 一个<b>星系</b>是游戏地图的最基础组成单元，可以将其理解为传统RPG游戏里的一张地图。<br>
 * 星系内可能包括数个空间站，以及包含矿物的小行星带、或自然生成的战斗异常（用于刷怪）等地点。<br>
 * 所有舰船都可以通过跃迁来抵达同星系内的其他地点。而只有通过星门，才可以抵达相邻的星系。
 */
public class SolarSystem {
    private final int id;

    public SolarSystem(int id) {
        this.id = id;
    }

    public List<Location> getLocations() {
        return LocationManager.INSTANCE.all()
                .filter(location -> this == location.getSolarSystem())
                .toList();
    }

    /**
     * 将会从宇宙中尝试获取此星系。
     * @param id
     * @return
     */
    public static SolarSystem of(int id) {
        return Universe.INSTANCE.getSolarSystem(id);
    }

    public int getId() {
        return id;
    }
}
