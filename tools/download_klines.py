import sys
import argparse
from datetime import datetime
#sys.path.append('./tests')
sys.path.append('.')
from cointrader.exchange.TraderSelectExchange import TraderSelectExchange
from cointrader.account.Account import Account
from cointrader.market.Market import Market

CLIENT_NAME = "cbadv"

def main(args):
    print(f"Exchange name: {args.exchange_name}")
    exchange = TraderSelectExchange(args.exchange_name).get_exchange()

    market = Market(exchange=exchange, db_path=args.db_path)
    account = Account(exchange=exchange, market=market)
    account.load_symbol_info()

    symbols = args.symbols.split(',')
    start_ts = int(datetime.fromisoformat(args.start_date).timestamp())

    if args.end_date == 'now':
        end_ts = int(datetime.now().timestamp())
    else:
        end_ts = int(datetime.fromisoformat(args.end_date).timestamp())

    print(f"Start ts: {start_ts} End ts: {end_ts}")
    print(f"Symbols: {symbols}")

    max_klines = market.market_get_max_kline_count(args.granularity)

    increment = args.granularity * max_klines
    print(f"Max klines: {max_klines} Increment: {increment}")
    for symbol in symbols:
        cur_start_ts = start_ts
        print(f"Getting klines for {symbol}")
        while cur_start_ts < end_ts:
            print(f"Getting klines for {symbol} at {cur_start_ts}")
            cur_end_ts = cur_start_ts + args.granularity
            klines = market.market_get_klines_range(symbol, start_ts=cur_start_ts, end_ts=cur_end_ts, granularity=args.granularity, store_db=True)
            print(klines)
            if len(klines) > 0:
                print(f"Klines for {symbol} at {cur_start_ts}: {klines}")
            cur_start_ts += args.granularity

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--exchange-name', type=str, default=CLIENT_NAME, help='Exchange account name to use for simulation')
    parser.add_argument('--db_path', type=str, default='market_data.db', help='Path to the database file')
    parser.add_argument('--symbols', type=str, default='BTC-USD,ETH-USD,SOL-USD', help='Comma separated list of symbols')
    parser.add_argument('--granularity', type=int, default=300)
    parser.add_argument('--start-date', type=str, default='2024-12-02', help='Start date for klines')
    parser.add_argument('--end-date', type=str, default='now', help='End date for klines')
    args = parser.parse_args()

    main(args)
