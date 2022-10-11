from telethon import TelegramClient, events, sync
from binance.client import Client
from binance.helpers import round_step_size
import json
import requests

# Remember to use your own values from my.telegram.org!
api_id = 
api_hash = ''
client = TelegramClient('anon', api_id, api_hash)

# Remember to us your own values from binance
api_key = ''
api_secret = ''

client_b = Client(api_key=api_key, api_secret=api_secret,testnet = False)

def get_account_balance():
    balance = client_b.futures_account_balance()[6]['balance']
    return float(balance)

per = 5 # the percentage of the balance I am willing to buy with
balance = get_account_balance() * per / 100

@client.on(events.NewMessage(chats='Signals Global Channel'))
async def my_event_handler(event):
    message = event.raw_text
    type = message.split().pop(6)
    signals = message.split().pop(2)
    coin = message.split().pop(1)
    close = message.split().pop(4)
    spot = message.split().pop(0)
    symbol = coin[1:]

    symbol_info = client_b.get_ticker(symbol=symbol)
    symbol_price = float(symbol_info['lastPrice'])
    quantity = int(10 * (balance / symbol_price))

        # get ticksize

    def get_min_quant(symbol):
        info = client_b.futures_exchange_info()
        for item in info['symbols']:
              if item['symbol'] == symbol:
               for f in item['filters']:
                   if f['filterType'] == 'PRICE_FILTER':
                      return f['tickSize']
    tick_size = float(get_min_quant(symbol))
    print(tick_size)

    #target and stop loss
    sl = float(symbol_price - (symbol_price * 8 / 100))
    stoploss = round_step_size(sl, tick_size)
    tp1 = float(symbol_price + (symbol_price * 10 / 100))
    take_profit1 = round_step_size(tp1, tick_size)
    tp2 = float(symbol_price + (symbol_price * 20 / 100))
    take_profit2 = round_step_size(tp2, tick_size)
    tp3 = float(symbol_price + (symbol_price * 30 / 100))
    take_profit3 = round_step_size(tp3,tick_size)

    #quantity to sell on target
    quantity_tp1 = int(quantity * 60 / 100)
    quantity_tp2 = int(quantity * 20 / 100)
    quantity_tp3 = int(quantity * 20 / 100)


    # creating order with condtional match

    if type == "Scalp" and signals == "New" and quantity != 0:
        # change the leverage and margin type
        client_b.futures_change_leverage(symbol=symbol, leverage=10)
       #  #order to buy
        client_b.futures_create_order(symbol=symbol, side='BUY', type='MARKET', quantity=quantity, isolated=True,)
       #  #stop loss order
        client_b.futures_create_order(symbol=symbol, side='SELL', type='STOP_MARKET', stopPrice=stoploss, closePosition='true')
       # #take take_profit1
        client_b.futures_create_order(symbol=symbol, side='SELL', type='LIMIT',timeInForce='GTC',quantity=quantity_tp1, price=take_profit1,reduceOnly='true')
        #take take_profit2
        client_b.futures_create_order(symbol=symbol, side='SELL', type='LIMIT',timeInForce='GTC',quantity=quantity_tp2, price=take_profit2,reduceOnly='true')
        #take take_profit3
        client_b.futures_create_order(symbol=symbol, side='SELL', type='LIMIT',timeInForce='GTC',quantity=quantity_tp3, price=take_profit3,reduceOnly='true')
        print("your order is place.")
    elif close == "closed.":
        print("your order is closed.")
    else:
        print(message)

client.start()
client.run_until_disconnected()