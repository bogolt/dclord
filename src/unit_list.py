import wx.aui
import logging
import db
import util
import event
import config
import image

log = logging.getLogger('dclord')

class UnitPrototypeWindow(wx.Window):
	def __init__(self, parent, proto):
		self.proto = proto
		wx.Window.__init__(self, parent, wx.ID_ANY)
		img = wx.StaticBitmap(self, wx.ID_ANY)
		
		bmp = None
		if proto['carapace']:
			bmp = image.getCarapaceImage( proto['carapace'], proto['color'] )
		
		if not bmp:
			bmp = image.getBcImage( proto['id'], ) 
			
		if not bmp:
			log.error('bitmap not found for %s'%(self.proto,))
			return

		img.SetBitmap( bmp )
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(sizer)
		sizer.Add(img)
		sizer.Layout()
		
		
class UnitPrototypeListWindow(wx.Window):
	def __init__(self, parent, player_id):
		wx.Window.__init__(self, parent, wx.ID_ANY)
		self.player_id = player_id
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.sizer)
		
	def setPlayer(self, id):
		self.player_id = id
		self.loadProto()
		
	def loadProto(self):
		log.debug('loading protos for user %s '%(self.player_id,))
		for p in db.prototypes(['owner_id=%s'%(self.player_id,)]):
			log.debug('loading proto %s '%(p,))
			self.sizer.Add( UnitPrototypeWindow(self, p))
		self.sizer.Layout()
		log.debug('protos for user %s loaded'%(self.player_id,))
