import json
import os
import os.path
import requests
import StateCode
import time


# 歌曲列表
# singer歌手 song歌曲名 id歌曲id path本地目录 no歌曲编号


# 获取歌单列表
# id - 歌单id
# 返回 歌单信息
def RequestList (id, callback):
	id = str(id)
	url = "http://music.163.com/api/playlist/detail?id=" + id
	headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			   'Accept-Language': 'zh-CN,zh;q=0.8',
			   'User-Agent': 'BM_Recluse , Python-requests',
			   'Upgrade-Insecure-Requests': '1',
			   'Connection': 'keep-alive',
			   'Host': 'music.163.com'}
	data = requests.get(url, headers = headers)
	if data.status_code != 200:
		return StateCode.CallBackCode.REQUEST_ERROR
	info = json.loads(data.text)
	res = info.get('result', None)
	ListName = None
	Creator = None
	if res == None or res['creator'] == None:
		callback(StateCode.CallBackCode.UNKNOW_ERROR, None)
		return
	ListName = res['name']  # 歌单名称
	Creator = res['creator']['nickname']  # 歌单创建者
	m_MusicList = {'listname': ListName, 'creator': Creator, 'list': []}
	lst = res['tracks']
	i = 0
	for it in lst:
		m_MusicList['list'].append(
			{'song': it['name'], 'singer': it['artists'][0]['name'], 'id': it['id'], 'path': '', 'no': i, 'lrc': ''})
		i = i + 1
	callback(StateCode.CallBackCode.MUSIC_LIST_RETURN, m_MusicList)
	pass


def RequestLrc (list, callback):
	for it in list:
		try:
			if len(it['path']) > 0:
				url = 'http://music.163.com/api/song/lyric?os=pc&id=' + str(it['id']) + '&lv=1'
				headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
						   'Accept-Encoding': 'gzip, deflate, sdch',
						   'Accept-Language': 'zh-CN,zh;q=0.8',
						   'User-Agent': 'BM_Recluse , Python-requests',
						   'Upgrade-Insecure-Requests': '1',
						   'Connection': 'keep-alive',
						   'Host': 'music.163.com'}
				data = requests.get(url, headers = headers)
				res = json.loads(data.text)
				isNoLrc = res.get('nolyric', False)
				if isNoLrc:
					callback(StateCode.CallBackCode.MUSIC_LRC_NONE, it)
					continue
				lrc = res['lrc']['lyric']
				lrc = disposeLrc(lrc)
				name, _format = splitNameFormat(it['path'])
				lrcPath = name + '.lrc'
				hFile = open(lrcPath, "w+", encoding = 'utf-8')
				hFile.write(lrc)
				hFile.close()
				it['lrc'] = lrcPath
				callback(StateCode.CallBackCode.MUSIC_LRC_RETURN, it)
			else:
				callback(StateCode.CallBackCode.MUSIC_LRC_NONE, it)
				continue
		except BaseException as e:
			callback(StateCode.CallBackCode.MUSIC_LRC_ERROR, {'music': it, 'info': e})
	callback(StateCode.CallBackCode.MUSIC_LRC_FINISHED, None)
	return


# 处理歌词字符，保证walkman能正确识别
def disposeLrc (lrc):
	data = ''
	i = 0
	while i < len(lrc):
		time = ''
		if lrc[i] == '[':
			i += 1
			while lrc[i] != ']':
				time += lrc[i]
				i += 1
			if ':' in time and '.' in time:
				if len(time) == 9:
					time = time[0:8]
			data += '[' + time + ']'
		else:
			data += lrc[i]
		i += 1
	return data


def FindLocalMusic (path, list, callback):
	try:
		for p in os.listdir(path):
			thisPath = path + '/' + p
			# print('---' + thisPath)
			if (os.path.isdir(thisPath)):
				# 如果是目录
				FindLocalMusic(thisPath, list, callback)
			elif (os.path.isfile(thisPath)):
				# 如果是文件
				#callback(StateCode.CallBackCode.MUSIC_SERACH_CURRENT, p)
				name, format = splitNameFormat(p)
				if format in FileFormat:
					filename = characterCodeUnify(name)
					for it in list:
						name_in_list = characterCodeUnify(str("%s-%s" % (it['singer'], it['song'])))
						if name_in_list == filename or (
								characterCodeUnify(it['singer']) in filename and characterCodeUnify(
								it['song']) in filename):
							#print(thisPath)
							callback(StateCode.CallBackCode.MUSIC_PATH_RETURN, {'no': it['no'], 'path': thisPath})
							break
		callback(StateCode.CallBackCode.MUSIC_PATH_END, None)
	except BaseException as e:
		print(e)
	return


FileFormat = ['mp3', "wma", 'flac', 'wav', 'aac', 'dsd', 'ape', 'mqa', 'MP3', 'WMA', 'FLAC', 'WAV', 'AAC', 'DSD', 'APE',
			  'MQA']


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
