#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Michael Shen'

import requests
import pickle
import AnalysisHtml
import re,json
import time
import random
import hashlib


class Guahao(object):
    def __init__(self,username,password):

        self.home_url = 'http://www.guahao.com/'
        self.login_url = 'http://www.guahao.com/user/login'
        self.validImage_url = 'http://www.guahao.com/validcode/genimage/1'
        self.orderlist_url = 'http://www.guahao.com/my/orderlist'
        self.search_url = 'http://www.guahao.com/search'
        self.loginId = username
        self.password = self.strToMd5(password)
        print(self.password)
        self.session = requests.Session()
        self.loginHeaders = {
            'Host': 'www.guahao.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'http://www.guahao.com/user/login?target=%2F',
            'Connection': 'keep-alive'

        }
        self.validHeaders = {
            'Host': 'www.guahao.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        self.homeHeaders={
            'Host': 'www.guahao.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        self.proxies_list=[]
        self.prox=dict()
        #初始化代理服务器列表
        with open('pro.txt','r') as f:
            for line in f.readlines():
                self.proxies_list.append(line.strip())

        try:
            # 加载持久化存储的session
            with open('session.file','rb') as f:
                self.session = pickle.load(f)
                r = self.session.get(self.home_url,headers = self.homeHeaders)
        except:
            #如果文件不存在
            self.getCookie()
            self.getVaildImage()
            self.login()





    #首次访问主页,用来获得cookie
    def getCookie(self):
        response = self.session.get(self.home_url,headers = self.homeHeaders)


    # 模拟登陆
    def login(self):
        validCode = input('输入验证码:')
        post_para = {
            'method':'dologin',
            'target':'/',
            'loginId':self.loginId,
            'password':self.password,
            'validCode':validCode
        }
        res = self.session.post(self.login_url,post_para)

        #持久化session 下次加载无需重新登陆
        with open('session.file','wb') as f:
            pickle.dump(self.session,f)

    #获取登陆验证码
    def getVaildImage(self):
        r = self.session.get(self.validImage_url,headers = self.validHeaders)
        imageData = r.content
        with open('vaild.jpg','wb') as f:
            f.write(imageData)


    def visitHomePage(self):

        #加载持久化存储的session
        with open('session.file','rb') as f:
            self.session = pickle.load(f)
        r = self.session.get(self.home_url,headers = self.homeHeaders)

    def search_doctor(self,doctor_name):
        post_para = {
            'q':doctor_name
        }
        r = self.session.post(self.search_url,post_para,headers = self.homeHeaders)

        return r.text

    def get_reg_info(self,doctor_name,regdate):

        list_deptId = []
        html_data = self.search_doctor(doctor_name)
        urls = AnalysisHtml.obtain_docUrl(html_data)
        vist_url = urls[0]
        linkre = re.compile('/.\d\S+\?')
        expertId = linkre.findall(urls[0])[0][1:-1]
        count = 0
        while True:
            try:
                #随机选取代理服务器地址
                self.prox['http']=random.choice(self.proxies_list)
                print(self.prox)
                count+=1
                resurl,link_url,status = self.registration(vist_url,expertId,regdate)
                print(count)
                if resurl != None:
                    break;
                elif status == 3:
                    print("手速慢啦,没号啦.........")
                    break
                elif status == 0:
                    print("截止暂不可约")
                    break
            except:
                print('访问请求失败...重新发起请求')
            # time.sleep(2)


        if(status == 4):
            self.submitreg(resurl,expertId,link_url)

    def registration(self,vist_url,expertId,regdate):

        r = self.session.get(vist_url,headers = self.homeHeaders,proxies=self.prox,timeout=1)
        urls = AnalysisHtml.obtain_depId_hospId_url(r.text)

        regJson_urls = [self.home_url+'expert/new/shiftcase/?expertId='+expertId+'&'+url for url in urls]
        reg_date_url = None
        link_url = ''
        status = None
        for reg_url in regJson_urls:
            r = json.loads(self.session.get(reg_url,headers = self.homeHeaders,proxies=self.prox,timeout=1).text)['data']['shiftSchedule']
            if r!= []:
                for i in range(len(r)):
                    if(regdate != r[i]['date']):
                        continue
                    elif 4==r[i]['status']:
                        reg_date_url =self.home_url+r[i]['url'][1:]
                        link_url = reg_url
                        status = 4
                        break
                    else:
                        status = r[i]['status']
                        break
                    #     break
                    # elif 0==r[i]['status']:
                    #     statuss = r[i]['status']
                    #     break
                    # # elif regdate == r[i]['date'] and 3==r[i]['status']:
                    # #     status = r[i]['status']
                    # # else:
                    # #     status = r[i]['status']
                # status = r[i]['status']
                if(status!=None):
                    return reg_date_url,link_url,status
                # else:
                #     break
        return None,link_url,None



    def submitreg(self,resurl,expertId,link_url):
        self.getVaildImage()
        r = self.session.get(resurl,headers = self.homeHeaders)
        linkre1 = re.compile('hospDeptId=\S+&')
        linkre2 = re.compile('hospId=\S+')
        linkre3 = re.compile('/\w+\?')
        hospDeptId = linkre1.findall(link_url)[0][11:-1]
        hospId = linkre2.findall(link_url)[0][7:]
        # shiftCaseId = linkre3.findall((resurl))[0][1:-1]
        shiftCaseId = resurl[77:-20]
        header = {
            'Host': 'www.guahao.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': resurl,
            'Connection': 'keep-alive'

        }
        (csrf_token,signdata,encodePatientId) = AnalysisHtml.obtain_submit_para(r.text)

        validCode = input('请输入验证码:')
        post_para = {
            'csrf_token':csrf_token,
            'shiftCaseId':shiftCaseId,
            'hospitalId':hospId,
            'expertId':expertId,
            'isNeedAgent':'0',
            'deptId':hospDeptId,
            'ageLowerLimit':'0',
            'ageTopLimit':'150',
            'sexLimit':'3',
            'patientListSize':'1',
            'signdata':signdata,
            'isZJPT':'',
            'patient.encodePatientId':encodePatientId,
            'RequireNameStr0':'',
            'visitType':'0',
            'RequireNameStr1':'1_require_0cardType,,就诊卡类型:1_require_0cardValue,,卡号:',
            '1_require_0cardType':'1',
            '1_require_0cardValue':'',
            'diseaseName':'尚未确诊',
            'diseaseId':'0',
            'validCode':validCode,
            'knowit':'on'
        }
        r = self.session.post('http://www.guahao.com/my/reservation/submitvalidate',post_para,headers = header)
        if AnalysisHtml.is_success(r.text):
            "预约成功"
        else:
            "预约失败"
    def strToMd5(self,str):
        md5 = hashlib.md5()
        md5.update(str.encode('utf-8'))
        return md5.hexdigest()





guahao= Guahao('xxxx','xxxx') #输入账号和密码
# guahao.visitHomePage()
guahao.get_reg_info('叶惟靖','2016-04-04') #医生名称,就诊日期.请确保医生在该日期正常出诊