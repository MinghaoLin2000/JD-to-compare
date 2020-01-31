from tornado import httpclient,gen,queues,ioloop
from tornado.concurrent import Future
from JDStack.util import choose_header
import re
import json
import pymysql
from functools import partial
import tormysql
class JdBot():
    def __init__(self):
        self.item_queue=queues.Queue()
        self.Sql_exe=MySql()
    @gen.coroutine
    def save_to_mysql(self):
        print("开始保存到数据库")
        item= yield self.item_queue.get()
        for coupon in item.get("coupons",[]):
            if coupon.get("couponstyle",0)==3:
                coupon_sql="""insert into coupon_info values(0,{couponstyle},"{couponbatch}","{discount}","{quota}","{key}","{roleId}","{name}","{timeDesc}");""".format(
                    couponstyle=coupon.get("couponstyle",0),
                    couponbatch=coupon.get("couponbatch",""),
                    discount=coupon.get("discountdesc",{}).get("info",[])[0].get("discount",""),
                    quota=coupon.get("discountdesc",{}).get("info",[])[0].get("quota",""),
                    key=coupon.get("key",""),
                    roleId=coupon.get("roleId",""),
                    name=coupon.get("name",""),
                    timeDesc=coupon.get("timeDesc","")
                )
            else:
                coupon_sql = """insert into coupon_info values(0,{couponstyle},"{couponbatch}","{discount}","{quota}","{key}","{roleId}","{name}","{timeDesc}");""".format(
                    couponstyle=coupon.get("couponstyle", 0),
                    couponbatch=coupon.get("couponbatch", ""),
                    discount=coupon.get("discount", ""),
                    quota=coupon.get("quota", ""),
                    key=coupon.get("key", ""),
                    roleId=coupon.get("roleId", ""),
                    name=coupon.get("name", ""),
                    timeDesc=coupon.get("timeDesc", ""))
            print(coupon_sql)
            yield self.Sql_exe.update_data(coupon_sql)
        for promo in item.get("promos",[]):
            if promo.get("subextinfo",""):
                promo_sql="""insert into promo_info values (0,"{pid}","{name}","{st}","{d}",'{subextinfo}')""".format(
                    pid=promo.get("pid","0_0").split("_")[0],
                    name=promo.get(re.findall(r'\d{1,2}',str(promo.keys()))[0],""),
                    st=promo.get("st",""),
                    d=promo.get("d",""),
                    subextinfo=promo.get("subextinfo","")
                )
                print(promo_sql)
                yield self.Sql_exe.update_data(promo_sql)
        ware_sql="""insert into ware_info values ("{wareid}","{warename}","{dredisprice}","{vender_id}","{ware_url}")""".format(
            wareid=item.get("wareid",""),
            warename=item.get("warename",""),
            dredisprice=item.get("dredisprice",""),
            vender_id=item.get("vender_id",""),
            ware_url=item.get("ware_url","")
        )
        yield self.Sql_exe.update_data(ware_sql)
    @gen.coroutine
    def async_fetch_future(self,url):
        http_client = httpclient.AsyncHTTPClient()
        my_future = Future()
        Requests=httpclient.HTTPRequest(
            url=url,
            method="GET",
            headers=choose_header()
        )
        fetch_future = http_client.fetch(Requests)
        fetch_future.add_done_callback(
            lambda f: my_future.set_result(f.result()))
        return my_future
    @gen.coroutine
    def parse_promo_response(self,item,future):
        """
        解析商品促销信息
        :param future:
        :return:
        """
        html=future.result().body.decode("utf8")
        data=json.loads(re.match(".*?({.*}).*", html, re.S).group(1))
        promos=data["data"][0]["pis"]
        item["promos"]=promos
        _bool = item.get("bool", False)
        if _bool:
            print(item)
            yield self.item_queue.put(item)
            yield self.save_to_mysql()

        else:
            item["bool"] = True
    @gen.coroutine
    def parse_coupon_response(self,item,future):
        """
        解析商品优惠卷信息
        :param future:
        :return:
        """
        html=future.result().body.decode("utf8")
        data=json.loads(re.match(r"getCouponListCBA\((.*?)\)$", html, re.S).group(1))
        coupons=data.get("coupons",[])
        item["coupons"]=coupons
        _bool=item.get("bool",False)
        if _bool:
            print(item)
            yield self.item_queue.put(item)
            yield self.save_to_mysql()

        else:
            item["bool"] = True
    @gen.coroutine
    def parse_items_response(self,future):
        """
        解析优惠卷里的商品
        :param future:
        :return:
        """
        html=future.result().body.decode("utf8")
        data = eval(re.sub("json", "", html))
        Paragraph = data["data"]["searchm"]["Paragraph"]
        if not len(Paragraph) == 0:
            for a in Paragraph:
                item_dict = {}
                item_dict["warename"] = a["Content"]["warename"]
                item_dict["wareid"] = a["wareid"]
                item_dict["dredisprice"] = a["dredisprice"]
                item_dict["vender_id"] = a["vender_id"]
                item_dict["coupon_t"] = a["coupon"]["t"]
                item_dict["pfdt"] = a["pfdt"]["t"]
                item_dict["ware_url"] = "https://item.m.jd.com/product/{}.html?from=qrcode".format(item_dict["wareid"])
                # print(item_dict)
                if item_dict["coupon_t"] != "0" and len(item_dict["pfdt"]) > 0:
                   # "存在双叠加"
                    yield self.get_double_stack_info(item_dict)
        else:
            return "没有获取到商品信息 "
    @gen.coroutine
    def get_double_stack_info(self,item):
        wareid=item.get("wareid","")
        if wareid:
            vender_id=item.get("vender_id","8888")
            coupon_url = "https://wq.jd.com/bases/couponsoa/avlCoupon?callback=getCouponListCBA&cid=7061&popId={}&sku={}&platform=4&t=0.866331016223141".format(
                vender_id, wareid)
            promo_url = "https://wq.jd.com/commodity/promo/get?skuid={}&callback=jsonp900789".format(str(wareid))
            print(coupon_url)
            print(promo_url)
            future=yield self.async_fetch_future(coupon_url)
            io_loop.add_future(future,partial(self.parse_coupon_response,item))
            future = yield self.async_fetch_future(promo_url)
            io_loop.add_future(future, partial(self.parse_promo_response,item))
    @gen.coroutine
    def main(self):
        @gen.coroutine
        def fetch_url():
            current_url = yield queue.get()
            print(current_url)
            try:
                future = yield self.async_fetch_future(current_url)
                io_loop.add_future(future=future, callback=self.parse_items_response)

            finally:
                # 队列内数据减一
                queue.task_done()

        @gen.coroutine
        # @staticmethod
        def worker():
            while True:
                # 保证程序持续运行
                yield fetch_url()
        # Start workers, then wait for the work queue to be empty.
        for _ in range(5):
            # 启动对应数量的worker
            worker()
        # 等待队列数据处理完成
        yield queue.join()
        # print(time.time() - a)

