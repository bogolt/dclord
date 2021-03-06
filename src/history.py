import wx.aui
import logging
import db
import util
import event
import config
import unit_list

log = logging.getLogger('dclord')

class HistoryPanel(wx.Window):
	def __init__(self, parent, turn = -1):
		wx.Window.__init__(self, parent, wx.ID_ANY, size=(201,201))
		self.turn = turn
		self.turns = {}
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.turnList = wx.ListBox(self)
		self.turnList.Bind(wx.EVT_LISTBOX, self.onTurnSelected)
		
		self.pos = 0
		self.sizer.Add(self.turnList, 1, flag=wx.EXPAND | wx.ALL)
		self.SetSizer(self.sizer)
		self.sizer.Layout()
		
		self.Bind(wx.EVT_SIZE, self.onSize, self)
		
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()
	
	def onSetActiveTurn(self, event):
		label = event.GetEventObject()
		if not isinstance(label, wx.StaticText):
			log.error("not a label")
			return
			
		turn = int(label.GetLabel())
		log.info('ok, turn %d'%(turn,))
		
	def onTurnSelected(self, evt):
		ind = evt.GetSelection()
		for turn, index in self.turns.items():
			if index == ind:
				print('set turn %d'%(turn,))
				wx.PostEvent(self.GetParent(), event.TurnSelected(attr1=turn))
				break
	
	def updateTurns(self, turn):
		for t in sorted(db.db.turns.keys()):
			if t in self.turns:
				continue
			self.turnList.Insert(str(t), self.pos)
			self.turns[t] = self.pos
			self.pos+=1
		
		if turn != self.turn and turn:
			self.turn = turn
			self.turnList.SetSelection(self.turns[self.turn])
