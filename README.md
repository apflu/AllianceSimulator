# Alliance Simulator
## 运行
由于使用了JLine来支持一些命令行的高级功能，正常调试最好是以以下方式进行：
在根目录下执行：
```
.\gradlew build
java -jar .\build\libs\AllianceSim2-1.0-SNAPSHOT-all.jar
```

如果你在IDE中直接使用运行，会导致JLine使用dumb terminal，可能会出现一些问题。例如，你输入到一半的命令会被新的输出信息清空。

不过一般而言，这并不会对调试造成太大的影响，除了输入到一半的命令会消失以外。
