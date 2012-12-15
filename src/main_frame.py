import wx.aui
import logging
import os.path
import db
import version
import util
import map
import event
import config
import import_raw
import serialization
import object_filter
import unit_list
import users
import area_panel
import request
import planet_window

log = logging.getLogger('dclord')

h = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
h.setFormatter(formatter)
log.addHandler(h)
log.setLevel(logging.DEBUG)

class DcFrame(wx.Frame):
	def __init__(self, parent):
		sz = int(config.options['window']['width']), int(config.options['window']['height'])
		wx.Frame.__init__(self, parent, -1, "dcLord (%s): Divide & Conquer client (www.the-game.ru)"%(version.getVersion(),), style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE, size=sz)
		
		if int(config.options['window']['is_maximized'])==1:
			self.Maximize()
			
		serialization.load()
		print 'db max turn is %s'%(db.getTurn(),)
		self.map = map.Map(self)
		self.map.turn = db.getTurn()
		print 'map turn is set to %s'%(self.map.turn,)
		self.map.update()
		
		import_raw.processAllUnpacked()
		#self.map.turn = db.db.max_turn
		
		
		self.info_panel = planet_window.InfoPanel(self)
		self.object_filter = object_filter.FilterPanel(self)
		self.unit_list = unit_list.UnitPrototypeListWindow(self, 0)
		
		#self.area_list = area_panel.AreaListWindow(self)
		
		self.pendingActions = {}
		
		self._mgr = wx.aui.AuiManager(self)
		
		info = wx.aui.AuiPaneInfo()
		info.CenterPane()
		info.Fixed()
		info.DefaultPane()
		info.Resizable(True)
		info.CaptionVisible(False)
		
		self._mgr.AddPane(self.map, info)
		self._mgr.AddPane(self.info_panel, wx.LEFT, "Info")
		self._mgr.AddPane(self.object_filter, wx.LEFT, "Filter")
		self._mgr.AddPane(self.unit_list, wx.RIGHT, "Units")
		#self._mgr.AddPane(self.area_list, wx.RIGHT, "Areas")
		
		self._mgr.Update()
		
		self.makeMenu()
		
		self.Bind(event.EVT_DATA_DOWNLOAD, self.onDownloadRawData)
		self.Bind(event.EVT_MAP_UPDATE, self.onMapUpdate)
		self.Bind(event.EVT_USER_SELECT, self.onSelectUser)
		self.Bind(event.EVT_ACTIONS_REPLY, self.onActionsReply)
		self.Bind(event.EVT_SELECT_OBJECT, self.info_panel.selectObject)
	
		#import_raw.processAllUnpacked()
		#serialization.save()
		
		#todo - restore previous state
		#self.Maximize()
		
	def makeMenu(self):
		fileMenu = wx.Menu()
		fileMenu.Append(wx.ID_EXIT, "E&xit")
		self.Bind(wx.EVT_MENU, self.onClose, id=wx.ID_EXIT)
		self.Bind(wx.EVT_MENU, self.onAbout, fileMenu.Append(wx.ID_ANY, "&About dcLord"))
		
		gameMenu = wx.Menu()
		self.updateMenu = gameMenu.Append(wx.ID_ANY, "&Download from sever")
		#self.uploadMenu = gameMenu.Append(wx.ID_ANY, "&Upload to server")
		usersMenu = gameMenu.Append(wx.ID_ANY, "U&sers")
		
		#actionMenu = wx.Menu()
		#actionDefineArea = actionMenu.Append(
		
		panel = wx.MenuBar()
		panel.Append(fileMenu, "&File")
		panel.Append(gameMenu, "G&ame")
		self.SetMenuBar(panel)
				
		self.Bind(wx.EVT_MENU, self.onUpdate, self.updateMenu)
		#self.Bind(wx.EVT_MENU, self.onUpload, self.uploadMenu)
		self.Bind(wx.EVT_MENU, self.onShowUsers, usersMenu)
	
		self.Bind(wx.EVT_CLOSE, self.onClose, self)
		
	def showHidePane(self, paneObject):
		pane = self._mgr.GetPane(paneObject)
		if pane.IsShown():
			self._mgr.ClosePane(pane)
		else:
			self._mgr.RestorePane(pane)
		self._mgr.Update()
	
	def onShowUsers(self, evt):
		p = users.UsersPanel(self)
		p.Show()
		#p.init()
	
	def onMapUpdate(self, evt):
		self.map.update()
		
	def onClose(self, event):
		self.updateConfig()
		#print '%s'%(self._mgr.SavePerspective(),)
		#self.conf.panes = 

		#print 'saving "%s"'%(self.conf.panes,)
		#self.conf.save()
		self.Destroy()
		
	def closeApp(self, event):
		self.Close()
		
	def updateConfig(self):
		w,h = self.GetClientSize()
		config.options['window']['height'] = h
		config.options['window']['width'] = w
		config.options['window']['is_maximized'] = int(self.IsMaximized())		

		config.options['map']['offset_pos_y'] = self.map.offset_pos[1]
		config.options['map']['offset_pos_x'] = self.map.offset_pos[0]
		
		config.options['map']['cell_size'] = self.map.cell_size

		config.saveOptions()
		
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
		'download and process info from server'
		import loader
		l = loader.AsyncLoader()
		
		out_dir = os.path.join(util.getTempDir(), config.options['data']['raw-dir'])
		util.assureDirClean(out_dir)
		for acc in config.accounts():
			log.info('requesting user %s info'%(acc['login'],))
			l.getUserInfo(self, acc['login'], out_dir)
		l.start()

	def onUpload(self, event):
		'upload pending events on server'
		import loader
		l = loader.AsyncLoader()
		
		out_dir = os.path.join(util.getTempDir(), config.options['data']['raw-dir'])
		util.assureDirClean(out_dir)
		for acc in config.accounts():
			log.info('requesting user %s info'%(acc['login'],))
			actions = request.RequestMaker()
			self.pendingActions[int(acc['id'])] = actions
			hw_planet = db.getUserHw(acc['id'])
			actions.createNewFleet(hw_planet, 'a_new_shiny_fleet')
			l.sendActions(self, acc['login'], actions, out_dir)
		l.start()
		
	def onActionsReply(self, event):
		user = event.attr1
		actions = event.attr2
		
		#self.pendingActions[int(user['id'])]
			
	def onDownloadRawData(self, evt):
		key = evt.attr1
		data = evt.attr2
		if not key:
			log.info('all requested data downloaded')
			serialization.save()
			return
		if not data:
			log.error('failed to load info for user %s'%(key,))
			return
		import_raw.processRawData(data)
		self.map.turn = db.db.max_turn
		self.map.update()
	
	def onSelectUser(self, evt):
		user_id = evt.attr1
		#user_id = int(config.users[login]['id'])
		self.unit_list.setPlayer( user_id )
		print 'selecting user %s'%(user_id, )
		self.map.selectUser( user_id) 
