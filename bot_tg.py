from array import array
import requests
from auth_info import *
import urllib.parse

class BotTG():
    def __init__(self):
        self.__API_Link = f"https://api.telegram.org/bot{tg_token}/"
        self._last_message_id = 0
        self._myID = my_tg_id
        self.__mailing_list = list()
        self.__updates_offset = 0
        self.__current_chat_id = None

    def sendMessageRequestGeneration(self,**kwargs):
        messageTemplate = self.__API_Link + f"sendMessage?"
        for item in kwargs:
            if item is not None:
                messageTemplate += f"{item}={kwargs[item]}&"

        return messageTemplate[:-1]

    def userAdd(self, chat_id: str):
        if chat_id not in self.__mailing_list:
            self.__mailing_list.append(chat_id)
            self.sendMessage(self.__API_Link + f"se")

    def sendMessage(self, messageText : str):
        send_message = requests.get(self.__API_Link + f"sendMessage?chat_id={self._myID}&text={messageText}").json()
        # print(send_message)

    def sendPhotoMessage(self, photo_link: str, caption=''):
        photo_raw = {'photo': photo_link}
        photo_encoded = urllib.parse.urlencode(photo_raw)
        r = requests.get(self.__API_Link + f"sendPhoto?chat_id={self._myID}&{photo_encoded}&caption={caption}").json()

    def sendAudioMessage(self, audio_link: str, caption='', title='unknown'):
        audio_raw = {'audio': audio_link}
        audio_encoded = urllib.parse.urlencode(audio_raw)
        r = requests.get(self.__API_Link + f"sendAudio?chat_id={self._myID}&{audio_encoded}&caption={caption}&title={title}").json()

    def sendVoiceMessage(self, voice_link: str, caption=''):
        voice_raw = {'voice': voice_link}
        voice_encoded = urllib.parse.urlencode(voice_raw)
        r = requests.get(self.__API_Link + f"sendVoice?chat_id={self._myID}&{voice_encoded}&caption={caption}").json()

    def sendMediaGroup(self, media_list : list, caption : str = ""):
        params = {
            'chat_id': self._myID,
            'media': media_list,
            'caption': caption
        }
        r = requests.post(self.__API_Link + f"sendMediaGroup", json=params).json()
        print(r)
        

    def sendGeneric(self, method: str, params: dict):
        params_str = ''
        for param in params:
            if params[param] is not None:
                param_raw = {param : params['param']}
                print(param_raw)

    def sendMultiMessage(self, messages : list):
        for message in messages:
            if len(message['attachments']['photo_urls']) > 0:
                photo_urls = message['attachments']['photo_urls']
                if len(photo_urls) == 1:
                    caption = f"От: {message['from']}\n{message['text']}\n{message['datetime']}"
                    self.sendPhotoMessage(photo_urls[0], caption)
                    return
                else:
                    for url in photo_urls:
                        pass
            if message['attachments']['audio_message'] is not None:
                self.sendVoiceMessage(message['attachments']['audio_message'])
                return
            if message['attachments']['audio_file'] is not None:
                audio = message['attachments']['audio_file']
                self.sendAudioMessage(audio_link=audio['url'], caption=message['text'], title=f"{audio['artist']} - {audio['title']}")
                return
            text = f"От: {message['from']}\n{message['text']}\n{message['datetime']}"
            self.sendMessage(text)

    def createMediaList(self, photos: list, videos: list):
        media_list = list()

        for photo in photos:
            media_list.append({
                'type': photo['type'],
                'media': photo['url'] 
            })

        for video in videos:
            media_list.append({
                'type': video['type'],
                'media': video['url']
            })

        return media_list

    def updatesInfo(self, updates):
            for item in updates['result']:
                print(item)
                if 'message' in item:
                    user = item['message']['from']
                    chat = item['message']['chat']
                    print(f"UPDATE ID: {item['update_id']}")
                    if 'title' in chat:
                        print(f"TITLE: {chat['title']} | TYPE {chat['type']} | CHAT ID: {chat['id']}")

                    print(f"USER NAME: {user['username']} | NAME: {user['first_name']}", end="")
                    if 'last_name' in user:
                        print(f" {user['last_name']}", end="")
                    print(f" | USER ID: {user['id']}")

                    if 'text' in item['message']:
                        print(f"MESSAGE: {item['message']['text']}")

                        if 'entities' in item['message']:
                            for entity in item['message']['entities']:
                                print(f"\tMESSAGE LENGTH: {entity['length']}")
                                print(f"\tMESSAGE TYPE: {entity['type']}")
                    print()

    def getUpdatesFromTelegram(self):
        req = requests.get(self.__API_Link + f"getUpdates?offset={self.__updates_offset}").json()
        updates = req['result']

        if updates:
            self.__updates_offset = int(updates[len(updates) - 1]['update_id']) + 1
        return updates
        #self.updatesInfo(updates)

    def listenForUpdates(self):
        import time
        while True:
            updates = self.getUpdatesFromTelegram()
            print(updates)
            if updates:
                for update in updates:
                    if 'text' in update['message'] and update['message']['text'][:1] == '/':
                        self.__ParseCommand(update['message']['text'])

            time.sleep(5)
        
    def __ParseCommand(self, command: str):
        command_data = command.split()

        if command_data[0] == "/chat":
            self.__GetChat(command_data[1])

    def __GetChat(self, chat_id: str):
        items = self.loadJSONData(chat_id)
        self.parseItems(items)


    def __GetMessagesFromCSV(self, path):
        import csv, json
        messages = list()

        with open(f'dialogs\\{path}', 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            for row in reader:
                obj = {
                    'message_id': None,
                    'status': None,
                    'items': None
                }

                obj['message_id'] = row[0]
                obj['status'] = row[1]
                obj['items'] = json.loads(row[2].replace("'", '"').replace('\n', ' ').replace('None', 'null'))
                messages.append(obj)
            
        return messages
    
    def listJSONFiles(self):
        import os

        json_files = list()
        root_dir = os.path.dirname(os.path.abspath(__file__))
        sub_dir = root_dir + '\\dialogs'

        for path in os.listdir(sub_dir):
            if os.path.isfile(os.path.join(sub_dir, path)):
                json_files.append(path)
        return json_files

    def loadJSONData(self, file):
        import json
        items = dict()
        path = f"dialogs\\{file}.json"

        with open(path, 'r', encoding='utf-8') as file:
            items = json.load(file)
        return items['items']

    def parseItems(self, items):
        for message in items:
            if 'attachments' in message:
                if message['attachments']['photo'] or message['attachments']['video']:
                    media_list = self.createMediaList()
                    self.sendMediaGroup(media_list)
                if message['attachments']['audio']:
                    pass
            else:
                self.sendMessage(message['text'])

