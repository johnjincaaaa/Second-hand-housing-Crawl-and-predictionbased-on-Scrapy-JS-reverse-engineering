import scrapy
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import json
import os
import csv

# 配置常量（统一管理，方便修改）
BASE_URL = "https://bj.ke.com/ershoufang/"
# 北京全量行政区（你之前补全的）
DISTRICTS = [
    "dongchengqu3",
    # "xichengqu3", "chaoyangqu5", "haidianqu6",
    # "fengtaiqu", "shijingshanqu", "tongzhouqu1", "changpingqu",
    # "daxingqu", "beijingjingjijishukaifaqu", "shunyiqu", "fangshanqu",
    # "mentougouqu", "pingguqu", "huairouqu", "miyunqu", "yanqingqu"
]
# 户型切分维度（一室）
ROOM_TYPES = ["l1", "l2", "l3", "l3", "l4", "l5", "l6"]
# 价格区间切分维度
PRICE_RANGES = [
    "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"
]
# 价格区间映射（用于URL拼接）
PRICE_URL_MAP = {
    "p1": "200w以下",
    "p2": "200-250w",
    "p3": "250-300w",
    "p4": "300-400w",
    "p5": "400-500w",
    "p6": "500-800w",
    "p7": "800-1000w",
    "p8": "1000w以上"
}
MAX_PAGE = 2


