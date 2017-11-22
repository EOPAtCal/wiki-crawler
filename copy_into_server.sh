#!/bin/sh
PUBLIC="../server/public"
rm -rf $PUBLIC
mkdir $PUBLIC
cp clean/* $PUBLIC

LOGS="../server/logs"
rm -rf $LOGS
mkdir $LOGS
cp logs/path.bfs $LOGS