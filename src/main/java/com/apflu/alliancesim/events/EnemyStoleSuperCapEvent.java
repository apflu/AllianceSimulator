package com.apflu.alliancesim.events;

import com.apflu.alliancesim.event.EventSession;
import com.apflu.alliancesim.event.GameEvent;
import com.apflu.alliancesim.event.GameEventOption;
import com.apflu.alliancesim.game.GameCharacter;

public class EnemyStoleSuperCapEvent extends GameEvent {
    public EnemyStoleSuperCapEvent(EventSession session) {
        super(session, new GameEventOption("okay.", "player {} lost a nyx", it -> {}));
    }

    @Override
    public String getText() {
        return "foo";
    }

    @Override
    public String getDescription() {
        return "bar";
    }

    @Override
    public boolean isEligible() {
        return session.getAlliance().getMembers().stream()
                .filter(GameCharacter::isInSpace)
                .anyMatch(member -> member.getCurrentShip().isSuperCapitalShip());
    }
}
