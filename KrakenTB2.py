#!/usr/bin/env python3

# Copyright Ali Raheem 2019
# GPLv3

import sqlite3, krakenex, datetime, sys

class DB():
	def __init__(self, path='orders.sqlite'):
		self.conn = sqlite3.connect(path)
		self.c = self.conn.cursor()
		self.initialise()
	def initialise(self):
		query = '''CREATE TABLE IF NOT EXISTS `orders`
				(txid TEXT,
				pair TEXT,
				price REAL,
				volume REAL,
				offset REAL,
				ticker TEXT,
				status INTEGER,
				note TEXT)'''
		self.c.execute(query)
	def commit(self):
		self.conn.commit()
	def getActiveTxid(self):
		return getTxid(self.getActive())
	def getNewTxid(self):
		return getTxid(self.getNew())

	def getOrders(self, status):
		query = '''SELECT * FROM `orders` WHERE `status` = ?'''
		self.c.execute(query, (status,) )
		return self.c.fetchall()
	def getActive(self):
		return self.getOrders(1)
	def getNew(self):
		return self.getOrders(2)

	def setNewActive(self):
		query = '''UPDATE `orders` SET `status` = 1 WHERE `status` = 2'''
		self.c.execute(query)

	def addOrder(self, txid, pair, price, volume, offset, ticker, status, note):
		query = '''INSERT INTO `orders` VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
		self.c.execute(query, (txid, pair, price, volume, offset, ticker, status, note))

	def cancelOrder(self, txid):
		self.setOrderStatus(txid, 0)
	def setOrderActive(self, txid):
		self.setOrderStatus(txid, 1)
	def setOrderStatus(self, txid, status):
		query = '''UPDATE `orders` SET `status` = ? WHERE `txid` = ?'''
		self.c.execute(query, (status, txid))

def getTickers(orders):
	res = []
	for _, _, _, _, _, ticker, _, _ in orders:
		res.append(ticker)
	return res
def getTxid(orders):
	res = []
	for txid, _, _, _, _, _, _, _ in orders:
		res.append(txid)
	return res

class API():
	def __init__(self, keyfile="kraken.key"):
		self.k = krakenex.API()
		self.k.load_key(keyfile)
	def getTicker(self, tickers):
		res = self.k.query_public('Ticker', {'pair': ','.join(tickers)})
		if len(res['error']) == 0:
			return res['result']
		raise Exception(res['error'][0])
	def getOpenOrders(self):
		return list(self.k.query_private('OpenOrders', {'trades': False})['result']['open'].keys())
	def cancelOrder(self, txid):
		if txid == None:
 			return None
		return self.k.query_private('CancelOrder', {'txid': txid})
	def addOrder(self, pair, price, volume):
		response = self.k.query_private('AddOrder', {
                                                'pair': pair,
                                                'type': 'sell',
                                                'ordertype': 'stop-loss',
                                                'price': price,
                                                'volume': volume})
		if len(response['error']) == 0:
			return response['result']['txid'][0]
		else:
			raise Exception(response['error'][0])
	def close(self):
		self.k.close()

if __name__ == "__main__":
	db = DB()
	api = API()

	print(datetime.datetime.now().strftime("%Y-%l-%d %H:%M:%S"))

# TODO: This should be handled by command line arguments.
# 	Maybe we can also pass active orders to start with,
#	of different inital offset and maintainence offset
#	db.addOrder("", "XRPEUR", 0, 50, 0.008, "XXRPZEUR", 2, "")

	active_orders_api = set(api.getOpenOrders())
	active_orders_db = set(db.getActiveTxid())
	stale_orders = active_orders_db - active_orders_api

	for order in stale_orders:
		print("Cancelling stale order", order)
		db.cancelOrder(order)

	db.commit() # Commit inactivating stale orders.


	db.setNewActive()

	active_tickers = set(getTickers(db.getActive()))
	if len(active_tickers) == 0:
		print("No orders to process.\nQuitting.")
		db.commit()
		api.close()
		sys.exit()
	prices = getTicker(active_tickers)


	print("Active Orders\n=============================")
	for txid, pair, price, volume, offset, ticker, status, note in db.getActive():
		close_price = round(float(prices[ticker]['c'][0]), 5)
		print(txid, "pair:", pair, "Stop price:", price, "volume:", volume)
		current_price = round(close_price - offset, 5)
		print("Close price:", close_price, "New stop:", current_price)
		if current_price > price: # TODO: Move this out to an evaluation function to allow buy and sell and more complex evaluation.
			print("Replaceing order", txid)
			api.cancelOrder(txid) # TODO: Handle errors here with an error status and note.
# TODO: I think the order shouldn't be cancelled but held in another status,
# 	which will automtically be readded next run.
			db.cancelOrder(txid) # Should we commit this?
			txid = api.addOrder(pair, current_price, volume)
			db.addOrder(txid, pair, current_price, volume, offset, ticker, 1, note)
			db.commit() # Commit each successfully added order.
		else:
			print("Keeping", txid)
		print("----------------------------------------------")

	print()
	db.commit()
	api.close()

