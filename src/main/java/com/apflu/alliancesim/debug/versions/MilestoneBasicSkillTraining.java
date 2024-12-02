package com.apflu.alliancesim.debug.versions;

import ch.qos.logback.classic.LoggerContext;
import ch.qos.logback.core.util.StatusPrinter2;
import com.apflu.alliancesim.debug.constants.TestCharacters;
import com.apflu.alliancesim.debug.constants.TestCoroutines;
import com.apflu.alliancesim.debug.constants.TestSkills;
import com.apflu.alliancesim.game.GameCharacter;
import com.apflu.alliancesim.game.training.SkillManager;
import com.apflu.alliancesim.gameschedule.Scheduler;
import com.apflu.alliancesim.gameschedule.SkillUpdaterBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashSet;

public final class MilestoneBasicSkillTraining {
    private static final Logger logger = LoggerFactory.getLogger(MilestoneBasicSkillTraining.class);
    public static void main(String[] args) {
        logger.debug("Running MilestoneBasicSkill 1...");
        System.out.println();

        LoggerContext lc = (LoggerContext) LoggerFactory.getILoggerFactory();
        new StatusPrinter2().print(lc);
        logger.debug("finished logger config output.");

        SkillManager.INSTANCE.addPlan(TestSkills.PlanAHAC,
                TestSkills.PlanCHAC,
                TestSkills.PlanGHAC,
                TestSkills.PlanMHAC,
                TestSkills.PlanMiner);

        // expect to do nothing, as the character list is empty
        SkillUpdaterBuilder updater = new SkillUpdaterBuilder(new HashSet<>(), 6000);
        Scheduler.INSTANCE.startSkillUpdater(updater, true);

        GameCharacter testChar = TestCharacters.Empty_CaldariCitizen;
        updater.addCharacter(testChar);

        TestCoroutines.INSTANCE.doInfiniteWait();
    }
}
