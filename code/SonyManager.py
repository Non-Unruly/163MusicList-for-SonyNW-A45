import Netease163Manager
import shutil
import StateCode


def CreateM3u_inside (m3uPath, playList, listname, callback):
	try:
		illegal = """/\"?|:<>*"""
		filename = ''
		for i in listname:
			if i in illegal:
				continue
			else:
				filename += i
		hFile = open(m3uPath + '/' + filename + '.m3u', 'w+', encoding = 'utf-8')
		hFile.write('#EXTM3U\n')
		lst = [None]
		for iter in playList:
			if iter == None:
				continue
			# print(iter['Path'])
			data = iter['path'].split('/')
			length = len(data)
			path = ''
			for i in range(2, length):
				path += data[i]
				if i < length - 1:
					path += '/'
			hFile.write('#EXTINF:,\n')
			hFile.write(path)
			hFile.write('\n')
		hFile.close()
		callback(StateCode.CallBackCode.PLAYER_M2U_FINISHED, None)
	except BaseException as e:
		print(e)
		callback(StateCode.CallBackCode.UNKNOW_ERROR, None)
	return


def CopyMusic (list, path, callback):
	if len(list) <= 0:
		return
	try:
		for it in list:
			musicname = it['path'].split('/')[-1]
			lrcname = it['lrc'].split('/')[-1]
			print(path + '/' + musicname)
			shutil.copyfile(it['path'], path + '/' + musicname)
			if len(it['lrc']) > 0:
				shutil.copyfile(it['lrc'], path + '/' + lrcname)
			callback(StateCode.CallBackCode.MUSIC_COPY_FILE, it)
	except BaseException as e:
		callback(StateCode.CallBackCode.MUSIC_COPY_ERROR, str(e))
		return
	callback(StateCode.CallBackCode.MUSIC_COPY_FINISHED, None)
	return

# netList, ErrorList = Netease163Manager.getMusicAbsPathList('H:\\MUSIC\\女声古风', '920755371')
# CreateLRC(netList)
