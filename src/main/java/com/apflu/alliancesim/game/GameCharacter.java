package com.apflu.alliancesim.game;

public class GameCharacter {
    private Skill currentTrainingSkill;

    /**
     * 逻辑最好不在这里处理。
     * @param interval 离上次更新的间隔；*毫秒*！
     */
    public void updateSkill(long interval) {

    }

    public Skill getCurrentTrainingSkill() {
        return currentTrainingSkill;
    }

    public Skill getNextCurrentTrainingSkill() {
        return null; // TODO
    }
}
