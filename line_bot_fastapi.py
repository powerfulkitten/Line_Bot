from fastapi import FastAPI, Request
# from pydantic import BaseModel
from bs4 import BeautifulSoup
import configparser
from linebot import LineBotApi, WebhookHandler
# from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
import paramiko
import uvicorn
import requests
import datetime
import Nike_Snkrs

name_list = list()

app = FastAPI()

config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.80", 22, "nadi", "nadiazure")

def line_bot_send_text(event, text_message):
    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = text_message)
        )

def line_bot_send_image(event, image_url):
    # image_url = 'https://secure-images.nike.com/is/image/DotCom/DQ0558_160_A_PREM?$SNKRS_COVER_WD$&align=0,1'
    line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(
                              original_content_url = image_url,
                              preview_image_url = image_url)
        )

def command_help(event):
    respond_content = """nike ---> 顯示Nike目前出售的鞋款
nike ---> 顯示Nike目前出售的鞋款
"""
    line_bot_send_text(event, respond_content)

def command_search(event, name):
    try:
        stdin, stdout, stderr = client.exec_command('cd /soyal/UDM/;cat log.log')
        for count in stdout.readlines():
            if name in count:
                result = count
        line_bot_send_text(event, result[34:48])
    except:
        if name == 'who':
            stdin, stdout, stderr = client.exec_command('cd /soyal/UDM/;cat log.log')
            for count in stdout.readlines():
                count = count[count.find('     ') + len('     '):len(count)][0:count[count.find('     ') + len('     '):len(count)].find('         ')]
                if count not in name_list:
                    if '/' not in count and 'Access by PIN' not in count and 'Normal Access' not in count:
                        name_list.append(count)
            line_bot_send_text(event, ''.join(name_list))
        else:
            line_bot_send_text(event, 'Not Find This Shxt!!!')

def nike_snkrs():
    Nike_Snkrs.check_updata()

def test3():
    return '3'

def test4():
    return '4'

@app.post("/")
async def callback(request: Request):
    signature = request.headers['x-line-signature']
    body = await request.body()
    body = body.decode('utf-8')
    handler.handle(body, signature)
    return 'OK'

@handler.add(MessageEvent, message = TextMessage)
def pretty_echo(event):
    receive_message = event.message.text.split("-")
    command_dict = {
            'help': command_help,
            's': command_search,
            'nike': nike_snkrs,
            '3': test3,
            "4": test4
            }
    if event:
        try:
            command_dict.get(receive_message[0])(event, receive_message[1])
        except:
            try:
                if command_dict.get(receive_message[0]) != 'help':
                    command_dict.get(receive_message[0])()
                else:
                    command_dict.get(receive_message[0])(event)
            except:
                line_bot_send_text(event, 'Fuck U Stupid People QQ')

if __name__=="__main__":
    uvicorn.run("line_bot_fastapi:app", port = 5000, reload=True)