import wx
import math

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


class Map(BufferedWindow):
	def __init__(self, parent):
		self.offset_pos = 0,0
		self.cell_size = 24
		self.screen_size = 4,4

		BufferedWindow.__init__(self, parent)		
		
	def resize(self, evt = None):
		BufferedWindow.resize(self, evt)
		self.calcScreenSize()
	
	def calcScreenSize(self):
		w,h = self.GetClientSize()
		x,y = self.offset_pos		
		width  = int(math.ceil(float(w) / self.cell_size))
		height = int(math.ceil(float(h) / self.cell_size))
		self.screen_size = width,height
	
	def paint(self, dc):
		w,h = self.screen_size
		for x in range(0,w):
			for y in range(0,h):
				
				a = x*self.cell_size
				b = y* self.cell_size
				dc.DrawCircle(a, b, 6)
				
