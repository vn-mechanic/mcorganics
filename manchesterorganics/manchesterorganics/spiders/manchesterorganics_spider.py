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
        next_page = response.xpath('//*[@id="content"]/div[4]/div[1]/ul/li[10]/a/@href').get()
        if next_page is not None:
            yield scrapy.Request(next_page, self.parse)

    def parse_item(self, response):
        matnr = response.xpath('//*[@id="content"]/div/div[2]/div[1]/p/span/text()').get()
        in_stock = 'n/a'
        namproden = response.xpath('//*[@id="content"]/div/div[2]/h1/text()').get()
        numcas = re.findall('\d+-\d+[-\d]*', response.xpath('//*[@id="content"]/div/div[2]/div[3]/text()').get())
        web_product_link = response.url[:41]
        frmsum = response.xpath('//*[@id="content"]/div/div[2]/div[4]').get().replace('\t', '').replace('\n', '').replace('<sub>', '').replace('</sub>', '').replace('</div>', '')[45:]
        nummdl = response.xpath('//*[@id="content"]/div/div[2]/div[6]/text()').get().strip().replace('MDL Number:', '')
        purity = response.xpath('//*[@id="content"]/div/div[2]/div[7]/text()').get().replace('Purity:', '').strip()
        sap_ehs_1013_037_value = re.findall('\d+\.\d+', response.xpath('//*[@id="content"]/div/div[2]/div[5]/text()').get())[0]
        qt_list = re.findall('(\d+(?:\.\d+)?)+g', "".join(response.xpath('//div[@class="form-group option-quantity-extension"]').get()))
        unit_list = list('g' for i in range(len(qt_list))),
        price_pack_list = [float(i) for i in re.findall("(\d+\.\d+)+[^g]", "".join(response.xpath('//div[@class="form-group option-quantity-extension"]').getall()))]
        currency_list = list('£' for i in range(len(unit_list))),
        price_unit_list = [round(i/float(j), 2) for i, j in zip(price_pack_list, qt_list)]

        yield {
            "matnr": matnr,
            "in_stock": in_stock,
            "namproden": namproden,
            "numcas": numcas,
            "web_product_link": web_product_link,
            "frmsum": frmsum,
            "nummdl": nummdl,
            "purity": purity,
            "sap_ehs_1013_037_value": sap_ehs_1013_037_value,
            "qt_list": qt_list,
            "unit_list": unit_list,
            "price_pack_list": price_pack_list,
            "currency_list": currency_list,
            "price_unit_list": price_unit_list
        }

