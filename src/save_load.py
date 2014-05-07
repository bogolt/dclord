from store import store
import csv
import os
import logging
import util

unicode_strings = [u'name', u'description']

def csv_open(path, keys):
	writer = csv.DictWriter(open(path, 'wt'), keys)
	writer.writeheader()
	return writer

def save_csv(path, data):
	if not data or data == {}:
		return
		
	writer = csv_open(path, data[0].keys())
	for p in data:
		writer.writerow({k:(v.encode('utf8') if (k in unicode_strings and v) else v) for k,v in p.items()})
			
		
def save_csv_table(path, table, data_filter):
	writer = None
	for p in store.iter_objects_list(table, data_filter):
		if not writer:
			writer = csv_open(os.path.join(path, '%s.csv'%(table,)), p.keys())
		writer.writerow({k:(v.encode('utf8') if (k in unicode_strings and v) else v) for k,v in p.items()})
		
def iter_csv(path):
	objs = []
	for p in csv.DictReader(open(path, 'rt')):
		yield {k:(v.decode('utf8') if (k in unicode_strings and v) else v) for k,v in p.items()}
			
def load_csv(path):
	objs = []
	for p in iter_csv(path):
		objs.append(p)
	return objs

def save_user_data(user_id, path):
	util.assureDirExist(path)
	
	user_filter = {'user_id':user_id}
	save_csv_table(path, 'user', {})
	save_csv_table(path, 'open_planet', user_filter)
	save_csv_table(path, 'race', user_filter)
	save_csv_table(path, 'diplomacy', user_filter)
	save_csv_table(path, 'hw', user_filter)

	save_csv_table(path, 'flying_fleet', user_filter)
	save_csv_table(path, 'flying_alien_fleet', user_filter)
	save_csv_table(path, 'user_planet', user_filter)
	save_csv_table(path, 'fleet', user_filter)
	save_csv_table(path, 'proto', user_filter)
	
	fleet_unit_writer = csv_open( os.path.join(path, 'fleet_unit.csv'), store.keys('fleet_unit'))
	unit_writer = csv_open( os.path.join(path, 'unit.csv'), store.keys('unit'))
	for fleet in store.iter_objects_list('fleet', {'user_id':user_id}):
		for fleet_unit in store.iter_objects_list('fleet_unit', {'fleet_id':fleet['fleet_id']}):
			fleet_unit_writer.writerow(fleet_unit)
			unit_writer.writerow( store.get_object('unit', {'unit_id':fleet_unit['unit_id']}) )
	
	#writer = csv_open(os.path.join(path, 'proto_action.csv'), store.keys('proto_action'))
	#for proto in store.iter_objects_list('proto', user_filter):
	#	for p_action in store.iter_objects_list('proto_action', {'proto_id':proto['proto_id']}):
	#		writer.writerow(p_action)
	
def save_all_data(path):
	util.assureDirExist(path)
	
	save_csv_table(path, 'planet', {})
	save_csv_table(path, 'planet_geo', {})
	save_csv_table(path, 'alien_fleet', {})
	#save_csv_table(path, 'alien_flying_fleet', {})
	#for user in store.iter_objects_list('user', 
	
	
	

import unittest
class TestSaveLoad(unittest.TestCase):
	def setUp(self):
		pass
	
	def test_load_save(self):
		user_id = 3
		user_data = {'user_id':user_id, 'race_id':22, 'name':u'test_user', 'turn':33}
		store.add_user(user_data)
		
		save_user_data(user_id, '/tmp/test')
		
if __name__ == '__main__':
	unittest.main()

