import logging
import db
import util
import event
import config
import math
from vec2d import vec2d
from store import store

log = logging.getLogger('dclord')

class FillArea:
	def __init__(self, cb):
		self.cb = cb
		
		#ok, some left-top and width,height < need unit selector >
		self.area = (1,2) , (4,4)
		self.unit_types = [234455,23332,454555]
		
		# find holes in the area
		
		# find available ships ( which are not in the area themselves, on which are in counts more then required at the single coord )
		
		# or - try to --move-- field, replacing sheeps with other ones, and flying to new holes


def get_distance(a, b):
	dx = a[0]-b[0]
	dy = a[1]-b[1]
	return math.sqrt( dx * dx + dy * dy)

def get_center(a, b):
	
	return abs(a[0] - b[0])/2.0, abs(a[1]-b[1])/2.0 


def nearest(dest, points):
	m = get_distance(dest, points[0])
	for pt in points:
		m = min(m, get_distance(dest, pt))
	return m

class Router:
	def __init__(self, fleet, fly_range, dest_pos):
		self.fleet = fleet
		self.fly_range = fly_range
		self.user_id = fleet['user_id']
		self.start_pos = fleet['x'], fleet['y']
		self.dest_pos = dest_pos
		self.exclude_planets = []
		
	
	def find_route(self):
		planet_opts = {'x':self.start_pos[0], 'y':self.start_pos[1], 'user_id':self.user_id}
		start_planet = store.get_object('open_planet', planet_opts)
		if start_planet:
			r = self.route_next(self.start_pos)
			if r:
				return [self.start_pos] + r
			return []
		
		print 'route: fleet needs landing'
		# fleet starts on non-jumpable planet
		for pl in store.iter_open_planets(self.fly_range, self.start_pos, self.dest_pos, self.exclude_planets):
			# it can appear here
			if pl in self.exclude_planets:
				continue
				
			self.exclude_planets.append(pl)
			print 'route: landing found %s'%(pl,)
			
			if pl == self.dest_pos:
				print 'route found: direct jump'
				return [self.start_pos, pl]
			
			r = self.route_next(pl)
			if r:
				return [self.start_pos, pl] + r
		
		# sorry, not route to host
		return []
		
	def route_next(self, cur_pos):
		dist = util.distance(cur_pos, self.dest_pos)
		print 'route: looking from %s (%f left)'%(cur_pos, dist)
		# are we close enough for direct jump?
		if dist <= self.fly_range:
			print 'route found: direct jump from %s'%(cur_pos,)
			return [self.dest_pos]
		
		for pl in store.iter_open_planets(self.fly_range*2, cur_pos, self.dest_pos, self.exclude_planets):
			if pl in self.exclude_planets:
				continue

			d2 = util.distance(pl, self.dest_pos)
			if d2 >= dist:
				continue

			r = [pl]
			intermediate_pt = None
			jump_dist = util.distance(cur_pos, pl)
			if jump_dist > self.fly_range:
				intermediate_pt = self.find_intermediate_jump_point(cur_pos, pl)
				if not intermediate_pt:
					continue
				#intermediate_pt = cur_pos[0]+intermediate_pt[0], cur_pos[1]+intermediate_pt[1]
				r.append(intermediate_pt)
			

			self.exclude_planets.append(pl)
			#if intermediate_pt:
			#	print 'route: jump to %s (though %s), distance: %s'%(pl, intermediate_pt, jump_dist)
			#else:
			#	print 'route: jump to %s, distance: %s'%(pl, jump_dist)
			
			if cur_pos == self.dest_pos:
				print 'route found: %s'%(pl,)
				return r

			res = self.route_next(pl)
			if res:
				return r + res
		return []
	
	def find_intermediate_jump_point(self, start, end):
		dx = start[0]-end[0]
		dy = start[1]-end[1]
		center_pos = start[0]-dx, start[1]-dy
		if self.fly_range > util.distance(start, center_pos):
			return None
		return center_pos
		
	def xfind_intermediate_jump_point(self, start, end):
		center = get_center(start, end)
		max_center = math.ceil(center[0]), math.ceil(center[1])
		dist = get_distance((0,0), max_center)
		if dist <= self.fly_range:
			min_x = min(start[0], end[0])
			min_y = min(start[1], end[1])
			return max_center[0]+min_x, max_center[1]+min_y
		
		min_center = math.floor(center[0]), math.floor(center[1])
		if get_distance((0,0), min_center) >= self.fly_range:
			return None
		
		center_a = max_center[1], min_center[0]
		dist_a = get_distance((0,0), center_a)
		if dist_a > self.fly_range:
			return None
		
		center_b = max_center[0], min_center[1]
		dist_b = get_distance((0,0), center_b)
		if dist_b > self.fly_range:
			return None

		min_x = min(start[0], end[0])
		min_y = min(start[1], end[1])
		return center_b[0]+min_x, center_b[1]+min_y
				

