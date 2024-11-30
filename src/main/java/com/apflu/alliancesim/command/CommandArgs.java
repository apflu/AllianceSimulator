package com.apflu.alliancesim.command;

import org.jline.console.CommandInput;
import org.jline.console.CommandRegistry;
import org.jline.terminal.Terminal;

import java.io.InputStream;
import java.io.PrintStream;

public class CommandArgs extends CommandInput {
    // 如此继承是为了解耦合JLine，虽然效果有限。

    public CommandArgs(String command, Object[] xargs, CommandRegistry.CommandSession session) {
        super(command, xargs, session);
    }

    public CommandArgs(String command, Object[] args, Terminal terminal, InputStream in, PrintStream out, PrintStream err) {
        super(command, args, terminal, in, out, err);
    }

    public CommandArgs(CommandInput input) {
        super(input.command(), input.xargs(), input.session());
    }
}
