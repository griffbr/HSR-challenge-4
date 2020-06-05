#!/usr/bin/python
# -*- coding: utf-8 -*-

import IPython
import cv2
import numpy as np
from gen_config import *

def intrinsic_matrix(shape=(240, 320)):
	H, W = shape
	return np.array([[275*W/320.0, 0, W/2.0],
					 [0, 275*H/240.0, H/2.0],
					 [0, 0, 1]])

def depth2pc(depth, Kinv=None):
	"""
	depth should be numpy array providing depth in mm
	Kinv should be an intrinsic matrix providing
	"""
	if Kinv is None:
		Kinv = np.linalg.inv(intrinsic_matrix(depth.shape))

	H, W = depth.shape
	uu, vv = np.meshgrid(np.arange(W), np.arange(H))
	XY = Kinv.dot(np.vstack((uu.flatten(), vv.flatten(), np.ones(uu.size))))
	#nonzerodepth = depth.flatten() != 0
	Z = depth.flatten().astype(np.float64) / 1000.
	pc = XY[:] * Z / XY[2]
	#pc = XY[:, nonzerodepth] * Z[nonzerodepth] / XY[2, nonzerodepth]
	return pc, H, W

def return_mask_points(mask, depth, obj):
	pc, H, W = depth2pc(depth)
	mask_2D = np.where(mask)
	lin_idx = mask_2D[1]*W + mask_2D[0]
	if LOG_IMG:	
		base_name = '%s%s_%s' % (obj.img_dir, obj.name, 'depth') 
		write_depth_seg_image(depth, mask, base_name+'.png', obj.overlay_color)
	return pc[:, lin_idx]

def write_depth_seg_image(dpth_img, msk, fname, overlay=[0,0,255], transp=0.15):
	img = dpth_img * (255.0/np.nanmax(dpth_img))
	img = np.stack((img,)*3, axis=-1)
	for i, hue in enumerate(overlay):
		img[msk, i] = hue*transp + img[msk, i] * (1 - transp)
	cv2.imwrite(fname, img)

