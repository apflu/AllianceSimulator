package com.apflu.alliancesim.debug;

import com.apflu.alliancesim.debug.constants.TestCharacters;
import com.apflu.alliancesim.debug.constants.TestSkills;
import com.apflu.alliancesim.game.training.SkillManager;
import com.apflu.alliancesim.util.exceptions.NoAvailablePlanException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public final class SkillIncreaseTest {
    private static final Logger logger = LoggerFactory.getLogger(SkillIncreaseTest.class);
    public static void main(String[] args) {
        SkillManager.INSTANCE.addPlan(TestSkills.PlanAHAC);
        SkillManager.INSTANCE.addPlan(TestSkills.PlanCHAC);
        SkillManager.INSTANCE.addPlan(TestSkills.PlanGHAC);
        SkillManager.INSTANCE.addPlan(TestSkills.PlanMHAC);
        SkillManager.INSTANCE.addPlan(TestSkills.PlanMiner);
        while(true) {
            try{
                SkillManager.INSTANCE.updateSkill(TestCharacters.Empty_CaldariCitizen, 60_000);
            } catch (NoAvailablePlanException e) {
                logger.info("No Available Skill Plan to Train");
                break;
            }
        }
    }
}
