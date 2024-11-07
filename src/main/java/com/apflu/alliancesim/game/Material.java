package com.apflu.alliancesim.game;

public class Material extends Item implements Salvageable {
    protected Material(int id) {
        super(id);
    }

    /**
     * 将
     * @param id
     * @return
     */
    public static Material of(int id) {
        return new Material(id); // TODO
    }
}
