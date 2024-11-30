plugins {
    id("java")
    kotlin("jvm") version "2.0.21"
    id("application")

    id("com.gradleup.shadow") version "9.0.0-beta2"
}

java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}

group = "org.example"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
}

val exposedVersion: String by project
val slf4jVersion: String by project

dependencies {
    // log
    implementation("io.github.oshai:kotlin-logging-jvm:7.0.0")
    implementation("ch.qos.logback:logback-classic:1.5.12")
    implementation("org.slf4j:slf4j-api:$slf4jVersion")
    implementation("org.slf4j:jul-to-slf4j:$slf4jVersion")

    // coroutine
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.8.1")

    // command line
    implementation("org.jline:jline:3.27.1")
    implementation("org.jline:jline-terminal-jni:3.27.1")
    implementation("org.fusesource.jansi:jansi:2.4.1")
    implementation("net.java.dev.jna:jna:5.15.0")

    // unit test
    testImplementation(platform("org.junit:junit-bom:5.10.0"))
    testImplementation("org.junit.jupiter:junit-jupiter")

    // SQL
    implementation("org.jetbrains.exposed:exposed-core:$exposedVersion")
    implementation("org.jetbrains.exposed:exposed-crypt:$exposedVersion")
    implementation("org.jetbrains.exposed:exposed-dao:$exposedVersion")
    implementation("org.jetbrains.exposed:exposed-jdbc:$exposedVersion")

    implementation("org.jetbrains.exposed:exposed-java-time:$exposedVersion")
    // or
    implementation("org.jetbrains.exposed:exposed-kotlin-datetime:$exposedVersion")

    implementation("org.jetbrains.exposed:exposed-json:$exposedVersion")
    implementation("org.jetbrains.exposed:exposed-money:$exposedVersion")
    implementation("org.jetbrains.exposed:exposed-spring-boot-starter:$exposedVersion")

}

application {
    mainClass = "com.apflu.alliancesim.debug.versions.MilestoneCommandLine"
}

tasks.test {
    useJUnitPlatform()
}

tasks.jar {
    manifest {
        attributes(
            "Main-Class" to application.mainClass
        )
    }
}

tasks.register<JavaExec>("bmining") {
    group = "application"
    description = "Basic Mining test"
    classpath = sourceSets["main"].runtimeClasspath
    mainClass.set("com.apflu.alliancesim.debug.versions.MilestoneBasicMining")
}

tasks.register<JavaExec>("bskill") {
    group = "application"
    description = "Basic Skill Training test"
    classpath = sourceSets["main"].runtimeClasspath
    mainClass.set("com.apflu.alliancesim.debug.versions.MilestoneBasicSkillTraining")
}

tasks.register<JavaExec>("linetest") {
    standardInput = System.`in`
    group = "application"
    description = "Command Line test"
    classpath = sourceSets["main"].runtimeClasspath
    mainClass.set("com.apflu.alliancesim.debug.CommandLineTest")
}