def route_find(fleet, fly_range, dest_pos):
	r = Router( fleet, fly_range, dest_pos )
	res = r.find_route()
	print res
	return res

import unittest

class AlgorithmTest(unittest.TestCase):
	
	def setUp(self):
		store.add_open_planet({'x':100, 'y':100, 'user_id':1})
		store.add_open_planet({'x':110, 'y':110, 'user_id':1})
		store.add_open_planet({'x':130, 'y':100, 'user_id':1})
		store.add_open_planet({'x':113, 'y':123, 'user_id':1})
		store.add_open_planet({'x':117, 'y':124, 'user_id':1})
	
	def test_iter_open_planets(self):
		router = Router({'x':111, 'y':122, 'user_id':1}, fly_range=8, dest_pos=(100,99))
		store.add_open_planet({'x':112, 'y':121, 'user_id':1})
		store.add_open_planet({'x':111, 'y':121, 'user_id':1})
		store.add_open_planet({'x':105, 'y':104, 'user_id':1})
		store.add_open_planet({'x':110, 'y':121, 'user_id':1})
		res = router.find_route()
		print '%s'%(res,)
		
if __name__ == '__main__':
	unittest.main()


#TODO
# * jump to/from closed planet
# * optimize path choosing
# * get all intermediate jump points

