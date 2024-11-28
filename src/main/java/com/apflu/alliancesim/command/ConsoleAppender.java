package com.apflu.alliancesim.command;

import ch.qos.logback.classic.Logger;
import ch.qos.logback.classic.LoggerContext;
import ch.qos.logback.classic.PatternLayout;
import ch.qos.logback.classic.encoder.PatternLayoutEncoder;
import ch.qos.logback.classic.spi.ILoggingEvent;
import ch.qos.logback.core.AppenderBase;
import ch.qos.logback.core.encoder.Encoder;
import org.jline.reader.LineReader;
import org.jline.reader.LineReaderBuilder;
import org.jline.terminal.Terminal;
import org.jline.terminal.TerminalBuilder;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.Arrays;

public class ConsoleAppender extends AppenderBase<ILoggingEvent> {
    private Terminal terminal;
    private LineReader reader;

    private final PatternLayoutEncoder encoder = new PatternLayoutEncoder();
    private final PatternLayout layout = new PatternLayout();


    @Override
    public void start() {
        try {
            Console.setTerminal(TerminalBuilder.terminal());
            Console.setReader(LineReaderBuilder.builder().terminal(terminal).build());
            terminal = Console.getTerminal();
            reader = Console.getReader();

            Logger rootLogger = (Logger) LoggerFactory.getLogger("root");
            LoggerContext loggerContext = rootLogger.getLoggerContext();

            layout.setPattern("%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n");
            layout.setContext(loggerContext);
            layout.start();
        } catch (IOException e) {
            addError("Error opening terminal", e);
        }
        super.start();
    }

    @Override
    protected void append(ILoggingEvent iLoggingEvent) {
        //String message = iLoggingEvent.getFormattedMessage();
        String result = layout.doLayout(iLoggingEvent);

        //Console.getReader().printAbove(message);
        Console.getReader().printAbove(result);
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
}
