package com.apflu.alliancesim.util;

import com.apflu.alliancesim.game.geography.Location;

public class AnomaliesBuilder implements LocationBuilder {
    AnomaliesBuilder(LocationBuilder builder) {

    }

    @Override
    public AnomaliesBuilder newLocation() {
        // TODO
        return this;
    }

    @Override
    public Location build() {
        AnomaliesBuilder builder = this.newLocation();
        return null;
    }
}
