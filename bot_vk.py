import requests
from auth_info import *

class BotVK():
    def __init__(self):
        self.__ID = my_vk_id
        self.__token = vk_token
        self.vk_uri = "https://api.vk.com/method/"
        self.version = "v=5.131"

    def message_parse(self, message_item : dict, users_list : dict):
        import datetime
        # print(message_item)
        message = dict()
        message['message_id'] = message_item['id']
        message['from'] = f"{users_list[message_item['from_id']]['first_name']} {users_list[message_item['from_id']]['last_name']}"
        message['text'] = message_item['text']
        message['datetime'] = datetime.datetime.fromtimestamp(message_item['date'])
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

    def messages_getHistory(self, user_ids):
        start_message_id = -1
        unread_messages = self.messages_GetConversationsById(user_ids)
        users_list = self.getConversationMembers(user_ids)

        while unread_messages > 0:
            if unread_messages >= 200:
                offset = -200
            else:
                offset = -unread_messages

            link = f"{self.vk_uri}/messages.getHistory?peer_id={user_ids}&access_token={self.__token}&{self.version}&offset={offset}&start_message_id={start_message_id}&count={-offset}&extended=1"
            request = requests.post(link).json()

            messages = list()
            for item in request['response']['items']:
                messages.append(self.message_parse(item, users_list))
            messages.reverse()

            # print(messages)

            unread_messages += offset
            start_message_id = self.writeMessageHistoryInCSV(user_ids, messages)


    def messages_getMessageID(self,  user_ids : str):
        offset = self.messages_GetConversationsById(user_ids)
        link = f"{self.vk_uri}/messages.getHistory?peer_id={user_ids}&access_token={self.__token}&{self.version}&offset={offset}&start_message_id=-1&count={-offset}&extended=1"
        request = requests.post(link).json()
        list_of_message_ID = list()
        for message in request['response']['items']:
            list_of_message_ID. append(message['id'])

        return list_of_message_ID[0]

    def messages_markAsRead(self, user_ids : str, message_ID : str):
        link = f"{self.vk_uri}/messages.markAsRead?peer_id={user_ids}&access_token={self.__token}&{self.version}&start_message_id={message_ID}"
        requests.post(link).json()

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
        message = {'sticker' : None, 'audio_message' : None, 'photo' : list(), 'link' : None, 'video' : list(), 'audio' : list(), 'gift' : None, 'wall' : None, 'doc' : list()}

        for attachment in attachments:
            if attachment['type'] == 'sticker':
                message['sticker'] = self.getStickerFromMessage(attachment['sticker'])
            if attachment['type'] == 'audio_message':
                message['audio_message'] =  self.getVoiceFromMessage(attachment)
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
        return {'type' : 'sticker', 'sticker_id' : sticker['sticker_id'], 'url': sticker['images'][len(sticker['images']) - 1]['url']}

    def getVoiceFromMessage(self, attachment):
        # print(f"Audio URL: {attachment['audio_message']['link_ogg']}")
        return {'type' : 'audio_message', 'url' : attachment['audio_message']['link_ogg']}

    def getImageFromMessage(self, attachment):
        max_size = 'a'
        picture_url = None
        for size in attachment['photo']['sizes']:
            if size['type'] == 'w':
                return {'type': 'photo', 'url': size['url']}

            if max_size < size['type']:
                max_size = size['type']
                picture_url = size['url']

        return {'type' : 'photo', 'url' : picture_url}


    def getVideoFromMessage(self, attachment):
        if 'files' in attachment['video']:
            if 'external' in attachment['video']['files']:
                return {'type' : 'video', 'url' : attachment['video']['files']['external']}

            max_key = "mp4_144"
            for key in attachment['video']['files']:
                if 'mp4_' in key and max_key < key:
                    max_key = key
            return {'type' : 'video', 'url' : attachment['video']['files'][max_key]}

        else:
            return {'type' : 'unavailable_video'}

    def getAudioFileFromMessage(self, attachment):
        return {'type' : 'audio', 'artist' : attachment['audio']['artist'], 'title' : attachment['audio']['title'], 'url' : attachment['audio']['url']}

    def getDocFileFromMessage(self, attachment):
        return {'type' : 'doc', 'title' : attachment['doc']['title'], 'url' : attachment['doc']['url']}

    def getLinkFromMessage(self, attachment):
        return {'type' : 'link', 'url' : attachment['link']['url'], 'title' : attachment['link']['title'], 'caption' : attachment['link']['caption']}

    def getWallFromMessage(self, attachment):
        wall = {'type' : 'wall'}
        wall['text'] = attachment['wall']['text']
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
        last_recorded_message_ID =self.getLastMessageIDFromCSV(peer_id)
        tmp = list()
        for message in messages:
            if message['message_id'] > last_recorded_message_ID:
                tmp.append([message['message_id'], message])

        if len(tmp) == 0:
            return messages[len(messages) - 1]['message_id']

        try:
            file = open(f"dialogs\{peer_id}.csv", mode="x", encoding="UTF-8")
            file_writer = csv.writer(file, delimiter=";", lineterminator="\n")
            file_writer.writerows(tmp)
        except FileExistsError:
            file = open(f"dialogs\{peer_id}.csv", mode="a", encoding="UTF-8")
            file_writer = csv.writer(file, delimiter=";", lineterminator="\n")
            file_writer.writerows(tmp)

        return tmp[len(tmp) - 1][0]

    def getLastMessageIDFromCSV(self, peer_id):
        import os, csv
        csv_items = None
        if os.path.exists(fr"dialogs\{peer_id}.csv"):
            file = open(f"dialogs\{peer_id}.csv", mode="r", encoding="UTF-8")
            csv_items = list(csv.reader(file, dialect='excel'))
            if len(csv_items) != 0:
                return int(csv_items[len(csv_items) - 1][0].split(';')[0])
        else:
            return 0