class ErshoufangSpider(scrapy.Spider):
    name = "ershoufang"

    allowed_domains = ["ke.com", "hip.ke.com"]

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Referer": "https://hip.ke.com/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Not:A-Brand\";v=\"99\", \"Google Chrome\";v=\"145\", \"Chromium\";v=\"145\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        with open('cookie.txt','r',encoding='utf-8') as f:
            cookie_str = f.read()
            print(cookie_str)
        self.cookies = self.parse_cookie(cookie_str=cookie_str)
        print(self.cookies)
        self.cookies = {
            "lianjia_uuid": "87202424-9799-4e89-a309-c6699ee66653",
            "crosSdkDT2019DeviceId": "-e8vmjx-8lw8p3-ltwi1cuerolysyk-5gh389lip",
            "lfrc_": "4dedac2e-687b-4d99-a2ba-23dd4f180657",
            "Hm_lvt_b160d5571570fd63c347b9d4ab5ca610": "1773979408,1773997023,1774419934",
            "HMACCOUNT": "00959BC5EB881F83",
            "select_city": "110000",
            "login_ucid": "2000000529560137",
            "security_ticket": "V0yAEZwe8Ytf6iw3iuSheHlvp9UZ4bngTxr28NcXZ+FTcQiOfR5JmcGAOMQ3f55B3hDUuNrswCYFKw1BwYT2S5laE9S5vS512xmdHw0L0sjhbiylV//5WLTx8kaPFzV8J+gSlByoghSSwCR0diwfXz7dgbbdpnsAgjzRl5YclKg=",
            "lianjia_token": "2.001362d7d04969c87502cffee1b0e3c838",
            "lianjia_token_secure": "2.001362d7d04969c87502cffee1b0e3c838",
            "sensorsdata2015jssdkcross": "%7B%22distinct_id%22%3A%2219d0a765fd07ad-0aab5e6582a9348-26061c51-1327104-19d0a765fd11bc0%22%2C%22%24device_id%22%3A%2219d0a765fd07ad-0aab5e6582a9348-26061c51-1327104-19d0a765fd11bc0%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D",
            "lianjia_ssid": "d95fa248-6fa9-43a5-ad90-6bb69bd314a0",
            "Hm_lpvt_b160d5571570fd63c347b9d4ab5ca610": "1774638792",
            "srcid": "eyJ0Ijoie1wiZGF0YVwiOlwiYWIwMzY4MDlkYjIzNGY1YTQ3NTBkZDM2YmE2YWFmYTJlYjA5YTRmODc1ZTY5ZGFiMGI2YWQ3NjI0ZTk4NGRhNTY4YWRkYmY2NDlhNWIzMmExOWI1N2RlMDVmNDBiMTljMjhmMjA2MDEzMjJmNjI5MTg0MWQ1ODBiZGNhODI3MjUwYjYwMDk0YmY3YmRiNWE2M2U2MjcyYjgyOWM1M2JkYzQ5ZDBhNjViNWZlYzcyZGUwMDliNjBmNWZjODgyNDczN2U4MTRiZGI5OWRhNjUyYmFiYWI1YjE1OGFlODgwOTFhMTFkNWZkNWI5YmFlZTk2MWMzMTE5ZjcxNjBhOTFmMjliYWEzNzA1ZmM2MTVkY2Y2ZTQ2YTlmYTk2YmE1M2IxOTM2MGUwOTNjN2NmYzA3OTY3ZGM3OWQyYjczMGI3ZjFcIixcImtleV9pZFwiOlwiMVwiLFwic2lnblwiOlwiOGI5OWQ0YWJcIn0iLCJyIjoiaHR0cHM6Ly9iai5rZS5jb20vZXJzaG91ZmFuZy9kb25nY2hlbmdxdTMvIiwib3MiOiJ3ZWIiLCJ2IjoiMC4xIn0="
        }        # 后期需要从登录接口获取（实现账号批量登录）

    @staticmethod
    def parse_cookie(cookie_str):
        cookie_dict = {}
        cookie_items = [item.strip() for item in cookie_str.split(';') if item.strip()]
        for item in cookie_items:
            key, value = item.split('=', 1)
            cookie_dict[key.strip()] = value.strip()
        return cookie_dict

    # 👇 新增：把字典格式的Cookie 保存到 txt 文件（持久化核心）
    @staticmethod
    def save_cookie(cookie_str):
        # 覆盖写入文件（永远保存最新的Cookie）
        with open('cookie.txt', 'w', encoding='utf-8') as f:
            f.write(cookie_str)


    def start_requests(self):
        """入口：遍历全量行政区，发起首次请求"""
        for district in DISTRICTS:
            url = urljoin(BASE_URL, f"{district}/")
            # 首次请求行政区列表页，获取总套数
            yield scrapy.Request(
                url=url,
                cookies=self.cookies,
                headers=self.headers,
                callback=self.parse,
                meta={"district": district, "level": "district"}  # 标记层级
            )


    def parse(self, response):
        """层级1：行政区解析，判断是否需要切分户型"""



        soup = BeautifulSoup(response.text, 'lxml')
        # ========== 加容错：找不到元素直接跳过，不报错 ==========
        total_tag = soup.find(class_='total fl')
        if not total_tag:
            # 说明是验证码页面/异常页面，重新请求
            self.logger.error("页面异常，重新请求...")
            yield response.request.replace(dont_filter=True)
            return

        total = soup.find(class_='total fl').text.strip().split(' ')[1]  # a找到套数
        district = response.meta["district"]
        print('层级1',total,district,response.meta["level"])
        # b. 如果 ≤3000：直接翻1~100页爬完
        if int(total) <= 3000:
            yield from self.crawl_pagination(response, district)  # yield from === for i in

        # c. 如果 >3000：自动按【户型】再切分（一室,二室...）
        else:
            # 按户型切分
            for room in ROOM_TYPES:
                url = urljoin(BASE_URL, f"{district}/{room}/")
                yield scrapy.Request(
                    url=url,
                    cookies=self.cookies,
                    headers=self.headers,
                    callback=self.parse_room,
                    meta={"district": district, "room": room, "level": "room"}
                )



    def parse_room(self, response):
        """层级2：户型解析，判断是否需要切分价格"""

        #  获取总套数
        soup = BeautifulSoup(response.text, 'lxml')
        total = soup.find(class_='total fl').text.strip().split(' ')[1]  # a找到套数
        district = response.meta["district"]
        room = response.meta["room"]
        print('层级2',total,district,response.meta['room'],response.meta["level"])
        # 第三步：判断是否切分
        if int(total) <= 3000:
            # 直接翻页爬取
            yield from self.crawl_pagination(response, district, room)
        else:
            # 按价格区间切分
            for price in PRICE_RANGES:
                url = urljoin(BASE_URL, f"{district}/{room}{price}/")
                yield scrapy.Request(
                    url=url,
                    cookies=self.cookies,
                    callback=self.parse_price,
                    meta={"district": district, "room": room, "price": price, "level": "price"}
                )

    def parse_price(self, response):
        """层级3：价格区间解析，直接翻页爬取（已切分足够细）"""
        # 第一步：pass过验证码，在中间件里面解决
        # 第二步：获取总套数（个别热门区域可能超3000套，直接翻页）
        soup = BeautifulSoup(response.text, 'lxml')
        total = soup.find(class_='total fl').text.strip().split(' ')[1]
        print('层级3',total,'套',response.meta['district'],response.meta['room'],response.meta['price'],response.meta["level"])
        district = response.meta["district"]
        room = response.meta["room"]
        price = response.meta["price"]

        # 第三步：直接翻页爬取
        yield from self.crawl_pagination(response, district, room, price)

    def crawl_pagination(self, response, district, room=None, price=None):
        """通用翻页函数：生成1~100页的请求"""
        # 第一步：解析当前页数据（你可以在这里补全解析逻辑）
        yield from self.parse_list_data(response)

        # 第二步：生成翻页请求
        base_url = response.url
        # 处理URL拼接（不同层级的URL结构）
        if room and price:
            base_pagination_url = urljoin(BASE_URL, f"{district}/{room}{price}pg")
        elif room:
            base_pagination_url = urljoin(BASE_URL, f"{district}/{room}pg")
        else:
            base_pagination_url = urljoin(BASE_URL, f"{district}/pg")

        # 生成1~100页请求
        for page_ in range(2, MAX_PAGE + 1):
            """
            翻页会触发反爬，测试阶段先跳过
            """

            url = f"{base_pagination_url}{page_}/"
            print('翻页url为',url)
            yield scrapy.Request(
                url=url,
                cookies=self.cookies,
                headers=self.headers,
                callback=self.parse_list_data,
                meta={"district": district, "room": room, "price": price, "page": page_}
            )

    def parse_list_data(self, response):
        """列表页数据解析：你在这里补全房源数据提取逻辑"""

        soup = BeautifulSoup(response.text, 'lxml')

        sellListContent = soup.find_all(class_='clear')
        data = []
        print(len(sellListContent))
        for item in sellListContent:
            try:
                house_name = item.find(class_='VIEWDATA CLICKDATA maidian-detail').text
                location_href = item.select('.positionInfo a')[0].get('href')
                location_name = item.find(class_='positionInfo').text.strip('\n')
                price = item.find(class_='priceInfo').text.replace('\n','').strip(' ')
                data.append(
                    {
                        'house_name': house_name,
                        'location_href': location_href,
                        'location_name': location_name,
                        'price': price
                    }
                )
            except Exception as e:
                print(e)

        # 去重
        result = list({tuple(d.items()) for d in data})
        result = [dict(item) for item in result]
        print('数据长度',len(result))

        # ========== 保存数据到JSON文件 ==========
        # 1. 创建数据目录（不存在则创建）
        if not os.path.exists('ershoufang_data'):
            os.makedirs('ershoufang_data')

        # 2. 按行政区+户型+价格命名文件
        district = response.meta.get('district', 'unknown')
        room = response.meta.get('room', 'all')
        price = response.meta.get('price', 'all')
        if price is None:
            price = 'all'
        page = response.meta.get('page', '1')
        filename = f'ershoufang_data/{district}_{room}_{price}.csv'

        # 3. 追加写入数据（避免覆盖,因为要翻页）
        with open(filename, 'a', encoding='utf-8',newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['house_name', 'location_href', 'location_name', 'price','page'])
            if not os.path.exists(filename):
                writer.writeheader()
            for item in result:
                item['page'] = page
                writer.writerow(item)

        yield result






