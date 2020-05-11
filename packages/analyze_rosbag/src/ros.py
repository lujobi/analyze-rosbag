#!/usr/bin/env python

import rosbag
import json
import re

import os
from duckietown import DTROS
from rospy_message_converter import  message_converter

class Ros_Analyze(DTROS):

    def __init__(self, node_name):
        super(Ros_Analyze, self).__init__(node_name=node_name)

    def run(self):
        lat = {'time': [], 'meas': []}

        find_msg_re = r'^(\[LineDetectorNode\] \d+:\sLatencies:\s)'
        find_line_re = r'\s+--pub_lines--\s+\|\s+total\s+latency\s+\d+.\d+ ms\s+'

        with rosbag.Bag('/data/'+os.environ['BAGNAME'], 'r') as bag:

            for _, msg, _ in bag.read_messages(topics=['/rosout']):
                temp = message_converter.convert_ros_message_to_dictionary(msg)
                                
                msg_string = temp.get('msg')
                if temp.get('name') == '/{}/line_detector_node'.format(os.environ['DUCKIEBOT']) and re.search(find_msg_re, temp.get('msg')):                  
                    time = temp.get('header').get('stamp').get('secs') + temp.get('header').get('stamp').get('nsecs')/1000000000.0

                    for line in msg_string.split('\n'):
                        if re.search(find_line_re,  line):
                            snippet = re.findall(find_line_re,  line)[0]
                            lat['time'].append(time)
                            lat['meas'].append(re.findall(r'\d+.\d+',snippet)[0])

        with open('/data/{}_latencies.json'.format(os.environ['BAGNAME']), 'w') as file:
            print(lat)
            file.write(json.dumps(lat))


if __name__ == '__main__':
    node = Ros_Analyze(node_name='ros_Analyze')
    node.run()

