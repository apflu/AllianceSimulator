package com.apflu.alliancesim;

import com.apflu.alliancesim.command.Console;
import com.apflu.alliancesim.debug.constants.TestCoroutines;
import com.apflu.alliancesim.debug.versions.MilestoneCommandLine;
import org.jline.reader.LineReader;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AllianceSim {
    private static final Logger logger = LoggerFactory.getLogger(AllianceSim.class);

    private static boolean alive = true;

    public static void main(final String[] args) {
        LineReader reader = Console.getReader();

        try {
            while (alive) {
                String command = reader.readLine("> ");

                logger.info("received command: {}", command);
            }
        } catch (Exception exception) {
            logger.warn(exception.getMessage(), exception);
        }
    }

    public static void end() {
        alive = false;
    }

    public static boolean isAlive() {
        return alive;
    }
}
