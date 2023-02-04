import os
import requests
from os import walk


class Sounds:
    def check_dir(self, server_id):
        path_file = os.path.dirname(__file__)
        path = os.path.join(path_file, "sounds")
        directorys = []
        for (dirpath, dirnames, filenames) in walk(path):
            directorys.extend(dirnames)
            break
        for dir in directorys:
            if dir == str(server_id):
                return True
        return False

    def add_sound(self, guild, attachments):
        path_file = os.path.dirname(__file__)
        add_list = []
        path = os.path.join(path_file, "sounds", str(guild.id))
        if not os.path.exists(path):
            os.chdir(path_file)
            os.chdir("sounds")
            os.mkdir(str(guild.id))
            os.chdir(str(guild.id))
            for i in attachments:
                if i.filename.split('.')[1] == 'mp3':
                    response = requests.get(i.url, stream=True)
                    if response.status_code == 200:
                        try:
                            with open(i.filename, 'wb') as file:
                                file.write(response.content)
                            add_list.append(i.filename)
                        except Exception as er:
                            print(er)
        else:
            os.chdir(path_file)
            os.chdir("sounds")
            os.chdir(str(guild.id))
            for i in attachments:
                if i.filename.split('.')[1] == 'mp3':
                    response = requests.get(i.url, stream=True)
                    if response.status_code == 200:
                        try:
                            with open(i.filename, 'wb') as file:
                                file.write(response.content)
                            add_list.append(i.filename)
                        except Exception as er:
                            print(er)
        return add_list

    def del_sound(self, guild, name):
        path_file = os.path.dirname(__file__)
        path = os.path.join(path_file, "sounds", str(guild.id))
        if not os.path.exists(path):
            return 0
        sounds = []

        for (dirpath, dirnames, filenames) in walk(path):
            sounds.extend(filenames)
            break
        try:
            name = int(name)
            if len(sounds)+1 > name and name > 0:
                name = sounds[name-1]
            else:
                return 2
        except Exception as er:
            print(er)
        for sound in sounds:
            if sound == name:
                # path.join(name)
                os.chdir(path_file)
                os.chdir("sounds")
                os.chdir(str(guild.id))
                os.remove(name)
                return 1
        return 0

    def get_sounds(self, guild):
        path_file = os.path.dirname(__file__)
        path = os.path.join(path_file, "sounds", str(guild.id))
        if not os.path.exists(path):
            return 0
        sounds = []
        for (dirpath, dirnames, filenames) in walk(path):
            sounds.extend(filenames)
            break
        return sounds
