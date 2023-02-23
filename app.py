from bot_tg import *
from bot_vk import *

def checkUnreadChats():
    unread_chats = BotVK().messages_getConversations()
    message = f"У вас есть {len(unread_chats)} беседы с непрочитанными сообщениями:\n"
    for u_chat in unread_chats:
        print(u_chat['id'], u_chat['from'])
        message+=f"\t-{u_chat['from']} ({u_chat['unread']})\n"
    BotTG().sendMessage(message)



if __name__ == '__main__':
    # u_chats = BotVK().messages_getConversations()
    # BotVK().messages_getHistory('223363592')
    # BotTG().getUpdatesFromTelegram()
    audio = "https://cs5-1v4.vkuseraudio.net/s/v1/acmp/3LJ-iXF-4JMK9_WglqJ9DGqhWvPS2U7LHd_NWH8ms3tF1f3WYqCT2Ne85YmAEMNzV_BnLBKfbxv3CejGx1if-MWLQOu4n4m1FxHoalXdtqKCjXIIlcsF_9f3i-zJbuLj5Yy3A68eH_BHeeHpXU-X0HuI5tEuyEGD0yiUQSygLNnOKewVbA.mp3"
    photo = "https://sun9-18.userapi.com/impg/md5rgO_79vYy-7k1URCSvWOIhZYQACthkkVaZA/aNoHz-Pi2r8.jpg?size=75x58&quality=96&sign=e2594e24ac91e559cb9d566044a39b82&c_uniq_tag=8a8J0kjmDKLd5Zo4lw78BefvoOKJB_7c2WXFHldNRbg&type=album"
    BotTG().sendMediaGroup([{'photo' : photo}, {'photo' : photo}])
    # BotTG().sendAudioMessage(audio, "Hello human", "Жоповоз - Эсмеральда")

