# coding: utf-8


def parse_price(exchange, data):
	if exchange == 'huobi':
		return _parse_huobi(data)
	elif exchange == 'okex':
		return _parse_okex(data)
	elif exchange == 'binance':
		return _parse_binance(data)
	elif exchange == 'bitfinex':
		return _parse_bitfinex(data)
	elif exchange == 'bibox':
		return _parse_bibox(data)
	elif exchange == 'zb':
		return _parse_zb(data)
	elif exchange == 'bigone':
		return _parse_bigone(data)
	elif exchange == 'kucoin':
		return _parse_kucoin(data)
	elif exchange == 'fcoin':
		return  _parse_kucoin(data)
	elif exchange == 'binmex':
		return _parse_binmex(data)
	elif exchange == 'otcbtc':
		return _parse_otcbtc(data)
	else:
		pass
	pass


def _parse_huobi(data):
	price = None
	return price
	pass


def _parse_okex(data):
	price = None
	return price
	pass


def _parse_binance(data):
	price = None
	return price
	pass


def _parse_bitfinex(data):
	price = None
	return price
	pass


def _parse_bibox(data):
	price = None
	return price
	pass


def _parse_zb(data):
	price = None
	return price
	pass


def _parse_bigone(data):
	price = None
	return price
	pass


def _parse_kucoin(data):
	price = None
	return price
	pass


def _parse_fcoin(data):
	price = None
	return price
	pass


def _parse_binmex(data):
	price = None
	return price
	pass


def _parse_otcbtc(data):
	price = None
	return price
	pass
