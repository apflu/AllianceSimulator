package com.apflu.alliancesim.debug.versions;

import com.apflu.alliancesim.command.Console;
import com.apflu.alliancesim.debug.constants.TestCoroutines;
import org.jline.reader.LineReader;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.bridge.SLF4JBridgeHandler;


public final class MilestoneCommandLine {
    static {
        SLF4JBridgeHandler.removeHandlersForRootLogger();
        SLF4JBridgeHandler.install();
        java.util.logging.Logger.getLogger("").setLevel(java.util.logging.Level.FINEST);
    }
    private static final Logger logger = LoggerFactory.getLogger(MilestoneCommandLine.class);

    @SuppressWarnings("InfiniteLoopStatement")
    public static void main(final String[] args) {
        LineReader reader = Console.getReader();
        try {
            TestCoroutines.INSTANCE.doNonBlockWait();

            while (true) {
                //System.out.print("\r\033[K");
                String command = reader.readLine("> ");

                logger.info("received command: {}", command);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
