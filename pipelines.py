# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


import scrapy
import hashlib  # Подключаю модуль, чтобы изменить работу file_path
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.python import to_bytes  # Подключаю модуль, чтобы изменить работу file_path


class LMImagesPipeLine(ImagesPipeline):

    def get_media_requests(self, item, info):
        if item['images']:
            for img in item['images']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        item['images'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):  # В качестве пути и названия файла используется (name)
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return f'full/{item["name"]}/{image_guid}.jpg'


class LeroyMerlinPipeline:

    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.db = client['LeroyMerlin']

    def process_item(self, item, spider):
        t = len(item['info_key'])  # Для того, чтобы объединить поля получаю длину списка ключей, чтобы для каждого имеющегося ключа подобрать значение
        item['info'] = self.process_info(item['info_key'], item['info_item'], t)  # Получаю поля содержащие в себе ключ: значение
        del item['info_key']  # Убираю более не нужные поля
        del item['info_item'] # Убираю более не нужные поля

        collection = self.db[spider.name]
        try:
            collection.insert_one(item)
        except:
            pass
        return item

    def process_info(self, key, item, t):  # Объединение списка ключей со списком значений
        li = {}
        for el in range(t):
            li.update({key[el].replace('\n', '').replace('  ', ''): item[el]})
        return li