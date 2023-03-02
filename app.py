from bot_tg import *
from bot_vk import *

def directoryChecker():
    import os
    if not os.path.exists('dialogs'):
        os.mkdir('dialogs')

    if not os.path.exists('files'):
        os.mkdir('files')

    folders = [
        'data',
        'photos',
        'videos'
    ]

    for folder in folders:
        if not os.path.exists(os.path.join('files', folder)):
            os.mkdir(os.path.join('files', folder))

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
        messages = BotVK().messages_getHistory(u_chat['id'])


# class A:
#     def test(self):
#         parsed_update = {
#                 'from': None,
#                 'date': None,
#                 'text': None,
#                 'photo': None,
#                 'video': None,
#                 'caption': None
#             }
#         return parsed_update
    
#     def test2():
#         return



if __name__ == '__main__':
    directoryChecker()
    

    bot_tg = BotTG()

    while True:
        for parsed_update in bot_tg.listenForUpdates():
            print(parsed_update['from'])

