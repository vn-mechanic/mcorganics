# -*- coding: utf-8 -*-
import scrapy
import re


class OrganicSpider(scrapy.Spider):
    name = "organic"
    start_urls = [
        "https://www.manchesterorganics.com/index.php?route=product/search&sort=p.sort_order&order=ASC&search=+&description=true"
    ]

    def parse(self, response):
        urls = response.xpath('.//h4[@class="name"]/a/@href').getall()
        for url in urls:
            yield scrapy.Request(url, callback=self.parse_item)
        # next_page = response.xpath('//*[@id="content"]/div[4]/div[1]/ul/li[10]/a/@href').get()
        # if next_page is not None:
        #     yield scrapy.Request(next_page, self.parse)

    def parse_item(self, response):
        yield {
            "matnr": self.matnr(response),
            "in_stock": self.in_stock(response),
            "namproden": self.namproden(response),
            "numcas": self.numcas(response),
            "web_product_link": self.web_product_link(response),
            "frmsum": self.frmsum(response),
            "nummdl": self.nummdl(response),
            "purity": self.purity(response),
            "sap_ehs_1013_037_value": self.sap_ehs_1013_037_value(response),
            "qt_list": self.qt_list(response),
            "unit_list": self.unit_list(response),
            "price_pack_list": self.price_pack_list(response),
            "currency_list": self.currency_list(response),
            "price_unit_list": self.price_unit_list(response)
        }

    def matnr(self, response):
        return response.xpath('//div[@class="product-mod"]/p/span/text()').get()

    def in_stock(self, response):
        if 'Availability: Please' in response.xpath('//div[@class="product-mod"]/h2/text()').get():
            return 'n/a'
        else:
            return ''

    def namproden(self, response):
        return response.xpath('//*[@id="content"]/div/div[2]/h1/text()').get()

    def numcas(self, response):
        numcas = re.findall('\d+-\d+[-\d]*',
                            response.xpath('//div[@class="att-new-table" and contains(text(), "CAS Number:")]').get())
        if len(numcas):
            return numcas[0]
        else:
            return ''

    def web_product_link(self, response):
        return response.url[:41]

    def frmsum(self, response):
        return response.xpath('//div[@class="att-new-table" and contains(text(), "Molecular Formula:")]').get(). \
            replace('<div class="att-new-table">', '').replace('\n', '').replace('\t', '').replace('<sub>', ''). \
            replace('</sub>', '').replace('</div>', '').replace('Molecular Formula:', '')


    def nummdl(self, response):
        return response.xpath(
            '//div[@class="att-new-table" and contains(text(), "MDL Number:")]/text()').get().strip().replace('MDL Number:', '')

    def purity(self, response):
        return response.xpath('//div[@class="att-new-table" and contains(text(), "Purity")]/text()').get().replace(
            'Purity:', '').strip()

    def sap_ehs_1013_037_value(self, response):
        mw = re.findall('\d+\.\d+', response.xpath(
            '//div[@class="att-new-table" and contains(text(), "Molecular Weight")]/text()').get())
        if len(mw):
            return mw[0]

    def qt_list(self, response):
        return re.findall('(\d+(?:\.\d+)?)+g',
                          "".join(response.xpath('//div[@class="form-group option-quantity-extension"]').get()))

    def unit_list(self, response):
        ul = re.findall('(\d+(\.\d+)?)+(kg|g|ml|mg|pack)', response.xpath('//div[@class="form-group '
                                                                          'option-quantity-extension"]').get())
        rt = []
        for lst in ul:
            for item in lst:
                if item in ('kg', 'g', 'mg', 'ml', 'pack'):
                    rt.append(item)
        return rt

    def price_pack_list(self, response):
        return [float(i) for i in re.findall("(\d+\.\d+)+[^g]", "".join(
            response.xpath('//div[@class="form-group option-quantity-extension"]').getall()))]

    def currency_list(self, response):
        return re.findall('£|USD', response.xpath('//div[@class="form-group option-quantity-extension"]').get())

    def price_unit_list(self, response):
        return [round(i / float(j), 2) for i, j in zip(self.price_pack_list(response), self.qt_list(response))]
