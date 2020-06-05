#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Brent Griffin (griffb@umich.edu)
Visual servo functions.
'''

import time
import os
import numpy as np
from copy import deepcopy

import robot
import vision
import data_log_utils
from gen_config import *

# VS
def reset_vs_pose(whole_body, vs, tts, pose=True):
	print('Reseting VS pose.')
	if pose:
		try:
			robot.load_pose(whole_body, POSE_DIR + vs.pose)
		except:
			tts.say('Could not load %s pose.' % vs.pose)
	q_command = deepcopy(robot.joint_position(whole_body, vs.joints))
	q_prev = deepcopy(q_command)
	vs.Je_pinv = deepcopy(vs.Je_pinv_prev)
	return q_command, q_prev

def base_vs(vs, whole_body, base, seg, obj, cam, tts,
		cycles = 5, update=0, seg_reps = 10, pose = True, date=''):
	tts.say('Centering on %s.' % obj.name)
	if pose:
		robot.load_pose(whole_body, POSE_DIR + vs.pose)
	vs.Je_pinv_prev = vs.Je_pinv
	vs.update = update
	s_all = np.zeros(shape=(cycles,2))
	e_all = np.zeros(shape=(cycles,2))
	for i in range(cycles):
		vision.track_object(seg,obj,cam,name='%s_%s_%ic_%ir'%(date,vs.name,i,0))
		s = obj.mask_center
		for j in range(seg_reps-1):
			vision.track_object(seg,obj,cam)
			s += obj.mask_center
		s /= seg_reps
		s_all[i,:] = deepcopy(s)
		e_all[i,:] = s - vs.s_des
		if not np.isnan(s).any():
			dq_e, error_sum = vs.delta_q(s)
			try: 
				base.go_rel(dq_e[0], dq_e[1], 0)	
			except: 
				print("Can't move there!")
				print('\n\n Add code to go back to home position here!\n\n')
				dq_e *= 0
			if update>0 and sum(abs(dq_e))>DQ_UPDATE: 
				print('\nUpdating Je_pinv.\n')
				vs.broyden_update(s, dq_e, base=True) 
		else: 
			print('\nStep %i: Object not in view!\n' % i)
			robot.move_joint_amount(whole_body, 'arm_lift_joint', 0.1)
	data_file = '%s%s_%s_%s.txt' % ( VS_DIR, date, vs.name, obj.name)
	data_log_utils.print_data_file(data_file,[s_all[:,0],s_all[:,1],
		e_all[:,0],e_all[:,1]],['s0','s1','e0','e1']) 

def joint_vs(vs, whole_body, seg, obj, cam, tts,
		cycles = 10, update=0, seg_reps = 10, date='', img_dir='', pose=True):
	vs.Je_pinv_prev = vs.Je_pinv
	vs.update = update
	q_command, q_prev = reset_vs_pose(whole_body, vs, tts, pose)
	print('\nJe_pinv initial is:'); print(vs.Je_pinv)
	if date=='':
		date = str(time.time()).split('.')[0]
	if img_dir == '':
		obj.img_dir = '%s%s/%s/%s/' % (IMG_DIR, date, obj.name, vs.name)
	else: obj.img_dir = img_dir
	if not os.path.isdir(obj.img_dir): os.makedirs(obj.img_dir)
	s_all = np.zeros(shape=(cycles,2))
	e_all = np.zeros(shape=(cycles,2))
	for i in range(cycles):
		print('\nStep %i:' % i)
		q = robot.joint_position(whole_body, vs.joints)
		print('q is:'); print(q)
		dq = q - q_prev
		vision.track_object(seg,obj,cam,name='%s_%s_%ic_%ir'%(date,vs.name,i,0))
		s = obj.mask_center
		for j in range(seg_reps-1):
			#track_object(cam, name='%s_%s_%ic_%ir' % (date, vs.name, i, j+1))
			vision.track_object(seg,obj,cam)
			s += obj.mask_center
		s /= seg_reps
		s_all[i,:] = deepcopy(s)
		e_all[i,:] = s - vs.s_des
		print('s is [%5.4f, %5.4f]' % (s[0], s[1]))
		if not np.isnan(s).any():
			if update>0 and sum(abs(dq))>DQ_UPDATE: 
				print('\nUpdating Je_pinv.\n')
				vs.broyden_update(s, q) 
				q_prev = deepcopy(q)
			dq_e, error_sum = vs.delta_q(s)
			q_command += dq_e
			try: 
				#move_to_n_joint_positions(whole_body, vs.joints, q_command)
				robot.move_n_joints(whole_body, vs.joints, dq_e)
			except: 
				print("Can't move there!")
				q_command, q_prev = reset_vs_pose(whole_body, vs, tts)
			print('q_prev is [%5.4f, %5.4f]' % (q_prev[0], q_prev[1]))
			print('dq is [%5.4f, %5.4f]' % (dq[0], dq[1]))
			print('dq_e is:'); print(dq_e)
			print('q_com:'); print(q_command)
			print('joints are:'); print(vs.joints)
		else: 
			print('\nStep %i: Object not in view!\n' % i)
			q_command, q_prev = reset_vs_pose(whole_body, vs, tts)
	#print('\nJe_pinv final is:'); print(vs.Je_pinv)
	#tts.say('Done with VS cycles.')
	data_file = '%s%s_%s_%s.txt' % ( VS_DIR, date, vs.name, obj.name)
	data_log_utils.print_data_file(data_file,[s_all[:,0],s_all[:,1],
		e_all[:,0],e_all[:,1]],['s0','s1','e0','e1']) 
