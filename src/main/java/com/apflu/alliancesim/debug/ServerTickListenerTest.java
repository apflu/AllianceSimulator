package com.apflu.alliancesim.debug;

import com.apflu.alliancesim.event.ListenerManager;
import com.apflu.alliancesim.event.ServerTickListener;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ServerTickListenerTest {
    private static final Logger logger = LoggerFactory.getLogger(ServerTickListenerTest.class);
    public static void main(String[] args) {
        ListenerManager.INSTANCE.register((ServerTickListener) () -> {
            logger.info("doing server tick");
        });
    }
}
