#!/bin/bash
set -e

gosu postgres postgres --single -jE <<-EOSQL
	CREATE DATABASE "twitch" ;
EOSQL

gosu postgres postgres --single twitch -jE < /files/create_tables.sql
