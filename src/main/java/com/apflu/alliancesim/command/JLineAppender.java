package com.apflu.alliancesim.command;

import ch.qos.logback.classic.Logger;
import ch.qos.logback.classic.LoggerContext;
import ch.qos.logback.classic.encoder.PatternLayoutEncoder;
import ch.qos.logback.classic.spi.ILoggingEvent;
import ch.qos.logback.core.AppenderBase;
import ch.qos.logback.core.Layout;
import org.jline.reader.LineReader;
import org.jline.reader.LineReaderBuilder;
import org.jline.terminal.Terminal;
import org.jline.terminal.TerminalBuilder;
import org.slf4j.LoggerFactory;

import java.io.IOException;

public class JLineAppender extends AppenderBase<ILoggingEvent> {
    private Terminal terminal;
    private LineReader reader;

    private final PatternLayoutEncoder encoder = new PatternLayoutEncoder();
    private Layout<ILoggingEvent> layout;

    @Override
    public void start() {
        try {
            Terminal terminal = TerminalBuilder.builder()
                    .dumb(false)
                    .build();
            LineReader reader = LineReaderBuilder.builder().terminal(terminal).build();

            Console.setTerminal(terminal);
            Console.setReader(reader);
        } catch (IOException e) {
            e.printStackTrace();
        }
        super.start();
    }

    @Override
    protected void append(ILoggingEvent iLoggingEvent) {
        String message = layout.doLayout(iLoggingEvent);
        Console.getReader().printAbove(message);
    }

    @Override
    public void stop() {
        if (terminal != null) {
            try {
                terminal.close();
            } catch (IOException e) {
                addError("Error closing terminal", e);
            }
        }
        super.stop();
    }

    public void setLayout(Layout<ILoggingEvent> layout) {
        this.layout = layout;
    }
}
