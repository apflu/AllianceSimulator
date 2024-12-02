package com.apflu.alliancesim.game;

import com.apflu.alliancesim.game.space.SpaceShip;
import com.apflu.alliancesim.game.training.SkillPlan;
import com.apflu.alliancesim.game.training.SkillSet;
import com.apflu.alliancesim.game.training.TrainedSkill;
import com.apflu.alliancesim.util.exceptions.InvalidSkillPlanException;
import com.apflu.alliancesim.util.exceptions.SkillPointsOverflowException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;

public class GameCharacter {
    private static final Logger logger = LoggerFactory.getLogger(GameCharacter.class);
    private final SkillSet trainedSkill = new SkillSet();
    private SkillPlan currPlan;
    private String name;
    private SpaceShip currentShip;

    public void updateSkill(double skillPoint) throws SkillPointsOverflowException, InvalidSkillPlanException {
        if(this.trainedSkill.getFocus() == null) {
            this.trainedSkill.setFocus(this.getNextToTrain());
        }
        this.trainedSkill.incrementSkill(skillPoint);
        logger.trace("Character {} gained {} skill points through training on skill {}.",
                this, skillPoint, this.getCurrentTrainingSkill().getName());
    }

    public void setCurrentTrainingSkill(Skill skill) {
        this.trainedSkill.setFocus(skill);
    }

    public void setCurrentPlan(SkillPlan plan) {
        this.currPlan = plan;
        logger.debug("Changed skill plan to {}", plan.getName());
        try {
            this.trainedSkill.setFocus(this.getNextToTrain());
        } catch (InvalidSkillPlanException e) {
            throw new RuntimeException("setCurrentPlan set an invalid plan.");
        }
    }

    public Skill getCurrentTrainingSkill() {
        return this.trainedSkill.getFocus();
    }

    public Skill getNextToTrain() throws InvalidSkillPlanException {
        if (this.currPlan == null) throw new InvalidSkillPlanException();
        List<Skill> ableToTrain = this.currPlan.getNotIncluded(trainedSkill);
        if (ableToTrain == null || ableToTrain.isEmpty()) {
            throw new InvalidSkillPlanException();
        }
        return ableToTrain.get(0);
    }

    public List<Skill> getCompleted() {
        return this.trainedSkill.getCompleted().values().stream().map(TrainedSkill::getSkill).collect(Collectors.toCollection(ArrayList::new));
    }

    public int getSkillLv(Skill skill) {
        return this.trainedSkill.getLv(skill);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof GameCharacter that)) return false;
        return Objects.equals(name, that.name);
    }

    @Override
    public int hashCode() {
        return Objects.hash(name);
    }

    public boolean isInSpace() {
        // TODO
        return false;
    }

    public SpaceShip getCurrentShip() {
        return currentShip;
    }

    public void setCurrentShip(SpaceShip currentShip) {
        this.currentShip = currentShip;
    }
}
