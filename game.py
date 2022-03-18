import json
import random

from numpy import outer

def message(*text, sep : str = ' ', end : str = '\n' ):
    out = list()
    for word in text:
        out.append(str(word))
    out.append(end)
    out = sep.join(out)
    return out

# Класс пользователя игры
class User(object):

    def __init__(self, name):
        self.name = name

    # Метод жеребьевки
    def randomize(self):
        return random.randint(0,100)
        
# Класс игрока
class Player(User):

    def __init__(self, name, id):
        super().__init__(name)
        # Параметры статистики
        self.id = id
        self.effort = 0
        self.errors = 0

    def step(self, letter):
        if letter:
            return message('Попытка номер', self.effort + 1, '!\n','Введите название города!', 'Вам на', letter,'!')
        else:
            return message('Ваш ход первый!', 'Введите название города')

    def correct(self):
        self.effort = 0

    def incorrect(self):
        self.effort += 1
        self.errors += 1

# Класс компьютера
class Bot(User):

    def __init__(self, name):
        super().__init__('PC-' + name)
        # Режим сложности
        # input_mode = input('Включить повышенный режим сложности д/н: ')
        self.id = 0
        self.mode = False
        # if len(input_mode) > 0:
            # if input_mode[0] == 'д':
                # self.mode = True

    def step(self, data):
        len_data = len(data)
        # Вывод ответа в зависимости от сложности бота
        if len_data > 0:
            if self.mode:
                return str(data[0]).upper()
            else:
                return str(data[random.randint(1,len_data) - 1]).upper()
        else:
            # Вывод проигрыша
            return '/loos'

