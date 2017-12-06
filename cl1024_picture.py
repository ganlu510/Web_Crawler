# -*- coding:utf-8 -*-
#   文件：cl1024_pciture.py              #
#   版本：1.2                            #
#   邮箱：ganlu510@126.com               #
#   日期：2017-11-11                     #
#   环境：Python 3.5                     #
#   功能：将网站的MM图片分目录存储到本地 #
#----------------------------------------#

from lxml import html
import requests,re,os,threading,time,random

UA = [
	'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',
	'Mozilla/5.0 (iPad; CPU OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3',
	'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
	'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36',
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20'
]

header = {
	'User-Agent':random.choice(UA),
	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
	'Accept-Encoding':'gzip, deflate',
	'Referer':'http://t66y.com/index.php',
	'Connection':'close',
}

requests.adapters.DEFAULT_RETRIES = 5
s = requests.Session()
postdata = {'validate':''}
num = 1

class download_thread(threading.Thread):
	'''创建继承于threading.Thread的子类'''
	def __init__(self,file_name,img_url,img_name):
		threading.Thread.__init__(self)
		self.file_name = file_name
		self.img_url = img_url
		self.img_name = img_name
	'''把要执行的代码写到run函数里面,线程在创建后会直接调用run函数中的代码块'''
	def run(self):
		save_img(self.file_name,self.img_url,self.img_name)

def get_html(url):
	''' 1.请求页面并判断响应码，如果是非200ok，那么休眠6秒后再重新请求一次
		2.捕捉页面请求的任何异常，并重新请求直至页面请求成功
	'''
	try:
		r = s.get(url=url,headers=header,timeout=12)
		if r.status_code == 404:
			print(' %s 响应状态码非200 OK,正在重试中......' % url)
			time.sleep(6)
			r = s.get(url=url,headers=header,timeout=15)
		global num
	except Exception as err:
		print(err,'\n请求 %s 失败，正在重试中......' % url)
		time.sleep(3)
		while True:
			try:
				r = s.get(url=url,headers=header,timeout=15)
				if r.status_code == 404:
					print(' %s 响应状态码非200 OK,正在重试中......' % url)
					time.sleep(6)
					r = s.get(url=url,headers=header,timeout=15)
			except Exception as err:
				print(err,'\n请求重试 %s 继续失败，继续重试中......' % url)
				time.sleep(3)
			else:
				r.encoding = 'GB18030'
				if r.text.find('404 Not Found') != -1:
					print(' %s 重试失败！放弃访问！' % url,r)
					return r.text
				else:
					print('请求重试 %s 成功！' % ('【'+str(num)+'】'+ url),r)
					num += 1
					return r.text
	else:
		r.encoding = 'GB18030'
		if r.text.find('404 Not Found') != -1:
			print(' %s 重试失败！放弃访问！' % url,r)
			return r.text
		else:
			print(' %s 访问成功！' % ('【'+str(num)+'】'+ url),r)
			num += 1
			return r.text

def list_page(url):
	'''获取每个页面（page1、page2、page n...）中主题条目的链接，使用了xpath和正则表达式相结合的方法'''
	page = get_html(url)
	tree = html.fromstring(page)
	pages_url = re.findall(r'htm_data/16/17\d+/\d{7}\.html',str(tree.xpath('//h3/a/@href')))
	for i in range(len(pages_url)):
		pages_url[i] = 'http://cl.5fy.xyz/'+pages_url[i]
		#get_html(pages_url[i])
	return pages_url

