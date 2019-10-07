#!/usr/bin/env python3

import krakenex, sqlite3, time

class API():
	def __init__(self, k):
		self.k = k
	def getTicker(self, pair):
		try:
			res = self.k.query_public('Ticker', {'pair': pair})
			res = res['result'][pair]
			price, volume = res['c']
			return (float(price), float(volume))
		except KeyError:
			return None
	def getSkew(self):
		return self.k.query_public('Time')
	def getOpenOrders(self):
		return self.k.query_private('OpenOrders', {'trades': True})
	def cancelOrder(self, txid):
		if txid == None:
			return None
		return self.k.query_private('CancelOrder', {'txid': txid})
	def addStopLoss(self, pair, type, price, volume):
		response = self.k.query_private('AddOrder', {
						'pair': pair,
						'type': type,
						'ordertype': 'stop-loss',
						'price': price,
						'volume': volume})
		if len(response['error']) == 0:
			return response['result']['txid'][0]
		else:
			raise Exception(response['error'][0])
class DB():
	def __init__(self, path='orders.db'):
		self.conn = sqlite3.connect(path)
		self.c = self.conn.cursor()
		query = "SELECT name FROM sqlite_master WHERE type='table' AND name='orders'"
		if self.c.execute(query) == None:
			self.init()
	def init(self):
		self.c.execute('''CREATE TABLE orders
				(datetime text, pair text, ticker text, volume real,
				price real, offset real, type text, txid text)''')
		self.commit()
	def createOrder(self, pair, ticker, volume, price, offset, type):
		# API create order get datetime and txid
		datetime = ''
		txid = ''
		self.c.execute('''INSERT INTO orders VALUES
				(datetime, pair, volume, price, ticker, offset, type, txid)''')
		self.commit()
	def commit(self):
		self.conn.commit()
	def close(self):
		self.conn.close()
def main():
	txid = None
	stop_price = 0
	offset = 0.004
	amount = 100

	kapi = krakenex.API()
	kapi.load_key('kraken.key')
	k = API(kapi)
	db = DB('test.db')
	while True:
		price, volume = k.getTicker('XXRPZEUR')
		print("Price:", price, " Volume:", volume)
		cur_price =  float("%.5f"%(price - offset))
		if cur_price > stop_price:
			stop_price = cur_price
			k.cancelOrder(txid)
			print("Order at", stop_price, "for", amount)
			txid = k.addStopLoss('XRPEUR', 'sell', str(cur_price), str(amount))
			print("New TxID:", txid)
		time.sleep(5)

if __name__ == "__main__":
	main()
