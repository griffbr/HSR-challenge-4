#!/usr/bin/python
# -*- coding: utf-8 -*-

# Misc. parameters.
POSE_DIR = './data/pose/'
GRASP_DIR = './data/g_msk/'
VIS_DIR = './data/models/'
LOG_IMG = True
IMG_DIR = './log/img/'
VS_DIR = './log/vs/'

# Find Object.
OFFSET = [-0.3, -0.2]
# OFFSET = [-0.3, -0.078]
TRAY_SCALE = 0.75
GUIDE_MODEL = 'hood.ckpt-10000'

# Grab Object.
Z_ARM_GRAB = 0.005
GRAB_LIFT = 0.2
GRAB_LIFT_FAR = 0.2
FAR_THRESH = 0.375
VIS_CHCK_THRESH = 0.5
GRASP_N_VS = 5