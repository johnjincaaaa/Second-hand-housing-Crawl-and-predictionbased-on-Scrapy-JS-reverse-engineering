# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from DrissionPage import ChromiumPage
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


    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):

        return None

    def process_response(self, request, response, spider):
        # 👇 你最关心的逻辑：遇到 302 跳验证码
        if response.status in (302, 301, 307):
            loc = response.headers.get('Location', b'').decode()
            if 'captcha' in loc or 'verify' in loc or 'passport' in loc:
                spider.logger.info(f"🚨 触发验证码：{loc}")

                # 👇 用 DP 打开原链接，过验证码
                self.page.get(request.url)

                # 👇 等待你手动/自动过验证码
                self.page.wait(1.5)
                while '验证码' in self.page.title or 'verify' in self.page.url:
                    self.page.wait(1)

                # 👇 过了验证码 → 拿到最新 cookie
                cookies = self.page.cookies()

                # 👇 把新 cookie 塞进原来的请求
                request.cookies = cookies

                # 👇 重新请求！
                return request.replace(
                    url=request.url,
                    cookies=cookies,
                    dont_filter=True
                )

        return response


    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

