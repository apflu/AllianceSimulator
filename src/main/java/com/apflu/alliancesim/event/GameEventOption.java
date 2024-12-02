package com.apflu.alliancesim.event;

import java.util.function.Consumer;

public class GameEventOption {
    private final String optionText;
    private final String tooltipText;
    private final Consumer<EventSession> onApply;

    public GameEventOption(String optionText, String tooltipText, Consumer<EventSession> onApply) {
        this.optionText = optionText;
        this.tooltipText = tooltipText;
        this.onApply = onApply;
    }

    public void apply(EventSession session) {
        onApply.accept(session);
    }

    public String getOptionText() {
        return optionText;
    }

    public String getTooltipText() {
        return tooltipText;
    }
}
