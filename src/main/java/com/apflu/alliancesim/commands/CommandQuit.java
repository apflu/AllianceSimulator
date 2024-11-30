package com.apflu.alliancesim.commands;

import com.apflu.alliancesim.AllianceSim;
import com.apflu.alliancesim.command.Command;
import com.apflu.alliancesim.command.CommandArgs;
import com.apflu.alliancesim.events.EventCore;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CommandQuit extends Command {
    private static final Logger logger = LoggerFactory.getLogger(CommandQuit.class);
    @Override
    public void execute(CommandArgs input) {
        logger.info("Attempting to quit. Notifying quit listeners...");
        EventCore.INSTANCE.notifySave()
                .notifyQuit();

        AllianceSim.end();

        logger.info("All jobs finished. Goodbye.");
    }
}
