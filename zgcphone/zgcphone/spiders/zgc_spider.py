#-*- encoding: UTF-8 -*-
#---------------------------------import------------------------------------
import scrapy
import re
from zgcphone.items import TutorialItem
import logging
from scrapy import Request
import requests
#---------------------------------------------------------------------------
class JdSpider(scrapy.Spider):
    name = "zgcphone"
    allowed_domains = ["zol.com.cn"]
    start_urls = [
        "http://detail.zol.com.cn/"
    ]

    def parse(self,response):
        '分别获得商品的地址和下一页地址'
        req = []
        for i in range(1, 100):
            url = "http://detail.zol.com.cn/cell_phone_index/subcate57_0_list_1_0_1_2_0_" + str(i) + ".html"
            logging.log(logging.DEBUG, url)
            r = Request(url, callback=self.parse)
            req.append(r)

        '商品地址'
        for sel in response.xpath('//ul[contains(@id, "J_PicMode")]/li'):
            item = TutorialItem()
            item['phonename'] = sel.xpath('a/img/@alt').extract()
            item['price'] = sel.xpath('div[contains(@class, "price-row")]/span[contains(@class, "price price-normal")]/b[contains(@class, "price-type")]/text()').extract()            
            logging.log(logging.DEBUG, sel.xpath('div[contains(@class, "price-row")]/span[contains(@class, "price price-normal")]/b[contains(@class, "price-type")]').extract())
            url = "http://detail.zol.com.cn" + str(sel.xpath('a/@href').extract_first())
            item['itemurl'] = url
            r = Request(url, callback=self.parse_product)
            r.meta['item'] = item
            req.append(r)
        return req

    def parse_product(self,response):
        t = response.xpath('//div[contains(@id, "_j_tag_nav")]/ul[contains(@class, "nav__list clearfix")]/li[4]/a/@href').extract_first()
        url = "http://detail.zol.com.cn" + str(t)
        #logging.log(logging.DEBUG, response.xpath('//div[contains(@id, "_j_tag_nav")]/ul[contains(@class, "nav__list clearfix")]/li[4]').extract())
        r = Request(url, callback=self.parse_issuedate)
        r.meta['item'] = response.meta['item']
        return r

    def parse_issuedate(self,response):
        item = response.meta['item']
        issuedate = response.xpath('//div[contains(@class, "param-content")]/ul[contains(@class, "category-param-list")]/li/span[2]/text()').extract_first()
        logging.log(logging.DEBUG,response.xpath('//div[contains(@class, "param-content")]/ul[contains(@class, "category-param-list")]/li/span[2]/text()').extract_first())
        item['issuedate'] = issuedate
        return item
############################################################################
