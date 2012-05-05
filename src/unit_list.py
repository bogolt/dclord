import wx.aui
import logging
import db
import util
import event
import config

log = logging.getLogger('dclord')

class UnitPrototypeWindow(wx.Window):
	def __init__(self, parent, id):
		self.id = id
		wx.Window.__init__(self, parent, wx.ID_ANY)
		
		
class UnitPrototypeListWindow(wx.Window):
	def __init__(self, parent, player_id):
		wx.Window.__init__(self, parent, wx.ID_ANY)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		#self.SetLayout(self.sizer)
