package com.apflu.alliancesim.debug.constants;

import com.apflu.alliancesim.game.Skill;
import com.apflu.alliancesim.game.training.SkillPlan;

import java.util.Arrays;

public final class TestSkills {
    public static final Skill Mining            = new Skill(1,0,"Mining");
    public static final Skill Gunnery           = new Skill(2,1,"Gunnery");
    public static final Skill GunneryAux        = new Skill(4,2,"Gunnery Supporting Skill");
    public static final Skill Missile           = new Skill(2,3,"Missile");
    public static final Skill MissileAux        = new Skill(4,4,"Missile Supporting Skill");
    public static final Skill HAC               = new Skill(5,5,"Heavy Assault Cruisers");
    public static final Skill ShieldAux         = new Skill(2,6,"Shield Supporting Skill");
    public static final Skill Ice               = new Skill(2,7,"Ice Mining");
    public static final Skill Gas               = new Skill(2,8,"Gas Mining");
    public static final Skill HybridM           = new Skill(2,9,"Medium Hybrid Turrets");
    public static final Skill HybridM2          = new Skill(4,10,"Medium Hybrid Turrets Specialization");
    public static final Skill ACruiser          = new Skill(3,11,"Amarr Cruiser");
    public static final Skill CCruiser          = new Skill(3,12,"Caldari Cruiser");
    public static final Skill GCruiser          = new Skill(3,13,"Gallente Cruiser");
    public static final Skill MCruiser          = new Skill(3,14,"Minmatar Cruiser");
    public static final Skill Ice2              = new Skill(4,15,"Ice Mining Specialization");
    public static final Skill Gas2              = new Skill(4,16,"Gas Mining Specialization");
    public static final Skill MissileM          = new Skill(2,17,"Medium Missile Launcher");
    public static final Skill MissileM2         = new Skill(4,18,"Medium Missile Launcher Specialization");
    public static final Skill EnergyM           = new Skill(2,19,"Medium Energy Turrets");
    public static final Skill EnergyM2          = new Skill(4,20,"Medium Energy Turrets Specialization");
    public static final Skill ProjectileM       = new Skill(2,21,"Medium Projectile Turrets");
    public static final Skill ProjectileM2      = new Skill(4,22,"Medium Projectile Turrets Specialization");
    public static final Skill ArmorAux          = new Skill(2,23,"Armor Supporting Skill");

    public static final SkillPlan PlanAHAC = new SkillPlan("Amarr HAC", Arrays.asList(Gunnery, ACruiser, HAC, EnergyM, EnergyM2, GunneryAux, ArmorAux));
    public static final SkillPlan PlanCHAC = new SkillPlan("Caldari HAC", Arrays.asList(Missile, CCruiser, HAC, MissileM, MissileM2, MissileAux, ShieldAux));
    public static final SkillPlan PlanGHAC = new SkillPlan("Gallente HAC", Arrays.asList(Gunnery, GCruiser, HAC, HybridM, HybridM2, GunneryAux, ArmorAux));
    public static final SkillPlan PlanMHAC = new SkillPlan("Minmatar HAC", Arrays.asList(Gunnery, MCruiser, HAC, ProjectileM, ProjectileM2, GunneryAux, ShieldAux));
    public static final SkillPlan PlanMiner    = new SkillPlan("Miner", Arrays.asList(Mining, Ice, Gas, Ice2, Gas2));
}
