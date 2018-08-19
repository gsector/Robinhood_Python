import requests
from bs4 import BeautifulSoup
import re


class Zacks():    

    def __init__(self):
        """Initialize class
        
        """

        pass
    
    def quote(self, symbol):
        """Get the Zacks quote for a stock
        
        Parameters
        ----------
        symbol : str
            Stock symbol to get a quote for
        
        Returns
        -------
        str
            Request HTML
        """

        url = 'https://www.zacks.com/stock/quote/' + str(symbol).upper()
        
        headers = dict()
        headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'

        r = requests.get(url=url, headers=headers)

        return r.content
    
    def zacks_rank(self, symbol):
        """Return Zacks Rank for a Stock
        
        Parameters
        ----------
        symbol : str
            Stock ticker symbol.
        
        Returns
        -------
        str
            String digit representing Zacks rank.
                1 = Strong Buy      4 = Sell
                2 = Buy             5 = Strong Sell
                3 = Hold            ? = Error Retrieving or Unknown
        """
        
        # Get Zacks quote data
        symbol = symbol.upper()
        c = self.quote(symbol=symbol)

        # Parse data for rank
        soup = BeautifulSoup(c, "html.parser")
        rank_box = '{}'.format(soup.find(name='div', class_='zr_rankbox'))
        try:
            r = '(?:rank_view">\s*)([12345])'
            rank = re.search(r, rank_box).group(1)
        except:
            rank = '?'
        return rank

