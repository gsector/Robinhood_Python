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


orders_json = trader._raw_nonzero_positions(nonzero=True)

with open('test.json','w') as f:
    f.write(json.dumps(orders_json))