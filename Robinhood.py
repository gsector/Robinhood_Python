"""
    Many of the methods included in Robinhood.py are copied with modification from:
        Robinhood.py: a collection of utilities for working with Robinhood's Private API
        https://github.com/Jamonek/Robinhood
    The following project was also leaned on heavily for reference material:
        https://github.com/sanko/Robinhood/
"""


import requests

class Robinhood:
    """Class for interacting with Robinhood """

    endpoints = {
        "login": "https://api.robinhood.com/api-token-auth/",
        "logout": "https://api.robinhood.com/api-token-logout/",
        "investment_profile": "https://api.robinhood.com/user/investment_profile/",
        "accounts": "https://api.robinhood.com/accounts/",
        "ach_iav_auth": "https://api.robinhood.com/ach/iav/auth/",
        "ach_relationships": "https://api.robinhood.com/ach/relationships/",
        "ach_transfers": "https://api.robinhood.com/ach/transfers/",
        "applications": "https://api.robinhood.com/applications/",
        "dividends": "https://api.robinhood.com/dividends/",
        "edocuments": "https://api.robinhood.com/documents/",
        "fundamentals": "https://api.robinhood.com/fundamentals/",
        "instruments": "https://api.robinhood.com/instruments/",
        "margin_upgrades": "https://api.robinhood.com/margin/upgrades/",
        "markets": "https://api.robinhood.com/markets/",
        "notifications": "https://api.robinhood.com/notifications/",
        "orders": "https://api.robinhood.com/orders/",
            # API expects https://api.robinhood.com/orders/{{orderId}}/cancel/
        "cancel_order": "https://api.robinhood.com/orders/",
        "password_reset": "https://api.robinhood.com/password_reset/request/",
        "portfolios": "https://api.robinhood.com/portfolios/",
        "positions": "https://api.robinhood.com/positions/",
        "quotes": "https://api.robinhood.com/quotes/",
        "historicals": "https://api.robinhood.com/quotes/historicals/",
        "document_requests": "https://api.robinhood.com/upload/document_requests/",
        "user": "https://api.robinhood.com/user/",
        "watchlists": "https://api.robinhood.com/watchlists/",
        "news": "https://api.robinhood.com/midlands/news/",
    }

    session = None
    username = None
    password = None
    headers = None
    auth_token = None
    no_trade_list = list()

    ###########################################################################
    #                       Logging in and Account Info
    ###########################################################################

    def __init__(self):
        """Robinhood class initialization

            Creats a session and establishes headers.
        """

        self.session = requests.session()
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "X-Robinhood-API-Version": "1.0.0",
            "Connection": "keep-alive",
            "User-Agent": "Robinhood/823 (iPhone; iOS 7.1.2; Scale/2.00)",
            "Authorization": None
        }
        self.session.headers = headers

    def login(self, username=None, password=None):
        """Logs a user into a Robinhood Session

        Parameters
        ----------
        username : str
            Robinhood username
        password : str
            Robinhood password

        Returns
        -------
        bool
            True if successful, False otherwise

        """

        if username:
            self.username = username
        if password:
            self.password = password

        assert self.username != None, 'Username must be included to login.'
        assert self.password != None, 'Password must be included to login.'

        payload = {
            'password': self.password,
            'username': self.username
        }

        try:
            res = self.session.post(self.endpoints['login'], data=payload)
            res.raise_for_status()
            data = res.json()
        except requests.exceptions.HTTPError:
            print('Login Failed')
            return False

        if 'token' in data.keys():
            auth_token = data['token']
            self.session.headers.update(
                {'Authorization': 'Token ' + auth_token})
            return True

        return False

    def get_account(self):
        """Fetch account information

        Returns
        -------
        dict
            `accounts` endpoint payload
        """

        res = self.session.get(self.endpoints['accounts'])
        res.raise_for_status()  # auth required
        res = res.json()

        return res['results'][0]

    def buying_power(self):
        """Buying power for the account

        Buying power defined as the total cash in the account minus
        any amount held for orders.

        Returns
        -------
        float
            The buying power in $
        """
        return self.cash() - self.cash_held_for_orders()

    def unsettled_funds(self):
        # TOD: Improve this documentation
        """Unsettled funds for the account

        Returns
        -------
        float
            Unsettled funds in $
        """

        return float(self.get_account()['unsettled_funds'])

    def cash_held_for_orders(self):
        # TOD: Improve this documentation
        """Cash held for open orders

        Returns
        -------
        float
            $ amount held for open orders
        """
        return float(self.get_account()['cash_held_for_orders'])

    def cash(self):
        """Total cash in the account

        Returns
        -------
        float
            Dollar amount of cash for the account.
        """
        return float(self.get_account()['cash'])

    def cash_for_orders(self):
        """Cash available for orders
        
        Returns
        -------
        float
            Dollar amount available for orders.
        """

        return self.buying_power() - self.cash_held_for_orders()

    def logout(self):
        """Logs user out of session
        
        """

        res = self.session.post(self.endpoints['logout'])
        res.raise_for_status()
    
    def __del__(self):
        """Destructor class.

        Currently only logs user out.
        
        """

        self.logout()



    ###########################################################################
    #                           GET ORDERS
    ###########################################################################

    def orders(self, order_id=None):
        """Returns all orders for the user.

        Can specify a single order_id to retrieve a single order by ID.

        Yields
        ------
        dict
            Orders data. Contents...
                "cancel":
                "reject_reason":
                "stop_price":
                "extended_hours":
                "position":
                "cumulative_quantity":
                "ref_id":
                "trigger": "stop",
                "average_price": null,
                "quantity": "4.00000",
                "override_dtbp_checks":
                "side":
                "state": "confirmed", [filled, cancelled, queued, confirmed, rejected]
                "last_transaction_at":
                "url":
                "updated_at":
                "id":
                "created_at":
                "time_in_force": "gtc",
                "price": null,
                "instrument":
                "account":
                "type": "market",
                "fees": "0.00",
                "override_day_trade_checks": false,
                "executions": []
        """

        # Return all the orders from the first page
        if order_id:
            url = self.endpoints['orders'] + order_id + '/'
        else:
            url = self.endpoints['orders']

        res = self.session.get(url)
        res.raise_for_status()
        orders_json = res.json()

        # When getting an order by ID, there is no ['result'] section.
        try:
            for order in orders_json['results']:
                yield order
        except:
            yield orders_json

        # Get additional pages of orders
        while orders_json['next']:
            orders_json = self.session.get(orders_json['next']).json()
            for order in orders_json['results']:
                yield order

    def open_orders(self):
        """Returns open orders for the user.

        Yields
        ------
        dict
            Open orders data. Contents...
                "cancel":
                "reject_reason":
                "stop_price":
                "extended_hours":
                "position":
                "cumulative_quantity":
                "ref_id":
                "trigger": "stop",
                "average_price": null,
                "quantity": "4.00000",
                "override_dtbp_checks":
                "side":
                "state": "confirmed", [filled, cancelled, queued, confirmed, rejected]
                "last_transaction_at":
                "url":
                "updated_at":
                "id":
                "created_at":
                "time_in_force": "gtc",
                "price": null,
                "instrument":
                "account":
                "type": "market",
                "fees": "0.00",
                "override_day_trade_checks": false,
                "executions": []
        """

        for order in self.orders():
            if order['cancel']:
                yield order

    def open_sell_orders(self):
        """Returns open sell orders for the user.

        Yields
        ------
        dict
            Open orders data. Contents...
                "cancel":
                "reject_reason":
                "stop_price":
                "extended_hours":
                "position":
                "cumulative_quantity":
                "ref_id":
                "trigger": "stop",
                "average_price": null,
                "quantity": "4.00000",
                "override_dtbp_checks":
                "side":
                "state": "confirmed", [filled, cancelled, queued, confirmed, rejected]
                "last_transaction_at":
                "url":
                "updated_at":
                "id":
                "created_at":
                "time_in_force": "gtc",
                "price": null,
                "instrument":
                "account":
                "type": "market",
                "fees": "0.00",
                "override_day_trade_checks": false,
                "executions": []
        """

        for order in self.open_orders():
            if order['side'] == 'sell':
                yield order

    def open_buy_orders(self):
        """Returns open buy orders for the user.

        Yields
        ------
        dict
            Open orders data. Contents...
                "cancel":
                "reject_reason":
                "stop_price":
                "extended_hours":
                "position":
                "cumulative_quantity":
                "ref_id":
                "trigger": "stop",
                "average_price": null,
                "quantity": "4.00000",
                "override_dtbp_checks":
                "side":
                "state": "confirmed", [filled, cancelled, queued, confirmed, rejected]
                "last_transaction_at":
                "url":
                "updated_at":
                "id":
                "created_at":
                "time_in_force": "gtc",
                "price": null,
                "instrument":
                "account":
                "type": "market",
                "fees": "0.00",
                "override_day_trade_checks": false,
                "executions": []
        """

        for order in self.open_orders():
            if order['side'] == 'buy':
                yield order

    ###########################################################################
    #                           GET POSITIONS
    ###########################################################################

    def positions(self):
        """Returns positions endpoint data

        Contains each position for the account. Stocks/securities for the positions
        may or may not be currently held.

        Yields
        ------
        dict
            Position Information. Contents...
                'instrument'
                'average_buy_price'
                'quantity'
                'intraday_quantity'
                'intraday_average_buy_price'
                'shares_held_for_sells'
                'shares_held_for_buys'
                'created_at'
                'updated_at'
                'shares_held_for_stock_grants'
                'url'
                'account'
        """

        positions = self.session.get(self.endpoints['positions']).json()

        for position in positions['results']:
            yield position

        # Get additional pages of securities
        while positions['next']:
            positions = self.session.get(positions['next']).json()
            for position in positions['results']:
                yield position

    def nonzero_positions_held(self):
        """Returns positions with shares held > 0

        Yields
        ------
        dict
            Positions with shares > 0. Contents...
                'instrument'
                'average_buy_price'
                'quantity'
                'intraday_quantity'
                'intraday_average_buy_price'
                'shares_held_for_sells'
                'shares_held_for_buys'
                'created_at'
                'updated_at'
                'shares_held_for_stock_grants'
                'url'
                'account'
        """

        for position in self.positions():
            if float(position['quantity']) > 0:
                yield position

    ###########################################################################
    #                           GET DATA
    ###########################################################################

    def instrument_results(self, url):
        """Returns instrument URL results

        Some results return an instrument URL without any additional information
        such as the symbol. That information can be found by following the url.

        Parameters
        ----------
        url : str
            URL for the intstrument

        Returns
        -------
        dict
            Dictionary containing instruments endpoint data. Contents:
                'symbol'
                'name'
                'splits'
                'quote'
                'tradeable'
                'day_trade_ratio'
                'tradability'
                'market'
                'list_date'
                'bloomberg_unique'
                'state'
                'fundamentals'
                'type'
                'simple_name'
                'id'
                'min_tick_size'
                'maintenance_ratio'
                'url'
                'margin_initial_ratio'
                'country'
         """

        res = self.session.get(url)
        return res.json()

    def instruments(self, stock):
        """Fetches the instrument URL for a given symbol.

        Most often used for supplying the instrument in a trade request since
        instrument is required, but trades are generally conducted on a symbol.

        Parameters
        ----------
        stock : str
            Ticker symbol (lower or upper case accepted)

        Returns
        -------
        dict
            Dictionary containing instruments request results
        """

        res = self.session.get(self.endpoints['instruments'], params={
                               'query': stock.upper()})
        res.raise_for_status()
        res = res.json()

        return res['results']

    def quote(self, symbol):
        """Fetch stock quote
            Args:
                stock (str): stock ticker, prompt if blank
            Returns:
                (:obj:`dict`): JSON contents from `quotes` endpoint
        """
        '''Contents:
                'trading_halted'
                'last_trade_price'
                'symbol'
                'previous_close_date'
                'updated_at'
                'bid_price'
                'ask_size'
                'bid_size'
                'last_extended_hours_trade_price'
                'previous_close'
                'ask_price'
                'adjusted_previous_close'
                'last_trade_price_source'
                'has_traded'
                'instrument' '''

        assert symbol != None, 'You must specify a stock ticker symbol'
        symbol = str(symbol).upper()

        url = self.endpoints['quotes'] + symbol + "/"
        res = requests.get(url)
        res.raise_for_status()

        return res.json()

    def fundamentals(self, symbol):
        """Fetches Fundamentals data from Robinhood

        Parameters
        ----------
        symbol : str
            Stock symbol, can be lower or upper case.

        Returns
        -------
        dict
            JSON dictionary of fundamentals data. Contents:
                'open',
                'headquarters_state',
                'shares_outstanding',
                'num_employees',
                'market_cap',
                'headquarters_city',
                'volume',
                'instrument',
                'year_founded',
                'high',
                'dividend_yield',
                'sector',
                'high_52_weeks',
                'average_volume_2_weeks',
                'low',
                'description',
                'pe_ratio',
                'low_52_weeks',
                'average_volume',
                'ceo'
        """

        symbol = str(symbol).upper()

        url = self.endpoints['fundamentals'] + symbol + "/"
        res = requests.get(url)
        res.raise_for_status()

        return res.json()

    def high_52_weeks(self, symbol):
        """52 week high for a given stock symbol

        Parameters
        ----------
        symbol : str
            Stock symbol, upper or lower case is fine.

        Returns
        -------
        float
            52 week high dollar amount for the given symbol.
        """

        x = self.fundamentals(symbol=symbol)['high_52_weeks']
        return float(x)


    def get_historical_quotes(self, symbol, interval='day', span='year'):
        """Fetches historical quote data for a stock

        Parameters
        ----------
        symbol : str
            Stock ticker symbol
        interval : str, optional
            Resolution of the data for historical results. (the default is 'day', which provides one result per day)
        span : str, optional
            Length of the data (the default is 'year', which returns data for the last year)

        Notes
        -----
        Valid interval/span configs
            interval = 5minute | 10minute + span = day, week
            interval = day + span = year
            interval = week

        Returns
        -------
        Dict
            List of historical data dictionary items. Order is not guaranteed. Contents:
                <data>['results']['historicals']
                # _ba = datetime.datetime.strptime(begins_at, '%Y-%m-%dT%H:%M:%SZ')
                'begins_at'
                'open_price'
                'interpolated'
                'volume'
                'high_price'
                'low_price'
                'close_price'
                'session'
        """

        params={'symbols': symbol.upper(),
                  'interval': interval,
                  'span': span}

        res=self.session.get(self.endpoints['historicals'], params=params)
        return res.json()

    ###########################################################################
    #                           TRADE ACTIONS
    ###########################################################################

    # Need a function to submit a single market stop loss order sell

    # Need a function to submit a single market price order sell

    def cancel_order(self, order_id=None, url=None):
        """Cancel an order by order ID or URL

        Parameters
        ----------
        order_id : str, optional
            Order ID of an order to be cancelled (the default is None, which means this parameter is ignored.)
        url : str, optional
            Cancle URL to request to cancel an order (the default is None, which means this parameter is ignored.)

        Returns
        -------
        bool
            True if successful, false otherwise

        Notes
        -----
        For cancelling orders, Robinhood expects: https://api.robinhood.com/orders/{{orderId}}/cancel/
        """

        if order_id is not None:
            url=self.endpoints['cancel_order'] + str(order_id) + '/cancel/'
        else:
            assert url, "An Order ID or URL must be provided to cancel an order"

        res=self.session.post(url)

        if res.json == {}:
            return True
        else:
            return False

    def cancel_all_sell_orders(self):
        """Creates and sends requests to cancel all existing sell orders.

        Returns
        -------
        int
            Number of orders cancelled as integer
        """

        success=0
        for order in self.open_sell_orders():
            res=self.session.post(order['cancel'])
            res.raise_for_status()

        return success

    def place_order(self, symbol, quantity, trigger, order_type, side, time_in_force, stop_price=0.0, price=0.0):
        """** TEST THIS ** Places an order

        Stocks are checked against the no trade list to validate that
        an order is no placed for somethign in the no trade list.
        Reference: https://github.com/sanko/Robinhood/blob/master/Order.md#place-an-order

        Notes
        -----
        If the order type is "limit" then you need to use "price". If
        the order type is "stop" then you need to use "stop_price".

        Parameters
        ----------
        symbol : str
            Stock symbol
        quantity : int
            Number of shares to order. Must be > 0.
        trigger : str
            Trigger for the order. 'immediate' or 'stop'
        order_type : str
            Type of order. 'market' or 'limit'
        side : str
            Side for the order. 'buy' or 'sell'
        time_in_force : str
            How long the order is good for. 'gfd' for good for day and 'gtc' for good until cancelled.
        stop_price : float, optional
            Price that triggers the order (the default is 0.0)
        price : float, optional
            Limit price for the order. (the default is 0.0)

        Returns
        -------
        Dict
            Dictionary containing order results. When the order is successful, ['reject_reason'] should == None
        """
        # TODO: Add "extended_hours" to the parameters and request

        # Check mandatory parameters
        symbol=symbol.upper()
        self.no_trade_list=[x.upper() for x in self.no_trade_list]
        assert symbol not in self.no_trade_list, 'You may not trade a stock in your no trade list'
        instrument=self.quote(symbol=symbol)['instrument']
        assert instrument != None, 'The instrument for the symbol provided could not be found. Recheck symbol {}'.format(
            symbol)
        assert quantity > 0 and quantity == int(
            quantity), 'Quantity must be an integer > 0.'
        assert trigger in ['immediate',
                           'stop'], "Trigger must be 'immediate' or 'stop'"
        assert order_type in [
            'market', 'limit'], "Order type must be 'market' or 'limit'"
        assert side in ['buy', 'sell'], "Side myst be 'buy' or 'sell'"
        assert time_in_force in [
            'gfd', 'gtc'], "Time in force must be 'gfd' or 'gtc'"

        # Create payload dictionary for the request
        payload={
            'account': self.get_account()['url'],
            'instrument': instrument,
            'symbol': symbol,
            'quantity': quantity,
            'trigger': trigger,
            'type': order_type,
            'side': side,
            'time_in_force': time_in_force,
        }

        # Check for optional parameters and add them to payload if provided
        if stop_price:
            assert self.is_number(
                stop_price), 'The stop price provided is not a valid number'
            payload['stop_price']=round(stop_price, 2)
        if price:
            assert self.is_number(
                price), "The price provided is not a valid number"
            payload['price']=round(price, 2)

        # Create trade in Robinhood
        res=self.session.post(self.endpoints['orders'], data=payload)
        res.raise_for_status()
        return res.json()

    ###########################################################################
    #                           OTHER HELPFUL THINGS
    ###########################################################################

    def is_number(self, n):
        """Checks to validate that a given number is a number.
        
        Parameters
        ----------
        n : [int, float, complex]
            A variable to check the type of
        
        Returns
        -------
        bool
            True if a number, False otherwise.
        """

        return type(n) in [int, float, complex]
