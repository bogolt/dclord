import gzip
import wx
import os
import os.path

def add(c1, c2):
	return (c1[0]+c2[0], c1[1]+c2[1])
def sub(c1, c2):
	return (c1[0]-c2[0], c1[1]-c2[1])
def div(c1, d):
	return (c1[0]/d, c1[1]/d)
def mul(c1, d):
	return (c1[0]*d, c1[1]*d)

def unpack(path_in, path_out):
	f = gzip.open(path_in, 'rb')
	with open(path_out, 'wb') as out:
		out.write(f.read())
	f.close()

def assureDirExist(d):
	if os.path.exists(d):
		return
	os.makedirs(d)

class BufferedWindow(wx.Window):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, -1, size=(-1,-1), style=wx.NO_FULL_REPAINT_ON_RESIZE)

		self.bg_color = wx.Color(255,255,255)
		self.image = None
		self.resize()
		self.Bind(wx.EVT_PAINT, self.onPaint)
		self.Bind(wx.EVT_SIZE, self.resize)

	def update(self):
		dc = wx.MemoryDC()
		dc.SelectObject(self.image)

		dc.Clear()
		dc.SetBrush(wx.Brush(self.bg_color))
		w,h = self.image.GetSize()
		dc.DrawRectangle(0,0, w,h)
		
		self.paint(dc)

		del dc # need to get rid of the MemoryDC before Update() is called.
		self.Refresh()
		self.Update()
		
	def paint(self, dc):
		pass
	
	def resize(self, _ = None):
		w,h = self.GetClientSize()
		self.image = wx.EmptyBitmap(w,h)
		self.update()
		
	def onPaint(self, _):
		'paint prerendered image on screen'
		dc = wx.BufferedPaintDC(self, self.image)
