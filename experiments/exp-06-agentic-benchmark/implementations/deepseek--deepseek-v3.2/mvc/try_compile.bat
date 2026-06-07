@echo off
echo Trying to compile with Maven...
call mvn --version
if %errorlevel% neq 0 (
    echo Maven not found, trying mvn.cmd...
    call mvn.cmd --version
)
if %errorlevel% neq 0 (
    echo Trying to compile Java directly...
    javac -version
)