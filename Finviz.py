import requests
from bs4 import BeautifulSoup

class Finviz():

    session = None
    username = None
    password = None
    url = None

    def __init__(self):
        self.session = requests.session()
    
    def login(self, username=None, password=None):
        self.username, self.password = username, password
        if self.username==None or self.password==None:
            print('Missing username or password to log into Finviz')
            return None
        else:
            #TODO: Login to Finviz
            return None
    
    def get_stocks(self, url=None):
        self.url = url
        assert(self.url!=None), "URL must be specified to get Finviz data."
        assert('v=111' in self.url), "URL must be from the 'Overview' screener page."
        
        c = self.session.get(url).content
        soup = BeautifulSoup(c, "html.parser")
        
        for ticker in soup.find_all(name='a', class_='screener-link-primary', text=True):
            yield ticker.text



