package com.apflu.alliancesim.game.training;

import com.apflu.alliancesim.game.Skill;
import com.apflu.alliancesim.util.exceptions.SkillPointsOverflowException;
import org.jetbrains.annotations.NotNull;

import java.util.Map;
import java.util.HashMap;
import java.util.stream.Collectors;


public class SkillSet {
    private final Map<Integer,TrainedSkill> skillDict = new HashMap<>();
    private int focusID;

    public SkillSet() {}

    public Map<Integer,TrainedSkill>  getCompleted() {
        return this.skillDict.entrySet().stream().filter(lambda -> lambda.getValue().isCompleted())
                .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
    }

    public Skill getFocus() {
        return skillDict.get(focusID).getSkill();
    }

    public void setFocus(@NotNull Skill skill) {
        if (this.skillDict.containsKey(skill.getID())) {
            this.focusID = skill.getID();
        }else {
            this.skillDict.put(skill.getID(), new TrainedSkill(skill));
        }
    }

    public void incrementSkill(double skillPoints) throws SkillPointsOverflowException {
        skillDict.get(focusID).addSkillPoint(skillPoints);
    }

    public int getLv(Skill skill) {
        TrainedSkill skillInSet = skillDict.get(skill.getID());
        if (skillInSet == null) return 0;
        else {
            return skillInSet.getLv();
        }
    }
}