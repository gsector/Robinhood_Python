from Robinhood import Robinhood
import config
import json

trader = Robinhood()
try:
    test = trader.login(username = config.robinhood['username'],
                    password = config.robinhood['password']
                )
except:
    print('Exiting after Failed Robinhood Login.')


test = trader.unsettled_funds()
print('{}'.format(test))