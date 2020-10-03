# Simple trace file
BASELINE = baseline1.bsl


WHENEVER smoist[0] < 450 or smoist[1] < 450
  WAIT wpump FOR 86400 # Make sure the water pump was turned on today

# Don't let the pump overwater things
WHENEVER wpump
  ENSURE smoist[0] < 600 and smoist[1] < 600 FOR 3600

WHENEVER temperature[0] > 30
  WAIT fan FOR 86400 # Wait one day for fan to turn on

