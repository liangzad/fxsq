"""

time: 2023.9.6
cron: 0 0 * * *
new Env('json格式化');

"""

import json
import time
import pathlib


def loadFile(filePath):
    with open(filePath, 'r', encoding='utf-8') as load_f:
        load_dict = json.load(load_f)  # 将json读取
    # print('tomato信息读取成功')
    # print(load_dict)
    user_arr = load_dict.get('userList')
    # print(user_arr)
    # 返回用户信息的数组
    return user_arr


def writeFile(filePath, json_dic):
    # filePath 文件路径
    # json_dic 字典类型的json文件
    try:
        with open(filePath, 'w+', encoding='utf-8') as f:
            json.dump(json_dic, f, indent=4, ensure_ascii=False)
        print('tomato信息写入成功')
        return 1
    except Exception:
        print('写入文件异常')
        return 0


# 构建一个pathlib.Path()对象
# 指定一个目录起始点："F:/path_test"
p = pathlib.Path(".")
# 只遍历当前目录
filePath_list = []
ret = p.glob("tomato_read.json")
for item in ret:
    print(item)
    filePath_list.append(item)

# 读取所有tomato.json文件
for filePath in filePath_list:
    print(filePath)
    userList = loadFile(filePath)
    new_userList = []
    for user_data in userList:
        name = user_data.get('name')
        sleep_finished = user_data.get('sleep_finished')
        next_open_treasure_box = user_data.get('next_open_treasure_box')
        title = user_data.get('title')
        formatted_time = time.strftime('%m-%d %H:%M:%S')  # 获取当前时间
        if next_open_treasure_box is None:
            next_open_treasure_box = 0
        temp = {
            "name": name,
            "amount": 0,
            "time": formatted_time,
            "sign": 0,
            "lottery": 0,
            "prev_task_timeStamp": 0,
            "treasure_task_cnt": 0,
            "shopping_earn_money_cnt": 15,
            "browse_products_cnt": 10,
            "excitation_ad_cnt": 10,
            "next_readComic": 1,
            "daily_play_game_cnt": 5,
            "next_readNovel": 0.5,
            "next_short_video": 0.5,
            "next_listenNoval": 0.5,
            "meal_finished": -1,
            "sleep_finished": sleep_finished,
            "excitation_ad_repeat_cnt": 96,
            "next_open_treasure_box": next_open_treasure_box,
            "title": title
        }
        new_userList.append(temp)

    print(new_userList)
    new_userList_json = {
        "userList": new_userList
    }
    writeFile(filePath, new_userList_json)
