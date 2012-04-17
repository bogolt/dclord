import wx.aui
import logging
import os.path
import db
import version
import map

log = logging.getLogger('dclord')

h = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
h.setFormatter(formatter)
log.addHandler(h)
log.setLevel(logging.DEBUG)

class DcFrame(wx.Frame):
	def __init__(self, parent):
		wx.Frame.__init__(self, parent, -1, "dcLord (%s): Divide & Conquer client (www.the-game.ru)"%(version.getVersion(),), style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
		
		self.map = map.Map(self)
		
		self._mgr = wx.aui.AuiManager(self)
		
		info = wx.aui.AuiPaneInfo()
		info.CenterPane()
		info.Fixed()
		info.DefaultPane()
		info.Resizable(True)
		info.CaptionVisible(False)
		
		self._mgr.AddPane(self.map, info)

		self._mgr.Update()
		
		self.makeMenu()
		
		#todo - restore previous state
		#self.Maximize()
		
	def makeMenu(self):
		fileMenu = wx.Menu()
		fileMenu.Append(wx.ID_EXIT, "E&xit")
		self.Bind(wx.EVT_MENU, self.onClose, id=wx.ID_EXIT)
		self.Bind(wx.EVT_MENU, self.onAbout, fileMenu.Append(wx.ID_ANY, "&About dcLord"))
		
		gameMenu = wx.Menu()
		self.updateMenu = gameMenu.Append(wx.ID_ANY, "&Update from sever")
		
		panel = wx.MenuBar()
		panel.Append(fileMenu, "&File")
		panel.Append(gameMenu, "G&ame")
		self.SetMenuBar(panel)
				
		self.Bind(wx.EVT_MENU, self.onUpdate, self.updateMenu)
	
		self.Bind(wx.EVT_CLOSE, self.onClose, self)
		
	def showHidePane(self, paneObject):
		pane = self._mgr.GetPane(paneObject)
		if pane.IsShown():
			self._mgr.ClosePane(pane)
		else:
			self._mgr.RestorePane(pane)
		self._mgr.Update()
		
	def onClose(self, event):
		#self.conf.panes = self._mgr.SavePerspective()

		#print 'saving "%s"'%(self.conf.panes,)
		#self.conf.save()
		self.Destroy()
		
	def closeApp(self, event):
		self.Close()
		
	def onAbout(self, event):
		info = wx.AboutDialogInfo()
		info.AddDeveloper('bogolt (bogolt@gmail.com)')
		info.SetName('dcLord')
		info.SetWebSite('https://github.com/bogolt/dclord')
		info.SetVersion(version.getVersion())
		info.SetDescription('Divide and Conquer\ngame client\nsee at: http://www.the-game.ru')
		wx.AboutBox(info)

	def showPlayersView(self, event):
		if self.players:
			self.players.Show(True)
			return

		self.players = self.res.LoadFrame(None, 'PlayersView')
		self.players.setConf(self.conf)
		self.players.Show(True)

	def onUpdate(self, event):
		pass

if __name__ == '__main__':
	app = wx.PySimpleApp()
	app.SetAppName('dcLord')
	
	frame = DcFrame(None)
	frame.Show(True)
	app.MainLoop()
