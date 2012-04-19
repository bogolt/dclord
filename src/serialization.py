import db
import csv
import config
import os
import os.path

def savePlanets():
	path = os.path.join(config.options['data']['path'], 'planets.csv')
	f = open(path, 'wt')
	writer = csv.DictWriter(f, ('x','y','owner_id','o','e','m','t','s'))
	writer.writeheader()
	for p in db.planets(None):
		writer.writerow(p)

def save():
	savePlanets()

def loadPlanets():
	path= os.path.join(config.options['data']['path'], 'planets.csv')
	for p in csv.DictReader(open(path, 'rt')):
		db.setData('planet', p)

def load():
	loadPlanets()
