def pos(name, coord):
	#return '<%s>%s:%s</%s>'%(name, coord[0],coord[1],name)
	return val(name, '%s:%s'%(coord[0],coord[1]))

def val(name, value):
	return '<%s>%s</%s>'%(name, value, name)

class Request:
	def __init__(self):
		self.id = 0
		self.req = ''

	def __str__(self):
		return val('x-dc-perform', self.req)

	def act(self, name, value):
		self.id+=1
		self.req+='<act id="%s" name="%s">%s</act>'%(self.id, name, value)
		return self.id
	
	def planetSetName(self, coord, name):
		return self.act("change_planet_name", pos('planetid', coord)+val('newname', name))
	#	return '<act name="change_planet_name" id="1"><newname>%s</newname><planetid>%s:%s</planetid></act>'%(name,coord[0],coord[1])
	
	def fleetMove(self, fleetId, to):
		return self.act('move_fleet', pos('move_to', to)+val('fleet_id',fleetId))
	#	return '<act name="fleet_move"><fleet_id>%s</fleet_id><move_to>%s:%s</move_to></act>'%(name,coord[0],coord[1])
		