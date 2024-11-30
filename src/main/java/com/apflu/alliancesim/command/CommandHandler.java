package com.apflu.alliancesim.command;

import java.util.HashMap;
import java.util.Map;

public class CommandHandler {
    // 之所以叫global是因为要保留为每个玩家创建一个instance的可能性
    public static final CommandHandler GLOBAL_INSTANCE = new CommandHandler();
    private final Map<String, Class<? extends Command>> commands= new HashMap<>();

    public void register(Class<? extends Command> commandClass, String commandBody) {
        commands.put(commandBody, commandClass);
    }

    public void register(Command commandClass, String... aliasCollection) {
        for (String alias : aliasCollection) {
            register(commandClass.getClass(), alias);
        }
    }

    public Command getCommand(String commandBody) throws Exception {
        Class<? extends Command> commandClass = commands.get(commandBody);
        if (commandClass == null) {
            throw new IllegalArgumentException("No such command: " + commandBody);
        }
        return commandClass.getDeclaredConstructor().newInstance();
    }
}
