#----- A simple TCP client program in Python using send() function -----
#----- A simple TCP client program in Python using send() function -----

import MetaTrader5 as mt5
import time
from datetime import datetime
import json
import random



#Login to account
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() fai5led, error code =",mt5.last_error())
    quit()
 
# display data on MetaTrader 5 version
print(mt5.version())


# now connect to another trading account specifying the password
account=5008311499
authorized=mt5.login(account, password="whh4zghu", server="MetaQuotes-Demo")
if authorized:
    print("Account authorized")
else:
    print("fail")
print("hi")
iteration = input("iteration ").upper()
#-------------------------------------
#F U N C T I O N S 
#-------------------------------------
def column(matrix, i):
    return [row[i] for row in matrix]
def check_settings(iteration):
    with open(iteration+'//settings.txt', 'r') as f:
        settings = json.loads(f.read())
    return settings
def upload_settings(settings,iteration):
    with open(iteration+'//settings.txt', 'w') as f:
        json.dump(settings, f)
    print("CONSOLE: SETTINGS UPLOAD")
def message(key, message,typ):
    if typ.upper() == "READ":
        with open('messages.txt', 'r') as f:
            dct = json.loads(f.read())
        return dct[key]
    elif typ.upper() == "SEND":
        with open('messages.txt', 'r') as f:
            dct = json.loads(f.read())
        dct[key] = message
        with open('messages.txt', 'w') as f:
            json.dump(dct, f)
        return "sent"
def filter_orders_magic(magic,switch=False):
            output = []
            orders=mt5.positions_get(magic=magic)
            #orders=mt5.positions_get()
            for order in orders:
                if int(order[6]) == magic:
                    output.append(order)
            orders = output
            output = []
            for order in orders:
                ticket = order[0]
                price = order[10]
                position = order[5]#0 if buy and 1 if sell
                if switch == False:
                    if position ==0:
                        position = "buy"
                    elif position == 1:
                        position = "sell"
                elif switch == True:
                    if position ==0:
                        position = "sell"
                    elif position == 1:
                        position = "buy"
                volume = order[9]
                symbol = order[16]
                profit = order[15]
                trade_magic =  order[6]
                output.append([ticket,price,position,volume,symbol,trade_magic,profit])
            return output
def calculate_spread_magic(magic):
    orders = filter_orders_magic(magic)
    spread = 0
    for order in orders:
        profit = order[6]
        spread-= profit
    return spread
def status_update(status,orders,magic,volume_coefficent):
    orders = filter_orders_magic(magic)
    if status == "restart" and len(orders) == 0:
        status = "regular"
    return status, volume_coefficent
def calc_lc(leverage,leverage_coef,orders,leverage_coefficient,start=False):
    global og_balance
    account_info_dict = mt5.account_info()._asdict()
    balance = account_info_dict.get('balance')
    if len(orders) == 0 or start == True:
        leverage_coefficient = balance/100000*leverage_coef*leverage/0.01
    return leverage_coefficient
def time_zone(dt,diff):
    from datetime import datetime, timedelta
    date = dt + timedelta(hours=diff)
    return date.strftime("%Y.%m.%d %H:%M:%S")
def footer(iteration):
    from datetime import datetime
    now = datetime.now()
    current_time = time_zone(now,-8)
    print(current_time)
    print("ITER:", iteration)
    print("---------------------")
def str_to_bool(string):
    if string.upper()== "TRUE":
        return True
    elif string.upper() == "FALSE":
        return False
    return False
def start_func(start,leverage,leverage_coef,orders,leverage_coefficient):
    if start == True:
        leverage_coefficient = calc_lc(leverage,leverage_coef,orders,leverage_coefficient,True)
    return leverage_coefficient,False
