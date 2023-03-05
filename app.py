import shutil
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
        message+=f"\t-{u_chat['from']} ({u_chat['unread']})\n"
    bot_tg.sendMessage(message)


def getAllUnreadMessages():
    unread_chats = BotVK().messages_getConversations()
    for u_chat in unread_chats:
        messages = BotVK().messages_getUnreadHistory(u_chat['id'])
        print(messages)


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



if __name__ == '__main__':
    directoryChecker()
    # checkUnreadChats()
    # getAllUnreadMessages()
    # BotVK().messages_markAsRead('2000000015', 150358)
    #BotVK().deletingRowsByID('2000000015', 150431)
    # print(BotVK().getLastMessageIDFromCSV('2000000015'))

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