class MySql():
    def __init__(self):
        "insert into coupon_info values("","","","","","","");"
        self.pool = tormysql.ConnectionPool(
            max_connections=500,
            idle_seconds=7500,
            wait_connection_timeout=600,
            host="127.0.0.1",
            user="root",
            passwd="",
            db="eesy",
            charset="utf8",
            cursorclass=pymysql.cursors.DictCursor
        )
    async def update_data(self, sql):
        """更新数据,执行sql数据"""

        async with await self.pool.Connection() as conn:
            try:
                async with conn.cursor() as cursor:
                    await cursor.execute(sql)
            except Exception as e:
                print(e)
                await conn.rollback()
            else:
                await conn.commit()
        return ""
    @gen.coroutine
    def main(self):
        yield self.update_data("show tables;")
if __name__ == '__main__':
    queue=queues.Queue()
    couponbatch=276521870
    for i in range(1):

        url = "https://so.m.jd.com/list/couponSearch._m2wq_list?couponbatch=%s&neverpop=yes&datatype=1&callback=json&page=1&pagesize=50" % (str(couponbatch))
        # queue.put("http://127.0.0.1:5000/index")
        queue.put(url)
    io_loop = ioloop.IOLoop.current()
    jd=JdBot()
    jd.main()
    io_loop.start()