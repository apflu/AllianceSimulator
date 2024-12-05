package com.apflu.alliancesim.command;

import org.jline.reader.LineReader;
import org.jline.reader.LineReaderBuilder;
import org.jline.terminal.Terminal;
import org.jline.terminal.TerminalBuilder;

import java.io.IOException;

public class ConsoleAppender implements EventAppender {
    private final LineReader lineReader;

    public ConsoleAppender(LineReader lineReader) {
        this.lineReader = lineReader;
    }

    public void print(String message) {
        lineReader.printAbove(message);
    }
    public static ConsoleAppender create() throws IOException {
        Terminal terminal = TerminalBuilder.terminal();
        // 待解决问题
        LineReader lineReader = LineReaderBuilder.builder()
                .terminal(terminal)
                .build();
        return new ConsoleAppender(lineReader);
    }
}