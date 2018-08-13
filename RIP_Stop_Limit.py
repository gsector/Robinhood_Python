import json
import os
import sys
import datetime

from Robinhood import Robinhood
import config



def process_stop_limit_sells(trader=None):

    ####################################################
    #              Process Stop Limit
    ####################################################
    

    trailing_stop_percent = config.sls['stop']
    limit_percent = config.sls['limit']

    # Cycle through positions and cancel nonzero order(s):
    for position in trader.nonzero_positions():
        # Get data field for nonzero position
        position['symbol'] = trader.instrument_results(position['instrument'])['symbol']
        position['max_price'] = float(position['average_buy_price'])
        position['created_dt'] = datetime.datetime.strptime(position['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
        
        # Get the highest price since purchasing the stock
        historical_quote = trader.get_historical_quotes(stock=position['symbol'])
        
        for record in historical_quote['results'][0]['historicals']:
            hist_date_time = datetime.datetime.strptime(record['begins_at'], '%Y-%m-%dT%H:%M:%SZ')
            if hist_date_time.date() >= position['created_dt'].date() and float(record['high_price']) > position['max_price']:
                position['max_price'] = float(record['high_price'])
        historical_quote.clear()

        # Cycle through open sell orders and compare against this order.
        r = None
        for order in trader.open_sell_orders():
            if order['instrument'] != position['instrument']: 
                continue

            # If order should be cancelled
            if (float(order['stop_price']) + 0.01 < ((1.0 - trailing_stop_percent) * position['max_price'])
                    or float(position['quantity']) > float(position['shares_held_for_sells'])):
                
                # Cancel the old order
                r = trader.cancel_order(url=order['cancel'])
                if r:
                    print('Cancelled {} order for {} shares.'.format(position['symbol'], position['quantity']))
                else:
                    print('Failed to cancel {} order for {} shares.'.format(position['symbol'], position['quantity']))
                break


    # Cycle through positions and place trailing stop limit sell order if there is none
    for position in trader.nonzero_positions():
        if float(position['shares_held_for_sells']) == 0.0:
            position['symbol'] = trader.instrument_results(position['instrument'])['symbol']
            position['max_price'] = float(position['average_buy_price'])
            position['created_dt'] = datetime.datetime.strptime(position['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')

            # Get historical max_price for sell
            historical_quote = trader.get_historical_quotes(stock=position['symbol'])
            for record in historical_quote['results'][0]['historicals']:
                hist_date_time = datetime.datetime.strptime(record['begins_at'], '%Y-%m-%dT%H:%M:%SZ')
                if hist_date_time.date() >= position['created_dt'].date() and float(record['high_price']) > position['max_price']:
                    position['max_price'] = float(record['high_price'])
            historical_quote.clear()

            # Place Order
            r = None
            position['stop_price'] = position['max_price'] * (1 - trailing_stop_percent)
            position['limit_price'] = position['max_price'] * (1- trailing_stop_percent - limit_percent)

            r = trader.place_stop_limit_order(instrument=position['instrument'],
                                              quantity=float(position['quantity']),
                                              stop_price=position['stop_price'],
                                              price=position['limit_price'],
                                              side='sell',
                                              time_in_force = 'gtc')
            # Print Results
            if r:
                print('Placed stop/limit {} order for {} shares at {}/{}.'.format(position['symbol'],
                                                                                  position['quantity'],
                                                                                  position['stop_price'],
                                                                                  position['limit_price']))
            else:
                print('Failed to place stop/limit {} order for {} shares at {}/{}.'.format(position['symbol'],
                                                                                           position['quantity'],
                                                                                           position['stop_price'],
                                                                                           position['limit_price']))

if __name__ == '__main__':
    """ When script is ran... """

    ####################################################
    #                 Login to Robinhood               #
    ####################################################
    trader = Robinhood()
    try:
        trader.login(username = config.robinhood['username'],
                     password = config.robinhood['password'])
    except:
        print('Exiting after Failed Robinhood Login.')
    
    # *************************************************
    #               Process Steps
    # *************************************************
    
    process_stop_limit_sells(trader=trader)
                    



    
