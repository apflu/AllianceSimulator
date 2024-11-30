package com.apflu.alliancesim.command;

import org.jline.console.CommandMethods;
import org.jline.console.CommandRegistry;
import org.jline.console.impl.JlineCommandRegistry;
import org.jline.reader.LineReader;
import org.jline.terminal.Terminal;

import java.util.Map;

public class JLineCommandHandler extends JlineCommandRegistry implements CommandRegistry {
    private LineReader reader;

    public JLineCommandHandler(Map<String, CommandMethods> commands) {
        super();
        registerCommands(commands);
    }

    public void setLineReader(LineReader reader) {
        this.reader = reader;
    }

    private Terminal terminal() {
        return reader.getTerminal();
    }
}
