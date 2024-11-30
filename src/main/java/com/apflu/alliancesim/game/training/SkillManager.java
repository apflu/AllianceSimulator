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
        try {
            updateSkillRecurse(character, getIncreasedSP(interval));
        }catch (InvalidSkillPlanException e) {
            List<SkillPlan> trainable = PLAN_LIST.stream().filter(lambda ->
                    (lambda.getNotIncluded(character.getCompleted())).size() > 0).collect(Collectors.toCollection(ArrayList::new));
            if (trainable.size() == 0) throw new NoAvailablePlanException();
            try {
                character.setCurrentPlan(trainable.get(rand.nextInt(trainable.size())));
            } catch (InvalidSkillPlanException ex) {
                throw new RuntimeException("Should have no InvalidSkillPlanException, but caught one.");
            }
        }
    }

    public void addPlan(SkillPlan plan) {
        PLAN_LIST.add(plan);
    }

    private void updateSkillRecurse(GameCharacter character, double skillPoints) throws InvalidSkillPlanException {
        try {
            character.updateSkill(skillPoints);
        }catch(SkillPointsOverflowException e) {
            character.setCurrentTrainingSkill(character.getNextToTrain());
            updateSkillRecurse(character, e.overflowAmount);
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
