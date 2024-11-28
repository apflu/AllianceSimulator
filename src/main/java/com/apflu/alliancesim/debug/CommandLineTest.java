package com.apflu.alliancesim.debug;

import com.apflu.alliancesim.debug.constants.TestCoroutines;
import com.apflu.alliancesim.debug.versions.MilestoneBasicSkillTraining;
import org.jline.reader.LineReader;
import org.jline.reader.LineReaderBuilder;
import org.jline.terminal.Terminal;
import org.jline.terminal.TerminalBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.bridge.SLF4JBridgeHandler;

import java.util.Scanner;


public final class CommandLineTest {
    static {
        SLF4JBridgeHandler.removeHandlersForRootLogger();
        SLF4JBridgeHandler.install();
        java.util.logging.Logger.getLogger("").setLevel(java.util.logging.Level.FINEST);
    }

    private static final Logger logger = LoggerFactory.getLogger(CommandLineTest.class);
    private static final Scanner scanner = new Scanner(System.in);
    @SuppressWarnings("InfiniteLoopStatement")
    public static void main(final String[] args) {

        try {
            //Terminal terminal = TerminalBuilder.terminal();
            //LineReader reader = LineReaderBuilder.builder().terminal(terminal).build();

            //Terminal terminal = Console.getTerminal();
            //LineReader reader = Console.getReader();
            //System.out.println(org.jline.utils.Log.isDebugEnabled());

            TestCoroutines.INSTANCE.doNonBlockWait();

            while (true) {
                //System.out.print("\r\033[K");
                String command = scanner.nextLine();

                logger.info("received command: {}", command);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
