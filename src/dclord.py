import wx.aui
import dcevent
from wx import xrc
import logging
import tasks
import request
import os.path
import units_panel

from map import Map
from loader import Loader, AsyncLoader
from property import PlanetProperty, FleetProperty, Messages
from db2 import Db
from settings import Settings
#from update import Update

#don't remove this - otherwise cxfreeze don't freeze it properly
from accounts_frame import AccountsFrame


version = '0.1.3'

log = logging.getLogger('dclord')

h = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
h.setFormatter(formatter)
log.addHandler(h)
log.setLevel(logging.DEBUG)

class DcFrame(wx.Frame):
	def __init__(self, parent):
		wx.Frame.__init__(self, parent, -1, "dcLord (%s): Divide & Conquer client (www.the-game.ru)"%(version,), style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

		self.players = None
		self.status = wx.StatusBar(self)
		self.status.SetStatusText("loading...")
		self.SetStatusBar(self.status)
		log.debug('dclord init')
		self.db = Db()
		self.conf = Settings(self)
		#self.update = Update(self, self.conf, version)
		
		self.loader = Loader(self.conf, self.db, self)
		self.loader.load()
				
		self.map = Map(self, self.db, self.conf)
		
		self._mgr = wx.aui.AuiManager(self)
		
		self.requeusts_queue = {}

		info = wx.aui.AuiPaneInfo()
		info.CenterPane()
		info.DefaultPane()
		info.Fixed()
		info.Resizable(True)
		info.CaptionVisible(False)

		self._mgr.AddPane(self.map, info)
		
		self.propPlanet = PlanetProperty(self, self.conf, self.db)
		self.propFleet = FleetProperty(self, self.conf, self.db)
		self.messages = Messages(self)
		self.tasks = tasks.TasksPanel(self, self.conf,  self.db)
		self.units_panel = units_panel.UnitsPanel(self, self.conf, self.db)
		
		self._mgr.AddPane(self.propPlanet, wx.LEFT, "Planet")
		self._mgr.AddPane(self.propFleet, wx.LEFT, "Fleets")
		self._mgr.AddPane(self.tasks, wx.LEFT, "Tasks")
		self._mgr.AddPane(self.messages, wx.BOTTOM, "Messages")
		self._mgr.AddPane(self.units_panel, wx.RIGHT, "Units")

		self._mgr.Update()

		self.res = xrc.XmlResource('res/dcLord.xrc')

		self.status.SetStatusText("ready")
	
		fileMenu = wx.Menu()
		fileMenu.Append(wx.ID_EXIT, "E&xit")
		about = fileMenu.Append(wx.ID_ANY, "&About dcLord")
		
		gameMenu = wx.Menu()
		self.syncMenu = gameMenu.Append(wx.ID_ANY, "G&et data")
		self.requestCommandsMenu = gameMenu.Append(wx.ID_ANY, "&Upload commands")
		playersView = gameMenu.Append(wx.ID_ANY, "&Accounts")
		
		viewMenu = wx.Menu()
		messagesVisible = viewMenu.Append(wx.ID_ANY, 'Me&ssages panel')
		propertiesVisible = viewMenu.Append(wx.ID_ANY, '&Properties panel')
		go_to_next_hw = viewMenu.Append(wx.ID_ANY, '&Go to next hw')

		panel = wx.MenuBar()
		panel.Append(fileMenu, "&File")
		panel.Append(viewMenu, "&View")
		panel.Append(gameMenu, "G&ame")
		self.SetMenuBar(panel)
		
		self.Bind(wx.EVT_MENU, self.closeApp, id=wx.ID_EXIT)
		self.Bind(wx.EVT_MENU, self.sync, self.syncMenu)
		self.Bind(wx.EVT_MENU, self.upload, self.requestCommandsMenu)
		self.Bind(wx.EVT_MENU, self.showPlayersView, playersView)
		
		self.Bind(wx.EVT_MENU, self.showMessagesView, messagesVisible)
		self.Bind(wx.EVT_MENU, self.showPropertiesView, propertiesVisible)
		self.Bind(wx.EVT_MENU, self.showNextHw, go_to_next_hw)
		self.Bind(wx.EVT_MENU, self.showAbout, about)
		
		self.Bind(dcevent.EVT_OBJECT_FOCUS, self.objectFocus)
		self.Bind(dcevent.EVT_REPORT, self.report)
		self.Bind(dcevent.EVT_LOADER, self.fileLoad)
		
		self.Bind(wx.EVT_CLOSE, self.onClose, self)
		
		self.Bind(dcevent.EVT_SET_MAP_POS, self.setMapPos)
		
		#disable actions for now
		#self.Bind(dcevent.EVT_REQUEST_ACTION_PERFORM, self.onPerformActionRequest)
		
		self.Bind(dcevent.EVT_SELECT_UNIT, self.showUnit)
		
		self.Maximize()
		
		self.accounts = []
		self.last_active_account_index = 0

		
	def showNextHw(self, evt):
		self.accounts = self.db.accounts
		if not self.accounts:
			return
		
		#self.last_active_account_index+=1
		#if self.last_active_account_index >= len(self.accounts):
		#	self.last_active_account_index = 0
		for acc in self.db.accounts.values():
			if acc.hw_pos:
				print 'set pos for hw of %s at %s'%(acc.login, acc.hw_pos)
				self.map.centerAt( acc.hw_pos )
			return
	
	def showUnit(self, event):
		self.units_panel.set_unit(event.attr1)
	
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

	def onPerformActionRequest(self, event):
		pass
		#self.requeusts_queue.setdefault( event.attr1[0], [] ).append( ( event.attr1[1], event.attr1[2] ) )
		
	def showAbout(self, event):
		info = wx.AboutDialogInfo()
		info.AddDeveloper('bogolt (bogolt@gmail.com)')
		info.AddDeveloper('librarian (menkovich@gmail.com)')
		info.SetName('dcLord')
		info.SetWebSite('https://github.com/bogolt/dclord')
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
	
	def explore_geo(self, evt):
		pass
		#find all planets which fit requirements of explorables
	
	def upload(self, _):
		
		#swap with empty value, to assure newly added commands will not interfere with sending ones
		tmp = {}
		tmp, self.requeusts_queue = self.requeusts_queue, tmp
		for user_id, actions in tmp.items():
			log.debug('request to send actions from user %d'%(user_id,))
			asyncLoader = AsyncLoader(self, self.conf)
			req = request.RequestMaker()
			for unit_id, action_id in actions:
				log.debug('store action %d %d'%(unit_id,action_id))
				req.store_action( unit_id, action_id)
			
			uname = self.db.get_login(user_id)
			log.debug('send actions %s for user %s'%(req, uname))
			asyncLoader.recvActionsReply( (uname,self.conf.users[uname]), req, self.conf.pathOut)
			asyncLoader.start()
	
	def sync(self, event):
		self.syncMenu.Enable(False)

		asyncLoader = AsyncLoader(self, self.conf)
		
		#import request
		#req = request.RequestMaker()
		#req.specific_action( (69, 120), 3277544, 16546296, 1)
		#req.store_action(16546296, 1)
		
		#req.createNewFleet( '822:978', 'client_generated_16429601')
		#reply <act id="ActionID" result="ok" return-id="fleet_id"/>
		
		for login in self.conf.users.items():
			asyncLoader.recvUserInfo(login, 'all', self.conf.pathArchive)
			asyncLoader.recvUserInfo(login, 'known_planets', self.conf.pathArchive)
		asyncLoader.start()
	
	def objectFocus(self, event):
		pos = event.attr1

		self.status.SetStatusText(str(pos))
		pl,fleets = event.attr2
		
		self.propPlanet.set(pl)
		self.propFleet.set(fleets)
	
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
			self.tasks.update()
			return
		
		#all files loaded(or not)
		self.syncMenu.Enable(True)
		
		self.SetStatusText('sync finished')
	
	def setMapPos(self, evt):
		self.map.centerAt(evt.attr1)

if __name__ == '__main__':
	app = wx.PySimpleApp()
	app.SetAppName('dcLord')
	
	frame = DcFrame(None)
	frame.Show(True)
	app.MainLoop()
