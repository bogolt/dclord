import sys
sys.path.append('../src')
from geometry import Coord, GameRect
import unittest

class CoordTest(unittest.TestCase):
	'test basic Coord operations'
	def test_cmp(self):
		a = Coord(1,2)
		b = Coord(1,2)
		c = Coord(2,1)
		d = Coord(22,22)
		
		self.assertEqual(a,b)
		self.assertNotEqual(d,b)
		self.assertNotEqual(b,c)
		self.assertNotEqual(b,d)
		self.assertEqual(d,d)
		
		self.assertTrue(a < d)
		self.assertTrue(a <= d)
		self.assertTrue(a <= b)
		self.assertTrue(c != a)

	def test_add(self):
		a = Coord(1,2)
		b = Coord(1,2)
		
		b+=a
		self.assertNotEqual(a,b)
		self.assertEqual(b, Coord(2,4))
		b+=(0,0)
		self.assertEqual(b, Coord(2,4))
		a+=b
		b+=(1,2)
		self.assertEqual(b,a)
		
		a = Coord(1,5)
		b = Coord(10, 1)
		
		c = a + b
		self.assertEqual(a, Coord(1,5))
		self.assertEqual(b, Coord(10,1))
		self.assertEqual(c, Coord(11,6))
		
	def test_sub(self):
		a = Coord(3,3)
		b = Coord(0,1)
		
		a-=b
		self.assertEqual(a, Coord(3,2))
		
		a-=b
		self.assertEqual(a, Coord(3,1))
		
		a-=b
		self.assertEqual(a, Coord(3,0))
		
		d = a - b
		self.assertEqual(a, Coord(3,0))
		self.assertEqual(b, Coord(0,1))
		self.assertEqual(d, Coord(3,-1))

class GameRectTest(unittest.TestCase):
	
	def test_cmp(self):
		rc = GameRect(Coord(1,1),(50,120))
			
		self.assertNotEqual(GameRect((1,1), (50,121)), rc)
		self.assertNotEqual(GameRect((1,2), (50,120)), rc)
		
	def test_split(self):
		
		# completly inside
		inside = GameRect(Coord(1,1),(50,120))
		insIter = iter(inside.rects())
		r = next(insIter)
		self.assertEqual(r, inside)
		
		# extend to the right
		left = Coord(200, 400)
		right = GameRect(left, (1100, 300))
		it = iter(right.rects())
		riCenter = next(it)
		
		self.assertEqual(riCenter[0], left)
		self.assertEqual(riCenter[1], (800, 300))
		
		riRight = next(it)
		self.assertEqual(riRight[0], Coord(1, 400))
		self.assertEqual(riRight[1], (300,300))
		
		# extend to the bottom
		bottom = GameRect(left, (333, 999))
		it = iter(bottom.rects())
		center = next(it)

		self.assertEqual(center[0], left)
		self.assertEqual(center[1], (333, 600))

		btm = next(it)
		self.assertEqual(btm[0], Coord(left.x, 1))
		self.assertEqual(btm[1], (333,399))
		
		# extend to both sides
		both = GameRect(left, (922, 655))
		it = iter(both.rects())
		ins = next(it)
		self.assertEqual(ins, (left, (800, 600)))
		
		right = next(it)
		self.assertEqual(right, ((1, left.y), (122, 655)))
		
		bottom = next(it)
		self.assertEqual(bottom, ((left.x, 1), (922, 55)))
		
		corner = next(it)
		self.assertEqual(corner, ((1,1), (122, 55)))
		

if __name__ == '__main__':
    unittest.main()
