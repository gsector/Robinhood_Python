""" 
    Vast majority of this Robinhood.py was copied with slight modifications from:
        Robinhood.py: a collection of utilities for working with Robinhood's Private API
        https://github.com/Jamonek/Robinhood
"""


import requests

class Robinhood:
    """Wrapper class for fetching/parsing Robinhood endpoints """

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
        "instruments": "https://api.robinhood.com/instruments/",
        "margin_upgrades": "https://api.robinhood.com/margin/upgrades/",
        "markets": "https://api.robinhood.com/markets/",
        "notifications": "https://api.robinhood.com/notifications/",
        "orders": "https://api.robinhood.com/orders/",
        "cancel_order": "https://api.robinhood.com/orders/",  # API expects https://api.robinhood.com/orders/{{orderId}}/cancel/
        "password_reset": "https://api.robinhood.com/password_reset/request/",
        "portfolios": "https://api.robinhood.com/portfolios/",
        "positions": "https://api.robinhood.com/positions/",
        "quotes": "https://api.robinhood.com/quotes/",
        "historicals": "https://api.robinhood.com/quotes/historicals/",
        "document_requests": "https://api.robinhood.com/upload/document_requests/",
        "user": "https://api.robinhood.com/user/",
        "watchlists": "https://api.robinhood.com/watchlists/",
        "news": "https://api.robinhood.com/midlands/news/",
        "fundamentals": "https://api.robinhood.com/fundamentals/",
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


    def login(self, 
              username=None, 
              password=None):
        """Save and test login info for Robinhood accounts
        Args:
            username (str): username
            password (str): password
        Returns:
            (bool): received valid auth token
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
            self.session.headers.update({'Authorization': 'Token ' + auth_token})
            return True

        return False


    def get_account(self):
        """Fetch account information
            Returns:
                (:obj:`dict`): `accounts` endpoint payload
        """

        res = self.session.get(self.endpoints['accounts'])
        res.raise_for_status()  #auth required
        res = res.json()

        return res['results'][0]
    
    def buying_power(self):
        #TOD: Improve this documentation
        """Fetch buying power
            Returns:
                float
        """
        return self.cash() - self.cash_held_for_orders()

    def unsettled_funds(self):
        #TOD: Improve this documentation

        return float(self.get_account()['unsettled_funds'])
    
    def cash_held_for_orders(self):
        #TOD: Improve this documentation
        """Fetch buying power
            Returns:
                float
        """
        return float(self.get_account()['cash_held_for_orders'])

    def cash(self):
        #TOD: Improve this documentation
        return float(self.get_account()['cash'])
    
    def cash_for_buying(self):
        #TODO: Improve documentation
        return self.buying_power() - self.cash_held_for_orders()


    def logout(self):
        """Logout from Robinhood
        
        Returns:
            (:obj:`requests.request`) result from logout endpoint
        """

        try:
            req = self.session.post(self.endpoints['logout'])
            req.raise_for_status()
        except requests.exceptions.HTTPError as err_msg:
            print('Failed to log out ' + repr(err_msg))

        self.session.headers.update({'Authorization': None})

        return req

    
    ###########################################################################
    #                           GET ORDERS
    ###########################################################################

    def orders(self, order_id=None):
        """Returns the user's orders data
            Args:
                order_id (str): Optional order ID to only return order for the ID specified
            
            Returns:
                (:object: `list`): list of JSON dicts, one for each individual order
        """
        
        # Return all the orders from the first page
        if order_id:
            url = self.endpoints['orders'] + order_id + '/'
        else:
            url = self.endpoints['orders']
        orders_json = self.session.get(url).json()
    
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
        """Returns the user's orders that haven't been executed yet
            
            Returns:
                (:object: `list`): list of JSON dicts for orders that haven't been executed
        """
        # Generate orders
        for order in self.orders():
            if order['cancel']:
                yield order    


    def open_sell_orders(self):
        """Returns the user's open sell orders that haven't been executed yet
            
            Returns:
                (:object: `list`): list of orders that haven't been executed
        """
        ''' Contents:
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
                "executions": [] '''

        # Generate orders
        for order in self.open_orders():
            if order['side'] == 'sell':
                yield order
        
    def open_buy_orders(self):
        """Returns the user's open sell orders that haven't been executed yet
            
            Returns:
                (:object: `list`): list of orders that haven't been executed
        """
        ''' Contents:
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
                "executions": [] '''

        # Generate orders
        for order in self.open_orders():
            if order['side'] == 'buy':
                yield order



    ###########################################################################
    #                           GET POSITIONS
    ###########################################################################

    def _raw_positions(self):
        """Returns list of securities' symbols that the user has shares in 
            Returns:
                (:object: `dict`): Non-zero positions
        """

        # Return all the securities from the first page
        return self.session.get(self.endpoints['positions']).json()

    def positions(self):
        """Returns list of securities' symbols that the user has shares in 
            Returns:
                (:object: `dict`): Non-zero positions
        """
        ''' Contents:
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
                'account' '''

        positions = self._raw_positions()

        for position in positions['results']:
                yield position

        # Get additional pages of securities
        while positions['next']:
            positions = self.session.get(positions['next']).json()
            for position in positions['results']:
                yield position

    def _raw_nonzero_positions(self, nonzero=None):
        if nonzero is True:
            payload = {'nonzero': 'true'}
        else:
            payload = {}
            
        return self.session.get(self.endpoints['positions'], params = payload).json()

    def nonzero_positions(self, nonzero=None):
        """Returns positions with shares held > 0

            Returns:
                (:object: 'dict'): Positions
        """
        
        if nonzero is True:
            positions = self._raw_nonzero_positions(nonzero=True)
        else:
            positions = self._raw_nonzero_positions(nonzero=None)
        
        for position in positions['results']:
            yield position
        
        while positions['next']:
            positions = self.session.get(positions['next']).json()
            for position in positions['results']:
                yield position



    ###########################################################################
    #                           GET DATA 
    ###########################################################################

    def instrument_results(self, url):
        """Fetch data from instrument url

            Args:
                url (str): Robinhood instrument URL

            Returns:
                (:dict:): information from instrument URL 
        """

        '''Contents:
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
                'country' '''
        
        res = self.session.get(url)
        return res.json()


    def instruments(self, stock):
        """Fetch instruments endpoint
            Args:
                stock (str): stock ticker

            Returns:
                (:obj:`dict`): JSON contents from `instruments` endpoint
        """

        res = self.session.get(self.endpoints['instruments'], params={'query': stock.upper()})
        res.raise_for_status()
        res = res.json()

        # if requesting all, return entire object so may paginate with ['next']
        if (stock == ""):
            return res

        return res['results']


    def quote_data(self, stock=''):
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

        url = None

        if stock.find(',') == -1:
            url = str(self.endpoints['quotes']) + str(stock) + "/"
        else:
            url = str(self.endpoints['quotes']) + "?symbols=" + str(stock)

        #Check for validity of symbol
        try:
            req = requests.get(url)
            req.raise_for_status()
            data = req.json()
        except:
            data = None
        
        return data
    
    
    def get_historical_quotes(self,
                              stock, 
                              interval = 'day', 
                              span='year'):
        """Fetch historical data for stock
            Note: valid interval/span configs
                interval = 5minute | 10minute + span = day, week
                interval = day + span = year
                interval = week
            Args:
                stock (str): stock ticker(s) for multiple - separate with comma
                interval (str): resolution of data
                span (str): length of data
            Returns:
                (:obj:`dict`) values returned from `historicals` endpoint """

        ''' Contents: <data>['results']['historicals']
                "begins_at"    # _ba = datetime.datetime.strptime(begins_at, '%Y-%m-%dT%H:%M:%SZ')
                "open_price"
                "interpolated"
                "volume"
                "high_price"
                "low_price"
                "close_price"
                "session"  '''
        
        params = {'symbols': stock,
                  'interval': interval,
                  'span': span }

        res = self.session.get(self.endpoints['historicals'], params=params)
        return res.json()


    ###########################################################################
    #                           TRADE ACTIONS
    ###########################################################################

    # Need a function to submit a single market stop loss order sell

    # Need a function to submit a single market price order sell

    def cancel_order(self, order_id=None, url=None):
        """Cancels a sell order by either url or id
            Args:
                (:str: 'id'): ID of the order to be cancelled
                (:str: 'url'): Cancel url for the order
            Returns:
                (boolean): True = orders cancelled. False = orders unable to be cancelled.
                """
        
        if order_id is not None: # API expects https://api.robinhood.com/orders/{{orderId}}/cancel/
            url = self.endpoints['cancel_order'] + str(order_id) + '/cancel/'
        res = self.session.post(url)

        if res.json == {}:
            return True
        else:
            return False

    def cancel_all_sell_orders(self):
        """Cancels all sell orders for the user

            Returns:
                (float): # of cancelled orders / Total # of sell orders.
        """

        total = 0
        success = 0
        for order in self.open_sell_orders():
            total += 1
            res = self.session.post(order['cancel'])
            if res is True:
                success += 1

        if success == total:
            return True
        else:
            return False
    

    def place_stop_limit_order(self,
                                instrument,
                                quantity=1,
                                trigger='stop',
                                order_type='limit',
                                stop_price=0.0,
                                price=0.0, # Limit price
                                side='sell',
                                time_in_force='gtc'):
        """Place an order with Robinhood
            Notes:
                OMFG TEST THIS PLEASE!
                Just realized this won't work since if type is LIMIT you need to use "price" and if
                a STOP you need to use "stop_price".  Oops.
                Reference: https://github.com/sanko/Robinhood/blob/master/Order.md#place-an-order
            Args:
                instrument (str): the instrument URL to be traded
                quantity (float): quantity of stocks in order
                trigger (str): 'immediate' or 'stop'
                type (str): type of order ('market' or 'limit')
                stop_price (float): stop price to trigger the order
                price (float): for a limit order, this is the limit price
                side (str): 'sell' or 'buy'
                time_in_force (str): 'gtc' or 'gfd' 
            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """

        payload = {
            'account': self.get_account()['url'],
            'instrument': instrument,
            'symbol': self.instrument_results(url=instrument)['symbol'],
            'quantity': quantity,
            'trigger': trigger,
            'type': order_type,
            'stop_price': round(stop_price, 2),
            'price': round(price, 2),
            'side': side,
            'time_in_force': time_in_force
        }

        #data = 'account=%s&instrument=%s&price=%f&quantity=%d&side=%s&symbol=%s#&time_in_force=gfd&trigger=immediate&type=market' % (
        #    self.get_account()['url'],
        #    urllib.parse.unquote(instrument['url']),
        #    float(bid_price),
        #    quantity,
        #    transaction,
        #    instrument['symbol']
        #)
        res = self.session.post(self.endpoints['orders'], data=payload)
        # res.raise_for_status()

        return res.json()
