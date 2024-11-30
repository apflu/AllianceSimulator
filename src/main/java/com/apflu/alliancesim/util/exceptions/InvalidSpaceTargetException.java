package com.apflu.alliancesim.util.exceptions;

import com.apflu.alliancesim.game.SpaceObject;

public class InvalidSpaceTargetException extends RuntimeException {
    public InvalidSpaceTargetException(SpaceObject target, String message) {
        super((target != null? target.toString(): "") + message);
    }
    public InvalidSpaceTargetException(String message) {
        super(message);
    }
}
