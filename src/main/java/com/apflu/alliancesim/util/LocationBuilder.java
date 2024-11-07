package com.apflu.alliancesim.util;

import com.apflu.alliancesim.game.geography.Location;

public interface LocationBuilder {

    LocationBuilder newLocation();
    Location build();
}
