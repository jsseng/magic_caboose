from time import sleep

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
                right_wrist_idx = pose.FindKeypoint('right_wrist')
                left_wrist_idx = pose.FindKeypoint('left_wrist')

                # if the keypoint index is < 0, it means it wasn't found in the image
                if right_wrist_idx < 0 or left_wrist_idx < 0:
                    continue
                
                left_wrist = pose.Keypoints[left_wrist_idx]
                right_wrist = pose.Keypoints[right_wrist_idx]

                #check if y value is above a certain point? if yes set threshold over 1
                if left_wrist.y > 20 or right_wrist.y > 20:
                    threshold = 2
                else:
                    threshold = 0

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