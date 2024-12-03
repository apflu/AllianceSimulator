package com.apflu.alliancesim.event;

import com.apflu.alliancesim.gameschedule.Scheduler;
import kotlin.Unit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class ListenerManager {
    public static final ListenerManager INSTANCE = new ListenerManager();
    private final Map<String, List<Listener>> listeners = new HashMap<>();
    private static final Logger logger = LoggerFactory.getLogger(ListenerManager.class);

    /**
     * start the server tick
     */
    public void start() {
        Scheduler.INSTANCE.registerAsLoop(() -> {
            // TODO
            return Unit.INSTANCE;
        });
    }

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

    public ListenerManager notifySave() {
        List<Listener> list = listeners.get("save");
        for (Listener listener : list) {
            if (listener instanceof SaveListener saveListener) {
                saveListener.onNotify();
            } else {
                warnDuplicate(listener);
            }
        }
        return this;
    }

    public ListenerManager notifyQuit() {
        List<Listener> list = listeners.get("quit");
        for (Listener listener : list) {
            if (listener instanceof QuitListener quitListener) {
                quitListener.onNotify();
            } else {
                warnDuplicate(listener);
            }
        }
        return this;
    }

    public ListenerManager notifyServerTick() {
        List<Listener> list = listeners.get("servertick");
        for (Listener listener : list) {
            if (listener instanceof ServerTickListener serverTickListener) {
                serverTickListener.onNotify();
            } else {
                warnDuplicate(listener);
            }
        }
        return this;
    }

    public ListenerManager doNotify(String name) {
        List<Listener> list = listeners.get(name);
        for (Listener listener : list) {
            listener.onNotify();
        }
        return this;
    }

    private void warnDuplicate(Listener listener) {
        logger.warn("Listener registered as {}, but not instance of {}!",
                listener.getClass().getName(), listener.getName());
    }
}
