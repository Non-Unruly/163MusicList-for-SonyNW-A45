import Netease163Manager


def CreateM3u_inside (m2uPath, playList):
	hFile = open(m2uPath, 'w+', encoding = 'utf-8')
	hFile.write('#EXTM3U\n')
	lst = [None]
	for iter in playList:
		if iter == None:
			continue
		print('---' + iter['Path'])
		data = iter['Path'].split('\\')
		length = len(data)
		path = ''
		for i in range(2, length):
			path += data[i]
			if i<length-1:
				path += '\\'
		hFile.write('#EXTINF:,\n')
		hFile.write(path)
		hFile.write('\n')
	hFile.close()
	pass


# netList,ErrorList = Netease163Manager.getMusicAbsPathList('E:\\Music', '111007305')
# CreateM3u_inside('d:\\list.m3u', netList)
