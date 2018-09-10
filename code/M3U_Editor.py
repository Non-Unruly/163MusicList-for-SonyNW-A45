def LoadM3U(path):
    try:
        path_item = path.split("\\")
        path_item = path_item[0:-1]
        first_path = "\\".join(path_item) + "\\"

        m3uFile = open(path, "r", encoding="utf-8")
        data = ""
        for line in m3uFile.readlines():
            data += line.replace(",", "").replace("\r", "").replace("\n", "").replace(":", "")
        tmpLst = data.split("#EXTINF")

        lst = []
        for item in tmpLst:
            if item == "#EXTM3U" or item == "":
                continue
            lst.append({"absolute": first_path + item, "relative": item})
        return lst
    except Exception as e:
        print("function -LoadM3U- Error: " + str(e))
        return False


# lst = LoadM3U("C:\\Users\\Administrator\\Desktop\\最近在听\\最近在听.m3u")
# for it in lst:
#     print(it)
