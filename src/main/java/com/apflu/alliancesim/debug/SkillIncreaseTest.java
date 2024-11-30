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
        SkillManager.INSTANCE.addPlan(TestSkills.PlanAHAC,
                TestSkills.PlanCHAC,
                TestSkills.PlanGHAC,
                TestSkills.PlanMHAC,
                TestSkills.PlanMiner);

        while(true) {
            try{
                SkillManager.INSTANCE.updateSkill(TestCharacters.Empty_CaldariCitizen, 1_000);
            } catch (NoAvailablePlanException e) {
                logger.info("No Available Skill Plan to Train");
                break;
            }
        }
    }
}
