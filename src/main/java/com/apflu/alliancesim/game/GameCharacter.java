package com.apflu.alliancesim.game;

import com.apflu.alliancesim.game.training.SkillPlan;
import com.apflu.alliancesim.game.training.SkillSet;
import com.apflu.alliancesim.game.training.TrainedSkill;
import com.apflu.alliancesim.util.exceptions.InvalidSkillPlanException;
import com.apflu.alliancesim.util.exceptions.SkillPointsOverflowException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

public class GameCharacter {
    private static final Logger logger = LoggerFactory.getLogger(GameCharacter.class);
    private final SkillSet trainedSkill = new SkillSet();
    private SkillPlan currPlan;

    public void updateSkill(double skillPoint) throws SkillPointsOverflowException, InvalidSkillPlanException {
        if(this.trainedSkill.getFocus() == null) {
            this.trainedSkill.setFocus(this.getNextToTrain());
            logger.debug("Changed training to {}", this.getCurrentTrainingSkill().getName());
        }
        this.trainedSkill.incrementSkill(skillPoint);
        logger.trace("Character {} gained {} skill points through training on skill {}.",
                this, skillPoint, this.getCurrentTrainingSkill().getName());
    }

    public void setCurrentTrainingSkill(Skill skill) throws InvalidSkillPlanException {
        this.trainedSkill.setFocus(skill);
    }

    public void setCurrentPlan(SkillPlan plan) throws InvalidSkillPlanException {
        this.currPlan = plan;
        this.trainedSkill.setFocus(this.getNextToTrain());
        logger.debug("Changed skill plan to {}", plan.getName());
    }

    public Skill getCurrentTrainingSkill() throws InvalidSkillPlanException {
        return this.trainedSkill.getFocus();
    }

    public Skill getNextToTrain() throws InvalidSkillPlanException {
        try {
            return this.currPlan.getNotIncluded(trainedSkill).get(0);
        }catch (IndexOutOfBoundsException e) {
            throw new InvalidSkillPlanException();
        }
    }

    public List<Skill> getCompleted() {
        return this.trainedSkill.getCompleted().values().stream().map(TrainedSkill::getSkill).collect(Collectors.toCollection(ArrayList::new));
    }

    public int getSkillLv(Skill skill) {
        return this.trainedSkill.getLv(skill);
    }

}
