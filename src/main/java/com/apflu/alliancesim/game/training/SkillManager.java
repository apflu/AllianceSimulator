package com.apflu.alliancesim.game.training;

import com.apflu.alliancesim.game.GameCharacter;
import com.apflu.alliancesim.util.exceptions.InvalidSkillPlanException;
import com.apflu.alliancesim.util.exceptions.NoAvailablePlanException;
import com.apflu.alliancesim.util.exceptions.SkillPointsOverflowException;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.Set;
import java.util.stream.Collectors;

public final class SkillManager {
    public static final SkillManager INSTANCE = new SkillManager();
    public static final List<SkillPlan> PLAN_LIST = new ArrayList<>();
    private static final Random rand = new Random();

    public void updateSkill(GameCharacter character, long interval) throws NoAvailablePlanException {
        updateSkillRecursePlan(character, getIncreasedSP(interval));
    }

    private void updateSkillRecursePlan(GameCharacter character, double skillPoints) throws NoAvailablePlanException {
        try {
            updateSkillRecursePoint(character, skillPoints);
        }catch (InvalidSkillPlanException e) {
            List<SkillPlan> trainable = PLAN_LIST.stream().filter(lambda ->
                    !(lambda.getNotIncluded(character.getCompleted())).isEmpty()).collect(Collectors.toCollection(ArrayList::new));
            if (trainable.isEmpty()) throw new NoAvailablePlanException();
            character.setCurrentPlan(trainable.get(rand.nextInt(trainable.size())));
            updateSkillRecursePlan(character, skillPoints);
        }
    }

    private void updateSkillRecursePoint(GameCharacter character, double skillPoints) throws InvalidSkillPlanException {
        try {
            character.updateSkill(skillPoints);
        }catch(SkillPointsOverflowException e) {
            character.setCurrentTrainingSkill(character.getNextToTrain());
            updateSkillRecursePoint(character, e.overflowAmount);
        }
    }

    public void addPlan(SkillPlan plan) {
        PLAN_LIST.add(plan);
    }

    public void addPlan(SkillPlan... plans) {
        for (SkillPlan plan : plans) {
            addPlan(plan);
        }
    }

    private double getIncreasedSP(long interval) {
        return (double) interval / 1000 * 0.5;
    }

    public void updateSkill(Set<GameCharacter> character, long interval) {
        // 一次更新一堆角色会有性能优势吗？不知道，有空研究一下
        // TODO
    }


}