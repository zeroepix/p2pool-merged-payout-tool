#!/usr/bin/env python
import json, urllib2, sys
from bitcoinrpc.authproxy import AuthServiceProxy

def get_proportional_hash_area(period):
	""" 	Takes in periods accepted by P2Pool - hour, day, week, month or year,
		then gets hash_data from the server running on localhost, parses it, 
		and calculates each miner's hash power against the total during that time. 
	"""
	import urllib2, json
	path1 = 'http://localhost:9332/web/graph_data/miner_hash_rates/last_'+period
	result1 = json.load(urllib2.urlopen(path1))
	path2 = 'http://localhost:9332/web/graph_data/miner_dead_hash_rates/last_'+period
	result2 = json.load(urllib2.urlopen(path2))
	
	hash_areas = {}
	total_hash_area = 0
	for row in result1:
		for address in row[1]:
			try:
				hash_areas[address] += row[1][address] * row[2]
			except KeyError:
				hash_areas[address] = row[1][address] * row[2]
			finally:
				total_hash_area += row[1][address] * row[2]
	
	for row in result2:
		for address in row[1]:
			hash_areas[address] -= row[1][address]*row[2]
			total_hash_area -= row[1][address] * row[2]

	proportions = {}	
	for address in hash_areas.keys():
		proportions[address] = hash_areas[address] / total_hash_area
		hash_areas[address] /= 1000000000000000
	
	return hash_areas, proportions

def get_quotes():
	"""	Gets btc per altcoin price for dvc, nmc and ixc from cryptys, and i0c from vircurex
	"""
	quotes = {'devcoin': {'code': 'DVC', 'id':40}, 'namecoin': {'code': 'NMC', 'id':29}, 'ixcoin': {'code':'IXC', 'id':38}}
	path = 'http://pubapi.cryptsy.com/api.php?method=singleorderdata&marketid='
	try:
		for key, value in quotes.iteritems():
			result = json.load(urllib2.urlopen(path+str(value['id'])))
			quotes[key]['price'] = result['return'][value['code']]['buyorders'][0]['price']
	except:
		raise
	
	# i0coin quotes from vircurex
	path = 'https://api.vircurex.com/api/get_last_trade.json?base=I0C&alt=BTC'
	try:
		req = urllib2.Request(path, headers={'User-Agent':"Magic Browser"})
		con = urllib2.urlopen(req)
		result = json.load(con)
		if result['value'] != None:
			quotes['i0coin'] = {'code': 'I0C', 'id':-1, 'price':result['value']}
	except:
		raise
	return quotes

def run(period, debug):
	miners, proportions = get_proportional_hash_area(period)

	if debug: print miners	

	with open('config', 'r') as f:
		config = json.load(f)

	# once we've read in the file, we need to:
	# load each with its own access point
	# get the balance of each
	
	coins = {}

	for coin, settings in config.iteritems():
		coins[coin] = {'access': AuthServiceProxy("http://%s:%s@%s:%s/" % (settings['rpcuser'], settings['rpcpass'], settings['rpcserver'], settings['rpcport']))}
		coins[coin]['balance'] = coins[coin]['access'].getbalance()	

	if debug: print coins
	
	prices = get_quotes()
	
	if debug: print prices

	# time to calculate the individual payouts
	
	# print current balances and their market rates / value
	print "Coin\tBalance\t\tMarket\n\t\t\tRate(btc)\tValue(btc)"
	total_value = 0.0
	for coin, balance in coins.iteritems():
		rate = float(prices[coin]['price'])
		value = rate * float(balance['balance'])
		total_value += value
		print "%s\t%.8f\t%.8f\t%.8f" % (prices[coin]['code'], balance['balance'], rate, value)

	print "----------------------------------------------------"
	print "Total\t\t\t\t\t%.8f btc\n" % total_value

	# print miners, their total hashpower and their percentage of hash power
	print "Miner\t\t\t\t\tPercentage of\tTotal Petahash\naddress\t\t\t\t\thash_power\t(%s)\n" % period
	for address, area in miners.iteritems():
		print "%s\t%.3f%%\t\t%.4f" % (address, proportions[address]*100, area)

	# print payout due converted to each coin
	total_dvc = 1/float(prices['devcoin']['price']) * total_value
	total_nmc = 1/float(prices['namecoin']['price']) * total_value
	total_ixc = 1/float(prices['ixcoin']['price']) * total_value
	total_i0c = 1/float(prices['i0coin']['price']) * total_value
	print "\nPayout due (converted into each coin for convenience)"
	print "Miner\t\t\t\t\tbtc\tdvc\tnmc\tixc\ti0c"
	for address, proportion in proportions.iteritems():
		print "%s\t%.8f\t%.8f\t%.8f\t%.8f\t%.8f" % (address, proportion*total_value, proportion*total_dvc, proportion*total_nmc, proportion*total_ixc, proportion*total_i0c)
	
if __name__ == "__main__":
	debug = False
	period = 'month'
	if len(sys.argv) > 1:
		if "-d" in sys.argv: debug = True
		if "-hour" in sys.argv: period = 'hour'
		elif "-day" in sys.argv: period = 'day'
		elif "-week" in sys.argv: period = 'week'
		elif "-year" in sys.argv: period = 'year'
		
	run(period, debug)
