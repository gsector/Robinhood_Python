import requests
from bs4 import BeautifulSoup


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

        Yields
        ------
        Stock symbols from the screen
        """

        self.url = url
        assert(self.url != None), "URL must be specified to get Finviz data."
        assert('v=111' in self.url), "URL must be from the 'Overview' screener page."

        c = self.session.get(url).content
        soup = BeautifulSoup(c, "html.parser")

        for ticker in soup.find_all(name='a', class_='screener-link-primary', text=True):
            yield ticker.text
            # TODO: Get results when there are multiple pages