class Game(object):

    def __init__(self, name, id):
        # Сообщение
        self.message = ''
        # Список участников
        self.users = list()
        # Имена ботов
        bot_names = ('Терминатор', 'Валли', 'R2D2')
        # Текущий город
        self.word = dict()
        # Буква, на которую необходимо назвать город
        self.char = ''
        # Использованные города
        self.used = set()
        # Буквы на которые нет городов
        self.letters = set('ЁЪЫЬ')
        self.step = 0
        # Список загруженных городов
        self.load = list()
        self.data = dict()
        # Существование игры
        self.exist = True
        # Выдача приветствия
        self.info()
        self.users.append(Bot(bot_names[random.randint(0,2)]))
        self.users.append(Player(name, id))
        self.users.sort(key=User.randomize)

    # Формирование сообщения
    def __add_mes_line(self, line : str):
        if self.message:
            self.message += '\n' + line
        else:
            self.message += line

    # Отправка сообщения
    def send_message(self):
        out = self.message
        self.message = ''
        return out

    # Метод "Игра"
    def game(self):
        users_count = len(self.users)
        self.step %= users_count
        # Если остался 1 участник, то он победил
        if users_count < 2:
            if users_count == 1:
                self.__add_mes_line(message('Победитель', self.users[0].name,'!'))
                # self.__log('Победитель',self.users[0].name,'!')
                self.status()
                self.exist = False
        else:
            # Ход игрока
            self.__add_mes_line(message('Ходит игрок', self.users[self.step].name))
            if type(self.users[self.step]) == Bot:
                self.__bot(self.users[self.step])
            else:
                self.__player(self.users[self.step])

    # Метод контроля игроков            
    def __control(self, check):
        if check:
            # Если игрок не ответил или вышел, то удаление из списка
            loser = self.users.pop(self.step)
            self.__add_mes_line(message('Игрок с именем', loser.name, 'выбывает из игры!'))
            # self.__log('Игрок',loser.name,'выбыл!')
        else:
            self.step += 1
        self.game()
    
    # Метод игрока
    def __player(self, player_obj : Player):
        if player_obj.effort < 5:
            self.__add_mes_line(player_obj.step(self.char))
        else:
            self.__control(True)

    def reply(self, text : str, id):
        player_obj = self.users[self.step]
        current = bool(player_obj.id == id)
        if current:
            answer = text.strip().upper()
            if answer == '/INFO':
                self.info()
            else:
                if answer == '/EXIT':
                    self.__add_mes_line(message('Игрок', player_obj.name, 'покидает игру!'))
                    self.__control(True)
                else:
                    if not self.__check_list(answer):
                        player_obj.incorrect()
                        self.__player(self.users[self.step])
                    else:
                        player_obj.correct()
                        self.__control(False)
        return current

    # Метод бота
    def __bot(self, bot_obj : Bot):
        if self.char == '':
            l = ''
            while l == '':
                l = random.randint(ord('А'), ord('Я'))
                l = chr(l)
                if l in self.letters:
                    l = ''
                else:
                    self.__load_data(l)
        answer = ''
        while len(answer) == 0:
            out = False
            answer = bot_obj.step(self.load)
            if answer == '/loos':
                out = True
            else:
                if not self.__check_list(answer):
                    answer = ''
                    out = True
                else:
                    self.__add_mes_line(message('Игрок', bot_obj.name, 'ответил:', self.word['name']))
                    # self.__log(bot_obj.name,':',self.word['name'])
        self.__control(out)

    # Метод информации
    def info(self):
        if self.char == '':
            self.__add_mes_line('Приветствую вас в игре "Города России"!')
            self.__add_mes_line('В игре доступны следующие команды:')
            self.__add_mes_line('/info - получить информацию о последнем городе')
            self.__add_mes_line('/status - статистика игры.')
            self.__add_mes_line('/exit - выйти из игры и сдаться.')
        else:
            self.__add_mes_line(message('\nГород:', self.word['name']))
            self.__add_mes_line(message('\tМестоположение:', self.word['Region']))
            self.__add_mes_line(message('\tПервое упоминание:', self.word['Mention']))
            self.__add_mes_line(message('\tСтатус города:', self.word['Status']))

    # Статус игры
    def status(self):
        self.__add_mes_line('Информация о текущей игре:')
        self.__add_mes_line(message('Количество названных городов:', len(self.used)))
        for unit in self.users:
            if type(unit) == Player:
                self.__add_mes_line(message('  Игрок', unit.name,':'))
                self.__add_mes_line(message('  Общее количество ошибок:', unit.errors))

    # Метод проверки введенного города
    def __check_list(self, answer, dynam = False):
        out = True
        if self.char != answer[0] and self.char != '':
            out = False
            self.__add_mes_line('Первая буква города не соответствует!')
        else:
            if answer in self.used:
                out = False
                self.__add_mes_line('Город уже назывался!')
                self.__reload()
            else:
                if self.char == '':
                    l = answer[0]
                    if 'A' <= l <= 'Я' and not l in self.letters:
                        self.__load_data(l)
                if not answer in self.data:
                    out = False
                    self.__add_mes_line('Такого города не существует! Или неправильное имя!')
                else:
                    self.used.add(answer)
                    if dynam:
                        self.data[answer]['frequency'] += 1
                        self.__save()
                    self.__change(answer)
        return out

    # Метод изменения текущих параметров игры
    def __change(self, city : str):
        city.strip()
        self.word.update(self.data[city])
        if city[0] == 'Й':
            self.letters.add('Й')
            self.__add_mes_line('Так как единственный город на "Й" был назван, то дальше слов на эту букву не будет!')
        self.char = ''
        iter = -1
        while self.char == '':
            self.char = city[iter]
            if self.char in self.letters:
                self.char = ''
                iter -= 1
        self.__load_data(self.char)

    # Загрузка актуальной базы
    def __load_data(self, character, sor = True):
        file = open('russian/' + character + '.json', "r", encoding='utf-16')
        raw_data = json.load(file)
        file.close()
        self.data.clear()
        keys = raw_data["Cities"].keys()
        for key in keys:
            city = str(key).upper()
            self.data[city] = dict()
            self.data[city]['name'] = key
            for k, d in raw_data["Cities"][key].items():
                self.data[city][k] = d
        if sor:
            self.load = sorted(self.data, key=self.__key_sort)
            self.__reload()

    # Сортировка городов по частым ответам (для увеличения сложности игры)
    def __key_sort(self, data : dict):
        out = 0
        for key, inside in self.data.items():
            out = inside['frequency']
        return out

    # Метод очищения списка от использованных городов для передачи в бота
    def __reload(self):
        control = True
        while control:
            control = False
            for city in self.load:
                if city in self.used:
                    self.load.remove(city)
                    control = True

    # Метод ведения лога
    def __log(self, *info, mode = 'a', sep = ' '):
        out = list()
        for unit in info:
            out.append(str(unit))
        out = sep.join(out)
        out += '\n'
        file = open('game.log', mode, encoding='utf-16')
        file.write(out)
        file.close()

    # Сохранение актуализированных данных с учетом названного города
    def __save(self):
        out = dict()
        out['Count'] = len(self.data)
        out['Cities'] = dict()
        character = self.char
        normal = 0
        for key in self.data:
            if character == '':
                character = key[0]
            name = self.data[key]['name']
            out['Cities'][name] = dict()
            out['Cities'][name]['Region'] = self.data[key]['Region']
            out['Cities'][name]['Mention'] = self.data[key]['Mention']
            out['Cities'][name]['Status'] = self.data[key]['Status']
            out['Cities'][name]['frequency'] = self.data[key]['frequency']
            normal += self.data[key]['frequency'] ** 2
        normal = normal ** 0.5
        if normal < 1:
            normal = 1
        for key in out['Cities']:
            value = int(((out['Cities'][key]['frequency'] / normal) * 1000) + 0.5)
            if value < 1:
                value = 1
            out['Cities'][key]['frequency'] = value
        file = open('russian/' + character + '.json', "w", encoding='utf-16')
        json.dump(out, file, indent=4, ensure_ascii=False)
        file.close()
