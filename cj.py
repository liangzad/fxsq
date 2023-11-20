"""

time: 2023.9.6
cron: 1 0 * * *
new Env('json创建');

"""

import json
import os.path
import json
import time
import pathlib

if os.name == 'nt':
    try:
        from dotenv import load_dotenv

        load_dotenv(dotenv_path='tomato.env', verbose=True)
    except EnvironmentError:
        print(EnvironmentError)

tomato_read_json = 'tomato_read.json'
cookies = os.getenv('tomato_read')
cookie_arr = cookies.split('\n')

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


def tomato_read_json_init():
    if os.path.exists(tomato_read_json):
        print('存在[tomato_read.json]文件，退出执行')
        exit(-1)
    else:
        print('无[tomato_read.json]自动创建')
        new_userList = []
        for count in range(len(cookie_arr)):
            sleep_finished = None
            formatted_time = time.strftime('%m-%d %H:%M:%S')  # 获取当前时间
            current_time = time.strftime('%H:%M:%S')
            if '05:00:00' <= current_time <= '08:00:00':
                sleep_finished = 'end_sleep'
            elif '22:00:00' <= current_time <= '23:45:00':
                sleep_finished = 'start_sleep'
            elif '23:45:00' < current_time <= '23:59:59' or '00:00:00' <= current_time <= '04:59:59':
                sleep_finished = 'start_sleep'
            elif '08:00:00' < current_time < '22:00:00':
                sleep_finished = 'end_sleep'
            temp = {
                "name": "none",
                "amount": 0,
                "time": formatted_time,
                "sign": 0,
                "lottery": 0,
                "prev_task_timeStamp": 0,
                "treasure_task_cnt": 0,
                "shopping_earn_money_cnt": 0,
                "browse_products_cnt": 0,
                "excitation_ad_cnt": 0,
                "next_readComic": 1,
                "daily_play_game_cnt": 0,
                "next_readNovel": 0.5,
                "next_listenNoval": 0.5,
                "meal_finished": -1,
                "sleep_finished": sleep_finished,
                "title": "none"
            }
            new_userList.append(temp)

        new_userList_json = {
            "userList": new_userList
        }
        writeFile(tomato_read_json, new_userList_json)


tomato_read_json_init()
