@echo off
setlocal
where mvn >nul 2>&1
if %errorlevel% equ 0 (
    mvn %*
    exit /b %errorlevel%
)
if defined MAVEN_HOME (
    "%MAVEN_HOME%\bin\mvn.cmd" %*
    exit /b %errorlevel%
)
echo [mvnw] Maven nao encontrado. Adicione mvn ao PATH ou defina MAVEN_HOME.
echo [mvnw] Download: https://maven.apache.org/download.cgi
exit /b 1
