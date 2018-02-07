import Netease163Manager


def CreateM3u_inside(m2uPath, playList):
    hFile = open(m2uPath, 'w+', encoding='utf-8')
    hFile.write('#EXTM3U\n')
    lst = [None]
    for iter in playList:
        if iter == None:
            continue
        # print(iter['Path'])
        data = iter['Path'].split('\\')
        length = len(data)
        path = ''
        for i in range(2, length):
            path += data[i]
            if i < length - 1:
                path += '\\'
        hFile.write('#EXTINF:,\n')
        hFile.write(path)
        hFile.write('\n')
    hFile.close()
    pass


# 创建歌词文件
def CreateLRC(netList):
    for it in netList:
        id = str(it['id'])
        path = it['Path']
        res = Netease163Manager.getMusicLyric(id, path)
        # print('%s %s' % (path, str(res)))
    pass


netList, ErrorList = Netease163Manager.getMusicAbsPathList('H:\\MUSIC\\女声古风', '920755371')
CreateLRC(netList)