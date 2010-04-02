class Coord:
	'two-dimentional coordinate on map'
	def __init__(self, x = 0, y = 0):
		self.x = x
		self.y = y

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
		
	def __getitem__(self, index):
		'return coordinates like if they are tuple pair'
		if index==0:
			return self.x
		return self.y


class GameRect:
	
	'default galaxy size'
	galaxySize = 1000,1000
	
	def __init__(self, pos, size):
		self.pos = pos
		self.size = size
	
	def rects(self):
		'split the rect into continious rects ( no crossing borders of the game field )'
		
		#check if entire rect is inside the galaxy rect, just return it in this case
		if self.pos+self.size < galaxySize:
			yield self.pos,self.size
			return
			

