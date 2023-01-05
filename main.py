import requests
from tqdm import tqdm
import json
import datetime



class VkUser:
    url = 'https://api.vk.com/method/'
    TOKEN_VK = ''  # В '' указываем свой токен API VK
    VERSION = '5.131'
    params = {
        'access_token': TOKEN_VK,
        'v': VERSION
    }

    def __init__(self, user_id=None):
        self.info_foto_list = []
        if user_id is not None:
            self.user_id = user_id
        else:
            self.user_id = requests.get(self.url + 'users.get', self.params).json()['response'][0]['id']


    def photos_get(self, count=None):
        photos_get_url = self.url + 'photos.get'
        if count is not None:
            counter = count
        else:
            counter = 5
        photos_get_params = {
            'owner_id': self.user_id,
            'album_id': 'profile',
            'extended': '1',
            'photo_sizes': '1',
            'count': counter,
            'rev': '1'
            }
        res = requests.get(photos_get_url, params={**self.params, **photos_get_params})
        res.raise_for_status()
        info_foto_dict = res.json()
        print(f'Информация из VK получена успешно')
        return info_foto_dict

    def conv_dict_list(self, information_dict):
        foto_list = []
        for dict_ in information_dict['response']['items']:
            dict_foto = {}
            dict_foto['date'] = datetime.datetime.fromtimestamp(dict_['date']).strftime('%d.%m.%Y %H.%M.%S')
            dict_foto['likes'] = dict_['likes']['count']
            example = 0
            for var_url in dict_['sizes']:
                size = var_url['height'] * var_url['width']
                if size > example:
                    example = size
                    dict_foto['url'] = var_url['url']
                    dict_foto['size'] = var_url['type']
            foto_list.append(dict_foto)

        info_foto_list = []
        num = len(foto_list)
        for i in range(num - 1):
            dict_ = foto_list.pop()
            for string in foto_list:
                if string['likes'] == dict_['likes']:
                    dict_['file-name'] = '(' + str(dict_['likes']) + ')' + str(dict_['date']) + '.jpg'
                    break
                else:
                    dict_['file-name'] = str(dict_['likes']) + '.jpg'

            info_foto_list.append(dict_)

        last_dict = foto_list.pop()
        last_dict['file-name'] = str(last_dict['likes']) + '.jpg'
        info_foto_list.append(last_dict)
        print(f'Информация сохранена в список')
        return info_foto_list

    def create_list_with_requested_information(self, count=None):
        self.info_foto_list = self.conv_dict_list(self.photos_get(count))
        return

    def create_json(self, name=None):
        if name is not None:
            name_file = name
        else:
            name_file = 'info_vk'
        info_list = self.info_foto_list
        for string in info_list:
            del string['likes'], string['date'], string['url']
        with open(name_file + '.json', "w") as f:
            json.dump(info_list, f, ensure_ascii=False, indent=4)
        print(f'Файл {name_file}.json с информацией по сохранённым фотографиям создан')
        return info_list



class YaUser:
    def __init__(self, token: str):
        self.token = token
        self.directory_upload = ''

    def create_folder(self, direct=None):
        if direct is not None:
            directory = direct
        else:
            directory = 'VK_profile_foto'
        response = requests.put(
            "https://cloud-api.yandex.net/v1/disk/resources",
            params={
                        "path": directory
            },
            headers={
                    "Authorization": f"OAuth {self.token}"
            }
            )
        self.directory_upload = directory
        if 'message' in response.json():
            print(f'Такая папка на Я.Диске уже существует')
        elif 'method' in response.json():
            print(f'Папка {directory} на Я.Диске создана успешно')
        else:
            response.raise_for_status()
        return directory


    def upload(self, user):
        if isinstance(user, VkUser):
            for load in tqdm(user.info_foto_list, desc='Файлы загружаются на Я.Диск', leave=True):
                file_name = load['file-name']
                file_url = load['url']
                response = requests.post(
                    "https://cloud-api.yandex.net/v1/disk/resources/upload",
                    params={
                        "path": f'{self.directory_upload}/{file_name}',
                        'url': file_url
                    },
                    headers={
                    "Authorization": f"OAuth {self.token}"
                    }
                )
                response.raise_for_status()
        print(f'Файлы загружены на Я.Диск')
        return


    def copying_photos_to_disk(self, user):
        if isinstance(user, VkUser):
            user.create_list_with_requested_information()
            self.create_folder()
            self.upload(user)
            user.create_json()
            print(f'\nВыполнение программы завершено успешно!')
            return


aim_sprut = VkUser()  # Вместо aim_sprut указываем свой VK ID
admin = YaUser('')  # В '' указываем свой токен API Я.Диска с Полигона

admin.copying_photos_to_disk(aim_sprut)