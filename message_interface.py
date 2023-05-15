import json
#---------------------------------
# F U N C T I O N S
#---------------------------------
def manage_message(key, message,typ):
    if typ.upper() == "READ":
        with open('messages.txt', 'r') as f:
            dct = json.loads(f.read())
        if key in dct.keys():
            return dct[key]
        else:
            return "bad key"
    elif typ.upper() == "SEND":
        with open('messages.txt', 'r') as f:
            dct = json.loads(f.read())
        dct[key] = message
        with open('messages.txt', 'w') as f:
            json.dump(dct, f)
        return "sent"
    return "error"
def open_messages():
    with open('messages.txt', 'r') as f:
        dct = json.loads(f.read())
    return dct
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
#---------------------------------
# M A I N
#---------------------------------
while True:
    key = input("key: ")
    message = input("message: ")
    typ = input("type: ")
    if key == "MENU":
        menu = open_messages()
        for keys in menu.keys():
            print(keys,":",menu[keys])
    else:
        print(manage_message(key,message,typ))
    footer()


