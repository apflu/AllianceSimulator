package com.apflu.alliancesim.game.training;

import com.apflu.alliancesim.game.Skill;

import java.util.Arrays;
import java.util.Collection;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

public class SkillPlan extends ArrayList<Skill>{
    private String name;

    public SkillPlan(String name) {
        super();
        this.name = name;
    }

    public SkillPlan(String name, Collection<? extends Skill> c) {
        super(c);
        this.name = name;
    }

    public SkillPlan(String name, Skill... skills) {
        this(name, Arrays.stream(skills).toList());
    }

    public String getName() {
        return this.name;
    }

    public List<Skill> getNotIncluded(SkillSet set) {
        return this.stream().filter(lambda ->
                !set.getCompleted().containsKey(lambda.getID())).collect(Collectors.toCollection(ArrayList::new));
    }

    public List<Skill> getNotIncluded(List<Skill> set) {
        return this.stream().filter(lambda ->
                !set.stream().map(Skill::getID).collect(Collectors.toCollection(ArrayList::new)).
                contains(lambda.getID())).collect(Collectors.toCollection(ArrayList::new));
    }
}
