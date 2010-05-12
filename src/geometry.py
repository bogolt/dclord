class Coord:
	
	maxSize = 1000
	'two-dimentional coordinate on map'
	def __init__(self, x = 0, y = 0):
		self.x = x
		self.y = y

	def is_valid(self):
		return self.x != 0 and self.y != 0

	def __eq__(self, c):
		'compare with the same object type for equality'
		return self.x==c[0] and self.y==c[1]

	def __neq__(self, c):
		'compare with the same object type for equality'
		return not self==c
		#return self.x!=c[0] or self.y!=c[1]

	def __lt__(self, c):
		return self.x < c[0] and self.y < c[1]

	def __le__(self, c):
		return self.x <= c[0] and self.y <= c[1]

	def __gt__(self, c):
		return not self <= c

	def __ge__(self, c):
		return not self < c
				
	def __iadd__(self, c):
		'add a simple tuple object'
		self.x += c[0]
		self.y += c[1]
		return self

	def __add__(self, c):
		'add a simple tuple object'
		return Coord(self.x + c[0], self.y + c[1])

	def __isub__(self, c):
		self.x -= c[0]
		self.y -= c[1]
		return self

	def __sub__(self, c):
		'add a simple tuple object'
		return Coord(self.x - c[0], self.y - c[1])
	
	def __str__(self):
		return '%s:%s'%(self.x,self.y)
		
	def __getitem__(self, index):
		'return coordinates like if they are tuple pair'
		if index==0:
			return self.x
		return self.y
		
	def minimize(self):
		return Coord(self.x % self.maxSize, self.y % self.maxSize)
		
	def shrink(self, size):
		return Coord(min(self.x, size[0]), min(self.y, size[1]))

class Rect:
	def __init__(self, c, sz):
		self.coord = c
		self.sz = sz

class GameRect:
	'game rect object, it can overlap game borders, so use rects() to get a list of plain rects'
	
	'default galaxy size'
	galaxySize = Coord.maxSize, Coord.maxSize
	
	def __init__(self, pos, size):
		'should be values between 1 and galaxySize as position and values not bigger then galaxySize as size'
		self.pos = pos
		self.size = size
	
	def __getitem__(self, index):
		'return coordinates like if they are tuple pair'
		if index==0:
			return self.pos
		return self.size
	
	def __eq__(self, r):
		'compare with the same object type for equality'
		return self.pos == r[0] and self.size == r[1]

	def __neq__(self, c):
		'compare with the same object type for equality'
		return not self==c

	def __str__(self):
		return '%s %s'%(self.pos, self.size)
		
	def rects(self):
		'split the rect into continious rects ( no crossing borders of the game field )'
		
		topRight = self.pos+self.size
		
		#check if entire rect is inside the galaxy rect, just return it in this case
		if topRight <= self.galaxySize:
			yield self.pos,self.size
			return			

		#otherwise, ok take the top-left corner ( before the border )
		topRightShrink = topRight.shrink(self.galaxySize)
		sizeTopLeft = topRightShrink-self.pos
		yield self.pos, sizeTopLeft
		
		ext = topRight-self.galaxySize
		if ext.x > 0:
			rightPos  = Coord(1, self.pos.y)
			rightSize = ext.x,self.size[1]
			yield rightPos, rightSize
		if ext.y > 0:
			leftPos  = Coord(self.pos.x, 1)
			leftSize = self.size[0], ext.y
			yield leftPos, leftSize
		
		if ext.x>0 and ext.y>0:
			yield Coord(1,1), ext
