#!/usr/bin/env python3
# This script is to determine the optimal strategy weights for a given set of strategies.
import logging
from coinbase.websocket import WSClient, WebsocketResponse
#from coinbase.rest import RESTExchange
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
from threading import Thread
from threading import RLock
import json
import sys
import time
import argparse
import itertools

try:
    import cointrader
except ImportError:
    sys.path.append('.')

import pandas as pd

from cointrader.exchange.TraderSelectExchange import TraderSelectExchange
from cointrader.account.AccountSimulate import AccountSimulate
from cointrader.execute.TradeExecuteSimulate import TraderExecuteSimulate
from cointrader.execute.pipeline.ExecutePipeline import ExecutePipeline
from cointrader.market.Market import Market
from cointrader.trade.MultiTrader import MultiTrader
from cointrader.trade.TraderConfig import TraderConfig
from cointrader.order.Orders import Orders
from cointrader.common.Kline import Kline
from cointrader.common.LogLevel import LogLevel
from cointrader.config import *
from cointrader.indicators.EMA import EMA
from cointrader.common.KlineEmitter import KlineEmitter
from concurrent.futures import ThreadPoolExecutor

class PipelineExecutionThread(Thread):
    def __init__(self, exec_pipe: ExecutePipeline):
        Thread.__init__(self)
        self._exec_pipe = exec_pipe

    def run(self):
        while True:
            self._exec_pipe.process_order_requests()
            time.sleep(1 / 1000) # sleep for 1ms

def run_trader(exchange: str, symbols: list[str], df: pd.DataFrame, initial_usdt: float, strategy_weights: dict[str, float] = None, count=0, name=""):
    tconfig = TraderConfig(path=f'config/{name}_trader_simulate_csv_config.json')
    if not tconfig.load_config():
        print(f"Failed to load config {tconfig.get_config_path()}")
        tconfig.save_config()
    else:
        #print(f"Loaded config {tconfig.get_config_path()}")
        pass

    tconfig.set_trade_symbols(symbols)

    if args.strategy and tconfig.strategy() != args.strategy:
        tconfig.set_strategy(args.strategy)

    #print(f"Using strategy: {tconfig.strategy()} db_path: {tconfig.orders_db_path()}")

    tconfig.set_log_level(LogLevel.NONE.value)

    granularity = tconfig.granularity()

    market = Market(exchange=exchange, db_path=None)#tconfig.market_db_path())
    account = AccountSimulate(exchange=exchange, market=market)
    account.load_symbol_info()
    account.load_asset_info()

    account.update_asset_balance("USDT", available=initial_usdt, hold=0.0)
    tconfig.set_global_current_balance_quote(balance=initial_usdt)

    if tconfig.log_level() >= LogLevel.INFO.value:
        print(account.get_account_balances())
        print("Start Total USDT Balance:")
        print(account.get_total_balance("USDT"))

    ex = TraderExecuteSimulate(exchange=exchange, account=account, config=tconfig)

    exec_pipe_threaded = False
    ep = ExecutePipeline(execute=ex, max_orders=100, threaded=exec_pipe_threaded)

    orders = Orders(config=tconfig, db_path=None, reset=True) #f"{tconfig.orders_db_path()}{count}", reset=True)

    mtrader = MultiTrader(account=account, exec_pipe=ep, config=tconfig, orders=orders, restore_positions=False, granularity=granularity, strategy_weights=strategy_weights)

    # update quote balance before trying to open positions
    mtrader.market_update_quote_balance(quote_name=tconfig.quote_currency())

    kline = Kline()
    #kline.set_dict_names(ts='start')

    first_prices = {}
    last_prices = {}

    kline_emitters: dict[str, KlineEmitter] = {}

    # emitter takes in hourly klines, and emits daily klines
    for symbol in symbols:
        kline_emitters[symbol] = KlineEmitter(src_granularity=granularity, dst_granularity=86400)

    #kline_emitter = KlineEmitter(src_granularity=granularity, dst_granularity=86400)

    # create thread
    if exec_pipe_threaded:
        exec_pipe_thread = PipelineExecutionThread(exec_pipe=ep)
        exec_pipe_thread.daemon = True
        exec_pipe_thread.start()


    found = False

    # iterate through all rows in the DataFrame
    for index, row in df.iterrows():
        if index >= 100000:
            if not found:
                position_count = 0
                for symbol in symbols:
                    position_count += mtrader.total_position_count(symbol)
                if position_count == 0:
                    #print(f"Exiting at index {index} with no positions")
                    break
                #print(f"{count} strategy_weights={strategy_weights}")
                found = True

        symbol = row['Symbol']
        if symbol in symbols:
            kline_data = {
                'ts': row['Timestamp'],
                'open': row['Open'],
                'high': row['High'],
                'low': row['Low'],
                'close': row['Close'],
                'volume': row['Volume USDT']
            }

            if symbol not in first_prices:
                first_prices[symbol] = kline_data['close']

            #print(kline_data)
            kline.from_dict(kline_data)
            kline.symbol = symbol
            kline.granularity = granularity

            # emit daily klines
            kline_emitter = kline_emitters[symbol]
            kline_emitter.update(kline)
            if kline_emitter.ready():
                kline_daily = kline_emitter.emit()
                if kline:
                    kline_daily.symbol = symbol
                    kline_daily.granularity = kline_emitter.granularity()
                    #mtrader.market_update(symbol=symbol, kline=kline, current_price=kline.close, current_ts=kline.ts, granularity=kline_emitter.granularity())
                    mtrader.market_update_kline_other_timeframe(symbol=symbol, kline=kline_daily, granularity=kline_emitter.granularity())

            mtrader.market_update_kline(symbol=symbol, kline=kline, granularity=granularity)

            # update quote balance before trying to open positions
            mtrader.market_update_quote_balance(quote_name=tconfig.quote_currency())

            mtrader.market_update_price(symbol=symbol, current_price=kline.close, current_ts=kline.ts, granularity=granularity)
            last_prices[symbol] = kline_data['close']

    #orders.commit()
    if tconfig.log_level() >= LogLevel.INFO.value:
        print(orders.get_active_orders(symbol=None))

    position_count = 0
    for symbol in symbols:
        position_count += mtrader.total_position_count(symbol)
    if position_count != 0:
        print(f"{count} strategy_weights={strategy_weights}")

    return mtrader, first_prices, last_prices


