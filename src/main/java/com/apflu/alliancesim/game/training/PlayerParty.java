package com.apflu.alliancesim.game.training;

public class PlayerParty {
    private final SkillPlan currentPlan;

    public PlayerParty(SkillPlan currentPlan) {
        this.currentPlan = currentPlan;
    }

    public SkillPlan getCurrentPlan() {
        return currentPlan;
    }
}
