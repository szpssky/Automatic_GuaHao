#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Michael Shen'

from bs4 import BeautifulSoup
import re
def obtain_docUrl(data):
    soup = BeautifulSoup(data,'html.parser')

    tag1 = soup.find_all(href=re.compile("hospDeptId"))[0]
    tag2 = soup.find_all(href=re.compile("hospDeptId"))[1]
    return (tag1['href'],tag2['href'])

def obtain_hospId(data):
    linkre = re.compile('data-hospId="\d\S+"')
    result = set()
    for s in linkre.findall(data):
        result.add(s[13:-1])
    return result

def obtain_depId(data):
    soup = BeautifulSoup(data,'html.parser')
    tags=soup.find_all(class_ = 'more-description-container')

    linkre = re.compile('(department/\S+")+')
    list = []
    for s in linkre.findall(str(tags[0])):
        list.append(s[11:-1])
    return list
def obtain_depId_hospId_url(data):
    soup = BeautifulSoup(data,'html.parser')
    tags = soup.find_all(id = 'schedules-dept')
    linkre1 = re.compile('deptid="\S+"')
    linkre2 = re.compile('hospid="\S+"')
    list_dep = []
    list_hos = []
    for s in linkre1.findall(str(tags[0])):
        list_dep.append(s[8:-1])
    for s in linkre2.findall(str(tags[0])):
        list_hos.append(s[8:-1])
    urls = []
    for i in range(list_hos.__len__()):
        urls.append('hospDeptId='+list_dep.pop()+'&'+'hospId='+list_hos.pop())
    return urls

def obtain_submit_para(data):
    soup = BeautifulSoup(data,'html.parser')
    tags = soup.find_all(class_='order-form')[0]
    csrf_token = tags.contents[1]['value']
    signdata = tags.contents[1].find(id='signdata')['value']
    encodePatientId=soup.find_all(class_='tool_id')[0]['data-id']
    return (csrf_token,signdata,encodePatientId)
def is_success(data):
    soup = BeautifulSoup(data,'html.parser')
    if '预约成功'==soup.title.string.split('|')[0].strip():
        return True
    else:
        return False



