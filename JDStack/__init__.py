# coding=gbk
'''
coupon-�Żݾ�
�Żݾ���couponstyle�ֶ�����
    if couponstyle==0:
    ��quota,����discount
    elif couponstyle==3:
    ��quota,����discount
promo_info-����
�������extType�ֶ�������
if extType==2 :
    ��ôÿ��needMoneyԪ���ɼ�rewardMoneyԪ�ֽ���߿��Լ���topMoneyԪ
elif extType==6:
    ��needMoney,����rewardMoney
elif extTyp==15:
    ��needNum������8.80
'''
#couponstyle����type�仯ʱ��
def coup(singlemoney,number,type,quota,discount):
    tmp=0
    final=singlemoney*number
    if type==0:
        if final>=quota:
            tmp=discount
    elif type==3:
        tmp=final-final*discount
    return tmp
#extType����type�仯
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
# ����۸�
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
bad={'warename': '�ȷ棨Singfun�� Զ��ң�� LED�� ����ȡů��/���õ�ů��/��ů��/12ƬS�͵�����͡ DS3342', 'wareid': '1205757', 'dredisprice': '389.00', 'vender_id': '1000002569', 'coupon_t': '1', 'pfdt': '1', 'ware_url': 'https://item.m.jd.com/product/1205757.html?from=qrcode', 'promos': [{'pid': '50071632555_1', 'st': '1579622400', 'd': '1580832000', 'subextinfo': '', 'adurl': '', 'ori': '1', 'customtag': '{"p":"389.00"}'}, {'pid': '50065241225_10', 'st': '1577980800', 'd': '1582991999', 'subextinfo': '{"extType":2,"needMoney":"100","rewardMoney":"10","subExtType":8,"subRuleList":[],"topMoney":"1000"}', 'adurl': '', 'ori': '1', '15': 'ÿ��100Ԫ���ɼ�10Ԫ�ֽ����ɼ�1000Ԫ', 'customtag': '{}'}, {'pid': '50069805843_10', 'st': '1579276800', 'd': '1581868799', 'subextinfo': '{"extType":24,"needNum":"1","subExtType":36,"subRuleList":[]}', 'adurl': '', 'ori': '1', '60': '����1�����Żݻ���������Ʒ', 'customtag': '{}'}], 'bool': True, 'coupons': [{'didget': '0', 'name': '���ɹ���С�ҵ粿����Ʒ', 'key': '88a8b5577c6e48a0b226ff9ffef9a929', 'timeDesc': '2020.01.31 - 2020.02.03', 'hourcoupon': 1, 'couponType': 1, 'roleId': 27561342, 'couponstyle': 0, 'couponKind': 1, 'userLabel': '0', 'businessLabel': '0', 'discountdesc': {}, 'quota': 999.0, 'discount': 100.0}, {'didget': '0', 'name': '���ɹ���С�ҵ粿����Ʒ', 'key': 'c09739672cf14bf3b987f426f5e8c7f0', 'timeDesc': '2020.01.31 - 2020.02.03', 'hourcoupon': 1, 'couponType': 1, 'roleId': 27561345, 'couponstyle': 0, 'couponKind': 1, 'userLabel': '0', 'businessLabel': '0', 'discountdesc': {}, 'quota': 599.0, 'discount': 60.0}, {'didget': '0', 'name': '���ɹ���С�ҵ粿����Ʒ', 'key': 'c79e4f52a1e943259199d7909870db2d', 'timeDesc': '2020.01.31 - 2020.02.03', 'hourcoupon': 1, 'couponType': 1, 'roleId': 27561348, 'couponstyle': 0, 'couponKind': 1, 'userLabel': '0', 'businessLabel': '0', 'discountdesc': {}, 'quota': 199.0, 'discount': 20.0}]}
price=count(bad,1)
print(price)
