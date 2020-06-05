import IPython; import cv2; import numpy as np
from copy import deepcopy
from skimage.measure import label
from scipy import ndimage
import tensorflow as tf
slim = tf.contrib.slim
import sys

from osvos_mod import osvos, osvos_arg_scope, interp_surgery, preprocess_img
from gen_config import *

# Segmenter class.
class osvos_seg:
	def __init__(self, file_location):
		self.checkpoint_file = file_location
		config = tf.ConfigProto()
		config.gpu_options.allow_growth = True
		config.allow_soft_placement = True
		tf.logging.set_verbosity(tf.logging.INFO)
		batch_size = 1
		self.input_image = tf.placeholder(tf.float32, [batch_size, None, None, 3])
		with slim.arg_scope(osvos_arg_scope()):
			net, end_points = osvos(self.input_image)
		self.probabilities = tf.nn.sigmoid(net)
		global_step = tf.Variable(0, name='global_step', trainable=False)
		self.saver = tf.train.Saver([v for v in tf.global_variables() if '-up' not in v.name and '-cr' not in v.name])
		self.sess = tf.Session(config=config)
		self.sess.run(tf.global_variables_initializer())
		self.sess.run(interp_surgery(tf.global_variables()))
		self.saver.restore(self.sess, self.checkpoint_file)

	def change_model(self, file_location):
		self.checkpoint_file = file_location
		self.saver.restore(self.sess, self.checkpoint_file)

	def segment_image(self, img, write_file = False, file_name = 'mask.png'):	
		image = preprocess_img(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
		res = self.sess.run(self.probabilities, feed_dict={self.input_image: image})
		res_np = res.astype(np.float32)[0, :, :, 0] > 162.0/255.0
		mask_img = res_np.astype(np.uint8)*255
		if write_file:
			cv2.imwrite(file_name, mask_img)
		return mask_img 

# Segmenter-based functions using other classes.
def initial_object_location(seg, VIS_DIR, obj):
	seg.change_model(VIS_DIR + obj.vision_model)
	track_object(seg)
	obj.init_center = deepcopy(obj.mask_center)

def track_object(seg, obj, cam, name=''):
	img = deepcopy(cam._input_image)
	mask_location(img, seg, obj)
	if LOG_IMG:
		base_name = '%s%s_%s' % (obj.img_dir, obj.name, name)
		write_seg_image(img, obj.mask, base_name + '.png', obj.overlay_color)
		if not name=='':
			cv2.imwrite(base_name + 'img.png', img)	
			cv2.imwrite(base_name + 'mask.png', obj.mask*255)

def mask_location(img, seg, obj):
	mask = seg.segment_image(img)
	obj.mask, obj.n_mask_pixels = largest_region_only(mask)
	obj.mask_center = find_mask_centroid(obj.mask)

# Vision functions.
def largest_region_only(init_mask):
	labels = label(init_mask)
	bin_count = np.bincount(labels.flat)
	if len(bin_count)>1:
		mask_bin = np.argmax(bin_count[1:]) + 1
		n_mask_pixels = bin_count[mask_bin]
		single_mask = labels == mask_bin
	else: single_mask = init_mask; n_mask_pixels = 0
	return single_mask, n_mask_pixels

def find_mask_centroid(mask):
	centroid_idx = np.array(ndimage.measurements.center_of_mass(mask))
	return centroid_idx

def combine_masks(mask_list):
	n_masks = len(mask_list)
	mask_out = mask_list[0]
	for i in range(1,n_masks):
		mask_out = mask_out | mask_list[i]
	return mask_out > 0

def eval_intersect(mask1, mask2):
	msk1 = mask1.astype(np.bool)
	msk2 = mask2.astype(np.bool)
	return np.sum((msk1 & msk2))

def write_seg_image(img_in, mask, file_name, overlay=[0,0,255], transparency=0.6):
	img = deepcopy(img_in) 
	for i, hue in enumerate(overlay):                                           
		img[mask,i] = hue*transparency + img[mask,i] * (1 - transparency)
	cv2.imwrite(file_name, img)
