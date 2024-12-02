package com.apflu.alliancesim.player;

import com.apflu.alliancesim.event.EventHandler;
import com.apflu.alliancesim.event.GameEvent;
import com.apflu.alliancesim.event.GameEventLine;
import com.apflu.alliancesim.event.GameEventOption;
import com.apflu.alliancesim.game.GameCharacter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.*;

public class Alliance {
    private static final Logger logger = LoggerFactory.getLogger(Alliance.class);
    private final Map<String, Object> flags = new HashMap<>();
    private final Set<GameCharacter> members = new HashSet<>();

    /**
     * 获取当前最上面的那件事件，并显示给玩家。
     * 最上面的事件应当唯一，同时只能处理一件事件；多次执行应当保证结果不变。
     */
    public void displayCurrentEvent() {
        // TODO
        getPendingEvents().get(0).immediate();
    }

    public void resolveEvent(GameEvent event, GameEventOption option) {
        if (event.getSession().getAlliance().equals(this)) {
            option.apply(event.getSession());
            event.after();
        } else {
            logger.warn("Trying to resolve event {}, but does not belong to alliance {}!", event, this);
        }
    }

    public List<GameEvent> getPendingEvents() {
        return EventHandler.INSTANCE.getPendingEvents(this);
    }

    public List<GameEventLine> getActiveEventLines() {
        return EventHandler.INSTANCE.getActiveEventLines(this);
    }

    public void checkAllEligible() {
        EventHandler.INSTANCE.checkAllEligible(this);
    }

    public Map.Entry<String, Object> getFlag(String key) {
        return flags.entrySet().stream()
                .filter(x -> x.getKey().equals(key))
                .findFirst().orElse(null);
    }

    public boolean setFlag(String key, Object value) {
        return flags.put(key, value) == null;
    }

    public boolean removeFlag(String key) {
        return flags.remove(key) != null;
    }

    public boolean addMember(GameCharacter character) {
        return members.add(character);
    }

    public boolean removeMember(GameCharacter character) {
        return members.remove(character);
    }

    public Set<GameCharacter> getMembers() {
        return Set.copyOf(members);
    }

    public int getSize() {
        return members.size();
    }
}
