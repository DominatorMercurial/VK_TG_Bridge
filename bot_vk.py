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
        if in_read_cmid > out_read_cmid:
            print("Your messages unread")
        elif out_read_cmid > in_read_cmid:
            offset =  in_read_cmid - out_read_cmid
            if offset < -200:
                offset = -200
            print(f"You have {-offset} unread messages")
        else:
            print("Nothing new")
        return offset

    def messages_getHistory(self, user_ids):

        offset = self.messages_GetConversationsById(user_ids)
        link = f"{self.vk_uri}/messages.getHistory?peer_id={user_ids}&access_token={self.__token}&{self.version}&offset={offset}&start_message_id=-1&count={-offset}&extended=1"
        request = requests.post(link).json()
        users_list = self._getUsers(request)

        messages = list()
        for item in request['response']['items']:
            messages.append(self.message_parse(item, users_list))
        messages.reverse()

        return messages

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
        users_list  = self._getUsers(request)

        chats_info = list()
        for item in request['response']['items']:
            chat_i = dict()
            chat_i["id"] = item['conversation']['peer']['id']
            if item['conversation']['peer']['type'] == 'chat':
                chat_i["from"] = item['conversation']['chat_settings']['title']
            else:
                chat_i["from"] = f"{users_list[chat_i['id']]['first_name']} {users_list[chat_i['id']]['last_name']}"
            chat_i['unread'] = item['conversation']['unread_count']
            chats_info.append(chat_i)

        return chats_info


    def _getUsers(self, request : dict):
        users_info = {-190195384 : {'first_name' : 'Сглыпа', 'last_name' : 'Ебаная'}}
        for user in request['response']['profiles']:
            users_info[user['id']] = {"first_name" : user['first_name'], 'last_name' : user['last_name']}
        return users_info

    def parseAttachments(self, attachments):
        message = {'sticker' : None, 'audio_message' : None, 'photo' : list(), 'link' : None, 'video' : None, 'audio' : list(), 'gift' : None, 'wall' : None}

        for attachment in attachments:
            # print(attachment)
            if 'sticker' in attachment:
                message['sticker'] = self.getSticker(attachment['sticker'])
        #     if attachment['type'] == 'video':
        #         self.getVideoMessage(attachment)
        #     if attachment['type'] == 'photo':
        #         message['photo_urls'].append(self.getImageMessage(attachment))
        #     if attachment['type'] == 'audio_message':
        #         message['audio_message'] =  self.getAudioMessage(attachment)
        #     if attachment['type'] == 'audio':
        #         message['audio_file'] = self.getAudioFileMessage(attachment)

        return message

    def getSticker(self, sticker):
        # print(f"Sticker ID: {sticker['sticker_id']}")
        # print(f"Sticker URL: {sticker['images'][len(sticker['images']) - 1]['url']}")
        return {'type' : 'sticker', 'sticker_id' : sticker['sticker_id'], 'url': sticker['images'][len(sticker['images']) - 1]['url']}

    def getImageMessage(self, attachment):
        max_size = 'a'
        picture_url = None
        for size in attachment['photo']['sizes']:
            if max_size < size['type']:
                max_size = size['type']
                picture_url = size['url']

        return picture_url


    def getVideoMessage(self, attachment):
        video_url = list()
        # print(attachment['video'])
        # # print(attachment['video']['qualities_info'])
        # for part in attachment['video']['files']:
        #     video_url.append(attachment['video']['files'][str(part)])
        # print(video_url)

    def getAudioMessage(self, attachment):
        voice_url = attachment['audio_message']['link_ogg']
        return voice_url

    def getAudioFileMessage(self, attachment):
        artist = attachment['audio']['artist']
        title = attachment['audio']['title']
        url = attachment['audio']['url']
        return {'artist' : artist, 'title' : title, 'url' : url}

    def getVoiceMessage(self, attachment):
        pass

    def getFileMessage(self, attachment):
        pass