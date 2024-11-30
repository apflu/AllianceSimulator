package com.apflu.alliancesim.events;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class EventCore {
    public static final EventCore INSTANCE = new EventCore();
    private final Map<String, List<Listener>> listeners = new HashMap<>();
    private static final Logger logger = LoggerFactory.getLogger(EventCore.class);

    public void register(Listener listener) {
        if (!listeners.containsKey(listener.getName())) {
            List<Listener> listenerList = this.listeners.get(listener.getName());
            listenerList.add(listener);
        } else {
            listeners.put(listener.getName(), new ArrayList<>(List.of(listener)));
        }
    }

    public void unregister(Listener listener) {
        // TODO
    }

    public EventCore notifySave() {
        List<Listener> list = listeners.get("save");
        for (Listener listener : list) {
            if (listener instanceof SaveListener saveListener) {
                saveListener.onSave();
            } else {
                warnDuplicate(listener);
            }
        }
        return this;
    }

    public EventCore notifyQuit() {
        List<Listener> list = listeners.get("quit");
        for (Listener listener : list) {
            if (listener instanceof QuitListener quitListener) {
                quitListener.onQuit();
            } else {
                warnDuplicate(listener);
            }
        }
        return this;
    }

    private void warnDuplicate(Listener listener) {
        logger.warn("Listener registered as {}, but not instance of {}!",
                listener.getClass().getName(), listener.getName());
    }
}
