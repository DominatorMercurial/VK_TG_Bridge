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

def checkUnreadChats(bot_tg: BotTG):
    unread_chats = BotVK().messages_getConversations()
    message = f"У вас есть {len(unread_chats)} бесед(ы) с непрочитанными сообщениями:\n"

    u_chat_list = list()
    for u_chat in unread_chats:
        print(u_chat['id'], u_chat['from'])
        u_chat_list.append({
            u_chat['from']: u_chat['id']
        })
        message+=f"\t-{u_chat['from']} ({u_chat['unread']})\n"
    bot_tg.sendMessage(message)

    return u_chat_list

def getAllUnreadMessages():
    unread_chats = BotVK().messages_getConversations()
    for u_chat in unread_chats:
        messages = BotVK().messages_getHistory(u_chat['id'])



if __name__ == '__main__':
    directoryChecker()
    

    bot_tg = BotTG()

    while True:
        for parsed_update in bot_tg.listenForUpdates():
            if parsed_update['command'] == "/unread":
               bot_tg.u_chat_list = checkUnreadChats(bot_tg)
            if parsed_update['command'] == "#too much mathes":
                bot_tg.sendMessage("<b>ERROR!</b>\nУкажите название беседы более конкретно, по вашему запросу найдено более одного совпадения")
            if parsed_update['command'] == "#no matches":
                bot_tg.sendMessage("<b>ERROR!</b>\nПо вашему запросу не найдено ни одного совпадения.")
            print(parsed_update)


