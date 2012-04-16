import db
import csv

def savePlanets():
	path='/tmp/dclord/planets1.csv'
	f = open(path, 'wt')
	writer = csv.DictWriter(f, ('x','y','owner_id','o','e','m','t','s'))
	writer.writeheader()
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
