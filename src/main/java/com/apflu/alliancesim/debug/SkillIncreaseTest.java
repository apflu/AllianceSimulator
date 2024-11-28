package com.apflu.alliancesim.debug;

import com.apflu.alliancesim.debug.constants.TestCharacters;
import com.apflu.alliancesim.debug.constants.TestSkills;
import com.apflu.alliancesim.game.training.SkillManager;
import com.apflu.alliancesim.util.exceptions.SkillPointsOverflowException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.concurrent.TimeUnit;

public final class SkillIncreaseTest {
    private static final Logger logger = LoggerFactory.getLogger(SkillIncreaseTest.class);
    public static void main(String[] args) throws InterruptedException {
        TestCharacters.Empty_CaldariCitizen.setCurrentTrainingSkill(TestSkills.Mining);
        while(true) {
            try{
                SkillManager.INSTANCE.updateSkill(TestCharacters.Empty_CaldariCitizen, 60_000_000);

            } catch (SkillPointsOverflowException e) {
                logger.info("SP overflow, amount: {}", e.overflowAmount);
                break;
            }
            TimeUnit.SECONDS.sleep(1);
        }
    }
}
