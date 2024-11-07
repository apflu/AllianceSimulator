package com.apflu.alliancesim.game;

public abstract class SpaceObject {
    /**
     * 如果为true，将会使血条隐藏。
     */
    protected boolean invulnerable = false;

    /**
     * 物件在受到伤害时触发的事件。一般包括记录log，扣减血量，以及触发特殊效果、ai判断等。
     * @param amount 伤害量
     */
    public abstract void takeDamage(int amount);

    public boolean isInvulnerable() {
        return invulnerable;
    }
}
