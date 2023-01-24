import json
import os

pathfile = os.path.dirname(__file__)
path = os.path.join(pathfile, "data", "pablics.json")


class Pablics:
    def check_server(self, file, server_id: int):
        for i in file['employee']:
            if i['server_id'] == server_id:
                return True
        return False

    def check_pablic(self, file, pablic_id: int, content_type):
        for i in file:
            if i['pablics'] == pablic_id and i['type'] == content_type:
                return True
        return False

    def get_pablics(self, server_id: int):
        with open(path) as load_file:
            json_file = json.load(load_file)
        for i in json_file['employee']:
            if i['server_id'] == server_id:
                return i['pablics']
        return 0

    def get_pablics_id_by_type(self, server_id: int, content_type):
        result = []
        with open(path) as load_file:
            json_file = json.load(load_file)
        for server in json_file['employee']:
            if server['server_id'] == server_id:
                for pablic in server['pablics']:
                    if pablic['type'] == content_type:
                        result.append(str(pablic['id']))
                break
        return result

    def add_pablic(self, pablic_id: int, server_id: int, content_type):

        if content_type is None:
            data = [{"id": pablic_id, "type": "text"}, {"id": pablic_id, "type": "image"}]
        elif content_type == "text" or content_type == "image":
            data = [{"id": pablic_id, "type": content_type}]
        else:
            return 0
        with open(path) as load_file:
            json_file = json.load(load_file)

        if not self.check_server(json_file, server_id):
            json_file['employee'].append({"server_id": server_id, "pablics": data})
            with open(path, "w") as write_file:
                json.dump(json_file, write_file, indent=4, ensure_ascii=False)
            return len(data)

        for i in json_file['employee']:
            if i['server_id'] == server_id:
                for j in i['pablics']:
                    for m in data:
                        if m == j:
                            data.remove(m)
                if len(data) <= 0:
                    return 0
                i['pablics'] += data
                break

        with open(path, "w") as write_file:
            json.dump(json_file, write_file, indent=4, ensure_ascii=False)
        return len(data)

    def del_pablic(self, server_id: int, pablic_id: int, content_type):
        if content_type is None:
            types = ["text", "image"]
        elif content_type == "text" or content_type == "image":
            types = [content_type]
        else:
            return 0
        with open(path) as load_file:
            json_file = json.load(load_file)

        if not self.check_server(json_file, server_id):
            return 1

        '''for server in json_file['employee']:
            if server['server_id'] == server_id:
                for pablic in server['pablics']:
                    # print(f'{pablic["id"]}: {pablic_id}: {int(pablic["id"]) == int(pablic_id)}\n{pablic["type"]}: {types}: {pablic["type"] in types}')
                    if pablic['id'] == int(pablic_id) and pablic['type'] in types:
                        server['pablics'].remove(pablic)
                        del_counter += 1'''

        del_counter = 0
        for server in json_file['employee']:
            if server['server_id'] == server_id:
                pablic_index = 0
                while pablic_index < len(server['pablics']):
                    if server['pablics'][pablic_index]['id'] == int(pablic_id) and server['pablics'][pablic_index]['type'] in types:
                        server['pablics'].remove(server['pablics'][pablic_index])
                        del_counter += 1
                    else:
                        pablic_index += 1
                break

        with open(path, "w") as write_file:
            json.dump(json_file, write_file, indent=4, ensure_ascii=False)
        return del_counter
