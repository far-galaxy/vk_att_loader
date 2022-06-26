# -*- coding: utf-8 -*-
""" Модуль для бота ВК, загружающий все вложения из пересланному ему сообщению
by far-galaxy

:copyright: (c) 2022 far-galaxy https://github.com/far-galaxy 
:license: GNU GPL v3.0, see LICENSE for more details.
"""
import vk_api

import os

class VkAttLoader(object):
    """ Класс инструмента для загрузки всех вложений из сообщения, пересланному боту"""
    def __init__(self):
        self.get_token()
        self.vk = vk_api.VkApi(token = self.token)
       
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
                
    
if __name__ == "__main__":
    bot = VkAttLoader()
        
