package com.apflu.alliancesim.game;

import com.apflu.alliancesim.debug.constants.TestSkills;
import com.apflu.alliancesim.game.training.SkillSet;
import com.apflu.alliancesim.util.exceptions.SkillPointsOverflowException;

public class GameCharacter {
    private final SkillSet trainedSkill = new SkillSet();

    public void updateSkill(double skillPoint) throws SkillPointsOverflowException {
        this.trainedSkill.incrementSkill(skillPoint);
    }

    public void setCurrentTrainingSKill(Skill skill) {
        this.trainedSkill.setFocus(skill);
    }

    public Skill getCurrentTrainingSkill() {
        return this.trainedSkill.getFocus();
    }

    public Skill getNextCurrentTrainingSkill() {
        return null; // TODO
    }
}
