import requests
import json
import os
from auth_info import *


class BotVK:
    def __init__(self):
        self.__ID = my_vk_id
        self.__token = vk_token
        self.vk_uri = "https://api.vk.com/method/"
        self.version = "v=5.131"

    def message_parse(self, message_item: dict, users_list: dict):
        import datetime
        # print(message_item)
        message = dict()
        message['message_id'] = message_item['id']
        message['from'] = f"{users_list[message_item['from_id']]['first_name']} {users_list[message_item['from_id']]['last_name']}"
        message['text'] = message_item['text']
        message['datetime'] = str(datetime.datetime.fromtimestamp(message_item['date']))
        if len(message_item['attachments']) > 0:
            message['attachments'] = self.parseAttachments(message_item['attachments'])

        if 'reply_message' in message_item:
            message['reply_message'] = self.message_parse(message_item['reply_message'], users_list)

        if 'fwd_messages' in message_item and len(message_item['fwd_messages']) > 0:
            message['fwd_messages'] = list()
            for fwd_message in message_item['fwd_messages']:
                message['fwd_messages'].append(self.message_parse(fwd_message, users_list))

        # print(message)
        return message

    def messages_GetConversationsById(self, user_ids):
        link = f"{self.vk_uri}/messages.getConversationsById?peer_ids={user_ids}&access_token={self.__token}&fields=unread_count&{self.version}"
        request = requests.post(link).json()
        in_read_cmid = request['response']['items'][0]['in_read_cmid']
        out_read_cmid = request['response']['items'][0]['out_read_cmid']
        unread_messages = 0
        if in_read_cmid > out_read_cmid:
            print("Your messages unread")
        elif out_read_cmid > in_read_cmid:
            unread_messages = out_read_cmid - in_read_cmid
            print(f"You have {unread_messages} unread messages")
        else:
            print("Nothing new")
        return unread_messages

    def getConversationMembers(self, peer_id):
        link = f"{self.vk_uri}/messages.getConversationMembers?peer_id={peer_id}&access_token={self.__token}&{self.version}"
        request = requests.post(link).json()

        users_info = dict()
        for user in request['response']['profiles']:
            users_info[user['id']] = {"first_name": user['first_name'], 'last_name': user['last_name']}
        if 'groups' in request['response']:
            for group in request['response']['groups']:
                users_info[-group['id']] = {'first_name': group['name'], 'last_name': ''}

        return users_info

    def messages_getUnreadHistory(self, peer_id):
        start_message_id = -1
        unread_messages = self.messages_GetConversationsById(peer_id)
        users_list = self.getConversationMembers(peer_id)

        while unread_messages > 0:
            if unread_messages >= 200:
                offset = -200
            else:
                offset = -unread_messages

            link = f"{self.vk_uri}/messages.getHistory?peer_id={peer_id}&access_token={self.__token}&{self.version}&offset={offset}&start_message_id={start_message_id}&count={-offset}&extended=1"
            request = requests.post(link).json()

            messages = list()
            for item in request['response']['items']:
                messages.append(self.message_parse(item, users_list))
            messages.reverse()

            # print(messages)

            unread_messages += offset
            # self.writeMessageHistoryInCSV(peer_id, messages)
            start_message_id = self.writeMessagesToJSON(peer_id, messages)

    def messages_getHistory(self, peer_id, start_message_id, number_of_messages):
        while number_of_messages > 0:
            if number_of_messages >= 200:
                count = 200
            else:
                count = number_of_messages
            link = f"{self.vk_uri}/messages.getHistory?peer_id={peer_id}&access_token={self.__token}&{self.version}&offset={0}&start_message_id={start_message_id}&count={count}&extended=1"
            users_list = self.getConversationMembers(peer_id)
            request = requests.post(link).json()

            messages = list()
            for item in request['response']['items']:
                messages.append(self.message_parse(item, users_list))
            messages.reverse()

            number_of_messages -= count
            start_message_id = messages[0]['message_id']
            return messages, start_message_id

    def messages_markAsRead(self, peer_id: str, message_id):
        link = f"{self.vk_uri}/messages.markAsRead?peer_id={peer_id}&access_token={self.__token}&{self.version}&start_message_id={message_id}"
        requests.post(link).json()
        self.deleteMessageByIDFromJSON(peer_id, message_id)

    def messages_getConversations(self):
        link = f"{self.vk_uri}/messages.getConversations?access_token={self.__token}&{self.version}&filter=unread&extended=1"
        request = requests.post(link).json()

        chats_info = list()
        for item in request['response']['items']:
            chat_i = dict()
            chat_i["id"] = item['conversation']['peer']['id']
            users_list = self.getConversationMembers(chat_i['id'])
            if item['conversation']['peer']['type'] == 'chat':
                chat_i["from"] = item['conversation']['chat_settings']['title']
            else:
                chat_i["from"] = f"{users_list[chat_i['id']]['first_name']} {users_list[chat_i['id']]['last_name']}"
            chat_i['unread'] = item['conversation']['unread_count']
            chats_info.append(chat_i)

        return chats_info

    def parseAttachments(self, attachments):
        message = {'sticker': None, 'audio_message': None, 'photo': list(), 'link': None, 'video': list(), 'audio': list(), 'gift': None, 'wall': None, 'doc': list()}

        for attachment in attachments:
            if attachment['type'] == 'sticker':
                message['sticker'] = self.getStickerFromMessage(attachment['sticker'])
            if attachment['type'] == 'audio_message':
                message['audio_message'] = self.getVoiceFromMessage(attachment)
            if attachment['type'] == 'video':
                message['video'].append(self.getVideoFromMessage(attachment))
            if attachment['type'] == 'photo':
                message['photo'].append(self.getImageFromMessage(attachment))
            if attachment['type'] == 'audio':
                message['audio'].append(self.getAudioFileFromMessage(attachment))
            if attachment['type'] == 'doc':
                message['doc'].append(self.getDocFileFromMessage(attachment))
            if attachment['type'] == 'link':
                message['link'] = (self.getLinkFromMessage(attachment))
            if attachment['type'] == 'wall':
                message['wall'] = self.getWallFromMessage(attachment)
            if attachment['type'] == 'gift':
                message['gift'] = self.getGiftFromMessage(attachment)

        return message

    def getStickerFromMessage(self, sticker):
        # print(f"Sticker ID: {sticker['sticker_id']}")
        # print(f"Sticker URL: {sticker['images'][len(sticker['images']) - 1]['url']}")

        return {'type': 'sticker', 'sticker_id': sticker['sticker_id'], 'url': sticker['images'][len(sticker['images']) - 1]['url']}

    def getVoiceFromMessage(self, attachment):
        # print(f"Audio URL: {attachment['audio_message']['link_ogg']}")
        return {'type': 'audio_message', 'url': attachment['audio_message']['link_ogg']}

    def getImageFromMessage(self, attachment):
        max_size = 'a'
        picture_url = None
        for size in attachment['photo']['sizes']:
            if size['type'] == 'w':
                return {'type': 'photo', 'url': size['url']}

            if max_size < size['type']:
                max_size = size['type']
                picture_url = size['url']

        return {'type': 'photo', 'url': picture_url}

    def getVideoFromMessage(self, attachment):
        if 'files' in attachment['video']:
            if 'external' in attachment['video']['files']:
                return {'type': 'video', 'url': attachment['video']['files']['external']}

            max_key = "mp4_144"
            for key in attachment['video']['files']:
                if 'mp4_' in key and max_key < key:
                    max_key = key
            return {'type': 'video', 'url': attachment['video']['files'][max_key]}

        else:
            return {'type': 'unavailable_video'}

    def getAudioFileFromMessage(self, attachment):
        return {'type': 'audio', 'artist': attachment['audio']['artist'], 'title': attachment['audio']['title'], 'url': attachment['audio']['url']}

    def getDocFileFromMessage(self, attachment):
        return {'type': 'doc', 'title': attachment['doc']['title'], 'url': attachment['doc']['url']}

    def getLinkFromMessage(self, attachment):
        return {'type': 'link', 'url': attachment['link']['url'], 'title': attachment['link']['title'], 'caption': attachment['link']['caption']}

    def getWallFromMessage(self, attachment):
        wall = {'type': 'wall', 'text': attachment['wall']['text']}
        if len(attachment['wall']['attachments']) > 0:
            wall['attachment'] = self.parseAttachments(attachment['wall']['attachments'])
        return wall

    def getGiftFromMessage(self, attachment):
        max_key = "thumb_0"
        for key in attachment['gift']:
            if 'thumb_' in key and max_key < key:
                max_key = key
        return {'type': 'gift', 'url': attachment['gift'][max_key]}

    def writeMessageHistoryInCSV(self, peer_id, messages):
        import csv
        last_recorded_message_ID = self.getLastMessageIDFromCSV(peer_id)
        tmp = list()
        for message in messages:
            if message['message_id'] > last_recorded_message_ID:
                tmp.append([message['message_id'], "unread",  message])

        if len(tmp) == 0:
            return messages[len(messages) - 1]['message_id']

        file = open(f"dialogs\\{peer_id}.csv", mode="a", encoding="UTF-8")
        file_writer = csv.writer(file, delimiter=";", lineterminator="\n")
        file_writer.writerows(tmp)

        return tmp[len(tmp) - 1][0]

    def getLastMessageIDFromCSV(self, peer_id):
        import csv
        csv_items = None
        if os.path.exists(f"dialogs\\{peer_id}.csv"):
            file = open(f"dialogs\\{peer_id}.csv", mode="r", encoding="UTF-8")
            csv_items = list(csv.reader(file, dialect='excel'))
            if len(csv_items) != 0:
                return int(csv_items[len(csv_items) - 1][0].split(';')[0])
        else:
            return 0

    # def deletingRowsByID(self, peer_id, message_id):
    #     import csv
    #     if os.path.exists(fr"dialogs\{peer_id}.csv"):
    #         file = open(f"dialogs\{peer_id}.csv", mode="r", encoding="UTF-8")
    #         message_table = list(csv.reader(file, dialect='excel'))
    #         print(message_table)

            # file = open(f"dialogs\{peer_id}.csv", mode="w", encoding="UTF-8")
            # csv.writer(file, delimiter=";", lineterminator="\n").writerows(updated_message_table)

    def writeMessagesToJSON(self, peer_id, unread_messages):
        last_message_id = 0
        old_data = list()
        if os.path.exists(f'dialogs/{peer_id}.json'):
            with open(f'dialogs/{peer_id}.json', mode='r', encoding='UTF-8') as file:
                old_data = json.loads(file.read())['items']
                last_message_id = old_data[len(old_data) - 1]['message_id']
                print(last_message_id)
        tmp_messages = list()

        for message in unread_messages:
            if message['message_id'] > last_message_id:
                tmp_messages.append(message)

        if len(tmp_messages) == 0:
            return unread_messages[len(unread_messages) - 1]['message_id']

        file = open(f'dialogs/{peer_id}.json', mode='w', encoding='UTF-8')
        json.dump({'count': len(old_data + tmp_messages), 'items': old_data + tmp_messages}, file, indent=4, ensure_ascii=False)

        return unread_messages[len(unread_messages) - 1]['message_id']

    def deleteMessageByIDFromJSON(self, peer_id, message_id):
        old_data = list()
        if os.path.exists(f'dialogs/{peer_id}.json'):
            with open(f'dialogs/{peer_id}.json', mode='r', encoding='UTF-8') as file:
                old_data = json.loads(file.read())['items']
        new_data = list()
        for message in old_data:
            if message['message_id'] > message_id:
                new_data.append(message)
        with open(f'dialogs/{peer_id}.json', mode='w', encoding='UTF-8') as file:
            json.dump({'count': len(new_data), 'items': new_data}, file, indent=4, ensure_ascii=False)

        if len(new_data) == 0:
            os.remove(f'dialogs/{peer_id}.json')

    def message_send(self, peer_id, content: list = '', message: str = ""):
        import time
        attachments = ''
        for item in content:
            attachments += item + ','

        link = f"{self.vk_uri}/messages.send?peer_ids={peer_id}&access_token={self.__token}&random_id={time.time()}&message={message}&attachment={attachments[0:-1]}&{self.version}"
        requests.post(link).json()
        # print(request)

    def docs_getMessagesUploadServer(self, doc_type, peer_id, filename, file_extention):
        link = f"{self.vk_uri}/docs.getMessagesUploadServer?{self.version}"
        params = {'access_token': self.__token, 'type': doc_type, "peer_id": peer_id}
        request = requests.post(link, params=params).json()

        upload_url = request['response']['upload_url']

        file = {'file': open(f'files/docs/{filename}.{file_extention}', mode='rb')}
        request = requests.post(upload_url, files=file).json()

        link = f"{self.vk_uri}/docs.save?&access_token={self.__token}&file={request['file']}&{self.version}"
        request = requests.post(link).json()

        attachment_type = request['response']['type']
        attachment_id = request['response'][request['response']['type']]['id']
        owner_id = request['response'][request['response']['type']]['owner_id']

        return f"{attachment_type}{owner_id}_{attachment_id}"

    def photos_getMessagesUploadServer(self, peer_id, filename, file_extention):
        link = f"{self.vk_uri}/photos.getMessagesUploadServer?peer_id={peer_id}&access_token={self.__token}&{self.version}"
        request = requests.post(link).json()
        # album_id = request['response']['album_id']
        upload_url = request['response']['upload_url']
        # user_id = request['response']['user_id']

        files = {'photo': open(f'files/images/{filename}.{file_extention}', mode='rb')}

        request = requests.post(upload_url, files=files).json()
        server = request['server']
        photo = request['photo']
        attachment_hash = request['hash']

        params = {"photo": photo, 'access_token': self.__token, 'server': server, 'hash': attachment_hash}
        link = f'{self.vk_uri}/photos.saveMessagesPhoto?{self.version}'
        request = requests.post(link, params=params).json()

        return f"photo{request['response'][0]['owner_id']}_{request['response'][0]['id']}"

    def audio_getUploadServer(self, peer_id, filename, file_extention , audio_info = []):
        link = f"{self.vk_uri}/audio.getUploadServer?&access_token={self.__token}&{self.version}"
        request = requests.post(link).json()
        upload_url = request['response']['upload_url']

        file = {'file' : open(fr'files/audios/{filename}.{file_extention}', mode='rb')}
        request = requests.post(upload_url, files=file).json()

        params = {'server' : request['server'], 'audio' : request['audio'], 'hash' : request['hash']}
        if audio_info:
            params['artist'] = audio_info[0]
            params['title'] = audio_info[1]

        link = f"{self.vk_uri}/audio.save?&access_token={self.__token}&{self.version}"
        request = requests.post(link, params=params).json()

        return f"audio{request['response']['owner_id']}_{request['response']['id']}"

    def video_save(self, file_name = None, file_extention = None, title = 'unknown', url = None):
        if len(title) > 128 :
            title = title[0:127]
        params = {'name' : title, 'link' : url, 'is_private' : 1}
        link = f"{self.vk_uri}/video.save?&access_token={self.__token}&{self.version}"
        request = requests.post(link, params=params).json()
        upload_url = request['response']['upload_url']
        video_id =  request['response']['video_id']
        owner_id = request['response']['owner_id']

        file = dict()
        if url is None and file_name is not None and file_extention is not None:
            file = { 'video_file' : open(f'files/videos/{file_name}.{file_extention}')}
        requests.post(upload_url, files=file)

        return f'video{owner_id}_{video_id}'
    def saveFileFromURL(self, url, directory, filename, file_extention):
        with open(f'files/{directory}/{filename}.{file_extention}', mode='wb') as docs:
            ufr = requests.get(url)
            docs.write(ufr.content)

    def deleteFileFromDisk(self, directory, filename, file_extantion):
        if os.path.exists(f'files/{directory}/{filename}.{file_extantion}'):
            os.remove(f'files/{directory}/{filename}.{file_extantion}')
