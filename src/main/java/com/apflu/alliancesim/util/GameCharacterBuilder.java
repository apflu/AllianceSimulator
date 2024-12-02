package com.apflu.alliancesim.util;

import com.apflu.alliancesim.game.GameCharacter;
import com.apflu.alliancesim.game.Skill;
import com.apflu.alliancesim.game.character.NameGenerator;
import com.apflu.alliancesim.game.training.SkillSet;

import java.util.ArrayList;
import java.util.List;

public class GameCharacterBuilder implements Builder {
    private final SkillSetBuilder skillSetBuilder;
    private final SkillSet trainedSkills;
    private final NameGenerator nameGenerator;
    private final String name;

    /**
     * 全能constructor；不利于手动创建，一般不进行手动调用
     * @param skillSetBuilder
     * @param trainedSkills
     * @param nameGenerator
     * @param name
     */
    public GameCharacterBuilder(SkillSetBuilder skillSetBuilder, SkillSet trainedSkills,
                                NameGenerator nameGenerator, String name) {
        this.skillSetBuilder = skillSetBuilder;
        this.trainedSkills = trainedSkills;
        this.nameGenerator = nameGenerator;
        this.name = name;
    }

    public GameCharacterBuilder(SkillSet trainedSkills, NameGenerator nameGenerator) {
        this.skillSetBuilder = null;
        this.trainedSkills = trainedSkills;
        this.nameGenerator = nameGenerator;
        this.name = null;
    }

    public GameCharacterBuilder(SkillSet trainedSkills, String name) {
        this.skillSetBuilder = null;
        this.trainedSkills = trainedSkills;
        this.nameGenerator = null;
        this.name = name;
    }


    public GameCharacterBuilder setSkillSetBuilder(SkillSetBuilder skillSetBuilder) {
        return new GameCharacterBuilder(skillSetBuilder, trainedSkills, nameGenerator, name);
    }

    public GameCharacterBuilder setTrainedSkills(SkillSet trainedSkills) {
        return new GameCharacterBuilder(skillSetBuilder, trainedSkills, nameGenerator, name);
    }

    public GameCharacterBuilder setTrainedSkill(Skill skill, int level) {
        //return new GameCharacterBuilder(skillSetBuilder, trainedSkills, generator, name);
        return null; // TODO
    }

    public GameCharacterBuilder setNameGenerator(NameGenerator generator) {
        return new GameCharacterBuilder(skillSetBuilder, trainedSkills, generator, name);
    }

    public GameCharacterBuilder setName(String nameGenerator) {
        return new GameCharacterBuilder(skillSetBuilder, trainedSkills, this.nameGenerator, nameGenerator);
    }

    public GameCharacter build() {
        // 如果trainedSkills已被指定，那么使用它；否则调用skillSetBuilder并进行build()，从而获取一个SkillSet

        // 如果name已被指定，那么使用它；否则调用nameGenerator并进行get()，从而获取一个名字

        return null; // TODO
    }

    public List<GameCharacter> batchBuild() {
        return new ArrayList<>(); // TODO
    }
}
