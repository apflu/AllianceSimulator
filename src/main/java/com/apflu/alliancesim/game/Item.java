package com.apflu.alliancesim.game;

public abstract class Item {
    // TODO: 临时解决方案。后期将删除这些字段，并创建i18n模块来解耦。
    private String name = "Unnamed Item";
    private String description = "";

    public float Volume = 0f;
    public final int ID;

    protected Item(int id) {
        ID = id;
    }

    public String getName() {
        return name;
    }

    public String getDescription() {
        return description;
    }
}
