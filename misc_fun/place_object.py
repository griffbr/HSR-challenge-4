#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Brent Griffin (griffb@umich.edu)
Place grasped object in goal location.
'''

import IPython
import cyclops
import robot
from gen_config import *

import location_config

def place(obj, whole_body, gripper, base, voice, tts):
	placement = location_config.locations()
	placement.set_location(obj.place_loc)
	placed = False
	while not placed:
		placed = move_and_place(obj,whole_body,gripper,base,voice,placement,tts)

def move_and_place(obj, whole_body, gripper, base, voice, plc, tts):
	placed = False
	try:
		robot.load_pose(whole_body,POSE_DIR+plc.robot_pose,['hand_motor_joint'])
		for _, pos in enumerate(plc.coordinates):
			cyclops.go_to_amcl_pose(base, pos)
		tts.say('%s placed at %s.' %(obj.name,plc.name))
		gripper.command(1.0)
		placed = True
		if voice.grab_object == 'grab none':
			tts.say('Which object should I grab next?')	
		if len(plc.coordinates) > 1:
			print('Moving back.')
			cyclops.go_to_amcl_pose(base, plc.coordinates[-2])
	except:
		tts.say('Cannot move to %s.' % plc.name)
		base.go_rel(-0.05,0,0)
	return placed
