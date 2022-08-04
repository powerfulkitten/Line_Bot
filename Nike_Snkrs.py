from bs4 import BeautifulSoup
import requests
import shutil
# import datetime
import os

path = 'https://www.nike.com/tw/launch?cp=78087397488_search_%7Ctw%7CBrand%2BProduct%3ATM%2B-%2BGN%2B-%2BSNKRS%2B-%2BLaunch%2BCalendar%2B-%2BCH_CH%2B-%2BExact%7CGOOGLE%7Csnkrs&s=upcoming'

def check_sell_time(sell_time):
    day = sell_time.split()[0]
    time = sell_time.split()[1]
    if time[0] == '下':
        if int(time[time.find('午')+1:time.find(':')]) + 12 + 8 > 24:
            old = day[day.find('/')+1:]
            new = str(int(old) + 1)
            change_day = day.replace(old, new)
            sell_time = sell_time.replace(day, change_day)

    hour = int(time[time.find('午')+1:time.find(':')]) + 8
    if hour > 12:
        hour = hour - 12
        change_time = time.replace(time[time.find('午')+1:time.find(':')], str(hour))
        if time[0] == '下':
            change_time = change_time.replace('下', '上')
        else:
            change_time = change_time.replace('上', '下')
        sell_time = sell_time.replace(time, change_time)
    else:
        change_time = time.replace(time[time.find('午')+1:time.find(':')], str(hour))
        sell_time = sell_time.replace(time, change_time)
    return sell_time

def send_message_to_multiverse(**message):
    token = "1cZZ3ovXaNGDRpYfM1WYpANQyRca9zfeqIgTMc2JEIr"
    url = 'https://notify-api.line.me/api/notify'
    headers = {
            "Authorization": f"Bearer {token}"
            }
    data = {
            'message':f'{message["item_name"]} 將於 {message["sell_time"]}'.replace('2:00', '10:00')
            }
    image = open(f'./item_image/{message["item_name"]}.jpg', 'rb')
    imageFile = {'imageFile' : image}
    requests.post(url, headers = headers, data = data, files = imageFile)

def check_updata():
    if os.path.isdir('item_image'):
        shutil.rmtree('item_image')
        os.mkdir("item_image")
    else:
        os.mkdir("item_image")
    response = requests.get(path)
    soup = BeautifulSoup(response.text, "html.parser")
    results = soup.find_all("div", class_ = "upcoming upcoming-card ncss-row mr0-sm ml0-sm")
    for index, item in enumerate(results):
        sell_time = item.find('div', class_ = 'available-date-component').getText()
        item_name = f"[{index+1}]{item.find('h3', class_ = 'headline-5 mb1-sm fs16-sm').getText()}"
        image_url = item.find('img', alt = 'image').get('src')
        get_item_image = requests.get(image_url)
        with open(f"item_image\\{item_name}.jpg", "wb") as file:
            file.write(get_item_image.content)
        sell_time = check_sell_time(sell_time)
        send_message_to_multiverse(item_name = item_name, sell_time = sell_time)