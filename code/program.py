import json
import os
import os.path

import requests

FileFormat = ['mp3', "wma", 'flac', 'wav', 'aac', 'dsd', 'ape', 'mqa']
MusicNameList = []


def CharacterCodeUnify(data):
    newData = u""
    for ch in data:
        if ch == u'/' or ch == u'(' or ch == u')':
            num = ord(ch) + 65248
            ch = chr(num)
        newData += ch
    return newData


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
        Song = ''.join(Song.split())
        Singer = ''.join(Singer.split())
        Singer = CharacterCodeUnify(Singer)
        Song = CharacterCodeUnify(Song)
        # print("Sone:%s  Singer:%s" % (Song, Singer))
        # obj = "%s - %s" % (Singer, Song)
        obj = {"Song": Song, "Singer": Singer}
        MusicNameList.append(obj)
    # print(len(MusicNameList))
    # print(MusicNameList)
    return MusicNameList


path = "d:\\Mr.Shi\\163music"


# 获取指定目录下存在歌单内的音频文件
def GetExistsFileAbsPathList(path):
    FileAbsPathList = []
    for p in os.listdir(path):
        thisPath = path + "\\" + p
        if os.path.isfile(thisPath):
            # 如果是文件
            content = p.split('.')
            first = content[0]  # 文件名
            last = content[1]  # 文件格式
            SandS = first.split(' - ')
            singer = SandS[0]  # 本地音频的歌曲名
            song = SandS[1]  # 本地音频的演唱者（存在多个演唱者）
            print("%s|%s|%s" % (singer, song, last))
            if (last in FileFormat):
                # 音频格式满足条件
                isMatching = False
                for it in MusicNameList:
                    _song = it['Song']
                    _singer = it['Singer']
                    if song == _song and _singer in singer:
                        isMatching = True
                        break
                if isMatching:
                    FileAbsPathList.append(thisPath)
                else:
                    print("  Error of name:" + thisPath)
            else:
                print("  Error of format:" + thisPath)
            pass
        elif os.path.isdir(thisPath):
            # 如果是目录
            FileAbsPathList.extend(GetExistsFileAbsPathList(thisPath))
            pass
    return FileAbsPathList


MusicNameList = GetMusicNameList("2073337416")
print("MusicNameList:")
for it in MusicNameList:
    print(it)
print("*************")
PathList = GetExistsFileAbsPathList(path)
print("#############")
print(len(PathList))
for it in PathList:
    print(it)
