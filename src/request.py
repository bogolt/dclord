def pos(name, coord):
	return val(name, '%s:%s'%(coord[0],coord[1]))

def val(name, value):
	return '<%s>%s</%s>'%(name, value, name)

class RequestMaker:
	GEO_EXPLORE = 1
	OFFER_VASSALAGE = 102
	def __init__(self):
		self.id = 0
		self.req = ''

	def __str__(self):
		return val('x-dc-perform', self.req)

	def act(self, name, value):
		self.id+=1
		self.req+='<act id="%s" name="%s">%s</act>'%(self.id, name, value)
		#self.req+='<action name="%s">%s</action>'%(name, value)
		return self.id
	
	def planetSetName(self, coord, name):
		return self.act("change_planet_name", pos('planetid', coord)+val('newname', name))
	
	def fleetMove(self, fleetId, to):
		return self.act('move_fleet', pos('move_to', to)+val('fleet_id',fleetId))
	
	def createNewFleet(self, planet, name):
		plId = pos('planetid', planet)
		nm = val('new_fleet_name', name)
		return self.act('create_new_fleet', plId + nm)
		
	#def createFleetFromChosen(self, coord, units, name):
		#return self.act('create_fleet_from_choosen', val('planetid', '%d:%d'%(coord[0], coord[1])) + val('new_fleet_name', name)+ val('fleetx', coord[0])+ val('fleety',coord[1]) + ''.join(val('
	
	# id==1 - get planet geo
	# id==102 - offer becoming vassal
	def store_action(self, unit_id, action_id):
		return self.act('store_action', val('unit_id', unit_id) + val('action_id',action_id))
		
	def moveUnitToFleet(self, fleetId, unitId):
		return self.act('move_unit_to_fleet', val('fleet_id', fleetId)+val('unit_id', unitId))
		
	def cancelJump(self, fleetId):
		return self.act('cancel_jump', val('fleet_id', fleetId))

class RequestList:
	def __init__(self):
		self.req = {}
		
#	def 
#
#class Command:
#	def __init__(self, db, player, cb):
#		self.db = db
#		self.player=player
#		self.req = RequestMaker()
#		self.cb = cb
		
	def renamePlanet(self, player, coord, name):
		return self.req[player].planetSetName(coord, name)
	
	def createFleet(self, player, coord, name):
		"""return pseudo fleet id
		"""
		return self.req[player].createNewFleet(coord, name)

	def moveFleet(self, player, fleet, coord):
		return self.req[player].fleetMove(fleet.id, coord)
		
	def cancelJump(self, player, fleet):
		return self.req[player].cancelJump(fleet.id)
		
#	def req(self):
#		al = AsyncLoader()
#	
#class RequestFrame(wx.Frame):
#	def __init__(self, parent):
#		wx.Frame.__init__(self, parent, wx.ID_ANY)
