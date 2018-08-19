import requests
from bs4 import BeautifulSoup
import time


class Finviz():

    session = None
    username = None
    password = None
    url = None

    def __init__(self):
        """Create session for requests

        """
        self.session = requests.session()

    def get_stocks(self, url):
        """Get stocks from a screen URL. 

        Parameters
        ----------
        url : str, optional
            URL for the screen

        Returns
        ------
        list
            list of stock symbols
        """

        self.url = url
        assert(self.url != None), "URL must be specified to get Finviz data."
        assert('v=111' in self.url), "URL must be from the 'Overview' screener page."
        
        symbol_list = list()

        while True:
            n_url = url + '&r={}'.format(len(symbol_list)+1)
            c = self.session.get(n_url).content

            soup = BeautifulSoup(c, "html.parser")

            for ticker in soup.find_all(name='a', class_='screener-link-primary', text=True):
                if ticker.text in symbol_list:
                    return symbol_list
                else:
                    symbol_list.append(ticker.text)
            time.sleep(1)

        return symbol_list