#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Script for running HSR challenge 4 (190415).
'''

import IPython
import time
import sys
sys.path.insert(0, './misc_fun/')

import object_config
import vs_config 
import vision
import robot
import cyclops
from gen_config import *

# With ROS depend.
from data_subscriber import *
import hsrb_interface

# Main task functions.
import find_object
import grab_object
import place_object

# Used in main.
def set_object():
	target_name = voice.grab_object.split(' ', 1)[1]
	obj.set_object(target_name)
	seg.change_model(VIS_DIR + obj.vision_model)
	voice.grab_object = 'grab none'
def return_home():
	go_to_map_home(base)
	rob.load_pose(whole_body, POSE_DIR + 'initial_view.pk')

# Main challenge script.
def	main():
	# Misc. Initialization.
	print('\n\nRobot moves next, make sure that you are ready!\n\n')
	# robot.load_pose(whole_body, POSE_DIR + 'initial_view.pk')

	asked = False
	tts.say('Which object should I grab?')
	while True:
		if 0:
			voice.grab_object = 'grab yellow block'
		# Get voice specification of target object.
		if voice.grab_object == 'grab none':
			if not asked:
				asked = True
				robot.load_pose(whole_body, POSE_DIR + 'head_cam_low.pk')
			time.sleep(0.250)
			continue
		date = str(time.time()).split('.')[0]
		set_object()
		found = find_object.find(obj,whole_body,seg,vs,head_cam,tts,base,depth,
			voice, date)
		if found:
			grasped = grab_object.grab(obj,whole_body,gripper,seg,vs,grasp_cam,
				tts,base,voice,date)
			if grasped:
				place_object.place(obj,whole_body,gripper,base,voice,tts)
		#return_home()
		asked = False;

if __name__ == '__main__':
	with hsrb_interface.Robot() as hsr:
		base = hsr.try_get('omni_base')
		whole_body = hsr.get('whole_body')
		gripper = hsr.get('gripper')
		tts = hsr.try_get('default_tts')
		tts.language = tts.ENGLISH
		grasp_cam = image_subscriber('/hsrb/hand_camera/image_raw', True)
		head_cam = image_subscriber(
			'/hsrb/head_rgbd_sensor/rgb/image_rect_color', True)
		depth = image_subscriber(
			'/hsrb/head_rgbd_sensor/depth_registered/image_raw', False)
			# '/hsrb/head_rgbd_sensor/depth_registered/image_rect_raw', False)
		robot_state = state_subscriber('/hsrb/joint_states')
		base_odom = odometry_subscriber('/hsrb/odom')
		voice = voice_subscriber('/zavengers/jarvis')
		seg = vision.osvos_seg('./data/models/r.ckpt-10003')
		obj = object_config.manipulation_objects()
		vs = vs_config.visual_servo()
		main()
