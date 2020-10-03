# Simple trace file
BASELINE = baseline4.bsl

WHENEVER 1-08:01:00
  WAIT fan FOR 1800 #fan should be on across two scheduled behaviors

WHENEVER 1-08:31:00
  WAIT fan FOR 1800 #fan should be on across two scheduled behaviors



