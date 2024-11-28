package com.apflu.alliancesim.game;

/**
 * A base class for all skills. Contains name, id, multiplier, and max level of that skill.
 */
public abstract class BaseSkill {
    protected final int multiplier;
    protected final int maxLv;
    protected final double maxSP;
    protected final int skillID;
    protected final String skillName;

    /**
     * Construction method
     * @param multiplier training time multiplier, determines the skill point required to train the skill
     * @param maxLv Max training level of this skill
     * @param id id of this skill
     * @param name name of this skill
     */
    public BaseSkill(int multiplier, int maxLv, int id, String name) {
        this.multiplier = multiplier;
        this.maxLv = maxLv;
        this.skillID = id;
        this.skillName = name;
        this.maxSP = this.getRequiredSP(this.maxLv);
    }

    /**
     * Calculate skill point required to reach a specific level (starting from no skill point)
     * @param level level to reach
     * @return total skill point needed
     */
    public abstract double getRequiredSP(int level);

    /**
     * Calculate skill level correspond to a specific amount of skill points
     * @param skillPoints skill points
     * @return Level of skill
     */
    public abstract int getLv(double skillPoints);

    /**
     * Returns the max skill point of the skill.
     * @return max skill points
     */
    public double getMaxSP(){
        return this.maxSP;
    }

    /**
     * returns the unique id of the skill
     * @return skill id
     */
    public int getID() {
        return this.skillID;
    }

    /**
     * returns the name of the skill
     * @return skill name
     */
    public String getName() {
        return this.skillName;
    }

}
