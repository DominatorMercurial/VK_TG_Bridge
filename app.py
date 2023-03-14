import shutil
from bot_tg import *
from bot_vk import *
import time

class App:


    def __init__(self):
        self.bot_tg = BotTG()
        self.bot_vk = BotVK()

    def start(self):
        import threading

        self.directoryChecker()

        threadVK = Thread(target=self.startBotVK)
        threadVK.start()

        threadTG = Thread(target=self.startBotTG)
        threadTG.start()

    def directoryChecker(self):
        if not os.path.exists('dialogs'):
            os.mkdir('dialogs')
        if not os.path.exists('files'):
            os.mkdir('files')
            os.mkdir('files/docs')
            os.mkdir('files/photos')
            os.mkdir('files/videos')
            os.mkdir('files/audios')
            os.mkdir('files/data')
            open('files/data/saved_update.txt', mode='w').close()

        # if not os.path.exists('files_tg'):
        #     os.mkdir('files_tg')

        # folders = [
        #     'data',
        #     'photos',
        #     'videos'
        # ]

        # for folder in folders:
        #     if not os.path.exists(os.path.join('files_tg', folder)):
        #         os.mkdir(os.path.join('files_tg', folder))


    def deleteAllFiles(self):
        shutil.rmtree('files')
        self.directoryChecker()


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

    def checkUnreadChats(self):
        unread_chats = self.bot_vk.messages_getConversations()
        message = f"У вас есть {len(unread_chats)} бесед(ы) с непрочитанными сообщениями:\n"

        u_chat_list = list()
        for u_chat in unread_chats:
            # print(u_chat['id'], u_chat['from'])
            u_chat_list.append({
                u_chat['from']: u_chat['id']
            })
            message+=f"\t-{u_chat['from']} ({u_chat['unread']})\n"
        self.bot_tg.sendMessage(message)
        
        return u_chat_list


    def getAllUnreadMessages(self):
        start_ids_list = list()
        unread_chats = self.bot_vk.messages_getConversations()
        for u_chat in unread_chats:
            start_message_id = self.bot_vk.messages_getUnreadHistory(u_chat['id'])
            # print(start_message_id)
            start_ids_list.append({
                str(u_chat['id']): start_message_id
            })

        return start_ids_list


    def saveImageFromUrlList(self, urls):
        name_counter = 0
        for url in urls:
            self.bot_vk.saveFileFromURL(url, 'images', name_counter, 'png')
            name_counter += 1


    def getAllPhotos(self, peer_id):
        content = list()
        image_name_list = os.listdir('files/photos')
        for name in image_name_list:
            filename = name.split(".")[0]
            file_extention = name.split(".")[1]
            content.append(self.bot_vk.photos_getMessagesUploadServer(peer_id, filename, file_extention))
        return content


    def getAllDocs(self, peer_id):
        list_of_audio_extention = ['mp3', 'mp4', 'asf', 'avi', 'wmv']
        content = list()
        image_name_list = os.listdir('files/docs')
        for name in image_name_list:
            filename = name.split(".")[0]
            file_extention = name.split(".")[1]
            doc_type = 'audio_message' if file_extention in list_of_audio_extention else 'doc'
            content.append(self.bot_vk.docs_getMessagesUploadServer(doc_type, peer_id, filename, file_extention))

        return content

    def getAllvideos(self):
        content = list()
        videos_name_list = os.listdir('files/videos')
        for name in videos_name_list:
            filename = name.split(".")[0]
            file_extention = name.split(".")[1]
            content.append(self.bot_vk.video_save(filename, file_extention))

        return content


    def getVideoByURL(self, link):
        content = list()
        content.append(self.bot_vk.video_save(url=link))
        return content

    def getSinglePhoto(self, file_path: str):
        items = file_path.split('.')
        return self.bot_vk.photos_getMessagesUploadServer(self.bot_tg.current_chat, items[0], items[1])
    
    def getSingleVideo(self, file_path: str):
        items = file_path.split('.')
        return self.bot_vk.video_save(file_name=items[0], file_extention=items[1])

    def startBotVK(self):
        
        sleep_time = 2

        while True:
            start_ids_list = self.getAllUnreadMessages()
            # print("START ID LIST", start_ids_list)
            if start_ids_list == []:
                sleep_time = 3
            else:
                sleep_time = 1
                self.bot_tg.start_ids_list = start_ids_list

            time.sleep(sleep_time)

    def startBotTG(self):
        sleep_time = 2
        
        while True:
            
            for parsed_update in self.bot_tg.listenForUpdates():
                if parsed_update['command'] == "/unread":
                    self.bot_tg.u_chat_list = self.checkUnreadChats()

                if parsed_update['command'] == "#too much mathes":
                    self.bot_tg.sendMessage("<b>ERROR!</b>\nУкажите название беседы более конкретно, по вашему запросу найдено более одного совпадения")

                if parsed_update['command'] == "#no matches":
                    self.bot_tg.sendMessage("<b>ERROR!</b>\nПо вашему запросу не найдено ни одного совпадения.")
                # print(parsed_update)


                content = list()
                flag_media = False
                if parsed_update['command'] == None:
                    if parsed_update['text'] != None:
                        self.bot_vk.message_send(self.bot_tg.current_chat, message=parsed_update['text'])
                    if parsed_update['photo'] != None:
                        content.append(self.getSinglePhoto(parsed_update['photo'][13:]))
                        flag_media = True
                    if parsed_update['video'] != None:
                        content.append(self.getSingleVideo(parsed_update['video'][13:]))
                        flag_media = True

                    if flag_media == True:
                        msg = ''
                        if parsed_update['caption'] != None:
                            msg = parsed_update['caption']
                        self.bot_vk.message_send(self.bot_tg.current_chat, content=content, message=msg)


                if parsed_update == []:
                    sleep_time = 3
                else:
                    sleep_time = 1

            time.sleep(sleep_time)

if __name__ == '__main__':
    app = App()
    app.start()

    

        
