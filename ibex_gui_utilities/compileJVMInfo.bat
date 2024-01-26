setlocal
REM dependent Jar path
SET "ROOT=%~dp0"
SET "BUDDY=net\bytebuddy\byte-buddy\1.14.11"
SET "AGENT=net\bytebuddy\byte-buddy-agent\1.14.11"
SET "JNA=net\java\dev\jna\jna\5.12.1"
SET "PLATFORM=net\java\dev\jna\jna-platform\5.12.1"

REM Setting the class path
SET "CLASSPATH=%ROOT%;%ROOT%%BUDDY%\byte-buddy-1.14.11.jar;%ROOT%%AGENT%\byte-buddy-agent-1.14.11.jar;%ROOT%%JNA%\jna-5.12.1.jar;%ROOT%%PLATFORM%\jna-platform-5.12.1.jar"
JAVAC "%ROOT%GetVMInfo.java"
pause
