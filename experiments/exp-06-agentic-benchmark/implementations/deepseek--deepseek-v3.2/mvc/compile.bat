@echo off
echo Testing Java compilation...
javac -version
if %errorlevel% equ 0 (
    echo Java is available
) else (
    echo Java is not available
)