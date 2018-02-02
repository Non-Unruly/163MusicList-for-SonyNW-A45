import json
import os
import os.path
import requests

FileFormat = ['mp3', "wma", 'flac', 'wav', 'aac', 'dsd', 'ape', 'mqa', 'MP3', 'WMA', 'FLAC', 'WAV', 'AAC', 'DSD', 'APE',
              'MQA']
MusicNameList = []

# 可能符号全部升级为全角
def CharacterCodeUnify(data):
    newData = ''
    for ch in data:
        if ch == u'/' or ch == u'(' or ch == u')' or ch == u':':
            num = ord(ch) + 65248
            ch = chr(num)
        newData += ch
    return newData


# 比较播放列表中的音频信息与本地文件是否一致
def compare(netInfo, localName):
    song = CharacterCodeUnify(netInfo['Song'])
    singer = CharacterCodeUnify(netInfo["Singer"])
    if song in localName and singer in localName:
        return True
    else:
        #data1 = " @@%s %s |" % (netInfo['Singer'], netInfo['Song'])
        #data2 = "%s %s \n" % (singer, song)
        #data3 = "%s || " % (localName)
        #hFile = open("d:\\log.txt", "a+", encoding="UTF-8")
        #hFile.write(data3)
        #hFile.write(data1)
        #hFile.write(data2)
        #hFile.close()
        return False


# 获取歌单详细信息
def requestGetList(id):
    url = "http://music.163.com/api/playlist/detail?id=" + id
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Accept-Language': 'zh-CN,zh;q=0.8',
               'User-Agent': 'BM_Recluse , Python-requests',
               'Upgrade-Insecure-Requests': '1',
               'Connection': 'keep-alive',
               'Host': 'music.163.com'}
    #    print("url: " + url)
    data = requests.get(url, headers=headers)
    print(data.status_code)
    print(data.headers, end="\n\n\n")
    return data.text


# 获取歌单内的全部歌曲的本地文件名
def GetMusicNameList(id):
    # data=requestGetList(id)
    data = requestGetList(id)
    listJson = json.loads(data)
    list = listJson['result']['tracks']
    for item in list:
        Song = item['name']
        Singer = item['artists'][0]['name']
        Singer = CharacterCodeUnify(Singer)
        Song = CharacterCodeUnify(Song)
        # print("Sone:%s  Singer:%s" % (Song, Singer))
        # obj = "%s - %s" % (Singer, Song)
        obj = {"Song": Song, "Singer": Singer}
        MusicNameList.append(obj)
    # print(len(MusicNameList))
    # print(MusicNameList)
    return MusicNameList


# 获取指定目录下存在歌单内的音频文件
def GetExistsFileAbsPathList(path):
    FileAbsPathList = []
    for p in os.listdir(path):
        thisPath = path + "\\" + p
        if os.path.isfile(thisPath):
            # 如果是文件
            i = -1
            format = ''
            while True:
                if p[i] != '.':
                    format = p[i] + format
                    i = i - 1
                else:
                    break
            name = p[0:len(p) - len(format)]
            name = CharacterCodeUnify(name)
            if format in FileFormat:
                isMatching = False
                for iter in MusicNameList:
                    if compare(iter, name):
                        FileAbsPathList.append(thisPath)
                        isMatching = True
                        break
                    else:
                        continue
                    pass
                if not isMatching:
                    print("  Error Name:" + p)
                    pass
            else:
                print("   Error Format:" + p)
                pass
            pass
        elif os.path.isdir(thisPath):
            # 如果是目录
            FileAbsPathList.extend(GetExistsFileAbsPathList(thisPath))
            pass
    return FileAbsPathList

#获取歌单中存在的本地音频文件的绝对路径列表
#DirPath本地音频目录路径
#MusicListId歌单ID
def getMusicAbsPathList(DirPath,MusicListId):
    MusicNameList = GetMusicNameList(MusicListId)
    print("MusicNameList:")
    for it in MusicNameList:
        print(it)
    PathList = GetExistsFileAbsPathList(path)
    print(len(PathList))
    for it in PathList:
        print(it)
    return PathList