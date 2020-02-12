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
        numcas = self.numcas(response)
        if numcas == "":
            return
        matnr = self.matnr(response)
        in_stock = self.in_stock(response)
        namproden = self.namproden(response)
        frmsum = self.frmsum(response)
        nummdl = self.nummdl(response)
        purity = self.purity(response)
        sap_ehs_1013_037_value = self.sap_ehs_1013_037_value(response)
        unit_list, qt_list = self.unit_list_qt_list(response)
        price_pack_list = self.price_pack_list(response)
        currency_list = self.currency_list(response)
        price_unit_list = self.price_unit_list(price_pack_list, qt_list)
        yield {
            "matnr": matnr,
            "in_stock": in_stock,
            "namproden": namproden,
            "numcas": numcas,
            "web_product_link": 'www.manchesterorganics.com/' + matnr,
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

    def matnr(self, response):
        return response.xpath('//div[@class="product-mod"]/p/span/text()').get()

    def in_stock(self, response):
        if 'Availability: Please' in response.xpath('//div[@class="product-mod"]/h2/text()').get():
            return 'n/a'
        elif 'Availability: We have' in response.xpath('//div[@class="product-mod"]/h2/text()').get():
            return 'yes'
        else:
            return 'no'

    def namproden(self, response):
        return response.xpath('//*[@id="content"]/div/div[2]/h1/text()').get()

    def numcas(self, response):
        numcas = re.findall('\d+-\d+[-\d]*',
                            response.xpath('//div[@class="att-new-table" and contains(text(), "CAS Number:")]').get())
        if len(numcas):
            return numcas[0]
        else:
            return ''

    def frmsum(self, response):
        return response.xpath('//div[@class="att-new-table" and contains(text(), "Molecular Formula:")]').get(). \
            replace('<div class="att-new-table">', '').replace('\n', '').replace('\t', '').replace('<sub>', ''). \
            replace('</sub>', '').replace('</div>', '').replace('Molecular Formula:', '')

    def nummdl(self, response):
        return response.xpath(
            '//div[@class="att-new-table" and contains(text(), "MDL Number:")]/text()').get().strip().replace(
            'MDL Number:', '')

    def purity(self, response):
        return response.xpath('//div[@class="att-new-table" and contains(text(), "Purity")]/text()').get().replace(
            'Purity:', '').strip()

    def sap_ehs_1013_037_value(self, response):
        mw = re.findall('\d+\.\d+', response.xpath(
            '//div[@class="att-new-table" and contains(text(), "Molecular Weight")]/text()').get())
        if len(mw):
            return mw[0]

    def unit_list_qt_list(self, response):
        lst = re.findall('((\d+(\.\d+)?)+(kg|g|mg|ml|pack))',
                         response.xpath('//div[@class="form-group option-quantity-extension"]').get())
        unit_list = [i[3] for i in lst]
        qt_list = [i[1] for i in lst]
        return unit_list, qt_list

    def price_pack_list(self, response):
        return [float(i) for i in re.findall("\d+\.\d\d(?!\d)\\n", response.xpath(
            '//div[@class="form-group option-quantity-extension"]').get())]

    def currency_list(self, response):
        return re.findall('£|USD', response.xpath('//div[@class="form-group option-quantity-extension"]').get())

    def price_unit_list(self, price_pack_list, qt_list):
        return [round(i / float(j), 2) for i, j in zip(price_pack_list, qt_list)]
