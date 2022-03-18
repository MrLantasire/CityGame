from threading import Timer
import requests
import game
import config

TOKEN = config.telegram_token
url = "https://api.telegram.org/bot"
OFFSET = 0
games = dict()

def send_message(id, message : str):
    metod = "/sendMessage"
    request = url + TOKEN + metod
    data = dict()
    data["chat_id"] = id
    data["text"] = message
    r = requests.post(request, data=data)
    if r.status_code // 100 != 2:
        print("Сообщение не доставлено!")
    
def get_message(offset):
    metod = "/getUpdates"
    request = url + TOKEN + metod
    data = dict()
    data['offset'] = offset
    out = requests.get(request, data=data).json()
    if out['ok']:
        out = out['result']
    else:
        print("Ничего не получено!")
        out = ''
    return out

def check_id(id):
    global games
    return id in games

def main():
    global OFFSET
    proc = Timer(1, main)
    del_list = list()

    data = get_message(OFFSET)
    for unit in data:
        if unit['update_id'] > OFFSET:
            OFFSET = unit['update_id']
            if 'message' in unit:
                chat_data = unit['message']
                message = chat_data['text'].strip().upper()
                c_id = chat_data['chat']['id']
                name = chat_data['from']['first_name']
                p_id = chat_data['from']['id']
                if message == '/GAME':
                    games[c_id] = game.Game(name, p_id)
                    games[c_id].game()
                    print('Играет', name)
                elif message == '/STATUS':
                    if check_id(c_id):
                        games[c_id].status()
                    else:
                        send_message(c_id, 'Нет активной игры!')        
                else:
                    if check_id(c_id):
                        if not games[c_id].reply(message,p_id):
                            print('Ошибка игрока!')
    for key in games:                
        reply = games[key].send_message()
        if reply:
            send_message(key,reply)
        if not games[key].exist:
            del_list.append(key)
    for key in del_list:
            games.pop(key)
            print('Удален')

    proc.start()

def init():
    global OFFSET
    data = get_message(-1)
    for unit in data:
        OFFSET = unit['update_id']

init()
main()
