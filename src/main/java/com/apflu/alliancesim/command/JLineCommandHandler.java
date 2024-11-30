package com.apflu.alliancesim.command;

import org.jline.console.CommandInput;
import org.jline.console.CommandMethods;
import org.jline.console.CommandRegistry;
import org.jline.console.impl.JlineCommandRegistry;
import org.jline.reader.LineReader;
import org.jline.terminal.Terminal;

import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Collectors;

public class JLineCommandHandler extends JlineCommandRegistry implements CommandRegistry {
    private LineReader reader;

    public JLineCommandHandler(Map<String, Class<? extends Command>> commands) throws Exception {
        Map<String, CommandMethods> commandExecute = new HashMap<>();
        for (Map.Entry<String, Class<? extends Command>> entry : commands.entrySet()) {
            Command command = entry.getValue().getDeclaredConstructor().newInstance();

            // ugly
            commandExecute.put(entry.getKey(), new CommandMethods(
                    commandInput -> {
                        command.execute(new CommandArgs(commandInput));
                    },
                    this::defaultCompleter));
        }
        registerCommands(commandExecute);
    }

    public void setLineReader(LineReader reader) {
        this.reader = reader;
    }

    private Terminal terminal() {
        return reader.getTerminal();
    }
}
