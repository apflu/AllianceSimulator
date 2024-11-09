package com.apflu.alliancesim.game.geography;

import com.apflu.alliancesim.game.SpaceObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;

public final class LocationManager {
    public static final LocationManager INSTANCE = new LocationManager();
    private final List<Location> locations = new ArrayList<>();
    private final Logger logger = LoggerFactory.getLogger(LocationManager.class);

    /**
     * 将重要物件添加至索引，并为其创建地点。
     * 例如，围绕着一块富含矿物的小行星，为其创建一个挖矿地点。
     */
    public Location register(ImportantSpaceObject spaceObject) {
        // TODO

        logger.debug("Creating new location from object: {}", spaceObject);
        return null; // TODO
    }

    /**
     * 当某样会创建新的物件被标记为摧毁时，应检测一遍，是否该地点内的所有“重要物件”都已被摧毁。
     * 如果是，那么销毁整个地点。
     * @param spaceObject
     */
    public void markDestroyed(ImportantSpaceObject spaceObject) {
        // TODO
    }

    public Stream<Location> all() {
        return locations.stream();
    }

    /**
     * 防止创建对象
     */
    private LocationManager() {}
}
