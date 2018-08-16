import json
import os
import sys
import datetime
import logging

from Robinhood import Robinhood

class Robinhood_Trailing_Stop:
    def __init__(self, username=None, password=None, trailing_percent=None, limit_percent=None):
        #TODO: Add description

        logging.basicConfig(filename='logs/Trailing_Stop.log', filemode='a', level=logging.INFO)
        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        logging.info('\nInitializing Robinhoos_Trailing_Stop.py')

        assert username != None, 'Username must be specified'
        assert password != None, 'Password must be specified'
        assert self._valid_percent(trailing_percent), 'Must provide trailing percent as a decimal'
        assert self._valid_percent(limit_percent), 'Must provide limit percent as a decimal'

        self.username = username
        self.password = password
        self.tp = float(trailing_percent)
        self.lp = float(limit_percent)

        logging.info('Trailing percent is is {} and limit percent is {}'.format(self.tp, self.lp))
        
        self.trader = Robinhood()
        self.trader.login(username = self.username, password = self.password)

        # Start the program
        self._main()

    def _valid_percent(self, n):
        #TODO: Add description
        try:
            return n < 1 and n > 0
        except:
            return False
        return False

    def _main(self):
        #TODO: add description
        last_cancel_check = datetime.datetime.now()
        last_sale_check = datetime.datetime.now()

        #TODO: Move these things to functions so that they can be called at the start of _main and on a schedule.

        while True:
            if (datetime.datetime.now()-last_cancel_check).total_seconds() > 60 * 60:

            # Cancel existing sell orders
            logging.info('Cancelling any open sell orders.')
            n = self.trader.cancel_all_sell_orders()
            logging.info('There were {} sell orders cancelled'.format(n))

            # Check Stock
            self.stock_list = [x for x in self.trader.nonzero_positions_held()]
            n = len(self.stock_list)
            logging.info('There are {} stocks held currently.'.format(n))
            for stock in self.stock_list:
                self.check_for_sale(stock)

    def check_for_sale(self, stock):
        #TODO: Add Description
        # Checks the stock bid price against the high to see if it has surpassed the stop price
        
        instrument = stock['instrument']
        quantity = int(float(stock['quantity']))
        symbol = self.trader.instrument_results(instrument)['symbol']
        
        assert symbol, "You must provide a symbol."
        hi = float(self.trader.high_52_weeks(symbol))
        last = float(self.trader.high_52_weeks(symbol))

        stop = (1-self.tp) * hi
        limit = (1 - self.tp - self.lp) * hi

        if last <= stop:
            # Place Order
            limit = round(limit,2)
            r = self.trader.place_order(symbol=symbol,
                                        quantity=quantity,
                                        trigger='immediate',
                                        order_type='limit',
                                        price=limit,
                                        side='sell',
                                        time_in_force='gfd')
            s1 = '{}: {} shares sold. Last: {}, High: {}, Stop: {}, Limit: {}'.format(symbol, quantity, last, hi, stop, limit)
            logging.info(s1)

    def cancel_all_sells(self):
        #TODO: add description

        try:
            c = self.trader.cancel_all_sell_orders()
            logging.info('Cancelled {} sell order(s).'.format(c))
            return True
        except:
            logging.warning('Failed to cancel sell orders.')
            return False