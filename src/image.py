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

def smaller(bitmap, ratio = 2):
	img = bitmap.ConvertToImage()
	w = img.GetWidth()
	h = img.GetHeight()
		
	scaled = img.Scale( w / ratio, h / ratio )
	return wx.BitmapFromImage(scaled)
	
def add_image(wx_img_list, obj):
	bc, carp, color = obj
	img = None
	if int(bc) < 113:
		img = getBcImage(bc)
	else:
		img = getCarapaceImage(carp, color)
	
	if not img:
		return None
	
	return wx_img_list.Add(img)
