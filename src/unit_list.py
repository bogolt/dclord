import wx.aui
import logging
import db
import util
import event
import config
import image

log = logging.getLogger('dclord')

def getProtoName(proto):
	if 'name' in proto:
		return proto['name']
	return 'serial'

class UnitPrototypeWindow(wx.Window):
	def __init__(self, parent, proto_u):
		wx.Window.__init__(self, parent, wx.ID_ANY)
		img = wx.StaticBitmap(self, wx.ID_ANY)
		
		proto = proto_u
		if not 'carapace' in proto_u:
			for pr in db.prototypes(['id=%d'%(proto['class'],)]):
				proto = pr
				break
		
		bmp = None
		if proto['carapace']:
			bmp = image.getCarapaceImage( proto['carapace'], proto['color'] )
		
		if not bmp:
			bmp = image.getBcImage( proto['id'], ) 
			
		if not bmp:
			log.error('bitmap not found for %s'%(proto,))
			return

		img.SetBitmap( bmp )
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(sizer)
		
		usz = wx.BoxSizer(wx.HORIZONTAL)
		usz.Add(img)
		usz.Add(wx.StaticText(self, wx.ID_ANY, '[%s]'%(getProtoName(proto),)))
		sizer.Add(usz)
		sizer.Layout()
		
		
class UnitPrototypeListWindow(wx.Window):
	def __init__(self, parent, player_id):
		wx.Window.__init__(self, parent, wx.ID_ANY, size=(220,200))
		self.player_id = player_id
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.sizer)
		
		self.filter_opts = []
		
		
	def setPlayer(self, id):
		self.player_id = id
		self.loadProto()
		
	def loadProto(self):
		log.info('setting protos for user %s'%(self.player_id,))
		fly_range=1
		fly_speed=2
		self.sizer.DeleteWindows()
		for p in db.prototypes(['fly_range>=%s'%(fly_range,), 'fly_speed>=%s'%(fly_speed,), 'owner_id=%s'%(self.player_id,)]):
			self.sizer.Add( UnitPrototypeWindow(self, p))
		self.sizer.Layout()
