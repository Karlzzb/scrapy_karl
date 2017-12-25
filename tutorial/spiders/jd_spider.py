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
    allowed_domains = ["jd.com"]
    start_urls = [
        "https://list.jd.com/list.html?cat=9987,653,655"
    ]

    def parse(self,response):
        '分别获得商品的地址和下一页地址'
        req = []
        for i in range(0, 10):
            url = "https://list.jd.com/list.html?cat=9987,653,655&page=" + str(i+1) + "&sort=sort%5Frank%5Fasc&trans=1&JL=6_0_0&ms=6"
            r = Request(url, callback=self.parse)
            req.append(r)

        '商品地址'
        logging.log(logging.DEBUG, response.xpath('//div[contains(@class, "p-img")]/a/@href').extract())
        for sel in response.xpath('//div[contains(@class, "p-img")]/a'):
            for i in sel.xpath('@href').extract():
                url = "https://" + i
                itemurl = url
                r = Request(url, callback=self.parse_product)
                req.append(r)
        return req

    def parse_product(self,response):
        '商品页获取title,price,product_id'
        phonename = response.xpath('//div/ul[contains(@class, "parameter2 p-parameter-list")]/li[1]/@title').extract_first()
        issueyear = response.xpath('//div[contains(@class, "Ptable-item")][1]/dl/dd/text()').re(u'[1-9][0-9][0-9][1-9]\u5e74')
        issuemonth = response.xpath('//div[contains(@class, "Ptable-item")][1]/dl/dd/text()').re(u'[1-9][0-9]*\u6708')
        pattern = r"(\d+)\.html$"
        id = re.findall(pattern, response.url) 
        priceUrl = "https://p.3.cn/prices/mgets?&skuIds=J_"+str(id[0])
        priceData = requests.get(priceUrl).content.decode("utf-8", "ignore")
        patt = r'"p":"(\d+\.\d+)"'
        price = re.findall(patt, priceData)
        logging.log(logging.DEBUG, id)
        item = TutorialItem()
        item['phonename'] = phonename
        item['issueyear'] = issueyear
        item['issuemonth'] = issuemonth
        item['price'] = price
        item['itemurl'] = response.url
        return item
############################################################################
