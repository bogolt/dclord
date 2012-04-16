import db
import csv

def savePlanets():
	path='/tmp/dclord/planets.csv'
	f = open(path, 'wt')
	writer = csv.writer(f)
	writer.writerow(('x','y','owner_id','o','e','m','t','s'))
	for p in db.planets():
		writer.writerow(p)

def save():
	savePlanets()

def loadPlanets():
	path='/tmp/dclord/planets.csv'
	for p in csv.DictReader(open(path, 'rt')):
		db.setData('planet', p)

def load():
	loadPlanets()
