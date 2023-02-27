import os
from bot_tg import *
from bot_vk import *

def directoryChecker():
    if not os.path.exists('dialogs'):
        os.mkdir('dialogs')
    if not os.path.exists('files'):
        os.mkdir('files')
        os.mkdir('files/docs')
        os.mkdir('files/images')
        os.mkdir('files/videos')
        os.mkdir('files/audios')

def checkUnreadChats():
    unread_chats = BotVK().messages_getConversations()
    message = f"У вас есть {len(unread_chats)} бесед(ы) с непрочитанными сообщениями:\n"
    for u_chat in unread_chats:
        print(u_chat['id'], u_chat['from'])
        message+=f"\t-{u_chat['from']} ({u_chat['unread']})\n"
    BotTG().sendMessage(message)

def getAllUnreadMessages():
    unread_chats = BotVK().messages_getConversations()
    for u_chat in unread_chats:
        messages = BotVK().messages_getUnreadHistory(u_chat['id'])

def saveImageFromUrlList(urls):
    name_counter = 0
    for url in urls:
        BotVK().saveFileFromURL(url, 'images', name_counter, 'png')
        name_counter += 1
def sendAllPhotos(peer_id, message):
    content = list()
    image_name_list = os.listdir('files/images')
    for name in image_name_list:
        filename = name.split(".")[0]
        file_extention = name.split(".")[1]
        content.append(BotVK().photos_getMessagesUploadServer(peer_id, filename, file_extention))
    BotVK().message_send(peer_id, content, message)

# url = 'https://sun5-4.userapi.com/impg/nKyAOQJRL8JMfKv5_9yuq3-YfulYvLMbXX4EHA/5AbaDXv8WHA.jpg?size=1920x1200&quality=96&sign=9fb04561d8052df80d5e6293cdd82ec6&c_uniq_tag=5mrEjqrBj-abKbPveEYRWNOl93Oerzef3iD9-fPVf9w&type=album'
if __name__ == '__main__':
    directoryChecker()