#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Brent Griffin (griffb@umich.edu)

Class for storing and using search and placement locations.
Class instances inherit properties of the initial object specified.
Class is defined such that object dictionary is extendable.
'''

import IPython

class locations:
	def __init__(self):
		self.location_dict = {
		# search locations
			'tray': {
			'robot_pose'   : 'bin_place.pk', 
			'coordinates'  : [(-0.1625, 0.197, 0.9766)],
			'name'         : 'tray'},
			'door': {
			'robot_pose'   : 'head_cam_floor.pk', 
			'coordinates'  : [(-0.184, 0.1945, -2.7206)],
			'name'         : 'door'},
			'guide': {
			'robot_pose'   : 'head_cam.pk', 
			'coordinates'  : [(-0.1176, 0.1846, -2.171)],
			'name'         : 'guide'},
		# place locations
			'garbage bin': {
			'robot_pose'   : 'bin_place.pk',
			'coordinates'  : [(-0.8299, 0.4446, 1.9857)],
			#'coordinates'  : [(-0.769, 0.516, 1.999)],
			#'coordinates'  : [(-0.771, 0.428, 2.2689)],
			'name'         : 'garbage_bin'},
			'cup bin': {
			'robot_pose'   : 'bin_place.pk',
			'coordinates'  : [(-0.5838, 0.759, 1.9479)],
			#'coordinates'  : [(-0.6599, 0.6449, 1.935)],
			#'coordinates'  : [(-0.598, 0.8139, 1.971)],
			'name'         : 'cup_bin'},
		# cubby place locations
			'top middle right cubby': {
			'robot_pose'   : 'tr2.pk', 
			'coordinates'  : [(0.3458,-0.0431,1.6524),(0.5568,0.2032,1.672)],
			'name'         : 'top_middle_right_cubby'},
			'bottom middle left cubby': {
			'robot_pose'   : 'bl3.pk', 
			'coordinates'  : [(-0.5582,0.5326,0.2055),(-0.3882,0.9442,-0.0519)],
			'name'         : 'bottom_middle_left_cubby'},
			'bottom left cubby': {
			'robot_pose'   : 'bl3.pk', 
			'coordinates'  : [(-0.1963,0.0395,1.003), (-0.6922,0.3662,0.5386),
				(-0.5093,0.7992,0.4734)],
			'name'         : 'bottom_left_cubby'},
			'top left cubby': {
			'robot_pose'   : 'tl2.pk', 
			'coordinates'  : [(-0.5327,0.5648,0.5903),(-0.5019,0.7865,0.4463)],
			'name'         : 'top_left_cubby'},
			'top middle left cubby': {
			'robot_pose'   : 'tl2.pk', 
			'coordinates'  : [(-0.5582,0.5326,0.2055),(-0.3882,0.9442,-0.0519)],
			'name'         : 'top_left_cubby'}
			}

	def set_location(self, loc_name):
		if loc_name in self.location_dict.keys():
			instance_dict = self.location_dict[loc_name]
			self.properties = instance_dict.keys()
			for _, key in enumerate(self.properties):
				setattr(self, key, instance_dict[key])
		else:
			print ('Error: place instance %s currently undefined.' % loc_name)
