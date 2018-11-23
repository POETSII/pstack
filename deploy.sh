#!/bin/bash

REDIS_HOST="coleridge"
DAEMON_HOSTS="aesop,coleridge,byron"

time fab -H $DAEMON_HOSTS install setup daemon:"$REDIS_HOST"
