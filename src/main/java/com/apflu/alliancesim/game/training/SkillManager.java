package com.apflu.alliancesim.game.training;

import com.apflu.alliancesim.game.GameCharacter;
import com.apflu.alliancesim.util.exceptions.SkillPointsOverflowException;

import java.util.Set;

public final class SkillManager {
    public static final SkillManager INSTANCE = new SkillManager();

    public void updateSkill(GameCharacter character, long interval) throws SkillPointsOverflowException {
        character.updateSkill(getIncreasedSP(interval));
    }

    private double getIncreasedSP(long interval) {
        return (double) interval / 1000 * 0.5;
    }

    public void updateSkill(Set<GameCharacter> character, long interval) {
        // 一次更新一堆角色会有性能优势吗？不知道，有空研究一下
        // TODO
    }


}
