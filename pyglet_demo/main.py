import pyglet
import math
import random

import color_utils
import configs
import app
import cameraInput

import sys
import argparse

from jetson_inference import poseNet
from jetson_utils import videoSource, videoOutput, Log

def main():
    parser = argparse.ArgumentParser(description="Run pose estimation DNN on a video/image stream.", 
                                 formatter_class=argparse.RawTextHelpFormatter, 
                                 epilog=poseNet.Usage() + videoSource.Usage() + videoOutput.Usage() + Log.Usage())

    parser.add_argument("input", type=str, default="", nargs='?', help="URI of the input stream")
    parser.add_argument("output", type=str, default="", nargs='?', help="URI of the output stream")
    parser.add_argument("--network", type=str, default="resnet18-body", help="pre-trained model to load (see below for options)")
    parser.add_argument("--overlay", type=str, default="links,keypoints", help="pose overlay flags (e.g. --overlay=links,keypoints)\nvalid combinations are:  'links', 'keypoints', 'boxes', 'none'")
    parser.add_argument("--threshold", type=float, default=0.15, help="minimum detection threshold to use") 

    try:
        args = parser.parse_known_args()[0]
    except:
        print("")
        parser.print_help()
        sys.exit(0)

    # load the pose estimation model
    net = poseNet(args.network, sys.argv, args.threshold)

    # create video sources & outputs
    input = videoSource(args.input, argv=sys.argv)
    output = videoOutput(args.output, argv=sys.argv)

    gl_background_color = tuple(map(lambda x : x / 255.0, configs.BACKGROUND_COLOR))

    config = pyglet.gl.Config(sample_buffers=1, samples=8)
    window = pyglet.window.Window(caption="Caboose Wheel", config=config, fullscreen=True)
    pyglet.gl.glClearColor(*gl_background_color, 1.0)
    pyglet.options['audio'] = ('openal', 'pulse', 'directsound', 'silent')

    game_app = app.App((window.width, window.height))

    @window.event
    def on_draw():
        pyglet.gl.glFlush()
        window.clear()

        game_app.on_draw()
    
    @window.event
    def on_mouse_press(x, y, button, modifiers):
        game_app.on_click(x, y, button)
    
    inputHandler = cameraInput.Input(game_app.spin, net, input, output, args)

    def update_all(deltaTime):
        inputHandler.update()
        game_app.on_update(deltaTime)

    pyglet.clock.schedule(update_all)
    pyglet.app.run()

if __name__ == "__main__":
    main()