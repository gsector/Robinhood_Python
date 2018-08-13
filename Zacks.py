import requests
from bs4 import BeautifulSoup
import re


class Zacks():    

    def __init__(self):
        pass
    
    def quote(self, symbol=None):
        #TODO: Add documentation
        assert symbol, 'A symbol must be provided to get quote information.'
        url = 'https://www.zacks.com/stock/quote/' + str(symbol).upper()
        
        headers = dict()
        headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'

        r = requests.get(url=url, headers=headers)

        return r.content
    
    def zacks_rank(self, symbol=None):
        #TODO: Add documentation
        
        c = self.quote(symbol=symbol)
        soup = BeautifulSoup(c, "html.parser")

        rank_box = '{}'.format(soup.find(name='div', class_='zr_rankbox'))
        return re.search('(?:rank_view">\s*)([12345])', rank_box).group(1)

