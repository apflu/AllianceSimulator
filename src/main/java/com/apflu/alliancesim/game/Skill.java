package com.apflu.alliancesim.game;

import java.lang.Math;

/**
 * Classic skill of EVE, 5 level max.
 */
public class Skill extends BaseSkill{

    /**
     * Construction method
     * @param multiplier Skill training time multiplier
     * @param id Skill id
     * @param name Skill name
     */
    public Skill(int multiplier, int id, String name){
        super(multiplier,5, id, name);
    }

    @Override public double getRequiredSP(int level){
        if ((level > this.maxLv) || (level < 0)) {
            throw new IndexOutOfBoundsException("Skill level out of bound");
        }
        return 250 * this.multiplier * Math.sqrt(Math.pow(32,level-1));
    }

    @Override public int getLv(double skillPoints) {
        if ((skillPoints > this.maxSP) || (skillPoints < 0)) {
            throw new IndexOutOfBoundsException("Skill point out of bound");
        }
        double val = Math.log(Math.pow((double) skillPoints / 250 / this.multiplier,2))/Math.log(32) + 1;
        return (int) Math.max(Math.floor(val),0);
    }
}