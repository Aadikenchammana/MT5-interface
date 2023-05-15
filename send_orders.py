def send_orders(replace_magic,mt5,volume_dict,ticket_dict,volume_coefficient,leverage_coefficient,new_trades):
    for order in new_trades:
        print("SEND: DATA")
        print(ticket_dict)
        print(order, len(new_trades))
        magic = replace_magic

        #O P E N   T R A D E
        if "open" in order:
            print("SEND: OPEN ORDER SENT")
            ticket_dict,volume_dict = open_trade(order,volume_coefficient,leverage_coefficient,magic,ticket_dict,volume_dict,mt5)
        
        #R E S T A R T
        if "restart" in order:
            print("SEND: RESTART ORDER SENT")
            ticket_dict,volume_dict = restart_trade(order,volume_coefficient,leverage_coefficient,magic,ticket_dict,volume_dict,mt5)
        
        #C L O S E   T R A D E
        if "close" in order:
            print("SEND: CLOSE ORDER SENT")
            ticket_dict, volume_dict = close_trade(order,volume_coefficient,leverage_coefficient,magic,ticket_dict,volume_dict,mt5)
        
        #F U L L   C L O S E
        if "full close" in order:
            print("SEND: FULL CLOSE ORDER SENT")
            ticket_dict, volume_dict = full_close_trade(order,volume_coefficient,leverage_coefficient,magic,ticket_dict,volume_dict,mt5)
            
    if new_trades != []:
        footer()
    return volume_dict,ticket_dict
def time_zone(dt,diff):
    from datetime import datetime, timedelta
    date = dt + timedelta(hours=diff)
    return date.strftime("%Y.%m.%d %H:%M:%S")
def footer():
    from datetime import datetime
    now = datetime.now()
    current_time = time_zone(now,-8)
    print(current_time)
    print("---------------------")
def cont(retcode):
    lst = [10013,10014,10017,10018,10019,10009]
    if int(retcode) in lst:
        return True
    return False
def check_volume(mt5,volume,max_orders):
    import math
    total = volume*100000*max_orders
    account_info_dict = mt5.account_info()._asdict()
    margin = account_info_dict.get('equity')*account_info_dict.get('leverage')
    if total/margin > 0.75:
        print("SEND: VOLUME ADJ", volume, max_orders)
        footer()
        volume = margin*0.75/max_orders
        volume = volume/100000
    return math.floor(volume*100)/100

def restart_trade(trade,volume_coefficient,leverage_coefficient,magic,ticket_dict,volume_dict,mt5):
    ticket = trade[0]
    price = trade[1]
    position = trade[2]
    volume = trade[3]
    symbol = trade[4]
    #
    #
    for tik in volume_dict.keys():
        volume = volume_dict[tik]*volume_coefficient
    import math
    volume = check_volume(mt5,volume,5)
    volume = math.floor(volume*100)/100
    if volume < 0.01:
        volume = 0.01
    volume_dict[ticket] = volume
    while True:
        new_ticket,retcode = open_order(position,symbol,100,volume,magic,mt5)
        if new_ticket != 0:
            print(new_ticket)
            ticket_dict[ticket] = int(new_ticket)
        else:
            print("SEND: NEW TICKET EQUAL TO ZERO")
        import time
        if cont(retcode):
            break
        else:
            print("SEND: ORDER SEND FAIL,",retcode)
            time.sleep(0.1)
    
    return ticket_dict, volume_dict

def close_trade(trade,volume_coefficient,leverage_coefficient,magic,ticket_dict,volume_dict,mt5):
    ticket = trade[0]
    position = trade[2]
    symbol = trade[4]
    new_ticket = ticket_dict[ticket]
    new_volume = volume_dict[ticket]
    while True:
        retcode = close_order(position, new_ticket, symbol, new_volume, 100,mt5)
        if cont(retcode):
            del ticket_dict[ticket]
            del volume_dict[ticket]
            break
        else:
            print("SEND: ORDER SEND FAIL,",retcode)
            import time
            time.sleep(0.1)
    return ticket_dict, volume_dict

def full_close_trade(trade,volume_coefficient,leverage_coefficient,magic,ticket_dict,volume_dict,mt5):
    ticket = trade[0]
    position = trade[2]
    symbol = trade[4]
    new_ticket = ticket_dict[ticket]
    new_volume = volume_dict[ticket]
    while True:
        retcode = close_order(position, new_ticket, symbol, new_volume, 100,mt5)
        if cont(retcode):
            break
        else:
            print("SEND: ORDER SEND FAIL,",retcode)
            import time
            time.sleep(0.1)
    return ticket_dict, volume_dict

def open_trade(trade,volume_coefficient,leverage_coefficient,magic,ticket_dict,volume_dict,mt5):
    ticket = trade[0]
    price = trade[1]
    position = trade[2]
    volume = trade[3]
    symbol = trade[4]
    #
    #
    volume = volume*volume_coefficient*leverage_coefficient
    volume = check_volume(mt5,volume,5)
    import math
    volume = math.floor(volume*100)/100
    if volume < 0.01:
        volume = 0.01
    volume_dict[ticket] = volume
    while True:
        new_ticket,retcode = open_order(position,symbol,100,volume,magic,mt5)
        if new_ticket != 0:
            print(new_ticket)
            ticket_dict[ticket] = int(new_ticket)
        else:
            print("SEND: NEW TICKET EQUAL TO ZERO")
        import time
        if cont(retcode):
            break
        else:
            print("SEND: ORDER SEND FAIL,",retcode)
            time.sleep(0.1)
    
    return ticket_dict, volume_dict


def open_order(position,tempsymbol,deviation,volume,magic,mt5):
    point = mt5.symbol_info(tempsymbol).point
    if position == "buy":
        typ = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(tempsymbol).ask
    if position == "sell":
        typ = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(tempsymbol).bid
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": tempsymbol,
        "volume": volume,
        "type": typ,
        "price": price,
        "deviation": deviation,
        "magic": magic,
        "comment": "",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
     
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        result_dict=result._asdict()
        for field in result_dict.keys():
            if field=="request":
                traderequest_dict=result_dict[field]._asdict()
    print(result)
    print(position+" order:", request["volume"], request["price"],request["comment"])
    return ("{}".format(result.order)),("{}".format(result.retcode))

def close_order(position, position_id, symbol, volume, deviation,mt5):
    if position == 'sell':
        trade_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).ask
    elif position =='buy':
        trade_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).bid

    close_request={
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": trade_type,
        "position": position_id,
        "price": price,
        "deviation": deviation,
        "type_time": mt5.ORDER_TIME_GTC, # good till cancelled
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    # send a close request
    result=mt5.order_send(close_request)
    print(result)
    print("TRADE CLOSE:",position_id)
    return ("{}".format(result.retcode))
