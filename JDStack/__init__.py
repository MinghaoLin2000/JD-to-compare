# coding=gbk
'''
coupon-优惠卷
优惠卷用couponstyle字段区分
    if couponstyle==0:
    满quota,减少discount
    elif couponstyle==3:
    满quota,乘以discount
promo_info-促销
促销活动用extType字段来区分
if extType==2 :
    那么每满needMoney元，可减rewardMoney元现金，最高可以减少topMoney元
elif extType==6:
    满needMoney,减少rewardMoney
elif extTyp==15:
    满needNum，乘以8.80
'''
#couponstyle随着type变化时。
def coup(singlemoney,number,type,quota,discount):
    tmp=0
    final=singlemoney*number
    if type==0:
        if final>=quota:
            tmp=discount
    elif type==3:
        tmp=final-final*discount
    return tmp
#extType随着type变化
def prom(singlemoney,number,type,dictory):
    tmp=0
    final = singlemoney * number
    if type==2:
        needmoney=eval(dictory['needMoney'])
        rewardmoney=eval(dictory['rewardMoney'])
        if "topMoney" in dictory.keys():
            topmoney=eval(dictory['topMoney'])
            charge=int(final/needmoney)
            tmp=charge*rewardmoney
            if tmp>topmoney:
                tmp=topmoney
        else:
            charge=int(final/needmoney)
            tmp=charge*rewardmoney
    elif type==6:
        ruleList=dictory['subRuleList']
        length=len(ruleList)
        for i in range(0,length):
            needmoney=ruleList[i]['needMoney']
            rewardmoney=ruleList[i]['rewardMoney']
            if final>=needmoney:
                tmp+=rewardmoney
    elif type==15:
        ruleList=dictory['subRuleList'][0]
        neednum=eval(ruleList['needNum'])
        rebate=eval(ruleList['rebate'])/10
        if number>=neednum:
            tmp=final-final*rebate
    print(tmp)
    return tmp
# 计算价格
def count(result,number):
    singlemoney=result['dredisprice']
    singlemoney = float(singlemoney)
    finalmoney=singlemoney*number
    lenc=len(result['coupons'])
    lenp=len(result['promos'])
    disapper=0
    for i in range(0,lenc):
        type = result['coupons'][i]['couponstyle']
        quota = 0
        discount = 0
        if type==0:
            quota=result['coupons'][i]['quota']
            discount=result['coupons'][i]['discount']
        elif type==3:
            quota=eval(result['coupons'][i]['discountdesc']['info'][0]['quota'])
            discount=eval(result['coupons'][i]['discountdesc']['info'][0]['discount'])
        disapper+=coup(singlemoney,number,type,quota,discount)
    for j in range(0,lenp):
        if result['promos'][j]['subextinfo']=='':
            continue
        dictory=eval(result['promos'][j]['subextinfo'])
        type=dictory['extType']
        disapper+=prom(singlemoney,number,type,dictory)
    print(disapper)
    finalmoney-=disapper
    return finalmoney
bad={'warename': '先锋（Singfun） 远程遥控 LED屏 智能取暖器/家用电暖器/电暖气/12片S型电热油汀 DS3342', 'wareid': '1205757', 'dredisprice': '389.00', 'vender_id': '1000002569', 'coupon_t': '1', 'pfdt': '1', 'ware_url': 'https://item.m.jd.com/product/1205757.html?from=qrcode', 'promos': [{'pid': '50071632555_1', 'st': '1579622400', 'd': '1580832000', 'subextinfo': '', 'adurl': '', 'ori': '1', 'customtag': '{"p":"389.00"}'}, {'pid': '50065241225_10', 'st': '1577980800', 'd': '1582991999', 'subextinfo': '{"extType":2,"needMoney":"100","rewardMoney":"10","subExtType":8,"subRuleList":[],"topMoney":"1000"}', 'adurl': '', 'ori': '1', '15': '每满100元，可减10元现金，最多可减1000元', 'customtag': '{}'}, {'pid': '50069805843_10', 'st': '1579276800', 'd': '1581868799', 'subextinfo': '{"extType":24,"needNum":"1","subExtType":36,"subRuleList":[]}', 'adurl': '', 'ori': '1', '60': '购买1件可优惠换购热销商品', 'customtag': '{}'}], 'bool': True, 'coupons': [{'didget': '0', 'name': '仅可购买小家电部分商品', 'key': '88a8b5577c6e48a0b226ff9ffef9a929', 'timeDesc': '2020.01.31 - 2020.02.03', 'hourcoupon': 1, 'couponType': 1, 'roleId': 27561342, 'couponstyle': 0, 'couponKind': 1, 'userLabel': '0', 'businessLabel': '0', 'discountdesc': {}, 'quota': 999.0, 'discount': 100.0}, {'didget': '0', 'name': '仅可购买小家电部分商品', 'key': 'c09739672cf14bf3b987f426f5e8c7f0', 'timeDesc': '2020.01.31 - 2020.02.03', 'hourcoupon': 1, 'couponType': 1, 'roleId': 27561345, 'couponstyle': 0, 'couponKind': 1, 'userLabel': '0', 'businessLabel': '0', 'discountdesc': {}, 'quota': 599.0, 'discount': 60.0}, {'didget': '0', 'name': '仅可购买小家电部分商品', 'key': 'c79e4f52a1e943259199d7909870db2d', 'timeDesc': '2020.01.31 - 2020.02.03', 'hourcoupon': 1, 'couponType': 1, 'roleId': 27561348, 'couponstyle': 0, 'couponKind': 1, 'userLabel': '0', 'businessLabel': '0', 'discountdesc': {}, 'quota': 199.0, 'discount': 20.0}]}
price=count(bad,1)
print(price)
