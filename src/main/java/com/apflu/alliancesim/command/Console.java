package com.apflu.alliancesim.command;

import org.jline.reader.LineReader;
import org.jline.terminal.Terminal;

public final class Console {
    private static Terminal terminal;
    private static LineReader reader;

    public static Terminal getTerminal() {
        return terminal;
    }

    public static LineReader getReader() {
        return reader;
    }

    public static void println(Object message) {
        reader.callWidget(LineReader.CLEAR);
        terminal.writer().println(message);
        reader.callWidget(LineReader.REDRAW_LINE);
        reader.callWidget(LineReader.REDISPLAY);
        terminal.writer().flush();
    }

    public static void setTerminal(Terminal terminal) {
        Console.terminal = terminal;
    }

    public static void setReader(LineReader reader) {
        Console.reader = reader;
    }
}
