plugins {
    kotlin("jvm") version "1.9.22"
    // all-open: CDI exige classes não-final; Kotlin fecha tudo por padrão
    kotlin("plugin.allopen") version "1.9.22"
    id("io.quarkus") version "3.8.3"
}

repositories {
    mavenCentral()
    mavenLocal()
}

val quarkusPlatformGroupId: String by project
val quarkusPlatformArtifactId: String by project
val quarkusPlatformVersion: String by project

dependencies {
    implementation(enforcedPlatform("$quarkusPlatformGroupId:$quarkusPlatformArtifactId:$quarkusPlatformVersion"))

    // REST + JSON
    implementation("io.quarkus:quarkus-resteasy-reactive")
    implementation("io.quarkus:quarkus-resteasy-reactive-jackson")

    // Validação de campos (@NotBlank, @Size)
    implementation("io.quarkus:quarkus-hibernate-validator")

    // CDI — injeção de dependências
    implementation("io.quarkus:quarkus-arc")

    // Suporte Kotlin no Quarkus + Jackson Kotlin module
    implementation("io.quarkus:quarkus-kotlin")
    implementation("org.jetbrains.kotlin:kotlin-stdlib")
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin")

    // Testes
    testImplementation("io.quarkus:quarkus-junit5")
    testImplementation("io.rest-assured:rest-assured")

    // Cobertura de código
    testImplementation("io.quarkus:quarkus-jacoco")
}

group = "com.benchmark"
version = "1.0.0-SNAPSHOT"

tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile> {
    kotlinOptions.jvmTarget = "21"
}

// Abre as classes anotadas para CDI (equivale ao all-open Maven)
allOpen {
    annotation("jakarta.enterprise.context.ApplicationScoped")
    annotation("jakarta.enterprise.context.RequestScoped")
    annotation("jakarta.ws.rs.Path")
    annotation("jakarta.ws.rs.ext.Provider")
}

tasks.withType<Test> {
    systemProperty("java.util.logging.manager", "org.jboss.logmanager.LogManager")
    useJUnitPlatform()
}
