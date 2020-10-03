# Simple trace file
BASELINE = baseline2.bsl


WHENEVER smoist[0] < 450 or smoist[1] < 450
  WAIT wpump FOR 86400 # Make sure the water pump was turned on in the next scheduled sessions

# Don't let the pump overwater things
WHENEVER wpump
  ENSURE smoist[0] < 600 and smoist[1] < 600 FOR 3600

WHENEVER smoist[0] > 650 or smoist[1] > 650
  SET soil = (smoist[0] + smoist[1])/2
  WAIT fan FOR 86400 # Make sure fan is turned on in the next scheduled behavior sessions
  WAIT (smoist[0] + smoist[1])/2 < soil FOR 86400 # after turning on the fan, make sure the avg soil moisture goes down over the day

