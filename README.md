# Kraken Trailing Bot

This bot takes a currency pair and an amount to trade and an "offset". It monitors the market and manages a stop-loss trade which is maintained no lower than the peak - some offset.

This means you can have a stop loss order but take advantages of gains.

## Dependencies
* [Krakenex](https://github.com/veox/python3-krakenex)
	* requests
* Sqlite3

### License

GPLv3
