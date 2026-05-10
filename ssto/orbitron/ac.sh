rm ./Orbitron-TestStand/Models/orbitron.ac
blender --python build_ac3d.py
python ./fix_screen_uv.py
fgfs --fg-aircraft=$PWD --aircraft=Orbitron-TestStand --timeofday=noon --season=summer --disable-ai-traffic --disable-real-weather-fetch --disable-clouds3d --prop:/sim/sound/chatter/volume=0.0 --prop:/sim/sound/atc/volume=0.0 --prop:/instrumentation/comm/volume=0.0