def main(args):
    name = args.exchange
    initial_usdt = args.initial_usdt

    exchange = TraderSelectExchange(name).get_exchange()

    symbols = args.symbols.split(',')

    start_ts = int(datetime.fromisoformat(args.start_date).timestamp())
    if args.end_date == 'now':
        end_ts = int(datetime.now().timestamp())
    else:
        end_ts = int(datetime.fromisoformat(args.end_date).timestamp())

    df = pd.read_csv(args.csv_path)

    # print all unique strings from the Symbols column
    unique_symbols = df['Symbol'].unique()
    print("Symbols:", unique_symbols)

    # Convert the Date column to datetime format
    df['Date'] = pd.to_datetime(df['Date'], format='mixed') #'%Y-%m-%d %H:%M:%S')
    # Convert the Date column to unix timestamp
    df['Timestamp'] = df['Date'].apply(lambda x: int(x.timestamp()))
    # Sort the DataFrame by the Date column
    df = df.sort_values(by='Date').reset_index(drop=True)
    # Convert all symbols ending with 'USDT' to '-USDT'
    df['Symbol'] = df['Symbol'].apply(lambda x: x.replace('USDT', '-USDT'))
    # Display the first few rows of the DataFrame
    print(df.head())

    # Filter the DataFrame by the Timestamp column
    df = df[(df['Timestamp'] >= start_ts) & (df['Timestamp'] <= end_ts)]

    # generate weights for strategies
    strategy_weights = {
                'macd': 0,
                'sama': 0,
                'zlema': 0,
                'rsi': 0,
                'stochastic': 0,
                'ema': 0,
                'sma': 0,
                'supertrend': 0.8,
                'adx': 0,
                'squeeze': 0,
                'roc': 0,
                'psar': 0,
                'vwap': 0,
                'ppo': 0,
                'cmf': 0,
                'cci': 0,
                'ao': 0,
                'uo': 0,
                'dpo': 0,
                'ichimoku': 0,
                'vo': 0,
                'kvo': 0,
                'eom': 0,
                'kst': 1.0,
                # minor signal weights
                'macd_change': 0,
                'rsi_change': 0,
                'stoch_change': 0,
                'adx_change': 0,
                'roc_change': 0,
                'vwap_change': 0,
                'vo_change': 0,
            }
    # Define possible weights for each indicator
    weight_values = [0, 0.5, 1.0]
    indicators = [
        'macd', 'sama', 'zlema', 'rsi', 'stochastic', 'ema', 'sma', 'supertrend', 
        'adx', 'squeeze', 'roc', 'psar', 'vwap', 'ppo', 'cmf', 'cci', 'ao', 
        'uo', 'dpo', 'ichimoku', 'vo', 'kvo', 'eom', 'kst'
    ]

    # Cartesian product of weights for all indicators
    all_combinations = itertools.product(weight_values, repeat=len(indicators))

    # Initialize variables
    best_weights = None
    best_positive_profit = float('-inf')
    best_negative_profit = float('inf')
    best_net_profit = float('-inf')

    best_positive_profit_weights = None
    best_negative_profit_weights = None
    best_net_profit_weights = None

    count = 0

    def simulate_combination(combination, count):
        strategy_weights = dict(zip(indicators, combination))
        
        # Ensure at least three weights are non-zero
        if sum(weight > 0 for weight in strategy_weights.values()) < 3:
            return None

        # Simulate trading with these weights
        mtrader, _, _ = run_trader(
            exchange, symbols, df, initial_usdt, strategy_weights, count, name
        )

        total_positive_profit = sum(
            mtrader.positive_profit_percent(symbol) for symbol in symbols
        )
        total_negative_profit = sum(
            mtrader.negative_profit_percent(symbol) for symbol in symbols
        )
        net_profit = total_positive_profit + total_negative_profit

        del mtrader

        # Ignore cases where any profits are zero or mostly negative profits
        if total_positive_profit == 0 or total_negative_profit == 0 or net_profit <= 0:
            return None

        print(f"{count} Positive profit: {total_positive_profit:.2f}%")
        print(f"{count} Negative profit: {total_negative_profit:.2f}%")
        print(f"{count} Net profit: {net_profit:.2f}%")

        return {
            'combination': combination,
            'total_positive_profit': total_positive_profit,
            'total_negative_profit': total_negative_profit,
            'net_profit': net_profit
        }

    lock = RLock()
    futures = []

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = []
        for count, combination in enumerate(all_combinations):
            result = simulate_combination(combination, count)
            if result:
                with lock:
                    combination = result['combination']
                    total_positive_profit = result['total_positive_profit']
                    total_negative_profit = result['total_negative_profit']
                    net_profit = result['net_profit']

                if total_positive_profit > best_positive_profit:
                    best_positive_profit = total_positive_profit
                    best_positive_profit_weights = combination
                    print(f"{count} Best positive profit: {best_positive_profit:.2f}% with weights {best_positive_profit_weights}")

                if total_negative_profit < best_negative_profit:
                    best_negative_profit = total_negative_profit
                    best_negative_profit_weights = combination
                    print(f"{count} Best negative profit: {best_negative_profit:.2f}% with weights {best_negative_profit_weights}")


                if net_profit > best_net_profit:
                    best_net_profit = net_profit
                    best_net_profit_weights = combination
                    print(f"{count} Best net profit: {best_net_profit:.2f}% with weights {best_net_profit_weights}")
            #print("Completed {count}")

    print(f"Final Best positive profit: {best_positive_profit:.2f}% with weights {best_positive_profit_weights}")
    print(f"Final Best negative profit: {best_negative_profit:.2f}% with weights {best_negative_profit_weights}")
    print(f"Final Best net profit: {best_net_profit:.2f}% with weights {best_net_profit_weights}")



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Trade simulation with past klines.')
    parser.add_argument('--initial_usdt', type=float, default=10000.0, help='Initial USDT amount for simulation')
    parser.add_argument('--exchange', type=str, default="cbadv", help='Account to use for simulation')
    #parser.add_argument('--granularity', type=int, default=3600, help='Granularity of klines')
    parser.add_argument('--csv_path', type=str, default='data/crypto_hourly_data/cryptotoken_full_binance_1h.csv', help='Path to the CSV file')
    parser.add_argument('--symbols', type=str, default='BTC-USDT,ETH-USDT,SOL-USDT,HBAR-USDT,DOT-USDT', help='Comma separated list of symbols')
    parser.add_argument('--strategy', type=str, default='', help='Strategy to use for simulation')
    parser.add_argument('--start_date', type=str, default='2020-08-11 06:00:00', help='Start date for klines')
    parser.add_argument('--end_date', type=str, default='2023-10-19 23:00:00', help='End date for klines')
    args = parser.parse_args()
    main(args)
