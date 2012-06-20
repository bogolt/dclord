import gzip
import wx
import os
import os.path
import shutil
import tempfile

def getTempDir():
	return os.path.join(tempfile.gettempdir(), 'dclord')

def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper
    	
def static_var(varname, value):
	'make a static variable inside a function'
	#http://stackoverflow.com/questions/279561/what-is-the-python-equivalent-of-static-variables-inside-a-function/279586#279586
	def decorate(func):
			setattr(func, varname, value)
			return func
	return decorate

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

def assureNotExist(d):
	if os.path.exists(d):
		shutil.rmtree(d)

class BufferedWindow(wx.Window):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, -1, size=(-1,-1), style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.NO_BORDER)

		self.bg_color = wx.Colour(255,255,255)
		self.image = None
		self.resize()
		self.Bind(wx.EVT_PAINT, self.onPaint)
		self.Bind(wx.EVT_SIZE, self.resize)

	def update(self):
		dc = wx.MemoryDC()
		dc.SelectObject(self.image)

		dc.Clear()		
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

