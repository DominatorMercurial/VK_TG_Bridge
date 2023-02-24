from bot_tg import *
from bot_vk import *

def directoryChecker():
    import os
    if not os.path.exists('dialogs'):
        os.mkdir('dialogs')

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

if __name__ == '__main__':
    directoryChecker()
    # checkUnreadChats()
    getAllUnreadMessages()
    # print(BotVK().getLastMessageIDFromCSV('2000000015'))