class PathFinder:
	def __init__(self, start_pos, end_pos, speed, max_distance, jumpable_points):
		self.start_pos = start_pos
		self.end_pos = end_pos
		self.speed = speed
		self.max_distance = max_distance
		self.jumpable_points = jumpable_points
		
		self.possible = {}
		self.unluckily_possible = {}
		self.distant = {}
		self.cur = {}
		
		# established routes
		self.routes = {self.start_pos:(self.start_pos, 0)}
		self.new_routes = [self.start_pos]
		
		self.angle = 5 #biggest possible deflection from direct route

	def extend(self):
		self.angle += 5
		self.new_routes = self.routes.copy()
		
	def is_found(self):
		if self.end_pos in self.routes:
			return True
		return False
		
	def is_done(self):
		return len(self.new_routes) == 0
		
	def old_best_route(self):
		route = {}
		
		#ps = self.routes[self.end_pos]
		prev = self.end_pos
		#ps = self.routes[prev]
		
		while prev != self.start_pos:
			ps = self.routes[prev]
			route[prev] = ps
			print 'route: %s %s'%(prev, ps[0])
			prev = ps[0]
		
		print 'ret route %s'%(route,)
		return route

	def best_route(self):
		route = [self.end_pos]
		
		prev = self.end_pos
		while prev != self.start_pos:
			ps = self.routes[prev]
			route.append(ps[0])
			#route[prev] = ps
			#print 'route: %s %s'%(prev, ps[0])
			prev = ps[0]
		
		print 'ret route %s'%(route,)
		return route
		
	def step(self):
		print '======================'
		self.fill_possible()
		self.calculate_next_step()
		
		if self.is_done():
			return True
		return False
	
	def get_real_length(self, start, end):
		ijp = self.find_intermediate_jump_point(start, end)
		if not ijp:
			return None
		
		dist = 0
		for pt, l in ijp:
			dist += l
		return dist
	
	def get_route_length(self, pos):
		
		prev = pos
		l = 0 
		while prev != self.start_pos:
			cur = self.routes[prev]
			l += cur[1]
			prev = cur[0]
		return l
	
	def best_path(self, point, src_list):
		if len(src_list) == 1:
			l = self.get_real_length(point, src_list[0])
			if not l:
				return None
			return src_list[0], l
			#print 'best route %s %s '%(point, self.routes[point])
		
		best_route = src_list[0][0]
		min_length = None
		for src in src_list:
			l = self.get_real_length(point, src)
			if not l:
				continue
			dist = self.routes[src][1] + l
			if not min_length or dist < min_length:
				best_route = src
				min_length = dist
		
		if not min_length:
			return None
		print 'path %s %s %d'%(point, best_route, min_length)
		return best_route, min_length
		
	
	def calculate_next_step(self):
		self.new_routes = []
		for pos, src_list in self.possible.iteritems():
			#print 'look for best route to %s from %s'%(pos, src_list)
			bp = self.best_path(pos, src_list)
			if bp:
				log.info('route %s %s '%(pos, bp))
				self.routes[pos] = bp
				self.new_routes.append(pos)
		
	
	def fill_possible(self):
		self.possible = {}
		for pos in self.new_routes:
			self.fill_possible_routes(pos)
			
	
	def fill_possible_routes(self, pos):
		
		ideal_vector = vec2d( self.end_pos[0] - pos[0], self.end_pos[1] - pos[1] )
		for point in self.jumpable_points:
			if point in self.routes:
				continue
				
			if not self.may_jump(pos, point):
				continue
			
			cur_v = vec2d( point[0] - pos[0], point[1] - pos[1] )
			angle = cur_v.get_angle_between(ideal_vector)
			if abs(angle) > self.angle:
				continue
			
			if self.can_jump(pos, point):
				log.info("add possible route %s %s, angle %d"%(pos, point, angle ))
				self.possible.setdefault(point, []).append(pos)
			
		print 'possible %d points: %s ' % (len(self.possible), self.possible,)
			
		

	def find(self):
		p, self.possible = self.possible,{}
		for pt, src in p.iteritems():
			d = get_distance(self.end_pos, pt)
			s = get_distance(self.end_pos, src)
			if d > s:
				self.distant[pt] = src
				continue
			self.cur[pt] = src

	
	def can_jump_direct(self, start, end):
		return None
	
	def may_jump(self, start, end):
		dist = get_distance(start, end)
		if self.max_distance * 2 < dist:
			return False
		
		return True
	
	def can_jump(self, start, end):
		dist = get_distance(start, end)
		if dist <= self.max_distance:
			#ok can do it in single jupm
			return True
		
		return self.find_intermediate_jump_point(start, end)
	
	def find_intermediate_jump_point(self, start, end):
		
		center = get_center(start, end)
		max_center = math.ceil(center[0]), math.ceil(center[1])
		dist = get_distance((0,0), max_center)
		if dist <= self.max_distance:
			return [(max_center, int(math.ceil(dist / self.speed)))]
		
		min_center = math.floor(center[0]), math.floor(center[1])
		if get_distance((0,0), min_center) >= self.max_distance:
			return None
		
		center_a = max_center[1], min_center[0]
		dist_a = get_distance((0,0), center_a)
		if dist_a > self.max_distance:
			return None
		
		center_b = max_center[0], min_center[1]
		dist_b = get_distance((0,0), center_b)
		if dist_b > self.max_distance:
			return None
		return [(center_b, int(math.ceil(dist_b / self.speed))), (center_a, int(math.ceil(dist_a / self.speed)))]
		
