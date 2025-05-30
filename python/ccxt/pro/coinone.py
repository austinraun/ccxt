# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

import ccxt.async_support
from ccxt.async_support.base.ws.cache import ArrayCache
from ccxt.base.types import Any, Int, Market, OrderBook, Ticker, Trade
from ccxt.async_support.base.ws.client import Client
from typing import List
from ccxt.base.errors import AuthenticationError


class coinone(ccxt.async_support.coinone):

    def describe(self) -> Any:
        return self.deep_extend(super(coinone, self).describe(), {
            'has': {
                'ws': True,
                'watchOrderBook': True,
                'watchOrders': False,
                'watchTrades': True,
                'watchTradesForSymbols': False,
                'watchOHLCV': False,
                'watchTicker': True,
                'watchTickers': False,
            },
            'urls': {
                'api': {
                    'ws': 'wss://stream.coinone.co.kr',
                },
            },
            'options': {
                'expiresIn': '',
                'userId': '',
                'wsSessionToken': '',
                'watchOrderBook': {
                    'snapshotDelay': 6,
                    'snapshotMaxRetries': 3,
                },
                'tradesLimit': 1000,
                'OHLCVLimit': 1000,
            },
            'exceptions': {
                'exact': {
                    '4009': AuthenticationError,
                },
            },
            'streaming': {
                'ping': self.ping,
                'keepAlive': 20000,
            },
        })

    async def watch_order_book(self, symbol: str, limit: Int = None, params={}) -> OrderBook:
        """
        watches information on open orders with bid(buy) and ask(sell) prices, volumes and other data

        https://docs.coinone.co.kr/reference/public-websocket-orderbook

        :param str symbol: unified symbol of the market to fetch the order book for
        :param int [limit]: the maximum amount of order book entries to return
        :param dict [params]: extra parameters specific to the exchange API endpoint
        :returns dict: A dictionary of `order book structures <https://docs.ccxt.com/#/?id=order-book-structure>` indexed by market symbols
        """
        await self.load_markets()
        market = self.market(symbol)
        messageHash = 'orderbook:' + market['symbol']
        url = self.urls['api']['ws']
        request: dict = {
            'request_type': 'SUBSCRIBE',
            'channel': 'ORDERBOOK',
            'topic': {
                'quote_currency': market['quote'],
                'target_currency': market['base'],
            },
        }
        message = self.extend(request, params)
        orderbook = await self.watch(url, messageHash, message, messageHash)
        return orderbook.limit()

    def handle_order_book(self, client, message):
        #
        #     {
        #         "response_type": "DATA",
        #         "channel": "ORDERBOOK",
        #         "data": {
        #             "quote_currency": "KRW",
        #             "target_currency": "BTC",
        #             "timestamp": 1705288918649,
        #             "id": "1705288918649001",
        #             "asks": [
        #                 {
        #                     "price": "58412000",
        #                     "qty": "0.59919807"
        #                 }
        #             ],
        #             "bids": [
        #                 {
        #                     "price": "58292000",
        #                     "qty": "0.1045"
        #                 }
        #             ]
        #         }
        #     }
        #
        data = self.safe_value(message, 'data', {})
        baseId = self.safe_string_upper(data, 'target_currency')
        quoteId = self.safe_string_upper(data, 'quote_currency')
        base = self.safe_currency_code(baseId)
        quote = self.safe_currency_code(quoteId)
        symbol = self.symbol(base + '/' + quote)
        timestamp = self.safe_integer(data, 'timestamp')
        orderbook = self.safe_value(self.orderbooks, symbol)
        if orderbook is None:
            orderbook = self.order_book()
        else:
            orderbook.reset()
        orderbook['symbol'] = symbol
        asks = self.safe_value(data, 'asks', [])
        bids = self.safe_value(data, 'bids', [])
        self.handle_deltas(orderbook['asks'], asks)
        self.handle_deltas(orderbook['bids'], bids)
        orderbook['timestamp'] = timestamp
        orderbook['datetime'] = self.iso8601(timestamp)
        messageHash = 'orderbook:' + symbol
        self.orderbooks[symbol] = orderbook
        client.resolve(orderbook, messageHash)

    def handle_delta(self, bookside, delta):
        bidAsk = self.parse_bid_ask(delta, 'price', 'qty')
        bookside.storeArray(bidAsk)

    async def watch_ticker(self, symbol: str, params={}) -> Ticker:
        """
        watches a price ticker, a statistical calculation with the information calculated over the past 24 hours for a specific market

        https://docs.coinone.co.kr/reference/public-websocket-ticker

        :param str symbol: unified symbol of the market to fetch the ticker for
        :param dict [params]: extra parameters specific to the exchange API endpoint
        :returns dict: a `ticker structure <https://docs.ccxt.com/#/?id=ticker-structure>`
        """
        await self.load_markets()
        market = self.market(symbol)
        messageHash = 'ticker:' + market['symbol']
        url = self.urls['api']['ws']
        request: dict = {
            'request_type': 'SUBSCRIBE',
            'channel': 'TICKER',
            'topic': {
                'quote_currency': market['quote'],
                'target_currency': market['base'],
            },
        }
        message = self.extend(request, params)
        return await self.watch(url, messageHash, message, messageHash)

    def handle_ticker(self, client: Client, message):
        #
        #     {
        #         "response_type": "DATA",
        #         "channel": "TICKER",
        #         "data": {
        #             "quote_currency": "KRW",
        #             "target_currency": "BTC",
        #             "timestamp": 1705301117198,
        #             "quote_volume": "19521465345.504",
        #             "target_volume": "334.81445168",
        #             "high": "58710000",
        #             "low": "57276000",
        #             "first": "57293000",
        #             "last": "58532000",
        #             "volume_power": "100",
        #             "ask_best_price": "58537000",
        #             "ask_best_qty": "0.1961",
        #             "bid_best_price": "58532000",
        #             "bid_best_qty": "0.00009258",
        #             "id": "1705301117198001",
        #             "yesterday_high": "59140000",
        #             "yesterday_low": "57273000",
        #             "yesterday_first": "58897000",
        #             "yesterday_last": "57301000",
        #             "yesterday_quote_volume": "12967227517.4262",
        #             "yesterday_target_volume": "220.09232233"
        #         }
        #     }
        #
        data = self.safe_value(message, 'data', {})
        ticker = self.parse_ws_ticker(data)
        symbol = ticker['symbol']
        self.tickers[symbol] = ticker
        messageHash = 'ticker:' + symbol
        client.resolve(self.tickers[symbol], messageHash)

    def parse_ws_ticker(self, ticker, market: Market = None) -> Ticker:
        #
        #     {
        #         "quote_currency": "KRW",
        #         "target_currency": "BTC",
        #         "timestamp": 1705301117198,
        #         "quote_volume": "19521465345.504",
        #         "target_volume": "334.81445168",
        #         "high": "58710000",
        #         "low": "57276000",
        #         "first": "57293000",
        #         "last": "58532000",
        #         "volume_power": "100",
        #         "ask_best_price": "58537000",
        #         "ask_best_qty": "0.1961",
        #         "bid_best_price": "58532000",
        #         "bid_best_qty": "0.00009258",
        #         "id": "1705301117198001",
        #         "yesterday_high": "59140000",
        #         "yesterday_low": "57273000",
        #         "yesterday_first": "58897000",
        #         "yesterday_last": "57301000",
        #         "yesterday_quote_volume": "12967227517.4262",
        #         "yesterday_target_volume": "220.09232233"
        #     }
        #
        timestamp = self.safe_integer(ticker, 'timestamp')
        last = self.safe_string(ticker, 'last')
        baseId = self.safe_string(ticker, 'target_currency')
        quoteId = self.safe_string(ticker, 'quote_currency')
        base = self.safe_currency_code(baseId)
        quote = self.safe_currency_code(quoteId)
        symbol = self.symbol(base + '/' + quote)
        return self.safe_ticker({
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_string(ticker, 'high'),
            'low': self.safe_string(ticker, 'low'),
            'bid': self.safe_number(ticker, 'bid_best_price'),
            'bidVolume': self.safe_number(ticker, 'bid_best_qty'),
            'ask': self.safe_number(ticker, 'ask_best_price'),
            'askVolume': self.safe_number(ticker, 'ask_best_qty'),
            'vwap': None,
            'open': self.safe_string(ticker, 'first'),
            'close': last,
            'last': last,
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': self.safe_string(ticker, 'target_volume'),
            'quoteVolume': self.safe_string(ticker, 'quote_volume'),
            'info': ticker,
        }, market)

    async def watch_trades(self, symbol: str, since: Int = None, limit: Int = None, params={}) -> List[Trade]:
        """
        watches information on multiple trades made in a market

        https://docs.coinone.co.kr/reference/public-websocket-trade

        :param str symbol: unified market symbol of the market trades were made in
        :param int [since]: the earliest time in ms to fetch trades for
        :param int [limit]: the maximum number of trade structures to retrieve
        :param dict [params]: extra parameters specific to the exchange API endpoint
        :returns dict[]: a list of `trade structures <https://docs.ccxt.com/#/?id=trade-structure>`
        """
        await self.load_markets()
        market = self.market(symbol)
        messageHash = 'trade:' + market['symbol']
        url = self.urls['api']['ws']
        request: dict = {
            'request_type': 'SUBSCRIBE',
            'channel': 'TRADE',
            'topic': {
                'quote_currency': market['quote'],
                'target_currency': market['base'],
            },
        }
        message = self.extend(request, params)
        trades = await self.watch(url, messageHash, message, messageHash)
        if self.newUpdates:
            limit = trades.getLimit(market['symbol'], limit)
        return self.filter_by_since_limit(trades, since, limit, 'timestamp', True)

    def handle_trades(self, client: Client, message):
        #
        #     {
        #         "response_type": "DATA",
        #         "channel": "TRADE",
        #         "data": {
        #             "quote_currency": "KRW",
        #             "target_currency": "BTC",
        #             "id": "1705303667916001",
        #             "timestamp": 1705303667916,
        #             "price": "58490000",
        #             "qty": "0.0008",
        #             "is_seller_maker": False
        #         }
        #     }
        #
        data = self.safe_value(message, 'data', {})
        trade = self.parse_ws_trade(data)
        symbol = trade['symbol']
        stored = self.safe_value(self.trades, symbol)
        if stored is None:
            limit = self.safe_integer(self.options, 'tradesLimit', 1000)
            stored = ArrayCache(limit)
            self.trades[symbol] = stored
        stored.append(trade)
        messageHash = 'trade:' + symbol
        client.resolve(stored, messageHash)

    def parse_ws_trade(self, trade: dict, market: Market = None) -> Trade:
        #
        #     {
        #         "quote_currency": "KRW",
        #         "target_currency": "BTC",
        #         "id": "1705303667916001",
        #         "timestamp": 1705303667916,
        #         "price": "58490000",
        #         "qty": "0.0008",
        #         "is_seller_maker": False
        #     }
        #
        baseId = self.safe_string_upper(trade, 'target_currency')
        quoteId = self.safe_string_upper(trade, 'quote_currency')
        base = self.safe_currency_code(baseId)
        quote = self.safe_currency_code(quoteId)
        symbol = base + '/' + quote
        timestamp = self.safe_integer(trade, 'timestamp')
        market = self.safe_market(symbol, market)
        isSellerMaker = self.safe_value(trade, 'is_seller_maker')
        side = None
        if isSellerMaker is not None:
            side = 'sell' if isSellerMaker else 'buy'
        priceString = self.safe_string(trade, 'price')
        amountString = self.safe_string(trade, 'qty')
        return self.safe_trade({
            'id': self.safe_string(trade, 'id'),
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'order': None,
            'symbol': market['symbol'],
            'type': None,
            'side': side,
            'takerOrMaker': None,
            'price': priceString,
            'amount': amountString,
            'cost': None,
            'fee': None,
        }, market)

    def handle_error_message(self, client: Client, message):
        #
        #     {
        #         "response_type": "ERROR",
        #         "error_code": 160012,
        #         "message": "Invalid Topic"
        #     }
        #
        type = self.safe_string(message, 'response_type', '')
        if type == 'ERROR':
            return True
        return False

    def handle_message(self, client: Client, message):
        if self.handle_error_message(client, message):
            return
        type = self.safe_string(message, 'response_type')
        if type == 'PONG':
            self.handle_pong(client, message)
            return
        if type == 'DATA':
            topic = self.safe_string(message, 'channel', '')
            methods: dict = {
                'ORDERBOOK': self.handle_order_book,
                'TICKER': self.handle_ticker,
                'TRADE': self.handle_trades,
            }
            exacMethod = self.safe_value(methods, topic)
            if exacMethod is not None:
                exacMethod(client, message)
                return
            keys = list(methods.keys())
            for i in range(0, len(keys)):
                key = keys[i]
                if topic.find(keys[i]) >= 0:
                    method = methods[key]
                    method(client, message)
                    return

    def ping(self, client: Client):
        return {
            'request_type': 'PING',
        }

    def handle_pong(self, client: Client, message):
        #
        #     {
        #         "response_type":"PONG"
        #     }
        #
        client.lastPong = self.milliseconds()
        return message
