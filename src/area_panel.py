import wx.aui
import logging
import db
import util
import event
import config
import image

log = logging.getLogger('dclord')

def splitText(text):
	coord_list = [t.strip() for t in text.split('-')]
	cl = []
	for c in coord_list:
		cl.append(tuple([int(x.strip()) for x in c.split(':')]))
	return cl

class AreaWindow(wx.Window):
	def __init__(self, parent, text):
		wx.Window.__init__(self, parent)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		t = wx.StaticText(self, label='%s'%(text,))
		self.sizer.Add(t)
		self.SetSizer(self.sizer)
		self.Layout()
		
class AreaListWindow(wx.Window):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, wx.ID_ANY, size=(220,200))
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.sizer)
		
		buttonAdd = wx.Button(self, label='Add area')
		self.sizer.Add(buttonAdd)
		self.Layout()
		
		self.Bind(wx.EVT_BUTTON, self.onAddArea, buttonAdd)

	def addArea(self, text):
		pt_list = splitText(text)		
		area = AreaWindow(self, pt_list)
		self.sizer.Add(area)
		self.Layout()
		
	def onAddArea(self, evt):
		if not wx.TheClipboard.IsOpened():  # may crash, otherwise
			do = wx.TextDataObject()
			wx.TheClipboard.Open()
			success = wx.TheClipboard.GetData(do)
			wx.TheClipboard.Close()
			if success:				
				self.addArea(do.GetText())
