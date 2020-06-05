#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Brent Griffin (griffb@umich.edu)
Find and approach specified object in room.
Object should be in view of grasp camera after using find.
'''

import IPython
import time
import os
import numpy as np
import cyclops
import vision
import vision_3D
import robot
import location_config
import vs_function as vs_fun
from gen_config import *

# ROS dependency.
import tf
import tf2_ros
import rospy

def find(obj, whole_body, seg, vs, cam, tts, base, depth, voice, date=''):
	# Check where to find object and locate its position.
	search = location_config.locations()
	search.set_location(obj.find_location)
	for _, location in enumerate(search.coordinates):
		cyclops.go_to_amcl_pose(base, location)
	vs.set_config('head_pan_head_tilt')
	if search.name == 'guide':
		guide_search(obj, whole_body, seg, vs, cam, tts, base, date)
	vs.pose = 'head_cam_low.pk'
	vs_fun.joint_vs(vs, whole_body, seg, obj, cam, tts, 3, 0, 10, date)
	obj.position, found = get_3D_position(seg, obj, cam, depth, tts, date)
	# Approach object and determine appropriate grasp strategy.
	if found:
		tts.say('%s found! Approximately %4.2f meters away'%
			(obj.name, obj.position[0]))
		vs.set_config('base_gripper')
		if search.name == 'tray':
			base.go_rel(0, (obj.position[1]+OFFSET[1]) * TRAY_SCALE, 0)
			grasp_strat = voice.grasp_config.split(' ', 1)[1]
			if grasp_strat == 'far':
				vs.set_config('far_grasp')
				voice.grasp_config = 'config rotation'
		else:
			base.go_rel(obj.position[0]+OFFSET[0],obj.position[1]+OFFSET[1],0)
			robot.load_pose(whole_body, POSE_DIR + 'x_lower.pk')
	return found

def get_3D_position(seg, obj, cam, depth, tts, date):
	found = False; obj_base = np.zeros(3)
	obj.img_dir = '%s%s/%s/%s/' % (IMG_DIR, date, obj.name, '3D_position')
	if not os.path.isdir(obj.img_dir): os.makedirs(obj.img_dir)
	vision.track_object(seg,obj,cam,name='%s_%s'%(date,'3D_pos'))
	if obj.n_mask_pixels > 0:
		try:
			obj_pc=vision_3D.return_mask_points(obj.mask,depth._input_image,obj)
			obj_c = np.nanmedian(obj_pc,axis=1)
			obj_base=transform_points(obj_c,'head_rgbd_sensor_link','base_link')
			print('Object is %4.3f x, %4.3f y, and %4.3f z away from base.' % 
				(obj_base[0], obj_base[1], obj_base[2]))
			found = True
		except:
			tts.say('Cannot determine 3D position of %s.' % obj.name)
	else:
		tts.say('Cannot see the %s.' % obj.name)
	return obj_base[:3], found
def transform_points(points, init_frame, end_frame):
	tf_buffer = tf2_ros.Buffer()
	tf_listener = tf2_ros.TransformListener(tf_buffer)
	while not tf_buffer.can_transform(init_frame, end_frame, rospy.Time()):
		print('Waiting for transform from %s to %s.' % (init_frame, end_frame))
		time.sleep(0.02)
	trans = tf_buffer.lookup_transform(end_frame, init_frame, rospy.Time())
	tfm =build_matrix_ros(trans.transform.translation,trans.transform.rotation)
	return np.matmul(tfm,np.insert(points,[3],1))
def build_matrix_ros(trans, quat):
	quaternion = [quat.x, quat.y, quat.z, quat.w]
	translation = [trans.x, trans.y, trans.z]
	return build_matrix(translation, quaternion)
def build_matrix(trans, quat):
	tf_matrix = tf.transformations.quaternion_matrix(quat)
	tf_matrix[0][3] = trans[0]
	tf_matrix[1][3] = trans[1]
	tf_matrix[2][3] = trans[2]
	return tf_matrix

def guide_search(obj, whole_body, seg, vs, cam, tts, base, date):
	tts.say('Please show me where to find the %s.' % obj.name)
	seg.change_model(VIS_DIR + GUIDE_MODEL)
	img_dir = '%s%s/%s/%s/' % (IMG_DIR, date, obj.name, 'guide')
	vs.pose = 'head_cam.pk'
	vs_fun.joint_vs(vs, whole_body, seg, obj, cam, tts, 7, 0, 10, date,
		img_dir=img_dir)
	obj_angle = whole_body.joint_positions['head_pan_joint']
	tts.say('Thank you for your help!')
	base.go_rel(0,0,obj_angle)
	seg.change_model(VIS_DIR + obj.vision_model)

'''
Working notes:

robot.load_pose(whole_body, POSE_DIR + vs.pose)
cyclops.get_amcl_pose()
'''
