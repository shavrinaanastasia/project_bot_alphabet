from pathlib import Path
import os
import telebot
import flask
import conf
import random
import sys
import matplotlib.pyplot as plt


WEBHOOK_URL_BASE = "https://{}:{}".format(conf.WEBHOOK_HOST, conf.WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(conf.TOKEN)


symbols_dict = {"Ա": "А", "Բ": "Б", "Գ": "Г", "Դ": "Д", "Ե": "Е", "Զ": "З", "Է": "Э", "Ը": "Ы", "Թ": "Т", "Ժ": "Ж", "Ի": "И", "Լ": "Л", "Խ": "Х", "Ծ": "Ц", "Կ": "К", "Հ": "Г", "Ձ": "Дз", "Ղ": "Г", "Ճ": "Ч", "Մ": "М", "Յ": "И", "Ն": "Н", "Շ": "Ш", "Ո": "В", "Չ": "Ч", "Պ": "П", "Ջ": "Дж", "Ռ": "Р", "Ս": "С", "Վ": "В", "Տ": "Т", "Ր": "Р", "Ց": "Ц", "Ւ": "У", "Փ": "Ф", "Ք": "К", "Օ": "О", "Ֆ": "Ф"}

bot = telebot.TeleBot(conf.TOKEN, threaded=False)
# ставим новый вебхук = Слышь, если кто мне напишет, стукни сюда — url
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)

app = flask.Flask(__name__)

score = 0
scores = {
    '1': 0,
    '2': 0,
    '3': 0,
    '4': 0
}

stop = 0
mode = None
current_round = 0
transliteration_dict = {}
is_bot_started = False
plots = 0

@bot.message_handler(commands=['start', 'help'])
def start(message):
    global is_bot_started
    is_bot_started = True
    bot.reply_to(message, "Здравствуйте! Это бот, который помогает учить армянский алфавит. Выберите режим: 1 (запоминание), 2 (тест), 3 (сложная игра) или 4 (образцы письменности, написанные от руки)")

# график для пользователя
@bot.message_handler(commands=['stop'])
def stop_handler(message):
    global is_bot_started, mode, score, scores, plots
    if is_bot_started:
        is_bot_started = False
        mode = None
        plots += 1
        bot.reply_to(message, f"Итоговый счет: {score}")
        score = 0
        plt.bar(scores.keys(), scores.values())
        plt.xlabel('Режимы')
        plt.ylabel('Счет')
        plt.title('Счет игрока в разных режимах')
        path = "/home/ashavrina/mysite/static/graph/plot_1.png"
        plt.savefig(path)  # Сохраняем график как изображение
        with open(path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)




# тут выбор режима
@bot.message_handler(func=lambda message: is_bot_started and mode is None)
def mode_handler(message):
    global mode
    mode = int(message.text)
    if mode == 1:
        bot.reply_to(message, "В режиме обучения вам будут присылаться буквы и их принятые транслитерации на латинице. После каждого сообщения введите нужную транслитерацию для запоминания. Если захотите закончить игру или попробовать другой режим, введите /stop ")
        send_random_symbol(message)
    elif mode == 2:
        bot.reply_to(message, "В режиме тестирования вам будут присылаться только буквы. После каждого сообщения введите нужную транслитерацию. Если захотите закончить игру или попробовать другой режим, введите /stop ")
        send_random_test(message)
    elif mode == 4:
        bot.reply_to(message, "В этом режиме бот будет присылать вам образцы рукописных надписей на армянском. Отгадайте, что написано")
        mode4(message)


@bot.message_handler(func=lambda message: is_bot_started and mode == 1)
def symbol_guess_handler(message):
    global score, scores, current_symbol
    guessed_symbol = message.text.upper()
    if guessed_symbol == current_symbol[1]:
        score += 1
        scores["1"] += 1
        bot.reply_to(message, "Верно.")
    else:
        bot.reply_to(message, "Неверно.")
    send_random_symbol(message)


def send_random_symbol(message):
    global current_symbol
    current_symbol = random.choice(list(symbols_dict.items()))
    bot.reply_to(message, f"{current_symbol[0]}:{current_symbol[1]}")

@bot.message_handler(func=lambda message: is_bot_started and mode == 2)
def test_guess_handler(message):
    global score, scores, current_symbol
    guessed_symbol = message.text.upper()
    if guessed_symbol == current_symbol[1]:
        score += 1
        scores["2"] += 1
        bot.reply_to(message, "Верно.")
    else:
        bot.reply_to(message, f"Неверно. Верный ответ: {current_symbol[1]}")
    send_random_test(message)

def send_random_test(message):
    global current_symbol
    current_symbol = random.choice(list(symbols_dict.items()))
    bot.reply_to(message, f"{current_symbol[0]}: ?")




@bot.message_handler(func=lambda message: is_bot_started and mode == 4)
def check_answer(message):
    global score, scores, correct_answer
    user_answer = message.text
    if user_answer.lower() == correct_answer.lower():
        score += 1
        scores["4"] += 1
        bot.reply_to(message, "Правильно!")
    else:
        bot.reply_to(message, f"Неправильно. Верный ответ: {correct_answer}")
    mode4(message)

# к сожалению, без полного абсолютного путя он ничего не находит
def mode4(message):
    global correct_answer
    path1 = "/home/ashavrina/mysite/static/IMG/сарин.png"
    path2 = "/home/ashavrina/mysite/static/IMG/сурб.png"
    path3 = "/home/ashavrina/mysite/static/IMG/чмеч.png"
    pathes = [path1, path2, path3]
    path = random.choice(pathes)
    if os.path.exists(path):
        with open(path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption="Что написано на этой картинке?")

        correct_answer = path.split("/")[-1][:-4]
    else:
        bot.send_message(message.chat.id, "Файл не найден по указанному пути.")


# пустая главная страничка для проверки
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'ok'


# обрабатываем вызовы вебхука = функция, которая запускается, когда к нам постучался телеграм
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)

if __name__ == '__main__':
    bot.polling(none_stop=True)

