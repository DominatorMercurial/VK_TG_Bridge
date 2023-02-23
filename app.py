from bot_tg import *
from bot_vk import *

def checkUnreadChats():
    unread_chats = BotVK().messages_getConversations()
    message = f"У вас есть {len(unread_chats)} беседы с непрочитанными сообщениями:\n"
    for u_chat in unread_chats:
        # print(u_chat['id'], u_chat['from'])
        message+=f"\t-{u_chat['from']} ({u_chat['unread']})\n"
    BotTG().sendMessage(message)

def getAllMessages():
    unread_chats = BotVK().messages_getConversations()
    for u_chat in unread_chats:
        messages = BotVK().messages_getHistory(u_chat['id'])
        # BotTG().sendMultiMessage(messages)

if __name__ == '__main__':
    # checkUnreadChats()
    getAllMessages()
    # messages = BotVK().messages_getHistory('227002628')
    # BotTG().sendMultiMessage(messages)



