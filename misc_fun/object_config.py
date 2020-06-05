#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Brent Griffin (griffb@umich.edu)

Class for storing and using manipulation object information.
Class instances inherit properties of the initial object specified.
Class is defined such that object dictionary is extendable.
'''

import IPython

# TODO: Add other c4 objects and appropriate properties (ideally, just change elevation of pose).

class manipulation_objects:
	def __init__(self):
		self.object_dict = {
			# Trash objects.
			'rag': {
			'overlay_color': [200,200,200],
			'vision_model' : 'rg.ckpt-10000',
			'find_location': 'guide',
			'place_loc'    : 'garbage bin',
			'grip_force'   : 0.2,
			'grip_min'     : -1.0,
			'name'         : 'rag'},
			'water bottle': {
			'overlay_color': [128,60,60],
			'vision_model' : 'wb.ckpt-10000',
			'find_location': 'guide',
			'place_loc'    : 'garbage bin',
			'grip_force'   : 0.2,
			'grip_min'     : -0.75,
			'name'         : 'water_bottle'},
			'coffee cup': {
			'overlay_color': [20,128,20],
			'vision_model' : 'cc.ckpt-10000',
			'find_location': 'guide',
			'place_loc'    : 'garbage bin',
			'grip_force'   : 0.2,
			'grip_min'     : -0.75,
			'name'         : 'coffee_cup'},
			'empty towel roll': {
			'overlay_color': [33,67,101],
			'vision_model' : 'etr.ckpt-10000',
			'find_location': 'guide',
			'place_loc'    : 'garbage bin',
			'grip_force'   : 0.2,
			'grip_min'    : -0.85,
			'name'         : 'empty_towel_roll'},
			# Dinosaur cups.
			'red cup': {
			'overlay_color': [0,0,255],
			'vision_model' : 'rc.ckpt-10000',
			'find_location': 'door',
			'place_loc'    : 'cup bin',
			'grip_force'   : 0.2,
			'grip_min'     : -0.75,
			'name'         : 'red_cup'},
			'purple cup': {
			'overlay_color': [128,0,128],
			'vision_model' : 'pc.ckpt-10000',
			'find_location': 'door',
			'place_loc'    : 'cup bin',
			'grip_force'   : 0.2,
			'grip_min'     : -0.75,
			'name'         : 'purple_cup'},
			'green cup': {
			'overlay_color': [0,255,0],
			'vision_model' : 'gc.ckpt-10000',
			'find_location': 'door',
			'place_loc'    : 'cup bin',
			'grip_force'   : 0.2,
			'grip_min'     : -0.75,
			'name'         : 'green_cup'},
			# Tray objects.
			'dollar bill': {
			'overlay_color': [0,255,0],
			'vision_model' : 'd.ckpt-10000',
			'find_location': 'tray',
			'place_loc'    : 'bottom middle left cubby',
			'grip_force'   : 0.2,
			'grip_min'     : -1.0,
			'name'         : 'dollar_bill'},
			'paper towel': {
			'overlay_color': [255,255,255],
			'vision_model' : 'p.ckpt-10000',
			'find_location': 'tray',
			'place_loc'    : 'garbage bin',
			'grip_force'   : 0.2,
			'grip_min'     : -1.0,
			'name'         : 'paper_towel'},
			'tong ends': {
			'overlay_color': [0,0,0],
			'vision_model' : 't2.ckpt-10003',
			'find_location': 'tray',
			'place_loc'    : 'bottom left cubby',
			'grip_force'   : 0.2,
			'grip_min'     : -1.0,
			'name'         : 'tong_ends'},
			'kitchen tongs': {
			'overlay_color': [0,0,0],
			'vision_model' : 't.ckpt-10003',
			'find_location': 'tray',
			'place_loc'    : 'bottom left cubby',
			'grip_force'   : 0.2,
			'grip_min'     : -1.0,
			'name'         : 'kitchen_tongs'},
			'red block': {
			'overlay_color': [0,0,255],
			'vision_model' : 'r.ckpt-10003',
			'find_location': 'tray',
			'place_loc'    : 'top left cubby',
			'grip_force'   : 0.4,
			'grip_min'     : -0.8,
			'name'         : 'red_block'},
			'blue block': {
			'overlay_color': [255,0,0],
			'vision_model' : 'b.ckpt-10003',
			'find_location': 'tray',
			'place_loc'    : 'top middle left cubby',
			'grip_force'   : 0.4,
			'grip_min'     : -0.8,
			'name'         : 'blue_block'},
			'yellow block': {
			'overlay_color': [0,255,255],
			'vision_model' : 'y.ckpt-10003',
			'find_location': 'tray',
			'place_loc'    : 'top middle right cubby',
			'grip_force'   : 0.4,
			'grip_min'     : -0.8,
			'name'         : 'yellow_block'}
			}
		self.nominal_attr = ['__doc__', '__init__', '__module__', 'object_dict'
			, 'set_object', 'nominal_attr', 'properties']

	def set_object(self, obj_name):
		if obj_name in self.object_dict.keys():
			instance_dict = self.object_dict[obj_name]
			self.properties = instance_dict.keys()
			prev_attr = dir(self)
			[delattr(self, attr_name) for attr_name in prev_attr if attr_name 
				not in self.nominal_attr and attr_name not in self.properties]
			for _, key in enumerate(self.properties):
				setattr(self, key, instance_dict[key])
		else:
			print ('Error: object instance %s currently undefined.' % obj_name)
