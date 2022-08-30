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
import requests
import shutil

class VkAttLoader(object):
    """ Класс инструмента для загрузки всех вложений из сообщения, пересланному боту"""
    def __init__(self):
        self.get_token()
        self.vk = vk_api.VkApi(token = self.token)
        self.longpoll = VkLongPoll(self.vk, wait=1)
        self.tools = VkTools(self.vk)
        self.messages = None
       
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
        
        :keyword: Команда, на которую будет откликаться бот и выполнять скачивание. \n
        При пустом значении keyword будет реагировать на любое сообщение (не рекомендуется)
        """
        events = self.longpoll.check()
        messages = []
        for event in events:
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if keyword == "" or (keyword != "" and event.text == keyword):
                    messages.append(event)
                    self.messages = messages
                    
        
    def get_att(self, messages):
        """Рекурсивная функция по поиску вложений в принятых сообщениях
        
        :messages: :class:`list` список `объектов сообщений ВК <https://dev.vk.com/reference/objects/message>`_.
        
        Подробнее, куда записываются вложения: \n
        Фото: :class:`get_photo`
        """
        for m in messages:
            if 'attachments' in m and len(m['attachments']) != 0:
                        for att in m['attachments']:  
                            # Фотографии
                            if 'photo' in att:
                                self.get_photo(att)
                            # Фото и документы из поста    
                            elif 'wall' in att:
                                docs = att['wall']['attachments']
                                for doc in docs:
                                    if 'photo' in doc:
                                        self.get_photo(doc)
                                    if 'doc' in doc:
                                        self.get_doc(doc)
                            # Документ
                            elif 'doc' in att:
                                self.get_doc(att)
                            
                            # Прочее
                            else:
                                print(att)
                                        
                                
            if 'fwd_messages' in m:
                self.get_att(m['fwd_messages'])
    
    def get_photo(self, photo):
        """Получить фото
        
        :photo: `объект медиавложения ВК <https://dev.vk.com/reference/objects/attachments-message>`_.
       
        Фото записывается в :class:`list` self.photos в формате: \n
        {'url':'Ссылка на файл'}
        """
        photo_el = {}
        photo_el["url"] = self.find_finest_photo(photo['photo']['sizes'])
        self.photos.append(photo_el) 
        
    def get_doc(self, doc):
        """Получить документ
        
        :photo: `объект медиавложения ВК <https://dev.vk.com/reference/objects/attachments-message>`_.
       
        Документ записывается в :class:`list` self.docs в формате: \n
        {'name':'Название файла','url':'Ссылка на файл'}
        """     
        document = {}
        document['name'] = doc['doc']['title']
        document['url'] = doc['doc']['url']
        self.docs.append(document)        
                                
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
    
    def download(self, folder, name, url):
        """ Скачивание файла
        
        Думаю, аргументы здесь очевидны (:
        """
        
        response = requests.get(url, stream=True)
        if not os.path.isdir(f'files\{folder}'):
            os.makedirs(f'files\{folder}') 
        filename = f'files\{folder}\{name}'
        path = os.path.abspath(filename) 
        with open(path, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
        
    def remove_doubles(self, li):
        """Удаляем все повторяющиеся элементы из списка li"""
        new_list = []
        [new_list.append(i) for i in li if i not in new_list]
        return new_list
        
        
    def load_attachments(self):
        """Загрузка всех вложений"""
        
        for message in self.messages:
            mid = message.message_id
            full_msg = self.tools.get_all_iter("messages.getById",
                                               100, 
                                               values = {"message_ids":mid})
            self.count = 0
            self.photos = []
            self.docs = []
            self.get_att(full_msg)
            
            self.photos = self.remove_doubles(self.photos)
            self.docs = self.remove_doubles(self.docs)
            
            photos_count = len(self.photos)
            docs_count = len(self.docs)
            
            self.msg(message.user_id, 
                     f"Загрузка вложений...\nВсего файлов: {photos_count+docs_count}")
            
            for num, photo in enumerate(self.photos):
                folder = f"{mid}_photos"
                name = f"photo_{num}.jpg"
                self.download(folder, name, photo['url'])
                
            for doc in self.docs:
                folder = f"{mid}_docs"
                name = doc['name']
                self.download(folder, name, doc['url'])
                
            
            self.msg(message.user_id, f"Вложения загружены")
            self.messages = None
        
                
    
if __name__ == "__main__":
    bot = VkAttLoader()
    print("Bot ready")
    
    while True:
        bot.check_messages()
        if bot.messages != None:
            bot.load_attachments()
        
