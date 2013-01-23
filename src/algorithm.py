import logging
import db
import util
import event
import config
import math

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
	
	return a[0] + (a[0] - b[0])/2, a[1] + (a[1]-b[1])/2 

class PathFinder:
	def __init__(self, start_pos, end_pos, speed, max_distance, jumpable_points):
		self.start_pos = start_pos
		self.end_pos = end_pos
		self.speed = speed
		self.max_distance = max_distance
		self.jumpable_points = jumpable_points
		
	
	def can_jump_direct(self, start, end):
		
		return self.max_distance >= distance:

	def can_jump(self, start, end):
		
		if self.can_jump_direct(start, end):
			return True
		
		return self.max_distance >= distance * 2
	
	def find_intermediate_jump_point(self, start, end):
		
		return get_center(start, end)
			
	
		
