import sys
import pprint
#sys.path.append('./tests')
sys.path.append('.')
from cointrader.client.TraderSelectClient import TraderSelectClient
from cointrader.order.OrderResult import OrderResult

CLIENT_NAME = "cbadv"

if __name__ == '__main__':
    client = TraderSelectClient(CLIENT_NAME).get_client()
    #print("client.trade_sell_market(\"BTC-USD\", 0.0001)")
    #result = client.trade_sell_market("BTC-USD", amount=0.0001)
    #print(str(result))

    # {'success': True, 'response': {'order_id': '01be5662-fd82-4d9d-929e-fdeb5e9fa597', 'product_id': 'BTC-USD', 'side': 'BUY', 'client_order_id': '63a394e967964fdd8b8bfd563efc5104', 'attached_order_id': ''}, 'order_configuration': {'limit_limit_gtc': {'base_size': '0.0001', 'limit_price': '200000', 'post_only': False, 'rfq_disabled': False}}}
    # Executes at market price
    #print("client.trade_buy_limit(\"BTC-USD\", 0.0001, 200000)")
    #result = client.trade_buy_limit("BTC-USD", amount=0.0001, price=200000)
    #print(str(result))

    # {'order': {'order_id': '01be5662-fd82-4d9d-929e-fdeb5e9fa597', 'product_id': 'BTC-USD', 'user_id': '449e61a2-b98d-5be4-8ad1-bcfbb826ca32', 'order_configuration': {'limit_limit_gtc': {'base_size': '0.0001', 'limit_price': '200000', 'post_only': False, 'rfq_disabled': False}}, 'side': 'BUY', 'client_order_id': '63a394e967964fdd8b8bfd563efc5104', 'status': 'FILLED', 'time_in_force': 'GOOD_UNTIL_CANCELLED', 'created_time': '2024-12-02T18:17:20.537264Z', 'completion_percentage': '100.00', 'filled_size': '0.0001', 'average_filled_price': '95397.16', 'fee': '', 'number_of_fills': '1', 'filled_value': '9.539716', 'pending_cancel': False, 'size_in_quote': False, 'total_fees': '0.02384929', 'size_inclusive_of_fees': False, 'total_value_after_fees': '9.56356529', 'trigger_status': 'INVALID_ORDER_TYPE', 'order_type': 'LIMIT', 'reject_reason': 'REJECT_REASON_UNSPECIFIED', 'settled': True, 'product_type': 'SPOT', 'reject_message': '', 'cancel_message': '', 'order_placement_source': 'RETAIL_ADVANCED', 'outstanding_hold_amount': '0', 'is_liquidation': False, 'last_fill_time': '2024-12-02T18:17:20.590397Z', 'edit_history': [], 'leverage': '', 'margin_type': 'UNKNOWN_MARGIN_TYPE', 'retail_portfolio_id': '449e61a2-b98d-5be4-8ad1-bcfbb826ca32', 'originating_order_id': '', 'attached_order_id': '', 'attached_order_configuration': None}}
    #print("client.trade_buy_limit(\"BTC-USD\", 0.0001, 200000)")
    #result = client.trade_get_order("BTC-USD", "01be5662-fd82-4d9d-929e-fdeb5e9fa597")
    #print(str(result))

    # {'success': True, 'response': {'order_id': '496d635b-26c5-4794-a171-0bb278139a5d', 'product_id': 'BTC-USD', 'side': 'BUY', 'client_order_id': 'd53cac98fb974e29a29c46b74f56a84d', 'attached_order_id': ''}, 'order_configuration': {'market_market_ioc': {'base_size': '0.0001', 'rfq_enabled': False, 'rfq_disabled': False}}}
    #print("client.trade_buy_market(\"BTC-USD\", 0.0001)")
    #result = client.trade_buy_market("BTC-USD", 0.0001)
    #print(str(result))

    #result = client.trade_get_order("BTC-USD", "7a984742-b2cb-41c5-b8b4-dd3f1144fe07")
    #print(str(result))

    # {'success': True, 'response': {'order_id': '7a984742-b2cb-41c5-b8b4-dd3f1144fe07', 'product_id': 'BTC-USD', 'side': 'BUY', 'client_order_id': 'c5312526dced49a39859fafbbc64c066', 'attached_order_id': ''}, 'order_configuration': {'limit_limit_gtc': {'base_size': '0.0001', 'limit_price': '10000', 'post_only': False, 'rfq_disabled': False}}}
    #buy_result = client.trade_buy_limit("BTC-USD", 0.0001, 10000)
    #print(str(buy_result))

    #print("Cancelling order with id {}".format(buy_result.id))
    #result = client.trade_cancel("BTC-USD", buy_result.id)
    #print(str(result))

    # {'success': True, 'response': {'order_id': '630939ab-6105-4062-b44a-342bcee33800', 'product_id': 'BTC-USD', 'side': 'BUY', 'client_order_id': '39bec75543d64aaf94d3dc3feeb24972', 'attached_order_id': ''}, 'order_configuration': {'stop_limit_stop_limit_gtc': {'base_size': '5e-05', 'limit_price': '200001', 'stop_price': '200000', 'stop_direction': 'STOP_DIRECTION_STOP_UP'}}}
    stop_result = client.trade_buy_stop_limit("BTC-USD", amount=0.00005, price=200001, stop_price=200000)
    print(str(stop_result))
    print(stop_result.id)

    print("Order Status")
    result = client.trade_get_order("BTC-USD", stop_result.id)
    print(str(result))

    print(f"Cancel order {stop_result.id}")
    result = client.trade_cancel_order("BTC-USD", stop_result.id)
    print(str(result))

    print("Order Status")
    result = client.trade_get_order("BTC-USD", stop_result.id)
    print(str(result))