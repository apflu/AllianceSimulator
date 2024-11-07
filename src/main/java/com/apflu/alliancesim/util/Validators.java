package com.apflu.alliancesim.util;

import com.apflu.alliancesim.game.SpaceObject;
import com.apflu.alliancesim.game.space.Asteroid;

public final class Validators {
    public static Validator<SpaceObject> Any = value -> true;
    public static Validator<SpaceObject> Attackable = new Validator<>() {
        @Override
        public boolean validate(SpaceObject value) {
            return !value.isInvulnerable();
        }

        @Override
        public String getName() {
            return "Attackable";
        }
    };

    public static Validator<SpaceObject> Mineable = new Validator<>() {
        @Override
        public boolean validate(SpaceObject value) {
            return value instanceof Asteroid;
        }

        @Override
        public String getName() {
            return "Mineable";
        }
    };
}
