package com.apflu.alliancesim.util;

import com.apflu.alliancesim.game.geography.Location;
import com.apflu.alliancesim.game.equipment.ShipModule;
import com.apflu.alliancesim.game.ship.ShipType;
import com.apflu.alliancesim.game.space.SpaceShip;
import org.jetbrains.annotations.NotNull;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.stream.Stream;

public class SpaceshipBuilder {
    private static final Logger logger = LoggerFactory.getLogger(SpaceshipBuilder.class);

    private final List<ShipModule> moduleList;
    private final ShipType shipType;
    private final Location location;

    public SpaceshipBuilder() {
        moduleList = new ArrayList<>();
        shipType = null;
        location = null;
    }

    public SpaceshipBuilder(@NotNull List<ShipModule> moduleList, ShipType shipType, Location location) {
        this.moduleList = moduleList;
        this.shipType = shipType;
        this.location = location;
    }

    public SpaceshipBuilder setShip(ShipType shipType) {
        logger.trace("Setting ship type to: {}", shipType);
        return new SpaceshipBuilder(moduleList, shipType, location);
    }

    public SpaceshipBuilder setLocation(Location location) {
        logger.trace("Setting location to: {}", location);
        return new SpaceshipBuilder(moduleList, shipType, location);
    }

    public SpaceshipBuilder fitModule(ShipModule... modules) {
        logger.trace("Adding modules: {}", (Object[]) modules);
        List<ShipModule> moduleList = Stream.concat(Stream.of(modules), this.moduleList.stream()).toList();
        return new SpaceshipBuilder(moduleList, shipType, location);
    }

    public SpaceshipBuilder fitModule(@NotNull Collection<ShipModule> modules) {
        logger.trace("Adding module collection: {}", modules);
        List<ShipModule> moduleList = Stream.concat(modules.stream(), this.moduleList.stream()).toList();
        return new SpaceshipBuilder(moduleList, shipType, location);
    }

    public boolean isValid() {
        return shipType != null;
    }

    public SpaceShip build() {
        if (!isValid()) {
            logger.error("Cannot build spaceship: invalid configuration");
            throw new IllegalStateException("Invalid Spaceship configuration");
        }
        logger.debug("Building spaceship with type: {}, location: {}, modules: {}", shipType, location, moduleList);
        return null;
    }
}
