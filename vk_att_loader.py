# -*- coding: utf-8 -*-
""" Модуль для бота ВК, загружающий все вложения из пересланному ему сообщению
by far-galaxy

:copyright: (c) 2022 far-galaxy https://github.com/far-galaxy 
:license: GNU GPL v3.0, see LICENSE for more details.
"""
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.tools import VkTools
from vk_api.utils import get_random_id
import os

class VkAttLoader(object):
    """ Класс инструмента для загрузки всех вложений из сообщения, пересланному боту"""
    def __init__(self):
        self.get_token()
        self.vk = vk_api.VkApi(token = self.token)
        self.longpoll = VkLongPoll(self.vk, wait=1)
        self.tools = VkTools(self.vk)
       
    def get_token(self):
        """Загрузка токена из файла `token.txt`
        
        Подробнее о получении токена для своего бота:
        https://dev.vk.com/api/access-token/getting-started
        
        Можно самостоятельно создать файл `token.txt` и вставить в него токен.
        
        Если этого не сделать, программа сама попросит ввести токен, после чего она сохранит его 
        для дальнейшего использования.
        """
        
        path = "token.txt"
        if os.path.exists(f"{path}"):
            with open(f"{path}", "r", encoding="utf-8") as f:
                self.token = f.read()                        
        else:
            self.token = input(f"Token file not found. Please type token now:")
            with open(f"{path}", "w", encoding="utf-8") as f:
                f.write(self.token)
                
    def msg(self, user_id, message):
        """Отправка сообщения
        
        :user_id: id пользователя
        :message: текст сообщения
        """
        data = {}
        data['user_id'] = user_id
        data['random_id'] = get_random_id()
        data['message'] = message
        return self.vk.method('messages.send', data)           
                
                
    def check_messages(self, keyword = ""):
        """Проверка наличия входящих сообщений и скачивание вложений
        
        :keyword: Команда, на которую будет откликаться бот и выполнять скачивание. При пустом значении будет реагировать на любое сообщение
        """
        events = self.longpoll.check()
        messages = []
        for event in events:
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if keyword == "" or (keyword != "" and event.text == keyword):
                    messages.append(event)
                    self.messages = messages
                    self.load_attachments()
        
    def get_att(self, messages):
        """Рекурсивная функция по поиску вложений в принятых сообщениях
        
        :messages: :class:`list` список `объектов сообщений ВК <https://dev.vk.com/reference/objects/message>`_.
        
        Ссылки на фотографии записываются в :class:`list` self.urls
        """
        for m in messages:
            if 'attachments' in m and len(m['attachments']) != 0:
                        for att in m['attachments']:  
                            # Фотографии
                            if 'photo' in att:
                                photo = self.find_finest_photo(att['photo']['sizes'])
                                self.urls.append(photo)
                                
            if 'fwd_messages' in m:
                self.get_att(m['fwd_messages'])
                                
    def find_finest_photo(self, sizes):
        """
        Поиск фотографии с наилучшим разрешением
        
        :sizes: :class:`list` список размеров фотографий
        
        :returns: :class:`str` ссылка на фотографию
        """
        max_s = 0
        max_i = 0
        for n, p in enumerate(sizes):
            s = p['height']*p['width']
            if s > max_s:
                max_i = n
                max_s = s
        return sizes[max_i]["url"]
            
        
    def load_attachments(self):
        """
        Загрузка всех вложений
        """
        
        for message in self.messages:
            full_msg = self.tools.get_all_iter("messages.getById",
                                               100, 
                                               values = {"message_ids":message.message_id})
            self.count = 0
            self.urls = []
            self.msg(message.user_id, "Загрузка вложений...")
            self.get_att(full_msg)
            print(self.urls)
            self.msg(message.user_id, "Вложения загружены")
        
                
    
if __name__ == "__main__":
    bot = VkAttLoader()
    print("Bot ready")
    
    while True:
        bot.check_messages()
        
