#!/usr/bin/env python3

import sqlite3

class DB():
	def __init__(self, path='orders.sqlite'):
		self.conn = sqlite3.connect(path)
		self.c = self.conn.cursor()
		self.initialise()
	def initialise(self):
		self.c.execute('''SELECT * FROM `sqlite_master` WHERE `tbl_name` = 'orders' ''')
		if self.c.fetchone() != None:
			return
		query = '''CREATE TABLE `orders`
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
		res = []
		for txid, _, _, _, _, _, _, _ in self.getActive():
			res.append(txid)
		return res
	def getOrders(self, status):
		query = '''SELECT * FROM `orders` WHERE `status` = ?'''
		self.c.execute(query, (status,) )
		return self.c.fetchall()
	def getActive(self):
		return self.getOrders(1)
	def getNew(self):
		return self.getOrders(2)

	def addOrder(self, txid, pair, price, volume, offset, ticker, status, note):
		query = '''INSERT INTO `orders` VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
		self.c.execute(query, (txid, pair, price, volume, offset, ticker, status, note))
	def setOrderStatus(self, txid, status):
		query = '''UPDATE `orders` SET `status` = ? WHERE `txid` = ?'''
		self.c.execute(query, (status, txid))
	def cancelOrder(self, txid):
		self.setOrderStatus(txid, 0)
	def setOrderActive(self, txid):
		self.setOrderStatus(txid, 1)

	@staticmethod
	def parseOrder(order):
		txid, pair, price, volume, offset, ticker, status, note = order
		return (txid, pair, price, volume, offset, ticker, status, note)

if __name__ == "__main__":
	db = DB()

	db.addOrder("TXID-001", "XRPEUR", 0.225, 50, 0.08, "XXRPZEUR", 2, "")
	db.addOrder("TXID-002", "XRPEUR", 0.220, 55, 0.08, "XXRPZEUR", 1, "")

	for order in db.getNew():
		txid, _, _, _, _, _, _, _ = order
		db.setOrderActive(txid)

	tickers_db = []
	for order in db.getActive():
		txid, pair, price, volume, offset, ticker, status, note = order
		tickers_db.append(ticker)
	tickers_db = set(tickers_db)

	print(tickers_db)

	for txid in db.getActiveTxid():
		print(txid)
		db.cancelOrder(txid)

	db.commit()

#	for txid, pair, price, volume, offset, ticker, status, note in db.getNew():
#		print(txid)

# Get active orders from DB
# Get active orders from API
# Inactivate orders in DB not in API
# Make new orders active
# Collect tickers into a set
# Get last price from tickers API
# current = last price - offset
# If last current > price
# Cancel order - or Error it out
# Add new order with price = current
# Update DB
