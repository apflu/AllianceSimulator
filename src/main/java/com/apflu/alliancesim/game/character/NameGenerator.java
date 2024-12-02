package com.apflu.alliancesim.game.character;

import java.util.Iterator;
import java.util.List;

public class NameGenerator implements Iterator<String> {


    private final Iterator<String> iterator;

    public NameGenerator(Iterator<String> iterator) {
        this.iterator = iterator;
    }

    @Override
    public boolean hasNext() {
        return iterator.hasNext();
    }

    /**
     * 与普通Iterator不同的是，在hasNext() = false时调用next()，
     * 应fallback回默认的NameGenerator。如果默认NameGenerator也耗尽了，那么使用随机字符串生成器。
     * @return 名字
     */
    @Override
    public String next() {
        return iterator.next();
    }

    public static NameGenerator from(Iterator<String> iterator) {
        return new NameGenerator(iterator);
    }

    public static NameGenerator from(List<String> list) {
        return from(list.iterator());
    }
}
