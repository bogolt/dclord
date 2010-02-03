import wx.aui
import dcevent
from wx import xrc

import os.path
from map import Map
from loader import Loader, AsyncLoader
from property import PlanetProperty, FleetProperty, Messages
from db import Db
from settings import Settings
#from update import Update

#don't remove this - otherwise cxfreeze don't freeze it properly
from accounts_frame import AccountsFrame

version = '0.1.3'

class DcFrame(wx.Frame):
	def __init__(self, parent):
		wx.Frame.__init__(self, parent, -1, "dcLord (%s): Divide & Conquer client (www.the-game.ru)"%(version,), style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

		#self.res, self.playerView = None,None
		self.players = None
		
		self.status = wx.StatusBar(self)
		self.status.SetStatusText("loading...")
		self.SetStatusBar(self.status)
		
		self.db = Db()
		self.conf = Settings(self)	
		
		#self.update = Update(self, self.conf, version)		
		
		self.loader = Loader(self.conf, self.db, self)
		self.loader.load()
				
		self.map = Map(self, self.db, self.conf)
		
		self._mgr = wx.aui.AuiManager(self)

		info = wx.aui.AuiPaneInfo()
		info.CenterPane()
		info.DefaultPane()
		info.Fixed()
		info.Resizable(True)
		info.CaptionVisible(False)

		self._mgr.AddPane(self.map, info)
		
		self.propPlanet = PlanetProperty(self, self.conf)
		self.propFleet = FleetProperty(self, self.conf)
		self.messages = Messages(self)
		
		self._mgr.AddPane(self.propPlanet, wx.RIGHT, "Planet")
		self._mgr.AddPane(self.propFleet, wx.RIGHT, "Fleets")
		self._mgr.AddPane(self.messages, wx.BOTTOM, "Messages")

		self._mgr.Update()
		#self._mgr.LoadPerspective(self.conf.panes, True)
		#update aui

		self.res = xrc.XmlResource('res/dcLord.xrc')

		self.status.SetStatusText("ready")
	
		fileMenu = wx.Menu()
		fileMenu.Append(wx.ID_EXIT, "E&xit")
		about = fileMenu.Append(wx.ID_ANY, "&About dcLord")
		
		gameMenu = wx.Menu()
		self.syncMenu = gameMenu.Append(wx.ID_ANY, "S&yncronize")
		playersView = gameMenu.Append(wx.ID_ANY, "&Accounts")
		
		viewMenu = wx.Menu()
		messagesVisible = viewMenu.Append(wx.ID_ANY, 'Me&ssages panel')
		propertiesVisible = viewMenu.Append(wx.ID_ANY, '&Properties panel')

		panel = wx.MenuBar()
		panel.Append(fileMenu, "&File")
		panel.Append(viewMenu, "&View")
		panel.Append(gameMenu, "G&ame")
		self.SetMenuBar(panel)
		
		self.Bind(wx.EVT_MENU, self.closeApp, id=wx.ID_EXIT)
		self.Bind(wx.EVT_MENU, self.sync, self.syncMenu)	
		self.Bind(wx.EVT_MENU, self.showPlayersView, playersView)
		
		self.Bind(wx.EVT_MENU, self.showMessagesView, messagesVisible)
		self.Bind(wx.EVT_MENU, self.showPropertiesView, propertiesVisible)
		self.Bind(wx.EVT_MENU, self.showAbout, about)
		
		self.Bind(dcevent.EVT_OBJECT_FOCUS, self.objectFocus)
		self.Bind(dcevent.EVT_REPORT, self.report)
		self.Bind(dcevent.EVT_LOADER, self.fileLoad)
		
		self.Bind(wx.EVT_CLOSE, self.onClose, self)
		
		self.Maximize()
	
	def showHidePane(self, paneObject):
		pane = self._mgr.GetPane(paneObject)
		if pane.IsShown():
			self._mgr.ClosePane(pane)
		else:
			self._mgr.RestorePane(pane)
		self._mgr.Update()
		
	def showPropertiesView(self, evt):
		self.showHidePane(self.propPlanet)
		#self.showHidePane(self.propFleet)

	def showMessagesView(self, evt):
		self.showHidePane(self.messages)
		
	def onClose(self, event):
		self.conf.panes = self._mgr.SavePerspective()
		#print 'saving "%s"'%(self.conf.panes,)
		#self.conf.save()
		self.Destroy()
		
	def closeApp(self, event):
		self.Close()

	def showAbout(self, event):
		info = wx.AboutDialogInfo()
		info.AddDeveloper('bogolt (bogolt@gmail.com)')
		info.SetName('dcLord')
		info.SetWebSite('http://sourceforge.net/projects/dclord')
		info.SetVersion(version)
		info.SetDescription('Divide and Conquer\ngame client\nsee at: http://www.the-game.ru')
		wx.AboutBox(info)

	def showPlayersView(self, event):
		if self.players:
			self.players.Show(True)
			return

		self.players = self.res.LoadFrame(None, 'PlayersView')
		self.players.setConf(self.conf)
		self.players.Show(True)
	
	def sync(self, event):
		self.syncMenu.Enable(False)
		
		#self.req = {'userid',req}

		asyncLoader = AsyncLoader(self, self.conf)
		for l in self.conf.users.items():
			asyncLoader.recvUserInfo(l, 'all', self.conf.pathArchive)
			asyncLoader.recvUserInfo(l, 'known_planets', self.conf.pathArchive)
			
			
			
#			asyncLoader.recvActionsReply(loginInfo, self.req[], self.conf.pathArchive)
		
		asyncLoader.start()

		#self.syncMenu.Enable(False)
		
		#self.loader = Loader(self.conf, self.db, self)
		#self.loader.sync()
	
	def objectFocus(self, event):
		pos = event.attr1

		self.status.SetStatusText(str(pos))
		self.propPlanet.set(event.attr2[0])
		self.propFleet.set(event.attr2[1])
	
	def report(self, event):
		self.status.SetStatusText(event.attr2)
		self.messages.addEvent(event.attr2)
		
	def fileLoad(self, event):
		if not event.attr1:
			self.messages.addEvent('file %s loaded'%(event.attr2,))
			if 'static.zip' == os.path.basename(event.attr2):
				self.conf.unpackStatic()
				return
			
			self.loader.loadFile(event.attr2)
			self.map.update()
			return
		
		#all files loaded(or not)
		self.syncMenu.Enable(True)
		
		self.SetStatusText('sync finished')

if __name__ == '__main__':
	app = wx.PySimpleApp()
	app.SetAppName('dcLord')
	
	frame = DcFrame(None)
	frame.Show(True)
	app.MainLoop()
