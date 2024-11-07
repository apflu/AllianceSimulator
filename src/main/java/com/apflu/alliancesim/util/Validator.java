package com.apflu.alliancesim.util;

public interface Validator<T> {
    boolean validate(T value);
    default String getName() {
        return "Unnamed Validator";
    }
}
