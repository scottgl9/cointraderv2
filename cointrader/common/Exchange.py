# Supported exchanges and modes

class Exchange(object):
    # exchange type
    EXCHANGE_UNKNOWN = 0
    EXCHANGE_CBADV = 1
    EXCHANGE_BINANCE = 2
    EXCHANGE_BITTREX = 3
    EXCHANGE_KRAKEN = 4
    EXCHANGE_POLONIEX = 5
    EXCHANGE_ROBINHOOD = 6
    # account mode
    ACCOUNT_MODE_UNKNOWN = 0
    ACCOUNT_MODE_CRYPTO = 1
    ACCOUNT_MODE_STOCKS = 2
    ACCOUNT_MODE_OPTIONS = 3
    # trader mode
    TRADER_MODE_NONE = 0
    TRADER_MODE_REALTIME = 1
    TRADER_MODE_HOURLY = 2

    def name(id):
        if id == Exchange.EXCHANGE_BINANCE:
            return "binance"
        elif id == Exchange.EXCHANGE_CBADV:
            return "cbadv"
        elif id == Exchange.EXCHANGE_BITTREX:
            return "bittrex"
        elif id == Exchange.EXCHANGE_KRAKEN:
            return "kraken"
        elif id == Exchange.EXCHANGE_POLONIEX:
            return "poloniex"
        elif id == Exchange.EXCHANGE_ROBINHOOD:
            return "robinhood"
        else:
            return "unknown"

    def id(name):
        if name == "binance":
            return Exchange.EXCHANGE_BINANCE
        elif name == "cbadv":
            return Exchange.EXCHANGE_CBADV
        elif name == "bittrex":
            return Exchange.EXCHANGE_BITTREX
        elif name == "kraken":
            return Exchange.EXCHANGE_KRAKEN
        elif name == "poloniex":
            return Exchange.EXCHANGE_POLONIEX
        elif name == "robinhood":
            return Exchange.EXCHANGE_ROBINHOOD
        else:
            return Exchange.EXCHANGE_UNKNOWN

    def account_mode(id):
        if id == Exchange.ACCOUNT_MODE_CRYPTO:
            return "crypto"
        elif id == Exchange.ACCOUNT_MODE_STOCKS:
            return "stocks"
        elif id == Exchange.ACCOUNT_MODE_OPTIONS:
            return "options"
        else:
            return "unknown"
