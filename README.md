# Kraken Trailing Bot

DISCLAIMER: I am not responsible for your lost money. I have lost **LOADS** of money with this, bugs can potentially cost you dearly. You have been warned.

This bot takes a currency pair and an amount to trade and an "offset". It monitors the market and manages a stop-loss trade which is maintained no lower than the peak - some offset.

This means you can have a stop loss order but take advantages of gains.

### Issues

* I'm not entirely sure the database mangement works, you might be better off deleting `orders.sqlite` if all the orders are done
* Really needs cleaning up
* I think there are race conditions in the orders being dealt with
* State -1 (error) is not yet implemented.
* Buy and take-profit types would also be good.

### Usage

Typically trialing stop-loss orders are used when you already have some gains. Add to the sqlite db a new order (status = 2) with the amount, currency pair and ticker symbol etc.

Now the bot should make a stop-loss sell order at the last price - offset and with each run will monitor it.


## Dependencies
* [Krakenex](https://github.com/veox/python3-krakenex)
	* requests
* Sqlite3

### License

GPLv3
