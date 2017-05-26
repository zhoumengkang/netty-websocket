#!/bin/bash
ps -ef|grep [n]etty-websocket |awk '{print "kill -9 ",$2}'|sh

CLASSPATH="."

for jar in `ls ./lib`
do
        CLASSPATH="$CLASSPATH:./lib/$jar"
done

CLASSPATH="./classes:$CLASSPATH"

export CLASSPATH

JAVA_OPTS='-Xms800m -Xmx800m -XX:+PrintGC -XX:+PrintGCTimeStamps -XX:+PrintGCDetails'

nohup /usr/java/jdk1.8.0_65/bin/java $JAVA_OPTS -Dapp.name=netty-websocket -Dapp.base=$PWD  net.mengkang.WebSocketServer >> ./logs/out.log 2>&1 &