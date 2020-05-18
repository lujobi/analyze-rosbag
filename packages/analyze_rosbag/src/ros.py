#!/usr/bin/env python

import rosbag
import json
import re
import yaml

import os
from duckietown import DTROS
from rospy_message_converter import  message_converter

class Ros_Analyze(DTROS):

    def __init__(self, node_name):
        super(Ros_Analyze, self).__init__(node_name=node_name)

    @staticmethod
    def stamp2time(stamp):
        return stamp.get('secs') + stamp.get('nsecs')/1000000000.0

    @staticmethod
    def retrieve_latencies(bag):
        lat = {'time': [], 'meas': []}

        find_msg_re = r'^(\[LineDetectorNode\] \d+:\sLatencies:\s)'
        find_line_re = r'\s+--pub_lines--\s+\|\s+total\s+latency\s+\d+.\d+ ms\s+'
        
        for _, msg, _ in bag.read_messages(topics=['/rosout']):
            temp = message_converter.convert_ros_message_to_dictionary(msg)
                            
            msg_string = temp.get('msg')
            if temp.get('name') == '/{}/line_detector_node'.format(os.environ['DUCKIEBOT']) and re.search(find_msg_re, temp.get('msg')):                  
                time = Ros_Analyze.stamp2time(temp.get('header').get('stamp'))
                for line in msg_string.split('\n'):
                    if re.search(find_line_re,  line):
                        snippet = re.findall(find_line_re,  line)[0]
                        lat['time'].append(time)
                        lat['meas'].append(re.findall(r'\d+.\d+',snippet)[0])
        return lat


    @staticmethod
    def retrieve_segment_count(bag):

        segs = {'time': [], 'meas': []}

        for _, msg, _ in bag.read_messages(topics=['/{}/line_detector_node/segment_list'.format(os.environ['DUCKIEBOT'])]):
            temp = message_converter.convert_ros_message_to_dictionary(msg)
            time = Ros_Analyze.stamp2time(temp.get('header').get('stamp'))
            
            segs['time'].append(time)
            segs['meas'].append(len(temp.get('segments')))
        return segs

    def run(self):

        with rosbag.Bag('/data/'+os.environ['BAGNAME']+'.bag', 'r') as bag:
            segs = self.retrieve_segment_count(bag)
            lat = self.retrieve_latencies(bag)
            
        with open('/data/{}_latencies.json'.format(os.environ['BAGNAME']), 'w') as file:
            print(lat)
            file.write(json.dumps(lat))

        with open('/data/{}_segment_counts.json'.format(os.environ['BAGNAME']), 'w') as file:
            print(segs)
            file.write(json.dumps(segs))

if __name__ == '__main__':
    node = Ros_Analyze(node_name='ros_Analyze')
    node.run()


# run command
# dts devel build -f --arch amd64