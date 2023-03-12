from array import array
import requests
from auth_info import *
import urllib.parse
from threading import *

class BotTG():
    def __init__(self):
        self.__API_Link = f"https://api.telegram.org/bot{tg_token}/"
        self._last_message_id = 0
        self.__myID = my_tg_id
        self.__vk_token = vk_token
        self.__mailing_list = list()
        self.__errors_count = 0
        self.__thread = None

        self.u_chat_list = None
        self.start_ids_list = None

        try:
            with open('files_tg/data/saved_update.txt', mode='r') as file:
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
        message_raw = {'text': messageText}
        message_encoded = urllib.parse.urlencode(message_raw)
        send_message = requests.get(self.__API_Link + f"sendMessage?chat_id={self.__myID}&{message_encoded}&parse_mode=HTML").json()
        # print(send_message)

    def sendPhotoMessage(self, photo_link: str, caption=''):
        photo_raw = {'photo': photo_link}
        photo_encoded = urllib.parse.urlencode(photo_raw)
        r = requests.get(self.__API_Link + f"sendPhoto?chat_id={self.__myID}&{photo_encoded}&caption={caption}").json()

    def sendAudioMessage(self, audio_link: str, caption='', title='unknown'):
        audio_raw = {'audio': audio_link}
        audio_encoded = urllib.parse.urlencode(audio_raw)
        r = requests.get(self.__API_Link + f"sendAudio?chat_id={self.__myID}&{audio_encoded}&caption={caption}&title={title}").json()

    def sendVoiceMessage(self, voice_link: str, caption=''):
        voice_raw = {'voice': voice_link}
        voice_encoded = urllib.parse.urlencode(voice_raw)
        r = requests.get(self.__API_Link + f"sendVoice?chat_id={self.__myID}&{voice_encoded}&caption={caption}").json()

    def sendVideoMessage(self, video_link: str = '', caption='', file = None):
        # video_raw = {'video': video_link}
        # video_encoded = urllib.parse.urlencode(video_raw)
        # r = requests.get(self.__API_Link + f"sendVideo?chat_id={self._myID}&{video_encoded}&caption={caption}").json()
        # print(r)
        params = {
            'chat_id': self.__myID
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
            'chat_id': self.__myID,
            'media': media_list,
            'caption': caption
        }
        r = requests.post(self.__API_Link + f"sendMediaGroup", json=params).json()
        
        if r['ok'] == False:
            if self.__errors_count == 5:
                self.__errors_count = 0
                return r
            
            self.__errors_count += 1
            # print(r)
            # print(media_list)
            return self.sendMediaGroup(media_list, caption=caption)
        

    def createMediaList(self, photos: list = [], videos: list = [], audios: list = [], docs: list = []):
        media_list = list()

        for photo in photos:
            media_list.append({
                'type': photo['type'],
                'media': photo['url'] 
            })

        for video in videos:
            if "https://www.youtube.com" not in video['url']:
                media_list.append({
                    'type': video['type'],
                    'media': video['url']
                })
            else:
                self.sendMessage(video['url'])

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

        #print(media_list)
        return media_list

    def getFilePath(self, file_id):
        r = requests.get(self.__API_Link + f"getFile?file_id={file_id}").json()
        return r['result']['file_path']
    
    def getFile(self, file_path):
        file_link = f"https://api.telegram.org/file/bot{tg_token}/{file_path}"
        r = requests.get(file_link)

        with open(f'files_tg/{file_path}', mode='wb') as photo:
            photo.write(r.content)


    def getUpdatesFromTelegram(self):
        req = requests.get(self.__API_Link + f"getUpdates?offset={self.__updates_offset}").json()
        updates = req['result']

        if updates:
            self.__updates_offset = int(updates[len(updates) - 1]['update_id']) + 1
        return updates

    def listenForUpdates(self):
        parsed_updates = list()
        while True:
            updates = self.getUpdatesFromTelegram()
            # print(updates)
            if updates:
                self.saveUpdateId(updates[len(updates) - 1]['update_id'])
                for update in updates:
                    parsed_updates.append(self.parseUpdate(update))
                      
            return parsed_updates


    def parseUpdate(self, update):
        import datetime

        parsed_update = {
            'from': None,
            'date': None,
            'text': None,
            'photo': None,
            'video': None,
            'caption': None,
            'command': None
        }

        parsed_update['from']  = update['message']['from']
        parsed_update['date'] = datetime.datetime.fromtimestamp(float(update['message']['date'])).strftime('%Y-%m-%d %H:%M:%S')

        if 'text' in update['message']:
            if update['message']['text'][:1] == '/':
               parsed_update['command'] = self.__ParseCommand(update['message']['text'])
            else:
                parsed_update['text'] = update['message']['text']
                    
        if 'photo' in update['message']:
            photos = update['message']['photo']
            photo_id = photos[len(photos) - 1]['file_id']
            photo_path = self.getFilePath(photo_id)
            self.getFile(photo_path)
            parsed_update['photo'] = 'files_tg/' + photo_path

        if 'video' in update['message']:
            video_id = update['message']['video']['file_id']
            video_path = self.getFilePath(video_id)
            self.getFile(video_path)
            parsed_update['video'] = 'files_tg/' + video_path

        if 'caption' in update['message']:
            parsed_update['caption'] = update['message']['caption']

        return parsed_update
        
    def __ParseCommand(self, command: str):
        command_data = command.split()
        target, args, result = None, None, None

        if command_data[0] == "/chat":
            chat_name = self.__findChatByName(command_data[1])
            if chat_name:
                if len(chat_name) > 1:
                    return "#too much mathes"
            else:
                return "#no matches"

            self.current_chat = str(chat_name[0])
            target = self.__GetChat
            args = (self.current_chat,)
            #self.__GetChat(command_data[1])

        if command_data[0] == "/unread":
            result = command_data[0]

        self.__thread = Thread(target=target, args=args)
        self.__thread.start()

        return result

    def __GetChat(self, chat_id: str):
        items = self.loadJSONData(chat_id)
        start_message_id = 0

        for obj in self.start_ids_list:
            if self.current_chat in obj:
                start_message_id = obj[self.current_chat]

        new_messages = list()
        if start_message_id > 0:
            x = self.__BinSearch(items, start_message_id)

            if x == -1:
                new_messages = items
            else:
                new_messages = items[x:]
        else:
            new_messages = items
                    


        self.parseItems(new_messages)

    def __BinSearch(self, items: list, message_id):
        left = 0
        right = len(items) - 1
        m = 0

        while right - left >= 0:
            m = (right + left) // 2
            if items[m]['message_id'] == message_id:
                return m
            if items[m]['message_id'] > message_id:
                right = m - 1
            if items[m]['message_id'] < message_id:
                left = m + 1
        
        return -1

    def __findChatByName(self, chat_name):
        result = list()
        for u_chat in self.u_chat_list:
            for key in u_chat:
                if chat_name.lower() in key.lower():
                    result.append(u_chat[key])
        return result
                


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
        import os

        items = dict()
        path = f"dialogs\\{file}.json"
        
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as file:
                items = json.load(file)
        else:
            self.sendMessage("Чат не найден. Подождите и попробуйте снова.")
        
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
                self.sendMessage(f"<u>{message['datetime']}</u>\n<b>{message['from']}</b>\n{message['text']}")

    def saveFileFromURL(self, url, directory, filename, file_extention):
        with open(f'files_tg/{directory}/{filename}.{file_extention}', mode='wb') as docs:
            headers = {
                'Authorization': f'Bearer {self.__vk_token}'
            }

            ufr = requests.get(url, headers=headers)
            print(ufr.content)
            docs.write(ufr.content)

    def saveUpdateId(self, update_id):
        with open('files_tg/data/saved_update.txt', mode='w') as file:
            file.write(str(update_id + 1))