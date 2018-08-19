import json
import os
import sys
import datetime
import logging
import time

from Robinhood import Robinhood

class Robinhood_Trailing_Stop:
    """Class for creating Trailing Stops for Robinhood
    """

    # TODO: Make limit_percent be optional. Update params, doc string, and sell.
    def __init__(self, username, password, trailing_percent, limit_percent, check_interval=60*2, run_length=7*60*60):
        """Initialization of Class

            Establishes Robinhood object, a trailing percent rule to follow and
            an optional limit percent for orders.

        Parameters
        ----------
        username : str
            username for logging into Robinhood
        password : str
            password for logging into Robinhood
        trailing_percent : float
            Trailing percnet used for stop trigger. Stop calculated via (1-traliing_percent) * 52_week_high
        limit_percent : float
            Optional limit percent to include when placing an order.
        check_interval : float, optional
            Optional number to represent how often owned stocks should be checked. (The default 2 minutes)
        run_length : float, optional
            Optional number to represent how long the loop should run for in seconds. (The default is 7 hours)

        """

        # Logging...
        logging.basicConfig(filename='logs/Trailing_Stop.log',
                            filemode='a', level=logging.INFO)
        logging.basicConfig(format='%(asctime)s %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p')
        logging.info('\nInitializing Robinhoos_Trailing_Stop.py')

        # Validate parameters
        assert self._validate_percent(
            trailing_percent), 'Must provide trailing percent as a decimal'
        assert self._validate_percent(
            limit_percent), 'Must provide limit percent as a decimal'

        self.username = username
        self.password = password
        self.tp = float(trailing_percent)
        self.lp = float(limit_percent)
        self.check_interval = check_interval
        self.run_length = run_length

        logging.info(
            'Trailing percent is is {} and limit percent is {}'.format(self.tp, self.lp))

        # Create Robinhood session
        self.trader = Robinhood()
        self.trader.login(username=self.username, password=self.password)

    def _validate_percent(self, n):
        """Validation check on variable to see if it is between 0 and 1.

        Parameters
        ----------
        n : float
            Variable to be validated.

        Returns
        -------
        bool
            True if a valid percent, otherwise False
        """

        try:
            return (n < 1 and n > 0)
        except:
            return False

    def main_loop(self):
        """Main loop that runs the processing steps for the trailing stop.

        Loop will run until the run_lenght time is reached. 

        """

        start_time = datetime.datetime.now()
        stock_check_time = datetime.datetime.now()

        while True:
            # Check if day is over, exit if so
            time_dif = (datetime.datetime.now() - start_time).total_seconds()
            if time_dif > self.run_length:
                break

            time_dif = (datetime.datetime.now() - stock_check_time).total_seconds()
            if time_dif > self.check_interval:
                stock_check_time = datetime.datetime.now()
                self.cancel_all_sells()
                time.sleep(10)
                self.check_stocks()

    def check_stocks(self):
        """Checks account for stocks owned. If any, then checks if a stop target has been met.

        """

        # Get a list of stocks that are currently held
        self.stock_list = [x for x in self.trader.nonzero_positions_held()]
        n = len(self.stock_list)
        logging.info('There are {} stocks held currently.'.format(n))

        # If there are no stocks... just exit
        if n == 0:
            return

        # Check each stock
        for stock in self.stock_list:
            self.check_stop(stock)

    def check_stop(self, stock):
        """Check a stock to see if the stop price has been hit and if so enters a sell

        Parameters
        ----------
        stock : dict
            Dictionary containing stock position information

        """

        # Get basic stock info needed
        instrument = stock['instrument']
        quantity = int(float(stock['quantity']))
        symbol = self.trader.instrument_results(instrument)['symbol']
        assert symbol, "You must provide a symbol."

        # Get Stock Price Info
        hi = float(self.trader.high_52_weeks(symbol))
        # If this is anything other than "Last", such as bid/ask, then need to check that price isn't $0 during after-hours
        last = float(self.trader.quote(symbol)['last_trade_price'])
        stop = (1-self.tp) * hi
        limit_price = (1 - self.lp) * last
        limit_price = round(limit_price, 2)

        # If the price has fallen below the threshold
        if last <= stop:
            # Place Order
            r = self.trader.place_order(symbol=symbol,
                                        quantity=quantity,
                                        trigger='immediate',
                                        order_type='limit',
                                        price=limit_price,
                                        side='sell',
                                        time_in_force='gfd')
            s1 = '{}: {} shares sold. Last: {}, High: {}, Stop: {}, Limit: {}'.format(
                symbol, quantity, last, hi, stop, limit_price)
            logging.info(s1)

    def cancel_all_sells(self):
        """Cancels all open sell orders
        
        Returns
        -------
        bool
            True if successful, False otherwise.
        """

        logging.info('Cancelling any open sell orders.')

        try:
            c = self.trader.cancel_all_sell_orders()
            logging.info('Cancelled {} sell order(s).'.format(c))
            return True
        except:
            logging.warning('Failed to cancel sell orders.')
            return False