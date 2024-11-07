package com.apflu.alliancesim.game.geography;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashMap;
import java.util.Map;

public class Universe {
    public static final Universe INSTANCE = new Universe();

    private final Map<Integer, SolarSystem> solarSystemMap = new HashMap<>();
    private static final Logger logger = LoggerFactory.getLogger(Universe.class);

    public SolarSystem getSolarSystem(int id) {
        if (solarSystemMap.containsKey(id)) {
            return solarSystemMap.get(id);
        } else {
            return solarSystemMap.put(id, new SolarSystem(id)); // 将返回新生成的星系
        }
    }

    public void register(SolarSystem solarSystem) {
        if (!solarSystemMap.containsValue(solarSystem)) {
            solarSystemMap.put(solarSystem.getId(), solarSystem);
            logger.debug("Created new solar system: {}", solarSystem);
        }
    }

    public Map<Integer, SolarSystem> getSolarSystemMap() {
        return solarSystemMap;
    }
}
