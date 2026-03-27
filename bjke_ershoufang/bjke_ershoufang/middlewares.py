# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from DrissionPage import ChromiumPage
import time
import asyncio
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BjkeErshoufangSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    async def process_start(self, start):
        # Called with an async iterator over the spider start() method or the
        # matching method of an earlier spider middleware.
        async for item_or_request in start:
            yield item_or_request

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class BjkeErshoufangDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self):
        self.page = ChromiumPage()
        self.verified = False  # 验证状态锁

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):

        return None

    async def process_response(self, request, response, spider):
        # 捕获302验证码
        if response.status == 302:
            location = response.headers.get('Location', b'').decode()
            if 'hip.ke.com' in location or 'captcha' in location:
                print(f"🚨 触发验证码，自动处理：{location}")

                # --------------- 核心：异步阻塞，真正卡住Scrapy ---------------
                self.page.get(request.url)
                cookies = spider.cookies
                for c in cookies.items():
                    coo = {'name': c[0], 'value': c[1], "domain": ".ke.com"}
                    self.page.set.cookies(coo)
                self.page.refresh()
                print("⌛ 【已完全阻塞】请在浏览器完成验证码！")

                # 异步死循环 + 强制等待（这才是Scrapy能用的阻塞！）
                while True:
                    current_url = self.page.url
                    # 验证成功：跳回bj.ke.com
                    if "bj.ke.com" in current_url and "hip.ke.com" not in current_url:
                        break
                    # 异步等待1秒（真正阻塞异步事件循环）
                    await asyncio.sleep(1)
                    print(f"当前URL：{current_url} → 等待验证...")

                # 验证通过，保存Cookie
                new_cookies = ';'.join([i.get('name')+'='+i.get('value') for i in self.page.cookies()])
                spider.save_cookie(new_cookies)
                print("✅ 验证通过！恢复爬取！")

                # 重新请求
                return request.replace(
                    cookies=spider.parse_cookie(new_cookies),
                    dont_filter=True
                )

        return response


    async def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

