#!/usr/bin/env python3
import sys
import pprint
#sys.path.append('./tests')
sys.path.append('.')
from cointrader.exchange.TraderSelectExchange import TraderSelectExchange
from cointrader.order.OrderResult import OrderResult

CLIENT_NAME = "cbadv"

if __name__ == '__main__':
    exchange = TraderSelectExchange(CLIENT_NAME).get_exchange()
    # {'success': True, 'success_response': {'order_id': 'f01d3875-5940-4660-b8b5-b80682e02209', 'product_id': 'AVAX-USD', 'side': 'BUY', 'client_order_id': 'da5167f74c19494db183d1542aef5cc7', 'attached_order_id': ''}, 'order_configuration': {'market_market_ioc': {'base_size': '0.01', 'rfq_enabled': False, 'rfq_disabled': False}}}

    # {'success': True, 'success_response': {'order_id': 'abf231e1-9231-4eaf-9d3b-aeadac489534', 'product_id': 'AVAX-USD', 'side': 'BUY', 'client_order_id': '8347d761e6ec4044b7172d929321e825', 'attached_order_id': ''}, 'order_configuration': {'market_market_ioc': {'base_size': '1e-05', 'rfq_enabled': False, 'rfq_disabled': False}}}
    # result = exchange.trade_buy_market('AVAX-USD', 0.00001)
    # print("")
    # print(result)
    # print("")

    # {'order': {'order_id': 'abf231e1-9231-4eaf-9d3b-aeadac489534', 'product_id': 'AVAX-USD', 'user_id': '449e61a2-b98d-5be4-8ad1-bcfbb826ca32', 'order_configuration': {'market_market_ioc': {'base_size': '0.00001', 'rfq_enabled': False, 'rfq_disabled': False}}, 'side': 'BUY', 'client_order_id': '8347d761e6ec4044b7172d929321e825', 'status': 'OPEN', 'time_in_force': 'IMMEDIATE_OR_CANCEL', 'created_time': '2024-12-18T21:09:24.242360Z', 'completion_percentage': '0', 'filled_size': '0', 'average_filled_price': '0', 'fee': '', 'number_of_fills': '0', 'filled_value': '0', 'pending_cancel': False, 'size_in_quote': False, 'total_fees': '0', 'size_inclusive_of_fees': False, 'total_value_after_fees': '0', 'trigger_status': 'INVALID_ORDER_TYPE', 'order_type': 'MARKET', 'reject_reason': 'REJECT_REASON_UNSPECIFIED', 'settled': False, 'product_type': 'SPOT', 'reject_message': '', 'cancel_message': '', 'order_placement_source': 'RETAIL_ADVANCED', 'outstanding_hold_amount': '0.0004632602625', 'is_liquidation': False, 'last_fill_time': None, 'edit_history': [], 'leverage': '', 'margin_type': 'UNKNOWN_MARGIN_TYPE', 'retail_portfolio_id': '449e61a2-b98d-5be4-8ad1-bcfbb826ca32', 'originating_order_id': '', 'attached_order_id': '', 'attached_order_configuration': None}}
    # result = exchange.trade_get_order("AVAX-USD", result.id)
    # print("")
    # print(result)

    #print("exchange.trade_sell_market(\"BTC-USD\", 0.0001)")
    #result = exchange.trade_sell_market("BTC-USD", amount=0.0001)
    #print(str(result))

    # {'success': True, 'response': {'order_id': '01be5662-fd82-4d9d-929e-fdeb5e9fa597', 'product_id': 'BTC-USD', 'side': 'BUY', 'exchange_order_id': '63a394e967964fdd8b8bfd563efc5104', 'attached_order_id': ''}, 'order_configuration': {'limit_limit_gtc': {'base_size': '0.0001', 'limit_price': '200000', 'post_only': False, 'rfq_disabled': False}}}
    # Executes at market price
    #print("exchange.trade_buy_limit(\"BTC-USD\", 0.0001, 200000)")
    #result = exchange.trade_buy_limit("BTC-USD", amount=0.0001, price=200000)
    #print(str(result))

    # {'order': {'order_id': '01be5662-fd82-4d9d-929e-fdeb5e9fa597', 'product_id': 'BTC-USD', 'user_id': '449e61a2-b98d-5be4-8ad1-bcfbb826ca32', 'order_configuration': {'limit_limit_gtc': {'base_size': '0.0001', 'limit_price': '200000', 'post_only': False, 'rfq_disabled': False}}, 'side': 'BUY', 'exchange_order_id': '63a394e967964fdd8b8bfd563efc5104', 'status': 'FILLED', 'time_in_force': 'GOOD_UNTIL_CANCELLED', 'created_time': '2024-12-02T18:17:20.537264Z', 'completion_percentage': '100.00', 'filled_size': '0.0001', 'average_filled_price': '95397.16', 'fee': '', 'number_of_fills': '1', 'filled_value': '9.539716', 'pending_cancel': False, 'size_in_quote': False, 'total_fees': '0.02384929', 'size_inclusive_of_fees': False, 'total_value_after_fees': '9.56356529', 'trigger_status': 'INVALID_ORDER_TYPE', 'order_type': 'LIMIT', 'reject_reason': 'REJECT_REASON_UNSPECIFIED', 'settled': True, 'product_type': 'SPOT', 'reject_message': '', 'cancel_message': '', 'order_placement_source': 'RETAIL_ADVANCED', 'outstanding_hold_amount': '0', 'is_liquidation': False, 'last_fill_time': '2024-12-02T18:17:20.590397Z', 'edit_history': [], 'leverage': '', 'margin_type': 'UNKNOWN_MARGIN_TYPE', 'retail_portfolio_id': '449e61a2-b98d-5be4-8ad1-bcfbb826ca32', 'originating_order_id': '', 'attached_order_id': '', 'attached_order_configuration': None}}
    #print("exchange.trade_buy_limit(\"BTC-USD\", 0.0001, 200000)")
    #result = exchange.trade_get_order("BTC-USD", "01be5662-fd82-4d9d-929e-fdeb5e9fa597")
    #print(str(result))

    # {'success': True, 'response': {'order_id': '496d635b-26c5-4794-a171-0bb278139a5d', 'product_id': 'BTC-USD', 'side': 'BUY', 'exchange_order_id': 'd53cac98fb974e29a29c46b74f56a84d', 'attached_order_id': ''}, 'order_configuration': {'market_market_ioc': {'base_size': '0.0001', 'rfq_enabled': False, 'rfq_disabled': False}}}
    #print("exchange.trade_buy_market(\"BTC-USD\", 0.0001)")
    #result = exchange.trade_buy_market("BTC-USD", 0.0001)
    #print(str(result))

    #result = exchange.trade_get_order("BTC-USD", "7a984742-b2cb-41c5-b8b4-dd3f1144fe07")
    #print(str(result))

    # {'success': True, 'response': {'order_id': '7a984742-b2cb-41c5-b8b4-dd3f1144fe07', 'product_id': 'BTC-USD', 'side': 'BUY', 'exchange_order_id': 'c5312526dced49a39859fafbbc64c066', 'attached_order_id': ''}, 'order_configuration': {'limit_limit_gtc': {'base_size': '0.0001', 'limit_price': '10000', 'post_only': False, 'rfq_disabled': False}}}
    #buy_result = exchange.trade_buy_limit("BTC-USD", 0.0001, 10000)
    #print(str(buy_result))

    #print("Cancelling order with id {}".format(buy_result.id))
    #result = exchange.trade_cancel("BTC-USD", buy_result.id)
    #print(str(result))

    # {'success': True, 'response': {'order_id': '630939ab-6105-4062-b44a-342bcee33800', 'product_id': 'BTC-USD', 'side': 'BUY', 'exchange_order_id': '39bec75543d64aaf94d3dc3feeb24972', 'attached_order_id': ''}, 'order_configuration': {'stop_limit_stop_limit_gtc': {'base_size': '5e-05', 'limit_price': '200001', 'stop_price': '200000', 'stop_direction': 'STOP_DIRECTION_STOP_UP'}}}
    stop_result = exchange.trade_buy_stop_limit("BTC-USD", amount=0.00005, price=200001, stop_price=200000)
    print("")
    print(str(stop_result))
    print("")
    #print(stop_result.id)

    #print("Order Status")
    result = exchange.trade_get_order("BTC-USD", stop_result.id)
    print("")
    print(str(result))
    print("")

    print(f"Cancel order {stop_result.id}")
    result = exchange.trade_cancel_order("BTC-USD", stop_result.id)
    print("")
    print(str(result))
    print("")

    # result = exchange.trade_buy_market('XRP-USDC', 1)
    # print(result)

    # print("Order Status")
    # result = exchange.trade_get_order("XRP-USDC", result.id)
    # print(str(result))