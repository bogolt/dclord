import pygame

pygame.init()

s = pygame.Surface((1000, 1000),)

mp = pygame.image.load('../map_/fizMap_W.bmp')
s.blit(mp, (0,0))

diff = 255.0 / 99

for X in range(0, 20):
	for Y in range(0, 20):
		xx = X * 50
		yy = Y * 50
		
		xxx = xx if xx > 0 else 1
		yyy = yy if yy > 0 else 1
		
		f = open('/home/xar/.config/dclord/data/geo_size/visible_size_%s_%s'%(xxx, yyy), 'wt')
		f.write('x,y,s\n')
		for y in range(yy, yy + 50):
			for x in range(xx, xx + 50):
				if x == 0 or y == 0:
					continue

				c = s.get_at((x,y),)
				f.write('%s,%s,%s\n'%(y, x, int(c.r / diff)))
		
		f.close()

#x,y,visible_size
