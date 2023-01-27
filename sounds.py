import os
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

    def add_sound(self, guild, name):
        path_file = os.path.dirname(__file__)
        if not os.path.exists(path_file + "sounds" + str(guild.id)):
            path = os.path.join(path_file, "sounds", str(guild.id))

            return 1

        # if not self.check_dir(str(guild.id)):

    def del_sound(self, guild, name):
        pass

    def get_sounds(self, guild):
        path_file = os.path.dirname(__file__)

        if not os.path.exists(path_file + "sounds" + str(guild.id)):
            return 0
        path = os.path.join(path_file, "sounds", str(guild.id))
        sounds = []
        for (dirpath, dirnames, filenames) in walk(path):
            sounds.extend(filenames)
            break
        return sounds
