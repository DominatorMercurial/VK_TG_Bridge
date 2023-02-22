import requests
from auth_info import *

class BotVK():
    def __init__(self):
        self.__ID = my_vk_id
        self.__token = vk_token
        self.vk_uri = "https://api.vk.com/method/"
        self.version = "v=5.131"

    def messages_GetConversationsById(self, user_ids):
        link = f"{self.vk_uri}/messages.getConversationsById?peer_ids={user_ids}&access_token={self.__token}&fields=unread_count&{self.version}"
        request = requests.post(link).json()
        in_read_cmid = request['response']['items'][0]['in_read_cmid']
        out_read_cmid = request['response']['items'][0]['out_read_cmid']
        if in_read_cmid > out_read_cmid:
            print("Your messages unread")
        elif out_read_cmid > in_read_cmid:
            offset =  in_read_cmid - out_read_cmid
            print(f"You have {-offset} unread messages")
        else:
            print("Nothing new")
        return offset

    def messages_getHistory(self, user_ids):
        import datetime
        offset = self.messages_GetConversationsById(user_ids)
        link = f"{self.vk_uri}/messages.getHistory?peer_id={user_ids}&access_token={self.__token}&{self.version}&offset={offset}&start_message_id=-1&count={-offset}&extended=1"
        request = requests.post(link).json()
        messages = list()
        users_list = self._getUsers(request)

        for item in request['response']['items']:
            message = ""
            message += f"От: {users_list[item['from_id']]['first_name']} {users_list[item['from_id']]['last_name']}\n{item['text']}\n"
            message += f"В: {datetime.datetime.fromtimestamp(item['date'])}"
            for attachment in item['attachments']:
                if attachment['type'] == 'video':
                    self.getVideoMessage(attachment)
                if attachment['type'] == 'photo':
                    self.getImageMessage(attachment)
            messages.append(message)
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
        users_info = dict()
        for user in request['response']['profiles']:
            users_info[user['id']] = {"first_name" : user['first_name'], 'last_name' : user['last_name']}
        return users_info

    def getImageMessage(self, attachment):
        print(attachment['photo'])
        for size in attachment['photo']['sizes']:
            print(size)
        print()
    def getVideoMessage(self, attachment):
        video_url = list
        print(attachment['video'])
        # # print(attachment['video']['qualities_info'])
        # for part in attachment['video']['files']:
        #     video_url.append(attachment['video']['files'][str(part)])
        # print(video_url)