def get_page_html(url):
	''' 1.主题中图片名称、链接的处理
		2.根据主题名称创建目录，已经下载过的图片不会重复下载
		3.使用多线程下载图片
	'''
	pages = list_page(url)
	for page in pages:
		page = get_html(page)
		tree = html.fromstring(page)
		title_name = tree.xpath('//h4/text()')
		if len(title_name) != 0:
			file_name = title_name[0].replace(':','_')\
									 .replace('?','_')\
									 .replace('<','(')\
									 .replace('>',')')\
									 .replace('"',' ')\
									 .replace('*','_')\
									 .replace('\u301c','')\
									 .replace('\xa0','_')
		else:
			file_name = None
			continue
		img_url_list = tree.xpath('//input/@src')
		if not os.path.exists('D:\\Download\\Pictrue\\'+file_name):
			try:
				os.makedirs('D:\\Download\\Pictrue\\' + file_name)
				os.chdir('D:\\Download\\Pictrue\\' + file_name)
				print('D:\Download\Pictrue\%s 主题目录创建成功！' % file_name)
			except Exception as err:
				print('主题目录创建失败！','\n'+err)
				continue
		else:
			print('D:\Download\Pictrue\%s 主题目录已存在！' % file_name)
		for img_url in img_url_list:
			img_name = img_url.split('/')[-1].translate(str.maketrans('<>?=&','____.'))
			if not os.path.isfile('D:\\Download\\Pictrue\\' + file_name+ '\\' + img_name):
				thread = download_thread(file_name,img_url,img_name)
				thread.start()
				time.sleep(1.5)
			else:
				print(img_name+' >>> 该图片已经下载过了！')
		print('该主题共有 %s 张图片!' % len(img_url_list))
		time.sleep(5)

def save_img(file_name,img_url,img_name):
	'''图片下载处理，如果图片url请求失败会重新请求一次'''
	with open('D:\\Download\\Pictrue\\' + file_name + '\\' + img_name,'wb') as file:
		print('正在使用线程 %s 下载：' % threading.current_thread().name + file_name +' >>> '+ img_name)
		try:
			file.write(s.get(img_url,headers=header,timeout=15).content)
			print('线程 %s 下载完成！' % threading.current_thread().name)
		except Exception as err:
			print(err,'\n'+img_url+' >>> URL请求失败,正在重新下载......')
			time.sleep(3)
			try:
				file.write(s.get(img_url,headers=header,timeout=18).content)
				print('线程 %s 重新下载完成！' % threading.current_thread().name)
			except Exception as err:
				print(err,'\n'+img_url+' >>> URL请求继续失败,放弃下载......')

if __name__ == '__main__':
	''' 1.爬取过于频繁会导致ip访问受限制，之后访问需要输入验证码
		2.根据不同网络环境判断访问是否需要输入验证码
		3.验证码保存在代码所在目录，并需要手动输入
	'''
	global r
	r = s.get('http://cl.5fy.xyz/index.php',headers=header,timeout=12)
	r.encoding = 'GB18030'
	#print(r,'\n'+r.text)
	if r.text.find('url=codeform.php') != -1:
		with open('code.png', 'wb') as file:
			print('正在下载验证码图片......\n请到 %s 目录找到code.png并手动输入！' % os.path.abspath('code.png'))
			file.write(s.get('http://cl.5fy.xyz/require/codeimg.php',headers=header,timeout=15).content)
			file.close()
		code = input('请输入验证码：')
		postdata['validate'] = code
		r = s.post('http://cl.5fy.xyz/codeform.php',headers=header,data=postdata)
		r.encoding = 'GB18030'
		while r.text.find('输入有误') != -1:
			print('验证码输入有误！')
			with open('code.png', 'wb') as file:
				file.write(s.get('http://cl.5fy.xyz/require/codeimg.php',headers=header,timeout=15).content)
				file.close()
			code = input('请重新输入验证码：')
			postdata['validate'] = code
			r = s.post('http://cl.5fy.xyz/codeform.php',headers=header,data=postdata)
			r.encoding = 'GB18030'
		for index in range(100):
			index += 1
			url = 'http://cl.5fy.xyz/thread0806.php?fid=16&search=&page='+str(index)
			get_page_html(url)
			time.sleep(3)
	else:
		for index in range(100):
			index += 1
			url = 'http://cl.5fy.xyz/thread0806.php?fid=16&search=&page='+str(index)
			get_page_html(url)
			time.sleep(3)
