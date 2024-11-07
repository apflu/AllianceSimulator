package com.apflu.alliancesim.util;

import com.apflu.alliancesim.game.geography.Location;
import com.apflu.alliancesim.game.equipment.ShipModule;
import com.apflu.alliancesim.game.ship.ShipType;
import com.apflu.alliancesim.game.space.SpaceShip;
import org.jetbrains.annotations.NotNull;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.stream.Stream;

public class SpaceshipBuilder {
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
        return new SpaceshipBuilder(moduleList, shipType, );
    }

    public SpaceshipBuilder setLocation(Location location) {
        return new SpaceshipBuilder(moduleList, shipType, location);
    }

    public SpaceshipBuilder fitModule(ShipModule... modules) {
        List<ShipModule> moduleList = Stream.concat(Stream.of(modules), this.moduleList.stream()).toList();
        return new SpaceshipBuilder(moduleList, shipType, location);
    }

    public SpaceshipBuilder fitModule(@NotNull Collection<ShipModule> modules) {
        List<ShipModule> moduleList = Stream.concat(modules.stream(), this.moduleList.stream()).toList();
        return new SpaceshipBuilder(moduleList, shipType, location);
    }

    public boolean isValid() {
        return shipType != null;
    }

    public SpaceShip build() {
        return null; // TODO
    }
}
