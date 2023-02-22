from array import array
import requests
from auth_info import *

class BotTG():
    def __init__(self):
        self.__API_Link = f"https://api.telegram.org/bot{tg_token}/"
        self._last_message_id = 0
        self._myID = my_tg_id
        self.__mailing_list = list()

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
        print(send_message)

    def updatesInfo(self, updates):
        for item in updates['result']:
            if 'message' in item:
                user = item['message']['from']
                chat = item['message']['chat']
                print(f"UPDATE ID: {item['update_id']}")
                if 'title' in chat:
                    print(f"TITLE: {chat['title']} | TYPE {chat['type']} | CHAT ID: {chat['id']}")
                print(f"USER NAME: {user['username']} | NAME: {user['first_name']} {user['last_name']} | USER ID: {user['id']}")

                if 'text' in item['message']:
                    print(f"MESSAGE: {item['message']['text']}")

                    if 'entities' in item['message']:
                        for entity in item['message']['entities']:
                            print(f"\tMESSAGE LENGTH: {entity['length']}")
                            print(f"\tMESSAGE TYPE: {entity['type']}")
                print()

    def getUpdatesFromTelegram(self):
        updates = requests.get(self.__API_Link + f"getUpdates?").json()
        self.updatesInfo(updates)
        # self._last_message_id = updates["result"][len(updates["result"]) - 1]['update_id']
        #
        # status = updates['ok']
        # message = updates['result'][0]['message']
        # chat_id = message['from']['id']
        # text = message['text']
        #
        # return {"status": status, "chat_id": chat_id, "text": text}

