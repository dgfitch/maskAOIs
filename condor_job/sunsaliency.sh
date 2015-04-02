#!/bin/sh

cd /home/fitch/aoi
nohup matlab -nosplash -nojvm -nodisplay -singleCompThread -logfile OUTPUT.txt <<<"aoiSunSaliency('$1')"
