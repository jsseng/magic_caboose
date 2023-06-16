# magic_caboose

## Steps to Run Docker Container with PoseNet

1. Make sure USB camera is plugged in BEFORE launching container
2. `cd jetson-inference`
3. `docker/run.sh -v ~/magic_caboose:/jetson-inference/build/aarch64/bin/magic_caboose`
    1. The -v command will allow you to load the latest version of the magic_caboose directory, and will save any changes you make to it within the Docker container back to local when you exit the container
    2. Make sure you are on the correct git branch before running this command
4. In order to run the pyglet demo with posenet (currently only on the posenet_demo branch):
    1. `cd build/aarch64/bin/magic_caboose/pyglet_demo`
    2. `./main.py /dev/video0`
        1. This part is not currently successfully integrated but it will run
5. If you just want to run the regular posenet demo (not integrated with pyglet)
    1. `cd build/aarch64/bin/`
    2. `./posenet.py /dev/video0`
