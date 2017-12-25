#-*- encoding: UTF-8 -*-
#---------------------------------import------------------------------------
import scrapy
import re
from tutorial.items import TutorialItem
import logging
from scrapy import Request
import requests
#---------------------------------------------------------------------------
class JdSpider(scrapy.Spider):
    name = "test"
    allowed_domains = ["jd.com","p.3.cn"]
    start_urls = [
        "https://list.jd.com/list.html?cat=9987,653,655"
    ]

    def parse(self,response):
        '分别获得商品的地址和下一页地址'
        req = []
        for i in range(1, 2):
            url = "https://list.jd.com/list.html?cat=9987,653,655&page=" + str(i+1) + "&sort=sort%5Frank%5Fasc&trans=1&JL=6_0_0&ms=6"
            r = Request(url, callback=self.parse)
            req.append(r)

        '商品地址'
        for sel in response.xpath('//div[contains(@class, "p-img")]/a'):
            for i in sel.xpath('@href').extract():
                url = "https://" + i
                itemurl = url
                r = Request(url, callback=self.parse_product)
                req.append(r)
        return req

    def parse_product(self,response):
        '商品页获取title,price,product_id'
        req = []
        phonename = response.xpath('//div/ul[contains(@class, "parameter2 p-parameter-list")]/li[1]/@title').extract_first()
        issueyear = response.xpath('//div[contains(@class, "Ptable-item")][1]/dl/dd/text()').re(u'[1-9][0-9][0-9][1-9]\u5e74')
        issuemonth = response.xpath('//div[contains(@class, "Ptable-item")][1]/dl/dd/text()').re(u'[1-9][0-9]*\u6708')
        pattern = r"(\d+)\.html$"
        id = re.findall(pattern, response.url) 
        priceUrl = "https://p.3.cn/prices/mgets?&skuIds=J_"+str(id[0])
        item = TutorialItem()
        item['phonename'] = phonename
        item['issueyear'] = issueyear
        item['issuemonth'] = issuemonth
        item['itemurl'] = response.url
        request = scrapy.Request(priceUrl, method="GET", callback=self.parse_price)
        request.meta['item'] = item
        logging.log(logging.DEBUG, request)
        yield request

    def parse_price(self,response):
        logging.log(logging.DEBUG, response.body)
        item = response.meta['item']
        priceData = response.body
        patt = r'"p":"(\d+\.\d+)"'
        price = re.findall(patt, str(priceData))
        item['price'] = price
        return item
############################################################################
