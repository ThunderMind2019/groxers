#!/usr/bin/env bash

for name in "alfatah" "gulahmed" "j." "khaadi" "mcc" "metro" "sanasafinaz" "warda";do
    curl http://18.217.191.191:6800/schedule.json -d project=groxers -d spider=$name &
done
