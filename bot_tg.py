from array import array
import requests
from auth_info import *
import urllib.parse

class BotTG():
    def __init__(self):
        self.__API_Link = f"https://api.telegram.org/bot{tg_token}/"
        self._last_message_id = 0
        self._myID = my_tg_id
        self.__vk_token = vk_token
        self.__mailing_list = list()
        self.__errors_count = 0

        try:
            with open('files/data/saved_update.txt', mode='r') as file:
                self.__updates_offset = file.read()
        except:
            self.__updates_offset = 0

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

    def sendVideoMessage(self, video_link: str = '', caption='', file = None):
        # video_raw = {'video': video_link}
        # video_encoded = urllib.parse.urlencode(video_raw)
        # r = requests.get(self.__API_Link + f"sendVideo?chat_id={self._myID}&{video_encoded}&caption={caption}").json()
        # print(r)
        params = {
            'chat_id': self._myID
        }

        file = { 
            'video': ('test.mp4', file)
        }

        headers = {
            'Content-Type': 'multipart/form-data'
        }

        r = requests.post("https://httpbin.org/post", json=params, files=file)
        print(r.text)


    def sendMediaGroup(self, media_list : list, caption : str = ""):
        params = {
            'chat_id': self._myID,
            'media': media_list,
            'caption': caption
        }
        r = requests.post(self.__API_Link + f"sendMediaGroup", json=params).json()
        
        if r['ok'] == False:
            if self.__errors_count == 5:
                self.__errors_count = 0
                return r
            
            self.__errors_count += 1
            print(r)
            print(media_list)
            return self.sendMediaGroup(media_list, caption=caption)
        

    def createMediaList(self, photos: list = [], videos: list = [], audios: list = [], docs: list = []):
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

        for audio in audios:
            media_list.append({
                'type': audio['type'],
                'media': audio['url'],
                'perfomer': audio['artist'],
                'title': audio['title']
            })
        
        for doc in docs:
            media_list.append({
                'type': 'document',
                'media': doc['url']
            })

        return media_list

    def getFilePath(self, file_id):
        r = requests.get(self.__API_Link + f"getFile?file_id={file_id}").json()
        print(r)
        return r['result']['file_path']
    
    def getFile(self, file_path):
        file_link = f"https://api.telegram.org/file/bot{tg_token}/{file_path}"
        r = requests.get(file_link)

        with open(f'files/{file_path}', mode='wb') as photo:
            photo.write(r.content)


    def getUpdatesFromTelegram(self):
        req = requests.get(self.__API_Link + f"getUpdates?offset={self.__updates_offset}").json()
        updates = req['result']

        if updates:
            self.__updates_offset = int(updates[len(updates) - 1]['update_id']) + 1
        return updates

    def listenForUpdates(self):
        import time
        time.sleep(2)
        while True:
            updates = self.getUpdatesFromTelegram()
            print(updates)
            if updates:
                self.saveUpdateId(updates[len(updates) - 1]['update_id'])
                for update in updates:
                    print(self.parseUpdate(update))
                    return self.parseUpdate(update)


    def parseUpdate(self, update):
        import datetime

        parsed_update = {
            'from': None,
            'date': None,
            'text': None,
            'photo': None,
            'video': None,
            'caption': None
        }

        parsed_update['from']  = update['message']['from']
        parsed_update['date'] = datetime.datetime.fromtimestamp(float(update['message']['date'])).strftime('%Y-%m-%d %H:%M:%S')

        if 'text' in update['message']:
            if update['message']['text'][:1] == '/':
                self.__ParseCommand(update['message']['text'])
            else:
                parsed_update['text'] = update['message']['text']
                    
        if 'photo' in update['message']:
            photos = update['message']['photo']
            photo_id = photos[len(photos) - 1]['file_id']
            photo_path = self.getFilePath(photo_id)
            self.getFile(photo_path)
            parsed_update['photo'] = 'files/' + photo_path

        if 'video' in update['message']:
            video_id = update['message']['video']['file_id']
            video_path = self.getFilePath(video_id)
            self.getFile(video_path)
            parsed_update['video'] = 'files/' + video_path

        if 'caption' in update['message']:
            parsed_update['caption'] = update['message']['caption']

        return parsed_update
        
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
                    media_list = self.createMediaList(photos=message['attachments']['photo'], videos=message['attachments']['video'])
                    self.sendMediaGroup(media_list, caption=message['text'])

                if message['attachments']['audio']:
                    media_list = self.createMediaList(audios=message['attachments']['audio'])
                    self.sendMediaGroup(media_list, caption=message['text'])

                if message['attachments']['doc']:
                    media_list = self.createMediaList(docs=message['attachments']['doc'])
                    self.sendMediaGroup(media_list, caption=message['text'])
            else:
                self.sendMessage(message['text'])

    def saveFileFromURL(self, url, directory, filename, file_extention):
        with open(f'files/{directory}/{filename}.{file_extention}', mode='wb') as docs:
            headers = {
                'Authorization': f'Bearer {self.__vk_token}'
            }

            ufr = requests.get(url, headers=headers)
            print(ufr.content)
            docs.write(ufr.content)

    def saveUpdateId(self, update_id):
        with open('files/data/saved_update.txt', mode='w') as file:
            file.write(str(update_id + 1))