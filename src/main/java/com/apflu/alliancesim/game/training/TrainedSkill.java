package com.apflu.alliancesim.game.training;

import com.apflu.alliancesim.game.Skill;
import com.apflu.alliancesim.util.exceptions.SkillPointsOverflowException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TrainedSkill {
    private static final Logger logger = LoggerFactory.getLogger(TrainedSkill.class);
    private final Skill skill;
    private double skillPoints = 0;

    public TrainedSkill(Skill skill) {
        this.skill = skill;
    }

    public TrainedSkill(Skill skill, double sp) {
        this.skill = skill;
        this.skillPoints = sp;
    }

    public Skill getSkill() {
        return this.skill;
    }

    public int getLv() {
        return this.skill.getLv(this.skillPoints);
    }

    public void addSkillPoint(double skillPoints) throws SkillPointsOverflowException {
        this.skillPoints += skillPoints;
        if (this.skillPoints >= this.skill.getMaxSP()) {
            double overflow = this.skillPoints - this.skill.getMaxSP();
            this.skillPoints = this.skill.getMaxSP();
            logger.info("Skill completed: {}", this);
            throw new SkillPointsOverflowException("Training overflow; change current training", overflow);
        }
        //logger.info(this.toString());
    }

    public boolean isCompleted() {
        return this.skillPoints == this.skill.getMaxSP();
    }

    @Override public String toString(){
        return this.skill.getName() + ": Lv " + this.getLv() + ", " + this.skillPoints + "SP";
    }

}
