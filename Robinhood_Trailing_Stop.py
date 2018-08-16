import json
import os
import sys
import datetime
import logging

from Robinhood import Robinhood

class Robinhood_Trailing_Stop:
    def __init__(self, username=None, password=None, trailing_percent=None, limit_percent=None):
        #TODO: Add description

        logging.basicConfig(filename='logs/Trailing_Stop.log', filemode='w', level=logging.DEBUG)
        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        logging.info('Initializing Robinhoos_Trailing_Stop.py')

        assert username != None, 'Username must be specified'
        assert password != None, 'Password must be specified'
        assert self._valid_percent(trailing_percent), 'Must provide trailing percent as a decimal'
        assert self._valid_percent(limit_percent), 'Must provide limit percent as a decimal'

        self.username = username
        self.password = password
        self.tp = trailing_percent
        self.lp = limit_percent

        logging.debug('Trailing percent is is {} and limit percent is {}'.format(self.tp, self.lp))
        
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

        # Verify there are stocks held to place orders for
        logging.info('Searching for non-zero positions held.')
        self.stock_list = [x for x in self.trader.nonzero_positions_held()]
        n = len(self.stock_list)
        logging.info('There are {} stocks held currently.'.format(n))
        assert n > 0, 'No nonzero positions held to process a stop limit sell for'

        # Cancel existing sell orders
        logging.info('Cancelling any open sell orders.')
        n = self.trader.cancel_all_sell_orders()
        logging.info('There were {} sell orders cancelled'.format(n))

    def cancel_all_sells(self):
        #TODO: add description

        logging.info('Attempting to cancel all sell orders.')
        try:
            c = self.trader.cancel_all_sell_orders()
            logging.info('Cancelled {} order(s).'.format(c))
            return True
        except:
            logging.warning('Failed to cancel orders.')
            return False