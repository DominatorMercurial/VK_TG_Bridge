import shutil
from bot_tg import *
from bot_vk import *
import time


def directoryChecker():
    if not os.path.exists('dialogs'):
        os.mkdir('dialogs')
    if not os.path.exists('files'):
        os.mkdir('files')
        os.mkdir('files/docs')
        os.mkdir('files/images')
        os.mkdir('files/videos')
        os.mkdir('files/audios')

    if not os.path.exists('files_tg'):
        os.mkdir('files_tg')

    folders = [
        'data',
        'photos',
        'videos'
    ]

    for folder in folders:
        if not os.path.exists(os.path.join('files_tg', folder)):
            os.mkdir(os.path.join('files_tg', folder))


def deleteAllFiles():
    shutil.rmtree('files')
    directoryChecker()


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
    start_ids_list = list()
    unread_chats = BotVK().messages_getConversations()
    for u_chat in unread_chats:
        start_message_id = BotVK().messages_getUnreadHistory(u_chat['id'])
        print(start_message_id)
        start_ids_list.append({
            str(u_chat['id']): start_message_id
        })

    return start_ids_list


def saveImageFromUrlList(urls):
    name_counter = 0
    for url in urls:
        BotVK().saveFileFromURL(url, 'images', name_counter, 'png')
        name_counter += 1


def getAllPhotos(peer_id):
    content = list()
    image_name_list = os.listdir('files/images')
    for name in image_name_list:
        filename = name.split(".")[0]
        file_extention = name.split(".")[1]
        content.append(BotVK().photos_getMessagesUploadServer(peer_id, filename, file_extention))
    return content


def getAllDocs(peer_id):
    list_of_audio_extention = ['mp3', 'mp4', 'asf', 'avi', 'wmv']
    content = list()
    image_name_list = os.listdir('files/docs')
    for name in image_name_list:
        filename = name.split(".")[0]
        file_extention = name.split(".")[1]
        doc_type = 'audio_message' if file_extention in list_of_audio_extention else 'doc'
        content.append(BotVK().docs_getMessagesUploadServer(doc_type, peer_id, filename, file_extention))

    return content

def getAllvideos():
    content = list()
    videos_name_list = os.listdir('files/videos')
    for name in videos_name_list:
        filename = name.split(".")[0]
        file_extention = name.split(".")[1]
        content.append(BotVK().video_save(filename, file_extention))

    return content


def getVideoByURL(link):
    content = list()
    content.append(BotVK().video_save(url=link))
    return content

def startBotVK(bot_tg: BotTG):
    
    sleep_time = 2

    while True:
        start_ids_list = getAllUnreadMessages()
        print("START ID LIST", start_ids_list)
        if start_ids_list == []:
            sleep_time = 3
        else:
            sleep_time = 1
            bot_tg.start_ids_list = start_ids_list

        time.sleep(sleep_time)

def startBotTG(bot_tg: BotTG):
    sleep_time = 2
    
    while True:
        
        for parsed_update in bot_tg.listenForUpdates():
            if parsed_update['command'] == "/unread":
               bot_tg.u_chat_list = checkUnreadChats(bot_tg)
            if parsed_update['command'] == "#too much mathes":
                bot_tg.sendMessage("<b>ERROR!</b>\nУкажите название беседы более конкретно, по вашему запросу найдено более одного совпадения")
            if parsed_update['command'] == "#no matches":
                bot_tg.sendMessage("<b>ERROR!</b>\nПо вашему запросу не найдено ни одного совпадения.")
            # print(parsed_update)
            if parsed_update == []:
                sleep_time = 3
            else:
                sleep_time = 1

        time.sleep(sleep_time)

if __name__ == '__main__':
    import threading

    directoryChecker()
    # checkUnreadChats()
    # getAllUnreadMessages()
    # BotVK().messages_markAsRead('2000000015', 150358)
    #BotVK().deletingRowsByID('2000000015', 150431)
    # print(BotVK().getLastMessageIDFromCSV('2000000015'))

    bot_tg = BotTG()
    args = (bot_tg,)

    threadVK = Thread(target=startBotVK, args=args)
    threadVK.start()

    threadTG = Thread(target=startBotTG, args=args)
    threadTG.start()

    

        
