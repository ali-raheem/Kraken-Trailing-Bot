# Kraken Trailing Bot

DISCLAIMER: I am not responsible for your lost money, or any trouble you get into to.
I have lost **LOADS** of money with this, bugs can potentially cost you dearly.
You have been warned.

## Description

This bot takes a currency pair and an amount to trade and an "offset". It monitors the market and manages a stop-loss trade which is maintained no lower than the peak - some offset.

This means you can have a stop loss order but take advantages of gains.

Please familiarise yourself with the [Kraken API docs](https://www.kraken.com/features/api). **Especially** the [call rate limit](https://www.kraken.com/features/api#api-call-rate-limit) which is part of the how not to be banned rules! Don't annoy Kraken with this.

## Issues

Not a complete list:

* I'm not entirely sure the database mangement works, you might be better off deleting `orders.sqlite` if all the orders are done
* Really needs cleaning up
* I think there are race conditions in the orders being dealt with
* State -1 (error) is not yet implemented.
* Buy and take-profit types would also be good.

## TODO

Issues I really care about

* Make it take command line arguments to add new orders?
* Make it more failsafe see note in code.
* Web monitor?

## Dependencies
* [Krakenex](https://github.com/veox/python3-krakenex)
  * requests

* Sqlite3

## Usage

Typically trialing stop-loss orders are used when you already have some gains. Add to the sqlite db a new order (status = 2) with the amount, currency pair and ticker symbol etc.

Now the bot should make a stop-loss sell order at the last price - offset and with each run will monitor it.

**You must have** an API key which allows trading. Duh!. Put this key in `kraken.key` `key` on the first line and then the `secret` on the second line. See the Krakenex library for more details.

## Running

This is how I run on my Raspbian:

```sh
while true; do
	python3 KrakenTB2.py
	sleep 15
done
```

I'm pretty sure it could run much more often as the only API call to raise the rate counter is OpenOrders (I think this raises it 1).

## License

GPLv3
