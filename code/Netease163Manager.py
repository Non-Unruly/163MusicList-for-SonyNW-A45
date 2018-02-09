import json
import os
import os.path

import requests

FileFormat = ['mp3', "wma", 'flac', 'wav', 'aac', 'dsd', 'ape', 'mqa', 'MP3', 'WMA', 'FLAC', 'WAV', 'AAC', 'DSD', 'APE',
			  'MQA']


# MusicNameList = []
# ErrorList = []  # 未能成功匹配的歌曲信息[列表内的标号，歌曲名]


# 分割文件名和后缀名
def splitNameFormat (path):
	slice = path.split('.')
	num = len(slice)
	name = '.'.join(slice[0:num - 1])
	format = slice[-1]
	return name, format
	pass


# 半角符号全部升级为全角
def characterCodeUnify (data):
	newData = ''
	for ch in data:
		if ch == u'/' or ch == u'(' or ch == u')' or ch == u':':
			num = ord(ch) + 65248
			ch = chr(num)
		newData += ch
	newData = newData.lower()  # 统一小写匹配
	newData = ''.join(newData.split(' '))
	return newData


# 比较播放列表中的音频信息与本地文件是否一致
def compare (netInfo, localName):
	song = characterCodeUnify(netInfo['Song'])
	singer = characterCodeUnify(netInfo["Singer"])
	if song in localName and singer in localName:
		return True
	else:
		return False


# 获取歌单详细信息
def requestGetList (id):
	url = "http://music.163.com/api/playlist/detail?id=" + id
	headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			   'Accept-Language': 'zh-CN,zh;q=0.8',
			   'User-Agent': 'BM_Recluse , Python-requests',
			   'Upgrade-Insecure-Requests': '1',
			   'Connection': 'keep-alive',
			   'Host': 'music.163.com'}
	#    print("url: " + url)
	data = requests.get(url, headers = headers)
	info = json.loads(data.text)
	res = info.get('result', None)
	ListName = None
	Creator = None
	if res == None or res['creator'] == None:
		return False, ListName, Creator
	ListName = res['name']
	Creator = res['creator']['nickname']
	return info, ListName, Creator


# 获取歌单内的全部歌曲的本地文件名
def getMusicNameList (data):
	MusicNameList = []
	listJson = data
	list = listJson['result']['tracks']
	for item in list:
		Song = item['name']
		Singer = item['artists'][0]['name']
		Singer = characterCodeUnify(Singer)
		Song = characterCodeUnify(Song)
		SongID = item['id']
		obj = {"Song": Song, "Singer": Singer, "id": SongID}
		MusicNameList.append(obj)
	return MusicNameList


# 获取指定目录下存在歌单内的音频文件
def getExistsFileAbsPathList (path, MusicNameList):
	FileAbsPathList = []
	for p in os.listdir(path):
		thisPath = path + "/" + p
		if os.path.isfile(thisPath):
			# 如果是文件
			name, format = splitNameFormat(p)
			name = characterCodeUnify(name)
			if format in FileFormat:
				isMatching = False
				num = len(MusicNameList)
				No = 0
				for No in range(num):
					if compare(MusicNameList[No], name):
						FileAbsPathList.append(
							{"No": No, "Path": thisPath, "id": MusicNameList[No]['id'], 'Name': str('%s - %s') % (
								MusicNameList[No]['Singer'], MusicNameList[No]['Song'])})  # 增加歌单顺序Key='No'
						isMatching = True
						break
					else:
						continue
				if not isMatching:
					# print("  Error Name:" + p)
					pass
			else:
				# print("   Error Format:" + p)
				pass
			pass
		elif os.path.isdir(thisPath):
			# 如果是目录
			FileAbsPathList.extend(getExistsFileAbsPathList(thisPath, MusicNameList))
			pass
	return FileAbsPathList


# 根据云歌单顺序进行本地歌单重排序
def sortAbsPathList (unorderedPathList, MusicNameList):
	ErrorList = []
	length = len(MusicNameList)
	orderedPathList = length * [None]
	for iter in unorderedPathList:
		No = iter['No']
		orderedPathList[No] = iter

	# 获取未能成功匹配的歌曲列表
	for i in range(0, length):
		if orderedPathList[i] == None:
			name = MusicNameList[i]['Singer'] + ' - ' + MusicNameList[i]['Song']
			ErrorList.append({'No': i, 'Name': name})

	return orderedPathList, ErrorList


# 获取歌词lyric
# 参数：歌曲id（网易云ID）
# 参数：音频文件地址
def getMusicLyric (id, path):
	url = 'http://music.163.com/api/song/lyric?os=pc&id=' + id + '&lv=1'
	headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			   'Accept-Encoding': 'gzip, deflate, sdch',
			   'Accept-Language': 'zh-CN,zh;q=0.8',
			   'User-Agent': 'BM_Recluse , Python-requests',
			   'Upgrade-Insecure-Requests': '1',
			   'Connection': 'keep-alive',
			   'Host': 'music.163.com'}
	data = requests.get(url, headers = headers)
	# print(data.text)
	res = json.loads(data.text)
	isNoLrc = res.get('nolyric', False)
	if isNoLrc:
		return False, ''
	lrc = res['lrc']['lyric']
	name, _format = splitNameFormat(path)
	lrcPath = name + '.lrc'
	hFile = open(lrcPath, "w+", encoding = 'utf-8')
	hFile.write(lrc)
	hFile.close()
	return True, lrcPath
	pass


# 云歌单与本地音频文件进行匹配，返回匹配成功的音频地址列表和未匹配到的歌曲列表
# DirPath本地音频存放目录
# MusicListId云歌单Id
def GetNeteasMusicRes (id, musciDir, isLrc):
	orderedPathList = None
	ErrorList = None
	res = False
	data, ListName, Creator = requestGetList(id)
	if data == False:
		return res, orderedPathList, ErrorList, ListName, Creator
	res = True
	MusicNameList = getMusicNameList(data)
	unorderedPathList = getExistsFileAbsPathList(musciDir, MusicNameList)
	orderedPathList, ErrorList = sortAbsPathList(unorderedPathList, MusicNameList)

	return res, orderedPathList, ErrorList, ListName, Creator
