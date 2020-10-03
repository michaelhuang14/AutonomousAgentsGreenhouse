# Simple trace file
BASELINE = baseline4.bsl

WHENEVER 1-08:00:00
  ENSURE not fan UNTIL 1-09:00:00 #fan should not be on during both behaviors

