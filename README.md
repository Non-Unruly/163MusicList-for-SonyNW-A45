# 2022-12-18
代码废弃

# 163MusicList-for-SonyNW-A45

导出网易云音乐的歌单，生成索尼NW-A45播放器可识别的歌单(Export playlist from 163music and create playlist for sony nw a45)

索尼 NW A45播放器不能自己创建歌单，必须使用索尼官方的Music Center for PC才能管理歌单，远没有各种PC网络播放器人性化

我用常听的歌单都在网易云上，就试着用导出网易云的歌单，然后处理成索尼A45的歌单传输到播放器上
 
 
第一阶段：先从网易云导出歌单详细信息

第二阶段：生成索尼可识别的歌单，并筛除掉并不存在A45上的音频文件

第三阶段：将本机上已下载的网易云音频文件和歌单一通输出到A45上

第四阶段：自动从网易云服务器上匹配歌词信息并导入A45上


Python3.6
Moudle:
1.requests(cmd: pip3 install requests)
2.requests(cmd: pip3 install PyQt5)
