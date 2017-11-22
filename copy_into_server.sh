#!/bin/sh
PUBLIC="../wiki-server/public"
rm -rf $PUBLIC
mkdir $PUBLIC
cp clean/* $PUBLIC

LOGS="../wiki-server/logs"
rm -rf $LOGS
mkdir $LOGS
cp logs/path.bfs $LOGS