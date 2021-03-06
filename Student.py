# -*- coding: utf-8 -*-
# @File 	: Student.py
# @Author 	: jianhuChen
# @Date 	: 2019-02-01 13:08:45
# @License 	: Copyright(C), USTC
# @Last Modified by  : jianhuChen
# @Last Modified time: 2019-03-07 10:50:11

import requests
import re
import os
import time 
import random
import threading # 多线程
import base64 # 加密x_state


from prettytable import PrettyTable  # 打印表格


class Student:
	def __init__(self, userAccount, userLocation, userYear, userTerm, sleepTime, errorKeepChoose=False, fullKeepChoose=True):
		'''
			作用：初始化用户信息
		'''
		self.userId = userAccount['userId']
		self.userPwd = userAccount['userPwd']
		self.userName = self.userId
		self.userLocation = userLocation
		self.userYear = userYear
		self.userTerm = userTerm
		self.userYearTerm = userYear + '-' + userTerm
		self.sleepTime = sleepTime
		self.errorKeepChoose = errorKeepChoose
		self.fullKeepChoose = fullKeepChoose
		self.count = 0
		# 构建一个Session对象，可以保存页面Cookie
		self.sess = requests.Session()
		# 构造请求报头
		self.headers = {'User-Agent' : 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)'}

	def getCheckcodeFromCookies(self, cookies):
		'''
			作用：获取验证码
			返回：验证码
		'''
		text = cookies['CheckCode']
		textNum = [int(x) for x in text]
		textSum = textNum[0] + textNum[1] + textNum[2] + textNum[3]
		return textSum

	def getStuInfoHtml(self):
		'''
			作用：获取个人信息页面源码，用于测试信息是否爬取成功
			返回：个人信息页面源码
		'''
		stuInfoUrl = 'http://mis.sse.ustc.edu.cn/PersonalSetting/ModifyPersonalInfoStu.aspx'
		response = self.sess.get(stuInfoUrl, headers=self.headers)
		stuInfoHtml = response.text.encode('utf-8')
		return stuInfoHtml

	def printStuInfo(self):
		'''
			作用：打印个人信息
			返回：是否登陆成功
		'''
		self.writeLogs('正在询您的个人信息，请稍候...')
		stuInfoHtml = self.getStuInfoHtml()
		try:
			namePattern = re.compile(r'txtName",allow.*?value:"(.*?)"', re.S)
			name = namePattern.findall(stuInfoHtml)[0].strip()
			stuNoPattern = re.compile(r'txtStuNo",allow.*?value:"(.*?)"', re.S)
			stuNo = stuNoPattern.findall(stuInfoHtml)[0].strip()
			nationPattern = re.compile(r'txtNation",max.*?value:"(.*?)"', re.S)
			nation = nationPattern.findall(stuInfoHtml)[0].strip()
			birthdayPattern = re.compile(r'dpBirthDay",value:"(.*?)"', re.S)
			birthday = birthdayPattern.findall(stuInfoHtml)[0].strip()
			emailPattern = re.compile(r'txtEmail",allow.*?value:"(.*?)"', re.S)
			email = emailPattern.findall(stuInfoHtml)[0].strip()
			phonePattern = re.compile(r'txtPhone",max.*?value:"(.*?)"', re.S)
			phone = phonePattern.findall(stuInfoHtml)[0].strip()
		except:
			self.writeLogs('查询您的个人信息失败...\n请检查您的账号/密码是否输入正确！', error=True)
			return False
		self.writeLogs('查询您的个人信息成功...')
		# 记录名字信息
		self.userName = name
		self.writeLogs('-'*60 + '\n' + \
			'学号：{}\t姓名：{}\t出生日期：{}'.format(stuNo, name, birthday) + '\n' + \
			'联系方式：{}\t电子邮件：{}'.format(phone, email) + '\n' + \
			'-'*60
			, info = False)
		return True
			
	def login(self):
		'''
			作用：登录软件学院信息化平台并获取学生信息页面
			返回：是否登陆成功
		'''
		# 登录接口
		loginUrl = 'http://mis.sse.ustc.edu.cn/default.aspx'
		# 验证码地址
		checkcodeUrl = 'http://mis.sse.ustc.edu.cn/ValidateCode.aspx?ValidateCodeType=1&0.011150883024061309'
		# 发送图片的请求，获取图片数据流
		response = self.sess.get(checkcodeUrl, headers=self.headers)
		# checkcodeData = response.content
		cookies = response.cookies.get_dict()
		# 获取验证码里的数字之和
		textSum = self.getCheckcodeFromCookies(cookies)
		# 构造登录数据
		data = {
			'__EVENTTARGET' : 'winLogin$sfLogin$ContentPanel1$btnLogin',
			'__EVENTARGUMENT' : '',
			'__VIEWSTATE' : '/wEPDwUKLTMzNjg2NDcwNGQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgwFCHdpbkxvZ2luBRB3aW5Mb2dpbiRzZkxvZ2luBRZ3aW5Mb2dpbiRzZkxvZ2luJGN0bDAwBR93aW5Mb2dpbiRzZkxvZ2luJHR4dFVzZXJMb2dpbklEBRx3aW5Mb2dpbiRzZkxvZ2luJHR4dFBhc3N3b3JkBRx3aW5Mb2dpbiRzZkxvZ2luJHR4dFZhbGlkYXRlBR53aW5Mb2dpbiRzZkxvZ2luJENvbnRlbnRQYW5lbDMFLHdpbkxvZ2luJHNmTG9naW4kQ29udGVudFBhbmVsMyRjYnhTYXZlTXlJbmZvBS53aW5Mb2dpbiRzZkxvZ2luJENvbnRlbnRQYW5lbDMkYnRuUmVmVmFsaWRDb2RlBR53aW5Mb2dpbiRzZkxvZ2luJENvbnRlbnRQYW5lbDEFJ3dpbkxvZ2luJHNmTG9naW4kQ29udGVudFBhbmVsMSRidG5Mb2dpbgUIV25kTW9kYWy2ePrTvZjBBql35+4HcyIqDYPkPGG8BipKo3FdUE8sdA==',
			'X_CHANGED' : 'true',
			'winLogin$sfLogin$txtUserLoginID' : self.userId,
			'winLogin$sfLogin$txtPassword' : self.userPwd,
			'winLogin$sfLogin$txtValidate' : textSum,
			'winLogin_Hidden' : 'false',
			'WndModal_Hidden' : 'true',
			'X_TARGET' : 'winLogin_sfLogin_ContentPanel1_btnLogin',
			'winLogin_sfLogin_ctl00_Collapsed' : 'false',
			'winLogin_sfLogin_ContentPanel3_Collapsed' : 'false',
			'winLogin_sfLogin_ContentPanel1_Collapsed' : 'false',
			'winLogin_sfLogin_Collapsed' : 'false',
			'winLogin_Collapsed' : 'false',
			'WndModal_Collapsed' : 'false',
			'X_STATE' : 'e30=',
			'X_AJAX' : 'true',
		}			
		# 发送登录需要的POST数据，获取登录后的Cookie(保存在sess里)
		self.writeLogs('正在进入软件学院信息化平台...')
		response = self.sess.post(loginUrl, data=data, headers=self.headers)
		# 测试是否登录成功	
		# try:
		# 	re.compile(r'HomePage', re.S).findall(response.text.encode('utf-8'))[0]
		# except:
		# 	isLogin = False
		# else:
		# 	isLogin = True
		# if isLogin:
		# 打印学生信息，并返回是否查询成功
		loginResult = self.printStuInfo()
		# 返回登录是否成功
		return loginResult

	def getStuChoosedHtml(self):
		'''
			作用：获取已选课程网页源码
			返回：已选课程网页源码
		'''
		self.writeLogs('正在查询您的已选课程，请稍候...')
		# 用已有登录状态的Cookie发送请求，获取目标页面源码
		stuChoosedUrl = 'http://mis.sse.ustc.edu.cn/Teaching/CourseChooseInfo/ListStudentChoosed.aspx'
		response = self.sess.post(stuChoosedUrl, headers=self.headers)
		stuChoosedHtml = response.text.encode('utf-8')
		return stuChoosedHtml

	def printStuChoosed(self):
		'''
			作用：打印已选课程
			stuChoosedHtml：包含已选课程信息的html页面
		'''
		stuChoosedHtml = self.getStuChoosedHtml()
		self.writeLogs('{}的已选课程信息如下：'.format(self.userName))
		# 已选学分
		choosedCreditPattern = re.compile(r'txtChoosedCredit",value:"(.*?)"', re.S)
		choosedCredit = choosedCreditPattern.findall(stuChoosedHtml)[0]
		# 限选学分
		maxCreditPattern = re.compile(r'txtMaxCredit",value:"(.*?)"', re.S)
		maxCredit = maxCreditPattern.findall(stuChoosedHtml)[0]
		self.writeLogs('\t'*3+'【学年学期：{}\t已选学分：{}\t限选学分：{}】'.format(self.userYearTerm, choosedCredit, maxCredit), info=False)
		tablebHead = ['序号', '课程编号', '课程名称', '学分', '班号', '授课老师', '授课时间地点', \
						'选课开始时间', '选课结束时间', '退选结束时间', '已选人数', '最大人数']
		choosedCoursePattern = re.compile(r'\["([SGB].*?)","<a.*?>(.*?)</a>","(.*?)","(.*?)","(.*?)","(.*?)","(.*?)","(.*?)","(.*?)","(.*?)","(.*?)",', re.S)
		choosedCourseInfo = choosedCoursePattern.findall(stuChoosedHtml)
		# print choosedCourseInfo
		# 开始打印已选课程 
		# 构造表格
		del tablebHead[6] # 删除上课时间和地点，信息太长，打印不方便
		prettyTableHead = tablebHead
		choosedCourseTable = PrettyTable(prettyTableHead)
		for i in range(len(choosedCourseInfo)): # 几门课
			oneChoosedCourse = list(choosedCourseInfo[i])
			del oneChoosedCourse[5] # 删除上课时间和地点，信息太长，打印不方便
			prettyTableRow = [i]+oneChoosedCourse # 加上序号
			choosedCourseTable.add_row(prettyTableRow)
		self.writeLogs(str(choosedCourseTable), info=False)

	def getCourseStatusHtml(self, courseName):
		'''
			作用：获取【选课列表】某门课的状态的网页源码，从而获取已选课人数和课程容量
			返回：【选课列表】某门课的状态的网页源码
		'''
		# 用已有登录状态的Cookie发送请求，获取目标页面源码
		stuChooseListUrl = 'http://mis.sse.ustc.edu.cn/Teaching/CourseChooseInfo/ListStudentToChoose.aspx'
		
		data = {
			'__EVENTTARGET' : 'global$QueryForm$ctl00$TriggerSearch',
			'__EVENTARGUMENT' : 'Trigger$2',
			'__VIEWSTATE' : '/wEPDwUKMTg4OTI4NDIxOA8WAh4JbWFqb3JUeXBlBRjlpKfmlbDmja7kuI7kurrlt6Xmmbrog71kGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYNBQZnbG9iYWwFEGdsb2JhbCRRdWVyeUZvcm0FJGdsb2JhbCRRdWVyeUZvcm0kY3RsMDAkVHJpZ2dlclNlYXJjaAUhZ2xvYmFsJFF1ZXJ5Rm9ybSRjdGwwMCRkZGxBZGRyZXNzBSNnbG9iYWwkUXVlcnlGb3JtJGN0bDAwJGRkbFN0dWR5WWVhcgUeZ2xvYmFsJFF1ZXJ5Rm9ybSRjdGwwMCRkZGxUZXJtBSdnbG9iYWwkUXVlcnlGb3JtJGN0bDAxJHR4dENob29zZWRDcmVkaXQFI2dsb2JhbCRRdWVyeUZvcm0kY3RsMDEkdHh0TWF4Q3JlZGl0BRBnbG9iYWwkTWFpblBhbmVsBTVnbG9iYWwkTWFpblBhbmVsJGdyaWRBY3RUQmFyJGJ0blZpZXdNdWx0aXBsZUNob2ljZU9uZQUZZ2xvYmFsJE1haW5QYW5lbCRHcmlkTGlzdAUIV25kTW9kYWwFDFduZE1vZGFsX01DT5z07eospMaEA3q5abbcC1AtMyFQ1txhYgDjzNrw/fHC',
			'global$QueryForm$ctl00$TriggerSearch' : courseName,
			'global$QueryForm$ctl00$ddlAddress' : self.userLocation,
			'global$QueryForm$ctl00$ddlStudyYear' : self.userYear,
			'global$QueryForm$ctl00$ddlTerm' : self.userTerm,
			'X_CHANGED' : 'true',
			'WndModal_Hidden' : 'true',
			'WndModal_MCO_Hidden' : 'true',
			'global_QueryForm_Collapsed' : 'false',
			'global_MainPanel_GridList_Collapsed' : 'false',
			'global_MainPanel_GridList_SelectedRowIndexArray' : '',
			'global_MainPanel_GridList_HiddenColumnIndexArray' : '',
			'global_MainPanel_GridList_RowStates' : '[]',
			'global_MainPanel_Collapsed' : 'false',
			'global_Collapsed' : 'false',
			'WndModal_Collapsed' : 'false',
			'WndModal_MCO_Collapsed' : 'false',
			'X_STATE' : 'eyJnbG9iYWxfUXVlcnlGb3JtX2N0bDAwX1RyaWdnZXJTZWFyY2giOnsiVGV4dCI6IuamgueOh+iuuiJ9LCJnbG9iYWxfUXVlcnlGb3JtX2N0bDAwX2RkbEFkZHJlc3MiOnsiWF9JdGVtcyI6W1si6IuP5beeIiwi6IuP5beeIiwxXSxbIuWQiOiCpSIsIuWQiOiCpSIsMV1dLCJTZWxlY3RlZFZhbHVlIjoi6IuP5beeIn0sImdsb2JhbF9RdWVyeUZvcm1fY3RsMDBfZGRsU3R1ZHlZZWFyIjp7IlhfSXRlbXMiOltbIjIwMTgiLCIyMDE4IiwxXSxbIjIwMTkiLCIyMDE5IiwxXV0sIlNlbGVjdGVkVmFsdWUiOiIyMDE4In0sImdsb2JhbF9RdWVyeUZvcm1fY3RsMDBfZGRsVGVybSI6eyJTZWxlY3RlZFZhbHVlIjoiMiIsIlhfSXRlbXMiOltbIjAiLCIwIiwxXSxbIjEiLCIxIiwxXSxbIjIiLCIyIiwxXV19LCJnbG9iYWxfUXVlcnlGb3JtX2N0bDAxX3R4dENob29zZWRDcmVkaXQiOnsiVGV4dCI6IjAifSwiZ2xvYmFsX1F1ZXJ5Rm9ybV9jdGwwMV90eHRNYXhDcmVkaXQiOnsiVGV4dCI6IjIzIn0sImdsb2JhbF9NYWluUGFuZWxfZ3JpZEFjdFRCYXJfYnRuVmlld011bHRpcGxlQ2hvaWNlT25lIjp7Ik9uQ2xpZW50Q2xpY2siOiJYKCdXbmRNb2RhbF9NQ08nKS5ib3hfc2hvdygnL1RlYWNoaW5nL0NvdXJzZUNob29zZUluZm8vQ29tbWVuY2VkTXVsdGlwbGVDaG9pY2VPbmVDb3Vyc2VMaXN0LmFzcHg/SW5wdXRlZEtleT0lZTYlYTYlODIlZTclOGUlODclZTglYWUlYmEmQWRkcmVzcz0lZTglOGIlOGYlZTUlYjclOWUmTWFqb3JUeXBlPSVlNSVhNCVhNyVlNiU5NSViMCVlNiU4ZCVhZSVlNCViOCU4ZSVlNCViYSViYSVlNSViNyVhNSVlNiU5OSViYSVlOCU4MyViZCZZZWFyVGVhbT0yMDE4LTImQ3VycmVudFVzZXJHdWlkPTExNTk5ZWNkLTc4MmEtNDY5NS1hYjlmLTFiYTlkYWYxMzAwYycsJ+afpeeci+WkmumAieS4gOivvueoiycpO3JldHVybiBmYWxzZTsifSwiZ2xvYmFsX01haW5QYW5lbF9HcmlkTGlzdCI6eyJYX1Jvd3MiOnsiVmFsdWVzIjpbXSwiRGF0YUtleXMiOltdfX19',
			'X_AJAX' : 'true',
		}
		response = self.sess.post(stuChooseListUrl, data=data, headers=self.headers)
		stuChooseListHtml = response.text.encode('utf-8')
		
		with open('a.html', 'w') as f:
			f.write(stuChooseListHtml)
		return stuChooseListHtml
	
	def printCourseStatus(self, courseName):
		'''
			作用：打印某门课的状态
			courseName ：课程名称
			返回：(已选人数，最大人数)
		'''
		self.writeLogs('正在查询课程【{}】状态...'.format(courseName))
		courseStatusHtml = self.getCourseStatusHtml(courseName)
		tablebHead = ['课程编号', '课程名称', '学分', '班号', '授课老师', '授课时间地点', \
						'选课开始时间', '选课结束时间', '已选人数', '最大人数']
		ChooseListPattern = re.compile(r'\["([SGB].*?)","<a.*?>(.*?)</a>","(.*?)","(.*?)","(.*?)","(.*?)","(.*?)","(.*?)","(.*?)","(.*?)",', re.S)
		courseStatus = ChooseListPattern.findall(courseStatusHtml)
		# 开始打印选课列表 
		# 构造表格
		del tablebHead[5] # 删除上课时间和地点，信息太长，打印不方便
		prettyTableHead = tablebHead
		ChooseListTable = PrettyTable(prettyTableHead)
		try:
			courseStatus = list(courseStatus[0])
		except:
			self.writeLogs('查询课程【{}】状态失败，请检查课程名字是否正确！'.format(courseName), error=True)
			return (0, 0)
		del courseStatus[5] # 删除上课时间和地点，信息太长，打印不方便
		prettyTableRow = courseStatus
		ChooseListTable.add_row(prettyTableRow)
		self.writeLogs(str(ChooseListTable), info=False)
		return (courseStatus[-2], courseStatus[-1])

	def chooseCourse(self, index, courseName):
		'''
			作用：抢某门课
		'''
		chooseCouserUrl = 'http://mis.sse.ustc.edu.cn/Teaching/CourseChooseInfo/ListStudentToChoose.aspx'
		if self.userLocation == '合肥':
			__VIEWSTATE = '/wEPDwUKMTg4OTI4NDIxOA8WAh4JbWFqb3JUeXBlBRLova/ku7bns7vnu5/orr7orqFkGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYNBQZnbG9iYWwFEGdsb2JhbCRRdWVyeUZvcm0FJGdsb2JhbCRRdWVyeUZvcm0kY3RsMDAkVHJpZ2dlclNlYXJjaAUhZ2xvYmFsJFF1ZXJ5Rm9ybSRjdGwwMCRkZGxBZGRyZXNzBSNnbG9iYWwkUXVlcnlGb3JtJGN0bDAwJGRkbFN0dWR5WWVhcgUeZ2xvYmFsJFF1ZXJ5Rm9ybSRjdGwwMCRkZGxUZXJtBSdnbG9iYWwkUXVlcnlGb3JtJGN0bDAxJHR4dENob29zZWRDcmVkaXQFI2dsb2JhbCRRdWVyeUZvcm0kY3RsMDEkdHh0TWF4Q3JlZGl0BRBnbG9iYWwkTWFpblBhbmVsBTVnbG9iYWwkTWFpblBhbmVsJGdyaWRBY3RUQmFyJGJ0blZpZXdNdWx0aXBsZUNob2ljZU9uZQUZZ2xvYmFsJE1haW5QYW5lbCRHcmlkTGlzdAUIV25kTW9kYWwFDFduZE1vZGFsX01DTyXYFUMMsTfoMZ1si5gUIvqr3Lj+xWc0FwsPrCue/H8A'
			X_STATE = 'eyJnbG9iYWxfUXVlcnlGb3JtX2N0bDAwX1RyaWdnZXJTZWFyY2giOnsiVGV4dCI6IumrmOe6p+aVsOaNruW6k+aKgOacryIsIlNob3dUcmlnZ2VyMSI6dHJ1ZX0sImdsb2JhbF9RdWVyeUZvcm1fY3RsMDBfZGRsQWRkcmVzcyI6eyJTZWxlY3RlZFZhbHVlIjoi5ZCI6IKlIiwiWF9JdGVtcyI6W1si6IuP5beeIiwi6IuP5beeIiwxXSxbIuWQiOiCpSIsIuWQiOiCpSIsMV1dfSwiZ2xvYmFsX1F1ZXJ5Rm9ybV9jdGwwMF9kZGxTdHVkeVllYXIiOnsiWF9JdGVtcyI6W1siMjAxOCIsIjIwMTgiLDFdLFsiMjAxOSIsIjIwMTkiLDFdXSwiU2VsZWN0ZWRWYWx1ZSI6IjIwMTgifSwiZ2xvYmFsX1F1ZXJ5Rm9ybV9jdGwwMF9kZGxUZXJtIjp7IlNlbGVjdGVkVmFsdWUiOiIyIiwiWF9JdGVtcyI6W1siMCIsIjAiLDFdLFsiMSIsIjEiLDFdLFsiMiIsIjIiLDFdXX0sImdsb2JhbF9RdWVyeUZvcm1fY3RsMDFfdHh0Q2hvb3NlZENyZWRpdCI6eyJUZXh0IjoiOSJ9LCJnbG9iYWxfUXVlcnlGb3JtX2N0bDAxX3R4dE1heENyZWRpdCI6eyJUZXh0IjoiMjMifSwiZ2xvYmFsX01haW5QYW5lbF9ncmlkQWN0VEJhcl9idG5WaWV3TXVsdGlwbGVDaG9pY2VPbmUiOnsiT25DbGllbnRDbGljayI6IlgoJ1duZE1vZGFsX01DTycpLmJveF9zaG93KCcvVGVhY2hpbmcvQ291cnNlQ2hvb3NlSW5mby9Db21tZW5jZWRNdWx0aXBsZUNob2ljZU9uZUNvdXJzZUxpc3QuYXNweD9JbnB1dGVkS2V5PSVlOSVhYiU5OCVlNyViYSVhNyVlNiU5NSViMCVlNiU4ZCVhZSVlNSViYSU5MyVlNiU4YSU4MCVlNiU5YyVhZiZBZGRyZXNzPSVlNSU5MCU4OCVlOCU4MiVhNSZNYWpvclR5cGU9JWU4JWJkJWFmJWU0JWJiJWI2JWU3JWIzJWJiJWU3JWJiJTlmJWU4JWFlJWJlJWU4JWFlJWExJlllYXJUZWFtPTIwMTgtMiZDdXJyZW50VXNlckd1aWQ9MjM2MDNkMmEtYjhlNC00OGUzLTg0ODgtNTJmNTZmNzQ4Yzg2Jywn5p+l55yL5aSa6YCJ5LiA6K++56iLJyk7cmV0dXJuIGZhbHNlOyJ9LCJnbG9iYWxfTWFpblBhbmVsX0dyaWRMaXN0Ijp7IlhfUm93cyI6eyJWYWx1ZXMiOltbIlNFMDUyMDMiLCI8YSBocmVmPVwiamF2YXNjcmlwdDo7XCIgb25jbGljaz1cImphdmFzY3JpcHQ6WCgmIzM5O1duZE1vZGFsJiMzOTspLmJveF9zaG93KCYjMzk7L1RlYWNoaW5nL0NvdXJzZUluZm8vVmlld0J5Q291cnNlSUQuYXNweD9Db3Vyc2VJRD1TRTA1MjAzJiMzOTssJiMzOTvpq5jnuqfmlbDmja7lupPmioDmnK8t6K+m57uGJiMzOTspO1wiPumrmOe6p+aVsOaNruW6k+aKgOacrzwvYT4iLCIzIiwi5ZCI6IKlIiwi6YeR5Z+55p2DKDA2MDkyKSIsIjEtMTgg5ZGoL+WRqOS4iS/kuIrljYgoM++8jDTvvIw1KS8yMDIiLCIyMDE5LTItMjEiLCIyMDE5LTMtMTEiLCI4MCIsIjgwIiwiPGEgaHJlZj1cImphdmFzY3JpcHQ6O1wiIG9uY2xpY2s9XCJFeHQuZGVmZXIoZnVuY3Rpb24oKXt3aW5kb3cuRXh0Lk1lc3NhZ2VCb3guc2hvdyh7dGl0bGU6JiMzOTvmj5DnpLomIzM5Oyxtc2c6JiMzOTvnoa7lrprpgInor74mIzM5OyxidXR0b25zOkV4dC5NZXNzYWdlQm94Lk9LQ0FOQ0VMLGljb246RXh0Lk1lc3NhZ2VCb3guSU5GTyxmbjpmdW5jdGlvbihidG4pe2lmKGJ0bj09JiMzOTtjYW5jZWwmIzM5Oyl7cmV0dXJuIGZhbHNlO31lbHNle19fZG9Qb3N0QmFjaygmIzM5O2dsb2JhbCRNYWluUGFuZWwkR3JpZExpc3QmIzM5OywmIzM5O0NvbW1hbmQkMCQxMCRTZWxlY3RDb3Vyc2UkJiMzOTspO319fSk7fSwwKTtYLnV0aWwuc3RvcEV2ZW50UHJvcGFnYXRpb24uYXBwbHkobnVsbCwgYXJndW1lbnRzKTtcIj7pgInmi6nmraTor748L2E+Il1dLCJEYXRhS2V5cyI6W1siZTgwM2M1NTYtYTA3NS00MTdkLWJjOWUtYjM1MWNhZTcwNDU5Il1dfSwiUmVjb3JkQ291bnQiOjEsIlhfU3RhdGVzIjpbW11dLCJTZWxlY3RlZFJvd0luZGV4QXJyYXkiOltdfX0='
		else:
			__VIEWSTATE = '/wEPDwUKMTg4OTI4NDIxOA8WAh4JbWFqb3JUeXBlBRjlpKfmlbDmja7kuI7kurrlt6Xmmbrog71kGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYNBQZnbG9iYWwFEGdsb2JhbCRRdWVyeUZvcm0FJGdsb2JhbCRRdWVyeUZvcm0kY3RsMDAkVHJpZ2dlclNlYXJjaAUhZ2xvYmFsJFF1ZXJ5Rm9ybSRjdGwwMCRkZGxBZGRyZXNzBSNnbG9iYWwkUXVlcnlGb3JtJGN0bDAwJGRkbFN0dWR5WWVhcgUeZ2xvYmFsJFF1ZXJ5Rm9ybSRjdGwwMCRkZGxUZXJtBSdnbG9iYWwkUXVlcnlGb3JtJGN0bDAxJHR4dENob29zZWRDcmVkaXQFI2dsb2JhbCRRdWVyeUZvcm0kY3RsMDEkdHh0TWF4Q3JlZGl0BRBnbG9iYWwkTWFpblBhbmVsBTVnbG9iYWwkTWFpblBhbmVsJGdyaWRBY3RUQmFyJGJ0blZpZXdNdWx0aXBsZUNob2ljZU9uZQUZZ2xvYmFsJE1haW5QYW5lbCRHcmlkTGlzdAUIV25kTW9kYWwFDFduZE1vZGFsX01DT5z07eospMaEA3q5abbcC1AtMyFQ1txhYgDjzNrw/fHC'
			X_STATE =  'eyJnbG9iYWxfUXVlcnlGb3JtX2N0bDAwX1RyaWdnZXJTZWFyY2giOnsiVGV4dCI6IumrmOe6p+WbvuWDjyIsIlNob3dUcmlnZ2VyMSI6dHJ1ZX0sImdsb2JhbF9RdWVyeUZvcm1fY3RsMDBfZGRsQWRkcmVzcyI6eyJYX0l0ZW1zIjpbWyLoi4/lt54iLCLoi4/lt54iLDFdLFsi5ZCI6IKlIiwi5ZCI6IKlIiwxXV0sIlNlbGVjdGVkVmFsdWUiOiLoi4/lt54ifSwiZ2xvYmFsX1F1ZXJ5Rm9ybV9jdGwwMF9kZGxTdHVkeVllYXIiOnsiWF9JdGVtcyI6W1siMjAxOCIsIjIwMTgiLDFdLFsiMjAxOSIsIjIwMTkiLDFdXSwiU2VsZWN0ZWRWYWx1ZSI6IjIwMTgifSwiZ2xvYmFsX1F1ZXJ5Rm9ybV9jdGwwMF9kZGxUZXJtIjp7IlNlbGVjdGVkVmFsdWUiOiIyIiwiWF9JdGVtcyI6W1siMCIsIjAiLDFdLFsiMSIsIjEiLDFdLFsiMiIsIjIiLDFdXX0sImdsb2JhbF9RdWVyeUZvcm1fY3RsMDFfdHh0Q2hvb3NlZENyZWRpdCI6eyJUZXh0IjoiMjAifSwiZ2xvYmFsX1F1ZXJ5Rm9ybV9jdGwwMV90eHRNYXhDcmVkaXQiOnsiVGV4dCI6IjIzIn0sImdsb2JhbF9NYWluUGFuZWxfZ3JpZEFjdFRCYXJfYnRuVmlld011bHRpcGxlQ2hvaWNlT25lIjp7Ik9uQ2xpZW50Q2xpY2siOiJYKCdXbmRNb2RhbF9NQ08nKS5ib3hfc2hvdygnL1RlYWNoaW5nL0NvdXJzZUNob29zZUluZm8vQ29tbWVuY2VkTXVsdGlwbGVDaG9pY2VPbmVDb3Vyc2VMaXN0LmFzcHg/SW5wdXRlZEtleT0lZTklYWIlOTglZTclYmElYTclZTUlOWIlYmUlZTUlODMlOGYmQWRkcmVzcz0lZTglOGIlOGYlZTUlYjclOWUmTWFqb3JUeXBlPSVlNSVhNCVhNyVlNiU5NSViMCVlNiU4ZCVhZSVlNCViOCU4ZSVlNCViYSViYSVlNSViNyVhNSVlNiU5OSViYSVlOCU4MyViZCZZZWFyVGVhbT0yMDE4LTImQ3VycmVudFVzZXJHdWlkPTExNTk5ZWNkLTc4MmEtNDY5NS1hYjlmLTFiYTlkYWYxMzAwYycsJ+afpeeci+WkmumAieS4gOivvueoiycpO3JldHVybiBmYWxzZTsifSwiZ2xvYmFsX01haW5QYW5lbF9HcmlkTGlzdCI6eyJYX1Jvd3MiOnsiVmFsdWVzIjpbWyJTRTA1NDAzYSIsIjxhIGhyZWY9XCJqYXZhc2NyaXB0OjtcIiBvbmNsaWNrPVwiamF2YXNjcmlwdDpYKCYjMzk7V25kTW9kYWwmIzM5OykuYm94X3Nob3coJiMzOTsvVGVhY2hpbmcvQ291cnNlSW5mby9WaWV3QnlDb3Vyc2VJRC5hc3B4P0NvdXJzZUlEPVNFMDU0MDNhJiMzOTssJiMzOTvpq5jnuqflm77lg4/lpITnkIbkuI7liIbmnpAt6K+m57uGJiMzOTspO1wiPumrmOe6p+WbvuWDj+WkhOeQhuS4juWIhuaekDwvYT4iLCIzIiwi6IuP5bee54+tIiwi55m95aSpKC3mmoLml6Dlt6Xlj7ctKSIsIjEtOCDlkagv5ZGo5LqML+S4i+WNiCg277yMN++8jDgpL+aYjuW+t+alvEMyNDBfMS04IOWRqC/lkajkuIkv5LiK5Y2IKDHvvIwy77yMMykv5piO5b635qW8QzI0MCIsIjIwMTktMi0yMSIsIjIwMTktMy00IiwiMTIwIiwiMTIwIiwiPGEgaHJlZj1cImphdmFzY3JpcHQ6O1wiIG9uY2xpY2s9XCJFeHQuZGVmZXIoZnVuY3Rpb24oKXt3aW5kb3cuRXh0Lk1lc3NhZ2VCb3guc2hvdyh7dGl0bGU6JiMzOTvmj5DnpLomIzM5Oyxtc2c6JiMzOTvnoa7lrprpgInor74mIzM5OyxidXR0b25zOkV4dC5NZXNzYWdlQm94Lk9LQ0FOQ0VMLGljb246RXh0Lk1lc3NhZ2VCb3guSU5GTyxmbjpmdW5jdGlvbihidG4pe2lmKGJ0bj09JiMzOTtjYW5jZWwmIzM5Oyl7cmV0dXJuIGZhbHNlO31lbHNle19fZG9Qb3N0QmFjaygmIzM5O2dsb2JhbCRNYWluUGFuZWwkR3JpZExpc3QmIzM5OywmIzM5O0NvbW1hbmQkMCQxMCRTZWxlY3RDb3Vyc2UkJiMzOTspO319fSk7fSwwKTtYLnV0aWwuc3RvcEV2ZW50UHJvcGFnYXRpb24uYXBwbHkobnVsbCwgYXJndW1lbnRzKTtcIj7pgInmi6nmraTor748L2E+Il1dLCJEYXRhS2V5cyI6W1siMjU2OTRkZGEtZWFlNy00NTk3LWE1YjgtNzkwN2RmODlmZGYxIl1dfSwiUmVjb3JkQ291bnQiOjEsIlhfU3RhdGVzIjpbW11dLCJTZWxlY3RlZFJvd0luZGV4QXJyYXkiOltdfX0='
		# 构造搜索表单
		data = {
			'__EVENTTARGET':'global$QueryForm$ctl00$TriggerSearch',
			'__EVENTARGUMENT':'Trigger$2',
			'__VIEWSTATE':__VIEWSTATE,
			'global$QueryForm$ctl00$TriggerSearch': courseName,
			'global$QueryForm$ctl00$ddlAddress':self.userLocation,
			'global$QueryForm$ctl00$ddlStudyYear':self.userYear,
			'global$QueryForm$ctl00$ddlTerm':self.userTerm,
			'X_CHANGED' : 'false',
			'WndModal_Hidden' : 'true',
			'WndModal_MCO_Hidden' : 'true',
			'global_QueryForm_Collapsed' : 'false',
			'global_MainPanel_GridList_Collapsed' : 'false',
			'global_MainPanel_GridList_SelectedRowIndexArray' : '',
			'global_MainPanel_GridList_HiddenColumnIndexArray' : '',
			'global_MainPanel_GridList_RowStates' : '[]',
			'global_MainPanel_Collapsed' : 'false',
			'global_Collapsed' : 'false',
			'WndModal_MCO_Collapsed' : 'false',
			'WndModal_Collapsed' : 'false',
			'X_STATE' : X_STATE,
			'X_AJAX':'false'
		}
		# 搜索课程，获取X_STATE
		response = self.sess.post(chooseCouserUrl, data=data, headers=self.headers)
		result = response.text.encode('utf-8')
		self.writeLogs(result, isPrint=False)
		# with open('f.html', 'w') as f:
		# 	f.write(result)
		searchPattern = re.compile(r'x_state:(.*?),id:', re.S)
		x_stateList = searchPattern.findall(result)
		# for i, item in enumerate(x_state):
		# 	print i, item
		x_state = '{"global_QueryForm_ctl00_TriggerSearch":'+x_stateList[0]+',"global_QueryForm_ctl00_ddlAddress":'+x_stateList[1]+',"global_QueryForm_ctl00_ddlStudyYear":'+x_stateList[2]+',"global_QueryForm_ctl00_ddlTerm":'+x_stateList[3]+',"global_QueryForm_ctl01_txtChoosedCredit":'+x_stateList[4]+',"global_QueryForm_ctl01_txtMaxCredit":'+x_stateList[5]+',"global_MainPanel_gridActTBar_btnViewMultipleChoiceOne":'+x_stateList[9]+',"global_MainPanel_GridList":'+x_stateList[13]+'}'
		# print x_state
		data = {
			'__EVENTTARGET' : 'global$MainPanel$GridList',
			'__EVENTARGUMENT' : 'Command$0$10$SelectCourse$',
			'__VIEWSTATE' : '/wEPDwUKMTg4OTI4NDIxOA8WAh4JbWFqb3JUeXBlBRjlpKfmlbDmja7kuI7kurrlt6Xmmbrog71kGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYNBQZnbG9iYWwFEGdsb2JhbCRRdWVyeUZvcm0FJGdsb2JhbCRRdWVyeUZvcm0kY3RsMDAkVHJpZ2dlclNlYXJjaAUhZ2xvYmFsJFF1ZXJ5Rm9ybSRjdGwwMCRkZGxBZGRyZXNzBSNnbG9iYWwkUXVlcnlGb3JtJGN0bDAwJGRkbFN0dWR5WWVhcgUeZ2xvYmFsJFF1ZXJ5Rm9ybSRjdGwwMCRkZGxUZXJtBSdnbG9iYWwkUXVlcnlGb3JtJGN0bDAxJHR4dENob29zZWRDcmVkaXQFI2dsb2JhbCRRdWVyeUZvcm0kY3RsMDEkdHh0TWF4Q3JlZGl0BRBnbG9iYWwkTWFpblBhbmVsBTVnbG9iYWwkTWFpblBhbmVsJGdyaWRBY3RUQmFyJGJ0blZpZXdNdWx0aXBsZUNob2ljZU9uZQUZZ2xvYmFsJE1haW5QYW5lbCRHcmlkTGlzdAUIV25kTW9kYWwFDFduZE1vZGFsX01DT5z07eospMaEA3q5abbcC1AtMyFQ1txhYgDjzNrw/fHC',
			'global$QueryForm$ctl00$TriggerSearch' : courseName,
			'global$QueryForm$ctl00$ddlAddress' : self.userLocation,
			'global$QueryForm$ctl00$ddlStudyYear' : self.userYear,
			'global$QueryForm$ctl00$ddlTerm' : self.userTerm,
			'X_CHANGED' : 'false',
			'WndModal_Hidden' : 'true',
			'WndModal_MCO_Hidden' : 'true',
			'global_QueryForm_Collapsed' : 'false',
			'global_MainPanel_GridList_Collapsed' : 'false',
			'global_MainPanel_GridList_SelectedRowIndexArray' : 0,
			'global_MainPanel_GridList_HiddenColumnIndexArray' : '',
			'global_MainPanel_GridList_RowStates' : '[]',
			'global_MainPanel_Collapsed' : 'false',
			'global_Collapsed' : 'false',
			'WndModal_MCO_Collapsed' : 'false',
			'WndModalSmall_Collapsed' : 'false',
			'X_STATE' : base64.b64encode(x_state),
			'X_AJAX' : 'true',
		}
		# 线程抢课
		while True:
			self.count += 1
			# 发送抢课需要的POST数据，获取登录后的Cookie(保存在sess里)
			response = self.sess.post(chooseCouserUrl, data=data, headers=self.headers)
			result = response.text.encode('utf-8')
			self.writeLogs(result, isPrint=False)
			try:
				result = re.compile(r'alert\(\'(.*)\'\)',re.S).findall(result)[0]
				# 一个元祖，里面包含该课程的 已选人数/最大人数
				leavingsCourse = re.compile(r',"(\d*)","(\d*)","<a',re.S).findall(x_stateList[13])[0]
			except IndexError:
				self.writeLogs('线程{}：正在抢课【{}】\t结果：未搜索到课程【{}】，请检查：课程名是否正确/或该课程已在您的选课列表中...'.format(index, courseName, courseName), error=True)					
				if self.errorKeepChoose:
					self.writeLogs('线程{}：持续为您抢课...'.format(index, courseName, result))
					threadSleepTime = random.uniform(self.sleepTime[0], self.sleepTime[1])
					self.writeLogs('线程{}：防止被发现，休息{:.2f}秒...'.format(index, threadSleepTime))
					time.sleep(threadSleepTime) # 休息一会儿
				else:
					self.writeLogs('线程{}：关闭...'.format(index))
					break
			else:
				self.writeLogs('线程{}：正在抢课【{}】\t结果：【{}】| {}'.format(index, courseName, result, leavingsCourse))
				# 选课成功，关闭线程
				if result == '选课成功':
					self.writeLogs('线程{}：正在打印已选课程列表...'.format(index))
					self.printStuChoosed() # 打印已选课程信息
					self.writeLogs('线程{}：关闭...'.format(index))
					break# 关闭该线程
				# 满了，继续抢
				elif result == '该课程已选满，请选择其它课程！':
					if self.fullKeepChoose:
						self.writeLogs('线程{}：持续为您抢课...'.format(index, courseName, result))
						threadSleepTime = random.uniform(self.sleepTime[0], self.sleepTime[1])
						self.writeLogs('线程{}：防止被发现，休息{:.2f}秒...'.format(index, threadSleepTime))
						time.sleep(threadSleepTime) # 休息一会儿
					else:
						self.writeLogs('线程{}：关闭...'.format(index))
						break
				else:
					self.writeLogs('线程{}：抢课【{}】时发生错误...错误信息：{}'.format(index, courseName, result))
					self.writeLogs('线程{}：关闭...'.format(index))
					break

	def chooseCourseMultiThread(self, wantedCourseList):
		'''多线程抢课'''
		if self.login():
			courseNum = len(wantedCourseList)
			self.printStuChoosed() # 打印已选课程信息
			self.writeLogs('共检测到{}个任务，正在分配线程处理...'.format(courseNum))
			for i, courseName in enumerate(wantedCourseList):
				thread = threading.Thread(target=self.chooseCourse, args=(i, courseName))
				thread.daemon = False # 这个线程是重要的，在进程退出的时候，等待这个线程退出
				thread.start()

	def writeLogs(self, log, isPrint=True, info=True, error=False):
		if error:
			log = '[ERROR] ' + log
		elif info:
			log = '[INFO] ' + log
		else: 
			pass
		if isPrint:
			print log
		with open('runtime.logs', 'a') as f:
			f.write('['+time.ctime()+']\n'+log+'\n\n')
