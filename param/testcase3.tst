# Simple trace file
BASELINE = baseline3.bsl

WHENEVER 1-02:00:00
  ENSURE not led UNTIL 1-03:59:59 #lightoff until 4:00AM
  WAIT led FOR 3600 #Raisetemp should trigger

WHENEVER led
  ENSURE temperature[0] < 28 # make sure doesnt overheat

