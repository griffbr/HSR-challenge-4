#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Brent Griffin (griffb@umich.edu)
Grab object using grasp camera and visual servoing.
'''

import IPython
import os
import glob
import cv2
import numpy as np
import time
from copy import deepcopy

import vision
import robot
import vs_function as vs_fun
from gen_config import *

def grab(obj, whole_body, gripper, seg, vs, cam, tts, base, voice, date=''):
	tts.say('Grabbing %s.' % obj.name)
	object_grasped = False; ct = 0
	lift = GRAB_LIFT
	'''
	if obj.find_location == 'tray' and obj.position[0] > FAR_THRESH:
		vs.set_config('far_grasp'); lift = GRAB_LIFT_FAR
	else:
		vs.set_config('base_gripper'); lift = GRAB_LIFT
	'''
	obj.img_dir = '%s%s/%s/%s/' % (IMG_DIR, date, obj.name, 'grab')
	if not os.path.isdir(obj.img_dir): os.makedirs(obj.img_dir) 
	while not object_grasped and ct<3:
		gripper.command(1.0)
		vs_fun.base_vs(vs,whole_body,base,seg,obj,cam,tts,GRASP_N_VS,0,10,
			True,date)
		if vs.name == 'base_gripper':
			rotate_gripper(obj, whole_body, seg, cam, voice, ct, date)
			robot.move_to_n_joint_positions(whole_body,['arm_lift_joint'],
				[Z_ARM_GRAB])
		object_grasped = try_grasp(seg, obj, cam, whole_body, gripper, voice, 
			tts, ct, lift, date)
		ct += 1
	return object_grasped

def rotate_gripper(obj, whole_body, seg, cam, voice, ct, date):
	vision.track_object(seg,obj,cam,name='%i_%s'%(ct, 'grasp_pos'))
	if not os.path.isdir(obj.img_dir): os.makedirs(obj.img_dir) 
	grasp_ang = np.radians(select_grasp_angle(obj.mask, GRASP_DIR))
	cur_ang = whole_body.joint_positions['wrist_roll_joint']
	cmd_wrist_angle = grasp_angle_to_pm90(cur_ang-grasp_ang, angle_mod=1.5708)
	grasp_mod = voice.grasp_config.split(' ',1)[1]
	if grasp_mod == 'horizontal': cmd_wrist_angle = 0.0
	elif grasp_mod == 'vertical': cmd_wrist_angle = 1.5708
	voice.grasp_config = 'config rotation'
	whole_body.move_to_joint_positions({'wrist_roll_joint': cmd_wrist_angle})

def select_grasp_angle(object_mask, grasp_dir):
	object_mask = np.atleast_3d(object_mask)[...,0]
	grasp_img_list = glob.glob(os.path.join(grasp_dir, '*.png'))
	n_grasps = len(grasp_img_list)
	grasp_cost = np.zeros(n_grasps)
	for i, grasp_img in enumerate(grasp_img_list):
		grasp_candidate = np.atleast_3d(cv2.imread(grasp_img))[...,0]
		grasp_cost[i] = vision.eval_intersect(grasp_candidate, object_mask)
	best_grasp_img = grasp_img_list[np.argmin(grasp_cost)]
	grasp_angle = float(best_grasp_img.split('/')[-1].split('.')[0])
	return grasp_angle
def grasp_angle_to_pm90(grasp_angle, angle_mod = 90):
	if grasp_angle < -angle_mod:
		grasp_angle %= angle_mod
	elif grasp_angle > angle_mod:
		grasp_angle = grasp_angle % angle_mod - angle_mod
	return grasp_angle

def try_grasp(seg,obj,cam,whole_body,gripper,voice,tts,ct,lift=0.1,date=''):
	grasped = False; answered = False
	vision.track_object(seg,obj,cam,name='%i_%s'%(ct,'try_grasp'))
	prev_pxls = deepcopy(obj.n_mask_pixels)
	try:
		print('Trying initial grab.')
		init_grip = smart_grasp(whole_body, gripper, force = obj.grip_force)
		if init_grip > obj.grip_min:
			print('Initial grip is %5.4f' % init_grip)
			robot.move_joint_amount(whole_body, 'arm_lift_joint', lift)
			print('Applying grip force of %1.2f again.' % obj.grip_force)
			gripper.apply_force(obj.grip_force)
			#print('Lifting object for visual check.')
			#robot.move_joint_amount(whole_body, 'arm_lift_joint', 0.2-lift)
			print('Object lifted.')
			time.sleep(0.25)
			if whole_body.joint_positions['hand_motor_joint'] > obj.grip_min:
				print('Visual grasp check')
				vision.track_object(seg,obj,cam,name='%i_%s'%(ct,'grasp_chck'))
				vis_ratio = float(obj.n_mask_pixels) / prev_pxls
				print('Visual ratio is %5.3f.' % vis_ratio)
				if vis_ratio > VIS_CHCK_THRESH:
					tts.say('Visual grasp for %s confirmed!' % obj.name)
					grasped = True
				else:
					tts.say('Did I get the %s?' % obj.name)
					while not answered:
						answer = voice.task_feedback.split(' ',1)[1]
						if answer == 'none':
							time.sleep(0.25)
						else:
							answered = True
							if answer == 'success':
								grasped = True
							voice.task_feedback = 'task none'
	except:
		tts.say('Could not grasp %s that time.' % obj.name)
	return grasped
def smart_grasp(whole_body, gripper, grip_min=-0.7, force=0.5):
	gripper.apply_force(force)
	init_grip = whole_body.joint_positions['hand_motor_joint']
	grip_pos = np.max([init_grip, grip_min])
	gripper.command(grip_pos)
	return init_grip
