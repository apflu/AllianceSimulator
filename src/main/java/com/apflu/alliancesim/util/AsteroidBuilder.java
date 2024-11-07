package com.apflu.alliancesim.util;

import com.apflu.alliancesim.game.Material;
import com.apflu.alliancesim.game.geography.Location;
import com.apflu.alliancesim.game.geography.SolarSystem;

public class AsteroidBuilder implements LocationBuilder {
    private final SolarSystem solarSystem;
    private final Location location;
    private final Material material;
    private final int amount;

    public AsteroidBuilder() {
        this.material = null;
        this.amount = 0;
        this.solarSystem = null;
        this.location = null;
    }

    public AsteroidBuilder(SolarSystem solarSystem, Location location, Material material, int amount) {
        this.solarSystem = solarSystem;
        this.location = location;
        this.material = material;
        this.amount = amount;
    }

    @Override
    public AsteroidBuilder newLocation() {
        return new AsteroidBuilder(solarSystem, new Location(), material, amount);
    }

    public AsteroidBuilder setSolarSystem(SolarSystem solarSystem) {
        if (!solarSystem.equals(this.solarSystem)) {
            return new AsteroidBuilder(solarSystem, new Location(), material, amount);
        } else {
            return new AsteroidBuilder(solarSystem, location, material, amount);
        }
    }

    public AsteroidBuilder setType(Material material) {
        return new AsteroidBuilder(solarSystem, location, material, amount);
    }

    public AsteroidBuilder setAmount(int amount) {
        return new AsteroidBuilder(solarSystem, location, material, amount);
    }

    public AnomaliesBuilder asAnomaliesBuilder() {
        // TODO
        return null;
    }

    public boolean isValid() {
        return (solarSystem != null) && (material != null) && (amount > 0);
    }

    @Override
    public Location build() {
        // TODO
        return null;
    }

    public Location batchBuild(int amount) {
        // TODO
        return null;
    }
}
