from bot_tg import *
from bot_vk import *

def checkUnreadChats():
    unread_chats = BotVK().messages_getConversations()
    message = f"У вас есть {len(unread_chats)} беседы с непрочитанными сообщениями:\n"
    for u_chat in unread_chats:
        message+=f"\t-{u_chat['from']} ({u_chat['unread']})\n"
    BotTG().sendMessage(message)



if __name__ == '__main__':
    u_chats = BotVK().messages_getConversations()
    BotVK().messages_getHistory('223363592')



