# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from hashlib import md5
from scrapy import log
from twisted.enterprise import adbapi
from scrapy_template.items import ScrapyTemplateItem


class ScrapyTemplatePipeline(object):
    def __init__(self, dbpool):
        self.urls_seen = set()
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)

    def process_item(self, item, spider):
        if isinstance(item, ScrapyTemplateItem):
            if item['url'] in self.urls_seen:
                raise DropItem("Duplicate item found: %s" % item['url'])
            else:
                self.urls_seen.add(item['url'])
                d = self.dbpool.runInteraction(self._do_upsert, item, spider)
                d.addErrback(self._handle_error, item, spider)
                d.addBoth(lambda _: item)
                return d
        else:
            return item

    def _do_upsert(self, conn, item, spider):
        guid = self._get_id(item)

        conn.execute("""SELECT EXISTS(
            SELECT 1 FROM example WHERE guid = %s
        )""", (guid, ))
        ret = conn.fetchone()[0]
        if not ret:
            conn.execute("""
                INSERT INTO example (category, name, color, images, price, url, guid)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (item['category'], item['name'], item['color'],
                  item['images'], item['price'], item['url'], guid))
            spider.log("Item stored in db: %s %r" % (guid, item))

    def _handle_error(self, failure, item, spider):
        log.err(failure)

    def _get_id(self, item):
        return md5(item['url']).hexdigest()