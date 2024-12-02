package com.apflu.alliancesim.game.geography;

import com.apflu.alliancesim.game.SpaceObject;

import java.util.ArrayList;
import java.util.List;

/**
 * 一个地点是游戏地图的最小组成单元。默认而言，会为所有的空间站以及星系内存在的各种异常各创建一个地点。
 * 地点的销毁应发生在制造它的来源消失时。
 */
public class Location {
    private final List<SpaceObject> ImportantList = new ArrayList<>();
    private SolarSystem solarSystem;

    public SolarSystem getSolarSystem() {
        return solarSystem;
    }

    public void setSolarSystem(SolarSystem solarSystem) {
        this.solarSystem = solarSystem;
    }

    public List<SpaceObject> getImportantList() {
        return new ArrayList<>(ImportantList);
    }

    public Location addObject(SpaceObject object) {
        // TODO
        return this;
    }

    public Location addImportantObject(SpaceObject object) {
        // TODO
        return this;
    }
}
