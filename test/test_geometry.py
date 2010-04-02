import sys
sys.path.append('../src')
from geometry import Coord
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

if __name__ == '__main__':
    unittest.main()
