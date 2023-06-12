import time

class Input:
    def __init__(self, on_trigger, net, input, output, args):
        self.on_trigger = on_trigger
        self.net = net
        self.input = input
        self.output = output
        self.args = args

    def update(self):
        threshold = 0

        while True:
            # capture the next image
            img = self.input.Capture()

            if img is None: # timeout
                continue  

            # perform pose estimation (with overlay)
            poses = self.net.Process(img, overlay=self.args.overlay)

            # print the pose results
            print("detected {:d} objects in image".format(len(poses)))

            for pose in poses:
                right_elbow_idx = pose.FindKeypoint('right_elbow')
                left_elbow_idx = pose.FindKeypoint('left_elbow')

                # if the keypoint index is < 0, it means it wasn't found in the image
                if right_elbow_idx < 0 or left_elbow_idx < 0:
                    continue
                
                left_elbow = pose.Keypoints[left_elbow_idx]
                right_elbow = pose.Keypoints[right_elbow_idx]

                #check if y value is above a certain point? if yes set threshold over 1
                if left_elbow.y > 20 or right_elbow.y > 20:
                    threshold = 1.1

            # render the image
            self.output.Render(img)

            # update the title bar
            self.output.SetStatus("{:s} | Network {:.0f} FPS".format(self.args.network, self.net.GetNetworkFPS()))

            # print out performance info
            self.net.PrintProfilerTimes()

            # exit on input/output EOS
            if not self.input.IsStreaming() or not self.output.IsStreaming():
                break

        if threshold > 1:
            self.on_trigger()