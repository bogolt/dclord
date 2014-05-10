import db
import util
import math
from store import store

def pos(name, coord):
	return val(name, '%s:%s'%(coord[0],coord[1]))

def val(name, value):
	return '<%s>%s</%s>'%(name, value, name)

class RequestMaker:
	GEO_EXPLORE = 1
	KILL_PEOPLE = 101
	OFFER_VASSALAGE = 102
	ARC_COLONISE=6
	COLONY_COLONISE=2
	def __init__(self, user_id = 0):
		self.act_id = 0
		self.req = ''
		self.user_id = user_id

	def __str__(self):
		return val('x-dc-perform', self.req)
		
	def is_empty(self):
		return len(self.req) == 0
		
	def clear(self):
		self.req = ''

	def act(self, name, value):
		self.act_id+=1
		self.req+='<act id="%s" name="%s">%s</act>'%(self.act_id, name, value)
		#self.req+='<action name="%s">%s</action>'%(name, value)
		
		return self.act_id
	
	def planetSetName(self, coord, name):
		return self.act("change_planet_name", pos('planetid', coord)+val('newname', name))
	
	def fleetMove(self, fleetId, to):
		act = self.act('move_fleet', pos('move_to', to)+val('fleet_id',fleetId))
		
		# save fleet info
		fleet = store.get_object('fleet', {'fleet_id':fleetId})
		
		speed, rng = store.get_fleet_speed_range(fleetId)
		cur_pos = util.get_coord(fleet)
		dist = util.distance(to, cur_pos)
		
		# cannot move this far
		if dist > rng:
			print 'Error - attempt to move fleet %s to distance %s which is longer then fleet max range %s'%(fleetId, dist, rng)
		
		turns = int(math.ceil(dist / speed))
		u = store.get_user(fleet['user_id'])
		cur_turn = u['turn']
		
		store.add_pending_action(self.act_id, 'fleet', 'erase', {'fleet_id':fleetId})
		store.add_pending_action(self.act_id, 'flying_fleet', 'insert', {'x':to[0], 'y':to[1], 'user_id':self.user_id, 'id':fleetId, 'from_x':fleet['x'], 'from_y':fleet['y'], 'arrival_turn':turns + cur_turn})
		
		#db.add_pending_action(self.act_id, db.Db.FLEET, 'erase', ['id=%s'%(fleetId,)])
		#db.add_pending_action(self.act_id, db.Db.FLYING_FLEET, 'insert', {'x':to[0], 'y':to[1], 'owner_id':self.user_id, 'id':fleetId, 'from_x':fleet['x'], 'from_y':fleet['y'], 'arrival_turn':turns + db.getTurn()})
		return act
		
	
	def createNewFleet(self, planet, name):
		
		plId = pos('planetid', planet)
		nm = val('new_fleet_name', name)
		act = self.act('create_new_fleet', plId + nm)
		#db.add_pending_action(self.act_id, db.Db.FLEET, 'insert', {'name':name, 'x':planet[0], 'y':planet[1], 'owner_id':self.user_id})
		return act
	
	def get_action_id(self):
		return self.act_id
		
#	def createFleetFromChosen(self, coord, units, name):
#		return self.act('create_fleet_from_choosen', val('planetid', '%d:%d'%(coord[0], coord[1])) + val('new_fleet_name', name)+ val('fleetx', coord[0])+ val('fleety',coord[1]) + ''.join(val('
	
	# id==1 - get planet geo
	# id==102 - offer becoming vassal
	def store_action(self, unit_id, action_id):
		return self.act('store_action', val('unit_id', unit_id) + val('action_id',action_id))

	# return id of cancel action
	def colonize_arc(self, unit_id):
		return self.store_action(unit_id, self.ARC_COLONISE)

	# return id of cancel action
	def colonize_colony(self, unit_id):
		return self.store_action(unit_id, self.COLONY_COLONISE)
		
	def moveUnitToFleet(self, fleetId, unitId):
		
		act = self.act('move_unit_to_fleet', val('fleet_id', fleetId)+val('unit_id', unitId))
		
		u = None
		for unit in db.units(db.getTurn(), ['id=%s'%(unitId,)]):
			u = unit
		
		if not u:
			for unit in db.garrison_units(db.getTurn(), ['id=%s'%(unitId,)], ('x', 'y', 'class', 'hp')):
				u = unit
			if not u:
				print 'local unit %s not found'%(unitId,)
				return act
			print 'get garrison unit %s'%(u,)
			db.add_pending_action(self.act_id, db.Db.GARRISON_UNIT, 'erase', {'id':unitId})
			del u['x']
			del u['y']
			u['fleet_id'] = fleetId
			db.add_pending_action(self.act_id, db.Db.UNIT, 'insert', u)
		else:
			print 'get fleet unit %s'%(u,)
			db.add_pending_action(self.act_id, db.Db.UNIT, 'update', ({'id':unitId}, {'fleet_id':fleetId}))
			
		return act
		
	def cancelJump(self, fleetId):
		return self.act('cancel_jump', val('fleet_id', fleetId))
		
	def add_building_to_que(self, planet, buildig_id):
		plId = pos('planetid', planet)
		return self.act('add_building_to_que', plId +val('building_id', building_id))
		
	def explore_planet(self, planet, unit_id):
		return self.act('store_action', val('unit_id', unit_id) + pos('planetid', planet) + val('action_id', self.GEO_EXPLORE))

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
	
	def explorePlanet(self, player, planet, unit_id):
		return self.req[player].explore_planet(planet, unit_id)
		
#	def req(self):
#		al = AsyncLoader()
#	
#class RequestFrame(wx.Frame):
#	def __init__(self, parent):
#		wx.Frame.__init__(self, parent, wx.ID_ANY)
