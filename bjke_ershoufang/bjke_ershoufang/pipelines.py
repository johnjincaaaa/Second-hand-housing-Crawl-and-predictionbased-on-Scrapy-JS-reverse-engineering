# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os
import sys

class BjkeErshoufangPipeline:
    def __init__(self):
        self.data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),'data')

    def process_item(self, item, spider):
        # print('这里',item)
        # with open(self.data_path+'/items', 'w', newline='',encoding='utf-8') as f:
        #     f.write(item)
        return item

    def __del__(self):
        pass