#-------------------------------------
#M A I N   V A R I A B L E S
#-------------------------------------
status = "regular"
prev_orders = []
volume_coefficient = 1
full_close_flag = "False"
restart_flag = "False"
volume_dict = {}
ticket_dict = {}
stored_values = {}
settings = check_settings(iteration)
settings["hi"]="True"
account_info_dict = mt5.account_info()._asdict()
balance = account_info_dict.get('balance')
og_balance = balance
timer = 61
leverage_coefficient = 1
interval = 60
start = True
#-------------------------------------
#O B S C U R E    V A R I A B L E S
#-------------------------------------
obscure_prev_orders = []
obscure_volume_dict = {}
obscure_ticket_dict = {}
#-------------------------------------
while True:
    #-------------------------------------------------------
    # C H E C K I N G   S E T T I N G S
    #-------------------------------------------------------
    if timer > interval:
        settings_temp = check_settings(iteration)
        if settings_temp != settings:
            settings = settings_temp
        
            #M A I N   S E T T I N G S
            magic = settings["magic"]
            replace_magic = settings["replace_magic"]
            diff = settings ["diff"]
            leverage = settings["leverage"]
            leverage_coef = settings["leverage_coef"]
            interval = settings["interval"]
            saftey = settings["saftey"]
            
            #O B S C U R E    S E T T I N G S
            obscure_magic = settings["obscure_magic"]
            obscure_magic_replace = settings["obscure_magic_replace"]
            
            #---------------
            print("CONSOLE: SETTINGS CHANGED")
            footer(iteration)
    leverage_coefficient, start = start_func(start,leverage,leverage_coef,[],leverage_coefficient)
    #-------------------------------------------------------
    # O B S C U R I N G   T R A D E S
    #-------------------------------------------------------
    obscure_new_trades = []
    obscure_orders = filter_orders_magic(obscure_magic,True)
    #order opened
    prev_orders_tickets = column(obscure_prev_orders,0)
    for order in obscure_orders:
        if order[0] not in prev_orders_tickets:
            print("OBSC: ORDER OPEN DETECTED")
            footer(iteration)
            lst = order
            lst.append("open")
            obscure_new_trades.append(lst)
    #Order closed
    orders_tickets = column(obscure_orders,0)
    for order in obscure_prev_orders:
        if order[0] not in orders_tickets:
            print("OBSC: ORDER CLOSE DETECTED")
            footer(iteration)
            lst = order
            lst.append("close")
            obscure_new_trades.append(lst)
    from send_orders import send_orders
    obscure_volume_dict,obscure_ticket_dict = send_orders(obscure_magic_replace,mt5,obscure_volume_dict,obscure_ticket_dict,1,1,obscure_new_trades)
    obscure_prev_orders = obscure_orders

    #-------------------------------------------------------3
    # M A I N
    #-------------------------------------------------------
    new_trades = []
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S") 
    orders = filter_orders_magic(magic)
    account_info_dict = mt5.account_info()._asdict()
    balance = account_info_dict.get('balance')
    equity = account_info_dict.get('equity')
    status, volume_coefficient = status_update(status,orders,magic,volume_coefficient)
    leverage_coefficient = calc_lc(leverage,leverage_coef,orders,leverage_coefficient)
    from transfer_trades import transfer_trades
    new_trades = transfer_trades(magic,orders,prev_orders,diff,status,new_trades,mt5)
    from send_orders import send_orders
    volume_dict,ticket_dict = send_orders(replace_magic,mt5,volume_dict,ticket_dict,volume_coefficient,leverage_coefficient,new_trades)
    #----------
    new_trades = []
    emergency_spread = calculate_spread_magic(magic)
    emergency = False
    if emergency_spread > diff + saftey and status != "full close":
        print("CONSOLE: FULL CLOSE INITIATED ON SAFTEY:",saftey)
        emergency = True
    elif emergency_spread < diff - saftey and status == "full close":
        emergency = True
        print("CONSOLE: RESTART INITIATED ON SAFTEY:",saftey)
    if timer > interval or emergency == True:
        timer = 0
        new_trades = []
        from full_close import full_close
        new_trades,status,temp,full_close_completed = full_close(magic,replace_magic, iteration,orders,status,diff,new_trades,mt5)
        if temp != {}:
            stored_values = temp
        if full_close_completed == False:
            from restart import restart
            new_trades, status,volume_coefficient = restart(magic,replace_magic,iteration,orders,diff,status,new_trades,stored_values,mt5)
        from send_orders import send_orders
        volume_dict,ticket_dict = send_orders(replace_magic,mt5,volume_dict,ticket_dict,volume_coefficient,leverage_coefficient,new_trades)
    #----------
    prev_orders = orders
    timer += 0.13
    time.sleep(0.1)
        
