import wx
import wx.aui
import dcevent

from map import Map
from loader import Loader
from property import Property
from db import Db

class DcFrame(wx.Frame):
	def __init__(self, parent):
		wx.Frame.__init__(self, parent, -1, "Divide & Conquer client", style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

		self.status = wx.StatusBar(self)
		self.status.SetStatusText("loading...")
		self.SetStatusBar(self.status)
		
		self.manager = wx.aui.AuiManager(self)

		self.db = Db()
		self.loader = Loader(self.db)
		self.loader.load()
		self.map = Map(self, self.db)

		info = wx.aui.AuiPaneInfo()
		info.CenterPane()
		info.DefaultPane()
		info.Fixed()
		info.Resizable(True)
		info.CaptionVisible(False)

		self.manager.AddPane(self.map, info)
		
		self.property = Property(self)
		self.manager.AddPane(self.property, wx.RIGHT, "Property")
		
		#update aui
		self.manager.Update()

		self.status.SetStatusText("ready")

		fileMenu = wx.Menu()
		fileMenu.Append(wx.ID_EXIT, "E&xit")
		
		gameMenu = wx.Menu();
		sync = gameMenu.Append(wx.ID_ANY, "S&yncronize")

		panel = wx.MenuBar()
		panel.Append(fileMenu, "&File")
		panel.Append(gameMenu, "G&ame")
		self.SetMenuBar(panel)
		
		self.Bind(wx.EVT_MENU, self.closeApp, id=wx.ID_EXIT)
		self.Bind(wx.EVT_MENU, self.sync, sync)
		self.Bind(dcevent.EVT_OBJECT_FOCUS, self.objectFocus)
		
	def closeApp(self, event):
		self.Close()
		
	def sync(self, event):
		self.loader.sync()
		self.map.update()
	
	def objectFocus(self, event):
		pos = event.attr1

		self.status.SetStatusText(str(pos)+" "+str(event.attr2))
		self.property.setData(self.map.getData(pos))

if __name__ == '__main__':
	app = wx.PySimpleApp()
	
	frame = DcFrame(None)
	frame.Show(True)
	app.MainLoop()

