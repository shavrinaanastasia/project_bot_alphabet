import telebot
import conf
import matplotlib
matplotlib.use('agg')

import random
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from telebot import types
import os
import matplotlib.pyplot as plt



model = GPT2LMHeadModel.from_pretrained("sberbank-ai/rugpt3small_based_on_gpt2")
tokenizer = GPT2Tokenizer.from_pretrained("sberbank-ai/rugpt3small_based_on_gpt2")

symbols_dict = {"Ա": "А", "Բ": "Б", "Գ": "Г", "Դ": "Д", "Ե": "Е", "Զ": "З", "Է": "Э", "Ը": "Ы", "Թ": "Т", "Ժ": "Ж", "Ի": "И", "Լ": "Л", "Խ": "Х", "Ծ": "Ц", "Կ": "К", "Հ": "Г", "Ձ": "Дз", "Ղ": "Г", "Ճ": "Ч", "Մ": "М", "Յ": "Й", "Ն": "Н", "Շ": "Ш", "Ո": "В", "Չ": "Ч", "Պ": "П", "Ջ": "Дж", "Ռ": "Р", "Ս": "С", "Վ": "В", "Տ": "Т", "Ր": "Р", "Ց": "Ц", "Ւ": "У", "Փ": "Ф", "Ք": "К", "Օ": "О", "Ֆ": "Ф"}

bot = telebot.TeleBot(conf.TOKEN)

bot.delete_webhook()

print("Вебхук успешно удален.")
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


@bot.message_handler(commands=['stop'])
def stop_handler(message):
    global is_bot_started, mode, score, scores, plots
    is_bot_started = False
    mode = None
    plots += 1
    bot.reply_to(message, f"Итоговый счет: {score}")
    score = 0
    plt.bar(scores.keys(), scores.values())
    plt.xlabel('Режимы')
    plt.ylabel('Счет')
    plt.title('Счет игрока в разных режимах')
    plt.savefig(f'plot_{plots}.png')  # Сохраняем график как изображение
    with open(f'plot_{plots}.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo)



@bot.callback_query_handler(func=lambda call: call.data == 'stop')
def stop_call_handler(call):
    global is_bot_started, mode, score, plots
    is_bot_started = False
    mode = None
    plots += 1
    bot.send_message(call.message.chat.id, f"Итоговый счет: {score}")
    score = 0
    plt.bar(scores.keys(), scores.values())
    plt.xlabel('Режимы')
    plt.ylabel('Счет')
    plt.title('Счет игрока в разных режимах')
    plt.savefig(f'plot_{plots}.png')  # Сохраняем график как изображение
    with open(f'plot_{plots}.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo)


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
    elif mode == 3:
        bot.reply_to(message, "В режиме игры вам предлагается придумывать слова на русском и вводить их боту. Бот сгенерирует предложение с таким началом и транслитерирует его. Ваша задача: прочитать предложение и ввести в поле ответа. В первой игре первым словом будет 'пример' ")
        message.text = "Пример"
        sentence_generation(message)
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

@bot.message_handler(func=lambda message: is_bot_started and mode == 3 and message.text != '/stop')

def translit_guess_handler(message):
    global score, scores, transliterated, generated_text
    guessed = message.text.upper()
    if guessed == generated_text.upper():
        score += 1
        scores["3"] += 1
        bot.reply_to(message, "Верно.")
    else:
        bot.reply_to(message, f"Неверно. Верный ответ: {generated_text}")
    #sentence_generation(message)
    bot.register_next_step_handler(message, sentence_generation)


def sentence_generation(message):
    if message.text != "/stop":
        global transliterated, generated_text
        input_text = message.text.lower()
        input_ids = tokenizer.encode(input_text, return_tensors='pt')
        output = model.generate(input_ids, max_length=50, num_return_sequences=1, pad_token_id=50256)
        generated_text = str(tokenizer.decode(output[0], skip_special_tokens=True).split(".")[0]) + "."
        transliterated_lst = []
        for s in list(generated_text):
            if s.isalpha() and s.upper() in list(symbols_dict.values()):
                transliterated_lst.append(list(symbols_dict.keys())[list(symbols_dict.values()).index(s.upper())])
            else:
                transliterated_lst.append(s)
        transliterated = "".join(transliterated_lst)
        bot.reply_to(message, transliterated)
    else:
        global is_bot_started, mode, score, plots
        is_bot_started = False
        mode = None
        plots += 1
        bot.reply_to(message, f"Итоговый счет: {score}")
        score = 0
        plt.bar(scores.keys(), scores.values())
        plt.xlabel('Режимы')
        plt.ylabel('Счет')
        plt.title('Счет игрока в разных режимах')
        plt.savefig(f'plot_{plots}.png')  # Сохраняем график как изображение
        with open(f'plot_{plots}.png', 'rb') as photo:
            bot.send_photo(message.chat.id, photo)


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

def mode4(message):
    global correct_answer
    images_dir = os.path.join(os.path.dirname(__file__), 'images')
    image_files = [f for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f))]

    image_file = random.choice(image_files)
    image_path = os.path.join(images_dir, image_file)

    with open(image_path, 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption="Что написано на этой картинке?")

    correct_answer = image_file[:-4]
    #bot.register_next_step_handler(message, check_answer, image_file[:-4])

if __name__ == '__main__':
    bot.polling(none_stop=True)

