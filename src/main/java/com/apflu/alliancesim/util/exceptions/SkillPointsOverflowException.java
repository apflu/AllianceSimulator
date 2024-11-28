package com.apflu.alliancesim.util.exceptions;

public class SkillPointsOverflowException extends Exception{
    public final double overflowAmount;

    public SkillPointsOverflowException(String message, double overflowAmount) {
        super(message);
        this.overflowAmount = overflowAmount;
    }

    public SkillPointsOverflowException(double overflowAmount) {
        super();
        this.overflowAmount = overflowAmount;
    }

    public SkillPointsOverflowException(String message) {
        super(message);
        this.overflowAmount = 0;
    }

    public SkillPointsOverflowException() {
        super();
        this.overflowAmount = 0;
    }
}
