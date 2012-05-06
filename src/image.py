import wx
import config
import logging
import os
import os.path

log = logging.getLogger('dclord')

image_carapace_cache = {}
image_bc_cache = {}

def loadBitmap(rel_path):
	imgPath = os.path.join(config.options['data']['images'], rel_path)
	if not os.path.exists(imgPath):
		log.error('image %s does not exist'%(imgPath,))
		return None
	return wx.Image(imgPath).ConvertToBitmap()

def loadCarapaceImage( carapace, color ):
	img = loadBitmap( 'carps/%s_%s.gif'%(carapace,color) )
	global image_carapace_cache
	image_carapace_cache[ (carapace, color) ] = img
	return img

def getCarapaceImage(carapace, color = None):
	key = (carapace,color)
	global image_carapace_cache
	return image_carapace_cache.setdefault(key, loadCarapaceImage(carapace, color))

def loadBcImage(bc):	
	img = loadBitmap( '%s.gif'%(bc,) )
	global image_bc_cache
	image_bc_cache[ bc ] = img
	return img

def getBcImage(bc):
	global image_bc_cache
	return image_bc_cache.setdefault(bc, loadBcImage(bc))
