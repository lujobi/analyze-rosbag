#!/usr/bin/env python

import yaml
import rosbag
import pyaml

import os
import rospy
from duckietown import DTROS
from std_msgs.msg import String

class Ros_Analyze(DTROS):

    def __init__(self, node_name):
        # initialize the DTROS parent class
        super(Ros_Analyze, self).__init__(node_name=node_name)
        # construct publisher
        self.pub = rospy.Publisher('chatter', String, queue_size=10)

    def run(self):
        # publish message every 1 second
        with rosbag.Bag('/data/bag.bag', 'r') as bag:
            info_dict = yaml.load(bag._get_yaml_info())
            print pyaml.dump(info_dict)

if __name__ == '__main__':
    # create the node
    node = Ros_Analyze(node_name='ros_Analyze')
    # run node
    node.run()
    # keep spinning
    rospy.spin()

