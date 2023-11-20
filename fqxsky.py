import json
import os
import random
import re
import time
import requests

wait_time_range = tuple ( map ( int, os.environ.get ( 'FQYC', '5,10' ).split ( ',' ) ) )
time_range = int ( os.environ.get ( 'BFYC', 3 ) )

if os.name == 'nt':
    from dotenv import load_dotenv

    try:
        load_dotenv ( dotenv_path='fanqie.env', verbose=True )
    except EnvironmentError:
        print ( EnvironmentError )

cookies = os.getenv ( 'tomato_read' )
filePath = 'tomato_read.json'
delay_minutes = 10  # 10分钟一次
exec_read = 1
limit_second = 275
excitation_ad_read_gain_mode = 1
s = requests.session ()
proxies = {
    "http": None,
    "https": None,
}
s.proxies = proxies
s.keep_alive = False

if 'tomato_read' in os.environ:
    cookies = os.getenv ( 'tomato_read' )
else:
    print ( "变量[tomato_read]不存在,请设置[tomato_read]变量后运行" )
    exit ( -1 )

if os.path.exists ( filePath ):
    pass
else:
    print ( "文件[tomato_read.json]不存在,请运行[json创建]进行创建json！" )
    exit ( -1 )


def loadFile(filePath):
    with open ( filePath, 'r', encoding='utf-8' ) as load_f:
        load_dict = json.load ( load_f )  # 将json读取
    # print('tomato信息读取成功')
    # print(load_dict)
    user_arr = load_dict.get ( 'userList' )
    # print(user_arr)
    # 返回用户信息的数组
    return user_arr


def writeFile(filePath, json_dic):
    # filePath 文件路径
    # json_dic 字典类型的json文件
    try:
        with open ( filePath, 'w+', encoding='utf-8' ) as f:
            json.dump ( json_dic, f, indent=4, ensure_ascii=False )
        print ( 'tomato信息写入成功' )
        return 1
    except Exception:
        print ( '写入文件异常' )
        return 0


userList = loadFile ( filePath )
new_userList = []


class tomato ():
    sdk_version = '2'

    flame_token = ''
    task_signToken = ''
    task_openTreasureToken = ''
    task_openTreasureVideoToken = ''
    task_adToken = ''
    treasure_chest_timestamp = 0
    ad_timestamp = 0
    amount = 0
    lottery_cnt = 0
    taskId = {}
    excitation_ad_repeat_cnt = None
    next_open_treasure_box = None

    def __init__(self, cookie1):

        self.task_url = cookie1.split ( "#" )[0]
        self.cookie = cookie1.split ( "#" )[1]
        self.argus = cookie1.split ( "#" )[2]
        self.ladon = cookie1.split ( "#" )[3]
        self.ua = cookie1.split ( "#" )[4]
        self.passport_sdk_version = cookie1.split ( "#" )[5]
        self.params = re.findall ( '\?(.*?)$', self.task_url )[0]

    def struct_requests(self, method, url, payload):
        # url 为完整的url
        host = re.findall ( 'https://(.*?)/', url )[0]

        if method == 'get':
            headers = {
                'Host': host,
                'User-Agent': self.ua,
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate',
                'sdk-version': self.sdk_version,
                'passport-sdk-version': self.passport_sdk_version,
                'Cookie': self.cookie
            }
            response = s.get ( url=url, headers=headers )
            # print(response.text)
            return response.json ()

        elif method == 'post':
            headers = {
                'Host': host,
                'User-Agent': self.ua,
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate',
                'Content-Type': 'application/json;encoding=utf-8',
                'Content-Length': str ( len ( payload ) ),
                'sdk-version': self.sdk_version,
                'passport-sdk-version': self.passport_sdk_version,
                'x-argus': self.argus,
                'x-ladon': self.ladon,
                'Cookie': self.cookie
            }
            response = s.post ( url=url, headers=headers, data=payload )
            # print(response.text)
            return response.json ()

    # 开宝箱

    def user0(self):
        url = f"https://api5-normal-sinfonlinea.fqnovel.com/luckycat/novel/v1/wallet/take_cash_page?_request_from=web&dynamic_settings_version=51&polling_settings_version=0&{self.params}"
        res = self.struct_requests ( method='get', url=url, payload='' )
        if res["err_no"] == 0:
            print (
                f'当前金币::{res["data"]["take_cash_info"]["income_data"]["score_balance"]}金币,现金:{int ( res["data"]["take_cash_info"]["income_data"]["cash_balance"] * 0.01 )}元' )

    def treasure_task(self, task_key):

        time.sleep ( random.uniform ( 1, 2 ) )
        time.strftime ( '%H:%M' )
        url = f'https://api3-normal-hl.fqnovel.com/luckycat/novel/v1/task/done/{task_key}?' + self.params
        payload = json.dumps ( {} )
        res = self.struct_requests ( method='post', url=url, payload=payload )
        if res.get ( 'err_no' ) == 0:
            amount = res.get ( 'data' ).get ( 'amount' )
            print ( f'【开宝箱】获得{amount}金币' )
            self.next_open_treasure_box = int ( time.time () ) + 1 + 300
            local = time.localtime ( self.next_open_treasure_box )
            formatTime = time.strftime ( '%H:%M:%S', local )
            print ( f'【开宝箱】下次宝箱时间:{formatTime}' )
            self.amount += amount
            self.excitation_ad_treasure_box ( 'excitation_ad_treasure_box' )
            self.excitation_ad_repeat ( 'excitation_ad_repeat' )
            return 1
        else:
            print ( '【开宝箱】' + res.get ( 'err_tips' ) )
            return 0

    # 看宝箱视频
    def excitation_ad_treasure_box(self, task_key):
        try:
            time.sleep ( random.uniform ( 4, 6 ) )
            url = f'https://api3-normal-hl.fqnovel.com/luckycat/novel/v1/task/done/{task_key}?' + self.params
            payload = json.dumps ( {
                "from": "reward_dialog_from_treasure_box",
                "position": "task_page",
                "task_key": task_key
            } )
            res = self.struct_requests ( method='post', url=url, payload=payload )
            if res.get ( 'err_no' ) == 0:
                amount = res.get ( 'data' ).get ( 'amount' )
                print ( f'【看宝箱视频】获得{amount}金币' )
                self.amount += amount
            else:
                print ( '【看宝箱视频】' + res.get ( 'err_tips' ) )
        except:

            print ( '【看宝箱视频】异常' )
            exit ( -1 )

    # print(res)

    # 看视频赚金币
    def excitation_ad(self, task_key):
        try:
            time.sleep ( random.uniform ( 4, 6 ) )
            url = f'https://api3-normal-hl.fqnovel.com/luckycat/novel/v1/task/done/{task_key}?' + self.params
            payload = json.dumps ( {
                "from": "task_list",
                "position": "task_page",
                "task_key": task_key
            } )
            res = self.struct_requests ( method='post', url=url, payload=payload )
            if res.get ( 'err_no' ) == 0:
                amount = res.get ( 'data' ).get ( 'amount' )
                print ( f'【看视频赚金币】获得{amount}金币' )
                self.amount += amount
                self.excitation_ad_repeat ( 'excitation_ad_repeat' )
                return 1
            else:
                print ( '【看视频赚金币】' + res.get ( 'err_tips' ) )
                if res.get ( 'err_tips' ) == '你已完成此任务':
                    return 1
                return 0
        except:
            print ( '【看视频赚金币】异常' )

    # print(res)

    # 看视频赚金币-追加视频
    def excitation_ad_repeat(self, task_key):
        if self.excitation_ad_repeat_cnt > 0:
            time.sleep ( random.uniform ( 4, 6 ) )
            url = f'https://api3-normal-hl.fqnovel.com/luckycat/novel/v1/task/done/{task_key}?' + self.params
            payload = json.dumps ( {
                "task_key": task_key
            } )
            res = self.struct_requests ( method='post', url=url, payload=payload )
            if res.get ( 'err_no' ) == 0:
                amount = res.get ( 'data' ).get ( 'amount' )
                print ( f'【看额外视频】获得{amount}金币' )
                self.excitation_ad_repeat_cnt -= 1
                self.amount += amount
            else:
                print ( '【看额外视频】' + res.get ( 'err_tips' ) )
                if res.get ( 'err_tips' ) == '你已完成此任务':
                    cur_time = time.strftime ( '%H:%M:%S' )
                    res = self.get_ad_info ( 'get_ad_info' )
                    if res.get ( 'err_no' ) == 0:
                        if res.get ( 'data' ).get ( 'score_amount' ) == 0 and cur_time > '09:00:00':
                            self.excitation_ad_repeat_cnt = 0

    def excitation_ad_listen(self, task_key):
        self.get_ad_info ( 'get_ad_info' )
        time.sleep ( random.uniform ( 4, 6 ) )
        url = f'https://api3-normal-hl.fqnovel.com/luckycat/novel/v1/task/done/{task_key}?' + self.params
        payload = json.dumps ( {
            "from": "gold_coin_reward_box_welfare",
            "position": "",
            "task_key": task_key
        } )
        res = self.struct_requests ( method='post', url=url, payload=payload )
        err = res.get ( 'err_tips' )
        amount = res.get ( 'data' ).get ( 'score_amount' )
        print ( f'【状态】: {err}!\n【预计奖励】: {amount}金币' )
        if res.get ( 'err_no' ) == 0:
            amount = res.get ( 'data' ).get ( 'amount' )
            print ( f'【看阅读广告】获得{amount}金币' )
            self.amount += amount
            return 1
        else:
            print ( '【看阅读广告】' + res.get ( 'err_tips' ) )
            return 0

    def daily_watch_short_video(self, short_video_task_key):
        self.get_ad_info ( 'get_ad_info' )
        time.sleep ( random.uniform ( 4, 6 ) )
        url = 'https://api5-normal-hl.fqnovel.com/luckycat/novel/v1/task/done/daily_watch_short_video?' + self.params
        payload = json.dumps ( {
            "short_video_task_key": short_video_task_key
        } )
        res = self.struct_requests ( method='post', url=url, payload=payload )
        if res.get ( 'err_no' ) == 0:
            amount = res.get ( 'data' ).get ( 'amount' )
            print ( f'【每日看短剧】获得{amount}金币' )
            self.amount += amount
            self.excitation_ad_repeat ( 'excitation_ad_repeat' )
            return 1
        else:
            print ( f'【每日看短剧】' + res.get ( 'err_tips' ) )
            if '你已完成此任务' == res.get ( 'err_tips' ):
                return 1
            return 0

    def task_read(self, task_key):
        # daily_read_30s_once
        # daily_read_2m
        # daily_read_5m
        if exec_read:
            time.sleep ( random.uniform ( 4, 6 ) )
            url = f'https://api3-normal-hl.fqnovel.com/luckycat/novel/v1/task/done/{task_key}?' + self.params
            payload = json.dumps ( {
                "action": "withdraw"
            } )
            res = self.struct_requests ( method='post', url=url, payload=payload )
            # print(res)
            tip = re.findall ( 'daily_(.*?)_', task_key )[0]
            if res.get ( 'err_no' ) == 0:
                amount = res.get ( 'data' ).get ( 'amount' )
                print ( f'【{tip}】获得{amount}金币' )
                self.amount += amount
                self.excitation_ad_listen ( 'excitation_ad_listen' )
                self.excitation_ad_repeat ( 'excitation_ad_repeat' )
                return 1
            else:
                print ( f'【{tip}】' + res.get ( 'err_tips' ) )
                if '你已完成此任务' == res.get ( 'err_tips' ):
                    return 1
                return 0

    def meal(self, task_key):
        #     time          meal_type
        # 05:00-09:00 早饭       0
        # 11:00-14:00 午饭		1
        # 17:00-20:00 晚饭		2
        # 21:00-24;00 夜宵		3
        time.sleep ( random.uniform ( 4, 6 ) )
        time_str = time.strftime ( "%H:%M:%S" )
        if '05:00:00' <= time_str <= '09:00:00':
            meal_type = 0
        elif '11:00:00' <= time_str <= '14:00:00':
            meal_type = 1
        elif '17:00:00' <= time_str <= '20:00:00':
            meal_type = 2
        elif '21:00:00' <= time_str <= '24:00:00':
            meal_type = 3
        else:
            print ( '未到吃饭时间' )
            return
        url = f'https://api3-normal-hl.fqnovel.com/luckycat/novel/v1/task/done/{task_key}?' + self.params
        payload = json.dumps ( {
            "meal_type": meal_type,
            "task_key": task_key
        } )
        res = self.struct_requests ( method='post', url=url, payload=payload )
        # print(res)
        if res.get ( 'err_no' ) == 0:
            amount = res.get ( 'data' ).get ( 'amount' )
            print ( f'【吃饭】获得{amount}金币' )
            self.excitation_ad_meal ( 'excitation_ad_meal' )
            self.excitation_ad_repeat ( 'excitation_ad_repeat' )
            return meal_type
        else:
            print ( '【吃饭】' + res.get ( 'err_tips' ) )
            if '你已完成此任务' == res.get ( 'err_tips' ):
                return meal_type
            return -1

    def excitation_ad_read_gain(self, payload_task_key):
        url = 'https://api5-normal-hl.fqnovel.com/luckycat/novel/v1/task/done/excitation_ad_read_gain?' + self.params
        payload = json.dumps ( {
            "task_key": payload_task_key
        } )
        res = self.struct_requests ( method='post', url=url, payload=payload )
        if res.get ( 'err_no' ) == 0:
            print ( '【奖励加倍】' + res.get ( 'err_tips' ) )
        else:
            print ( '【奖励加倍】' + res.get ( 'err_tips' ) )

    def excitation_ad_meal(self, task_key):
        time.sleep ( random.uniform ( 4, 8 ) )
        url = f'https://api3-normal-hl.fqnovel.com/luckycat/novel/v1/task/done/{task_key}?' + self.params
        payload = json.dumps ( {
            "from": "gold_coin_reward_dialog_open_treasure",
            "position": "",
            "task_key": task_key
        } )
        res = self.struct_requests ( method='post', url=url, payload=payload )
        if res.get ( 'err_no' ) == 0:
            amount = res.get ( 'data' ).get ( 'amount' )
            print ( f'【看吃饭广告】获得{amount}金币' )
            self.amount += amount
        else:
            print ( '【看吃饭广告】' + res.get ( 'err_tips' ) )

    def get_ad_info(self, task_key):
        time.sleep ( random.uniform ( 2, 4 ) )
        url = f'https://api3-normal-hl.fqnovel.com/luckycat/novel/v1/task/{task_key}?' + self.params
        res = self.struct_requests ( method='get', url=url, payload='' )
        print ( '------------[repeat]获取广告信息如下------------' )
        err = res.get ( 'err_tips' )
        amount = res.get ( 'data' ).get ( 'score_amount' )
        print ( f'【状态】: {err}!\n【预计奖励】: {amount}金币' )
        print ( '-----------------------' )
        return res

    # 浏览商品赚钱 60秒
    def browse_products(self, task_key):
        time.sleep ( random.uniform ( 6, 10 ) )
        url = f'https://api3-normal-hl.fqnovel.com/luckycat/novel/v1/task/done/{task_key}?' + self.params
        payload = json.dumps ( {
            "task_key": task_key
        } )
        res = self.struct_requests ( method='post', url=url, payload=payload )
        if res.get ( 'err_no' ) == 0:
            amount = res.get ( 'data' ).get ( 'amount' )
            print ( f'【浏览商品赚钱】获得{amount}金币' )
            self.amount += amount
            return 1
        else:
            print ( '【浏览商品赚钱】' + res.get ( 'err_tips' ) )
            if res.get ( 'err_tips' ) == '你已完成此任务':
                return 1
            return 0

    # print(res)

    # 逛街赚金币
    def shopping_earn_money(self, task_key):
        time.sleep ( random.uniform ( 6, 10 ) )
        url = f'https://api3-normal-hl.fqnovel.com/luckycat/novel/v1/task/done/{task_key}?' + self.params
        payload = json.dumps ( {
            "task_key": task_key
        } )
        res = self.struct_requests ( method='post', url=url, payload=payload )
        if res.get ( 'err_no' ) == 0:
            amount = res.get ( 'data' ).get ( 'amount' )
            print ( f'【逛街赚金币】获得{amount}金币' )
            self.amount += amount
            return 1
        else:
            print ( '【逛街赚金币】' + res.get ( 'err_tips' ) )
            if res.get ( 'err_tips' ) == '你已完成此任务':
                return 1
            return 0

    # print(res)

    # 开始睡觉
    def sleep(self, task_key):
        time_str = time.strftime ( "%H:%M:%S" )
        # done_type == "start_sleep" || "end_sleep"
        if '22:00:00' <= time_str <= '23:45:00':
            done_type = "start_sleep"
            url = f'https://api3-normal-hl.fqnovel.com/luckycat/novel/v1/task/done/{task_key}?' + self.params
            payload = json.dumps ( {
                "done_type": done_type,
                "task_key": task_key
            } )
            res = self.struct_requests ( method='post', url=url, payload=payload )
            print ( res )
            if res.get ( 'err_no' ) == 0:
                print ( '【去睡觉】' )
                # self.excitation_ad_repeat('excitation_ad_repeat')
                return 1
            else:
                print ( '【去睡觉】' + res.get ( 'err_tips' ) )
                if '你已完成此任务' == res.get ( 'err_tips' ):
                    return 1
                return 0
        elif '05:00:00' <= time_str <= '08:00:00':
            done_type = "end_sleep"
            url = f'https://api3-normal-hl.fqnovel.com/luckycat/novel/v1/task/done/{task_key}?' + self.params
            payload = json.dumps ( {
                "done_type": done_type,
                "task_key": task_key
            } )
            res = self.struct_requests ( method='post', url=url, payload=payload )
            print ( res )
            if 'err_no' in res:
                if res.get ( 'err_no' ) == 10007:
                    return 0
                elif res.get ( 'err_no' ) == 0:
                    amount = res.get ( 'data' ).get ( 'income_info' ).get ( 'amount' )
                    payload = json.dumps ( {
                        "done_type": "receive_awards",
                        "amount": int ( amount ),
                        "task_key": task_key
                    } )
                    time.sleep ( random.uniform ( 2, 8 ) )
                    res = self.struct_requests ( method='post', url=url, payload=payload )
                    if res.get ( 'err_no' ) == 0:
                        amount = res.get ( 'data' ).get ( 'amount' )
                        print ( f'【结束睡觉】获得{amount}金币' )
                        self.amount += amount
                        # 执行广告
                        self.sleep_ad ( 'sleep_ad' )
                        # 再次执行广告
                        self.excitation_ad_repeat ( 'excitation_ad_repeat' )
                        return 1
                    else:
                        print ( '【结束睡觉】' + res.get ( 'err_tips' ) )
                        if '你已完成此任务' == res.get ( 'err_tips' ):
                            return 1
                        return 0
            else:
                print ( '不在睡觉时间' )
                return 0

    def sleep_ad(self, task_key):
        time.sleep ( random.uniform ( 6, 8 ) )
        url = f'https://api3-normal-hl.fqnovel.com/luckycat/novel/v1/task/done/{task_key}?' + self.params
        payload = json.dumps ( {
            "from": "gold_coin_reward_dialog_open_treasure",
            "position": "",
            "task_key": task_key
        } )
        res = self.struct_requests ( method='post', url=url, payload=payload )
        if res.get ( 'err_no' ) == 0:
            amount = res.get ( 'data' ).get ( 'amount' )
            print ( f'【看睡觉广告】获得{amount}金币' )
            self.amount += amount
            self.excitation_ad_repeat ( 'excitation_ad_repeat' )
            return 1
        else:
            print ( '【看睡觉广告】' + res.get ( 'err_tips' ) )
            if '你已完成此任务' == res.get ( 'err_tips' ):
                return 1
            return 0

    def page(self, task_key):
        url = f'https://api3-normal-hl.fqnovel.com/luckycat/novel/v1/task/{task_key}?' + self.params
        res = self.struct_requests ( method='get', url=url, payload='' )
        print ( res )

    def daily_read_comics(self, task_key):
        if exec_read:
            time.sleep ( random.uniform ( 6, 10 ) )
            url = 'https://api3-normal-hl.fqnovel.com/luckycat/novel/v1/task/done/daily_read_comics?' + self.params
            payload = json.dumps ( {
                "read_comics_task_key": task_key,
                "task_key": "daily_read_comics"
            } )
            res = self.struct_requests ( method='post', url=url, payload=payload )
            # print(res)
            if res.get ( 'err_no' ) == 0:
                amount = res.get ( 'data' ).get ( 'amount' )
                print ( f'【看漫画】获得{amount}金币' )
                self.amount += amount
                # self.excitation_ad_repeat('excitation_ad_repeat')
                return 1
            else:
                print ( '【看漫画】' + res.get ( 'err_tips' ) )
                if '你已完成此任务' == res.get ( 'err_tips' ):
                    return 1
                return 0

    def getUserInfo(self):
        time.sleep ( random.uniform ( 2, 4 ) )
        url = 'https://api5-normal-hl.fqnovel.com/reading/user/info/v/?' + self.params
        res = self.struct_requests ( method='get', url=url, payload='' )
        if res.get ( 'code' ) == 0:
            user_name = res.get ( 'data' ).get ( 'user_name' )
            return user_name
        else:
            print ( '获取用户名失败' )
            return 'none'

    def sign_in(self, task_key):
        time.sleep ( random.uniform ( 4, 6 ) )
        url = f'https://api5-normal-hl.fqnovel.com/luckycat/novel/v1/task/done/{task_key}?' + self.params
        payload = json.dumps ( {} )
        res = self.struct_requests ( method='post', url=url, payload=payload )
        # print(res)
        if res.get ( 'err_no' ) == 0:
            amount = res.get ( 'data' ).get ( 'amount' )
            task_key = res.get ( 'data' ).get ( 'new_excitation_ad' ).get ( 'task_key' )
            print ( f'【签到】获得{amount}金币' )
            self.amount += amount
            self.excitation_ad ( task_key )
            return 1
        else:
            print ( '【签到】' + res.get ( 'err_tips' ) )
            if '你已完成此任务' == res.get ( 'err_tips' ):
                return 1
            return 0

    def daily_play_game(self, task_key):
        time.sleep ( random.uniform ( 6, 10 ) )
        url = f'https://api5-normal-hl.fqnovel.com/luckycat/novel/v1/task/done/{task_key}?' + self.params
        payload = json.dumps ( {} )
        res = self.struct_requests ( method='post', url=url, payload=payload )
        if res.get ( 'err_no' ) == 0:
            amount = res.get ( 'data' ).get ( 'amount' )
            print ( f'【每日玩游戏】获得{amount}金币' )
            self.amount += amount
            return 1
        else:
            print ( '【每日玩游戏】' + res.get ( 'err_tips' ) )
            if '你已完成此任务' == res.get ( 'err_tips' ):
                return 1
            return 0

    def lottery(self, task_key):
        url = f'https://api5-normal-hl.fqnovel.com/luckycat/novel/v1/lottery/{task_key}?' + self.params
        if task_key == 'page':
            time.sleep ( random.uniform ( 5, 10 ) )
            res = self.struct_requests ( 'get', url, '' )
            if res.get ( 'err_no' ) == 0:
                print ( res )
                self.lottery_cnt = res.get ( 'data' ).get ( 'can_lottery_times' )
            else:
                print ( '【查询抽奖页面】' + res.get ( 'err_tips' ) )
        elif task_key == 'lottery_task_page':
            # 查询抽奖任务
            time.sleep ( random.uniform ( 4, 6 ) )
            res = self.struct_requests ( 'get', url, '' )
            if res.get ( 'err_no' ) == 0:
                # print(res)
                task_list = res.get ( 'data' ).get ( 'task_list' )
                taskId = {}
                for task_data in task_list:
                    # print(task_data)
                    task_id = task_data.get ( 'task_id' )
                    chance_time = task_data.get ( 'chance_times' )
                    taskId[task_id] = chance_time
                print ( '返回taskId success' )
                self.taskId = taskId
            else:
                print ( '【查询抽奖页面】' + res.get ( 'err_tips' ) )
        elif task_key == 'update_chance':
            # 去抽奖
            # task_id : 73[看视频抽奖（0/10）],74[阅读抽奖（0/1）],75[逛街抽奖（0/1）]
            time.sleep ( random.uniform ( 5, 10 ) )
            taskId = self.taskId
            for tid in taskId:
                tid_cnt = taskId.get ( tid )
                for i in range ( tid_cnt ):
                    payload = json.dumps ( {
                        "task_id": tid
                    } )
                    res = self.struct_requests ( method='post', url=url, payload=payload )
                    # if res.get('err_no') != 0:
                    print ( '【增加抽奖机会】' + res.get ( 'err_tips' ) )
                    time.sleep ( random.uniform ( 6, 8 ) )

        elif task_key == 'do_lottery':
            # 去抽奖
            time.sleep ( random.uniform ( 6, 8 ) )
            for lottery_cnt in range ( self.lottery_cnt ):
                payload = json.dumps ( {} )
                res = self.struct_requests ( method='post', url=url, payload=payload )
                if res.get ( 'err_no' ) == 0:
                    amount = res.get ( 'data' ).get ( 'reward' ).get ( 'amount' )
                    print ( f'【抽奖】获得{amount}' )
                    self.amount += amount
                    time.sleep ( random.uniform ( 2, 3 ) )
                else:
                    print ( '【抽奖】' + res.get ( 'err_tips' ) )

        elif task_key == 'continue_lottery':
            # 每日抽奖签到
            time.sleep ( random.uniform ( 6, 8 ) )
            payload = json.dumps ( {} )
            res = self.struct_requests ( method='post', url=url, payload=payload )
            if res.get ( 'err_no' ) == 0:
                amount = res.get ( 'data' ).get ( 'amount' )
                print ( f'【每日抽奖签到】获得{amount}' )
                self.amount += amount
            else:
                print ( '【每日抽奖签到】' + res.get ( 'err_tips' ) )

    def run(self, userIndex):
        user_data = userList[userIndex]
        # 查询
        name = user_data.get ( 'name' )
        amount = user_data.get ( 'amount' )
        sign = user_data.get ( 'sign' )
        treasure_task_cnt = user_data.get ( 'treasure_task_cnt' )
        shopping_earn_money_cnt = user_data.get ( 'shopping_earn_money_cnt' )
        browse_products_cnt = user_data.get ( 'browse_products_cnt' )
        excitation_ad_cnt = user_data.get ( 'excitation_ad_cnt' )
        daily_play_game_cnt = user_data.get ( 'daily_play_game_cnt' )
        next_readComic = user_data.get ( 'next_readComic' )
        next_readNovel = user_data.get ( 'next_readNovel' )
        next_listenNoval = user_data.get ( 'next_listenNoval' )
        meal_finished = user_data.get ( 'meal_finished' )
        sleep_finished = user_data.get ( 'sleep_finished' )
        prev_task_timeStamp = user_data.get ( 'prev_task_timeStamp' )
        title = user_data.get ( 'title' )
        lottery = user_data.get ( 'lottery' )
        next_short_video = user_data.get ( 'next_short_video' )
        next_open_treasure_box = user_data.get ( 'next_open_treasure_box' )
        excitation_ad_repeat_cnt = user_data.get ( 'excitation_ad_repeat_cnt' )
        self.excitation_ad_repeat_cnt = excitation_ad_repeat_cnt
        # 执行
        if name == 'none':
            name = self.getUserInfo ()
        print ( f'用户【{name}】' )

        self.next_open_treasure_box = next_open_treasure_box
        remain_second = next_open_treasure_box - int ( time.time () ) + 1
        self.user0 ()
        print ( f'当前remaid_second:{remain_second}' )
        if 0 < remain_second < limit_second:
            print ( f'【开宝箱】等待{remain_second}s开宝箱' )
            time.sleep ( remain_second )
            treasure_task_cnt += self.treasure_task ( 'treasure_task' )
        elif remain_second < 0:
            treasure_task_cnt += self.treasure_task ( 'treasure_task' )

        current_time = time.strftime ( '%H:%M:%S' )
        #     time          meal_type
        # 05:00-09:00 早饭       0
        # 11:00-14:00 午饭		1
        # 17:00-20:00 晚饭		2
        # 21:00-24;00 夜宵		3
        meal_judge = {
            0: '05:00:00-09:00:00',
            1: '11:00:00-14:00:00',
            2: '17:00:00-20:00:00',
            3: '21:00:00-24:00:00'
        }

        if sign == 0:
            sign = self.sign_in ( 'sign_in' )

            # 带有【excitation_ad_repeat】的任务
        if time.time () >= (delay_minutes * 60) + prev_task_timeStamp:

            if current_time > '06:00:00':
                if shopping_earn_money_cnt != 0:
                    shopping_earn_money_cnt -= self.shopping_earn_money ( 'shopping_earn_money' )

                if daily_play_game_cnt != 0:
                    daily_play_game_cnt -= self.daily_play_game ( 'daily_play_game' )

            if current_time > '09:00:00':
                if browse_products_cnt != 0:
                    browse_products_cnt -= self.browse_products ( 'browse_products' )

            if current_time > '11:00:00':
                if excitation_ad_cnt != 0:
                    excitation_ad_cnt -= self.excitation_ad ( 'excitation_ad' )

            # 需要完成结束睡觉
            if sleep_finished == 'start_sleep' and '05:00:00' <= current_time <= '08:00:00':
                print ( '需要完成结束睡觉' )
                if self.sleep ( 'sleep' ):
                    sleep_finished = 'end_sleep'

                # 需要完成去睡觉
            elif sleep_finished == 'end_sleep' and '22:00:00' <= current_time <= '23:45:00':
                print ( '需要完成去睡觉' )
                if self.sleep ( 'sleep' ):
                    sleep_finished = 'start_sleep'

            if meal_finished == -1:
                for mid in range ( 4 ):
                    key_time = meal_judge.get ( mid )
                    # print(key_time)
                    start_time = re.findall ( '^(.*?)-', key_time )[0]
                    end_time = re.findall ( '-(.*?)$', key_time )[0]
                    if start_time <= current_time <= end_time:
                        meal_finished = self.meal ( 'meal' )

            else:
                if meal_finished == 3:
                    key_time = meal_judge.get ( 0 )
                else:
                    key_time = meal_judge.get ( meal_finished + 1 )
                # key和time是否对应

                start_time = re.findall ( '^(.*?)-', key_time )[0]
                end_time = re.findall ( '-(.*?)$', key_time )[0]
                if start_time <= current_time <= end_time:
                    meal_finished = self.meal ( 'meal' )

            # 阅读
            # print(f'阅读本次：{next_readNovel}')
            if exec_read:
                if current_time > '14:00:00':
                    read_id = [0.5, 2, 5, 10, 30, 60, 120, 180]
                    if next_readNovel != -1:
                        read_start = read_id.index ( next_readNovel )
                        # for rid in range(len(read_id) - read_start):
                        if read_id[read_start] == 0.5:

                            read_minute = '30s_once'
                            key = 'daily_read_' + read_minute
                            if excitation_ad_read_gain_mode:
                                self.excitation_ad_read_gain ( key )
                                time.sleep ( random.uniform ( 5, 10 ) )
                            read_start += self.task_read ( key )
                        else:
                            read_minute = f'{read_id[read_start]}m'
                            key = f'daily_read_{read_minute}'
                            if excitation_ad_read_gain_mode:
                                self.excitation_ad_read_gain ( key )
                                time.sleep ( random.uniform ( 5, 10 ) )
                            read_start += self.task_read ( key )
                        if read_start <= len ( read_id ) - 1:
                            next_readNovel = read_id[read_start]
                        else:
                            next_readNovel = -1

                    # 听书
                    # print(f'听书本次：{next_listenNoval}')
                if current_time > '17:00:00':
                    listen_id = [0.5, 2, 5, 10, 30, 60, 120, 180]
                    if next_listenNoval != -1:
                        listen_start = listen_id.index ( next_listenNoval )
                        # for lid in range(len(listen_id) - listen_start):
                        if listen_id[listen_start] == 0.5:
                            listen_minute = '30s'
                        else:
                            listen_minute = f'{listen_id[listen_start]}m'
                        listen_start += self.task_read ( 'daily_listen_' + listen_minute )
                        if listen_start <= len ( listen_id ) - 1:
                            next_listenNoval = listen_id[listen_start]
                        else:
                            next_listenNoval = -1

                if current_time > '19:00:00':
                    # 看短剧
                    short_video_id = [0.5, 2, 5, 10, 30, 60, 120]
                    if next_short_video != -1:
                        short_video_start = short_video_id.index ( next_short_video )

                        if short_video_id[short_video_start] == 0.5:
                            short_video_minute = '30s'
                        else:
                            short_video_minute = f'{short_video_id[short_video_start]}m'
                        short_video_start += self.daily_watch_short_video (
                            'daily_short_video_' + short_video_minute )
                        if short_video_start <= len ( short_video_id ) - 1:
                            next_short_video = short_video_id[short_video_start]
                        else:
                            next_short_video = -1

                if current_time > '21:00:00':
                    # 看漫画
                    # print(f'看漫画本次：{next_readComic}')
                    comic_id = [1, 5, 10, 25, 45, 60]
                    if next_readComic != -1:
                        comic_start = comic_id.index ( next_readComic )
                        # for cid in range(len(comic_id) - comic_start):
                        # self.daily_read_comics(f'daily_read_comics_{comic_id[cid + comic_start]}m')
                        comic_start += self.daily_read_comics ( f'daily_read_comics_{comic_id[comic_start]}m' )
                        self.excitation_ad_repeat ( 'excitation_ad_repeat' )
                        if comic_start <= len ( comic_id ) - 1:
                            next_readComic = comic_id[comic_start]
                        else:
                            next_readComic = -1
            prev_task_timeStamp = int ( time.time () ) + 1

        if '22:30:00' <= current_time <= '23:30:00':
            if lottery == 0:
                self.lottery ( 'lottery_task_page' )
                self.lottery ( 'update_chance' )
                lottery = 1
            elif lottery == 1:
                self.lottery ( 'page' )
                self.lottery ( 'do_lottery' )
                lottery = -1

        print (f'【开宝箱】已开宝箱{treasure_task_cnt}次' )
        print ( f'本次执行获得{self.amount}金币' )

        # 写回
        current_time = time.localtime ()  # 获取当前时间
        formatted_time = time.strftime ( '%m-%d %H:%M:%S', current_time )  # 格式化时间为字符串

        temp = {
            "name": name,
            "amount": self.amount + amount,
            "time": formatted_time,
            "sign": sign,
            "lottery": lottery,
            "prev_task_timeStamp": prev_task_timeStamp,
            "treasure_task_cnt": treasure_task_cnt,
            "shopping_earn_money_cnt": shopping_earn_money_cnt,
            "browse_products_cnt": browse_products_cnt,
            "excitation_ad_cnt": excitation_ad_cnt,
            "daily_play_game_cnt": daily_play_game_cnt,
            "next_readComic": next_readComic,
            "next_readNovel": next_readNovel,
            "next_listenNoval": next_listenNoval,
            "next_short_video": next_short_video,
            "meal_finished": meal_finished,
            "sleep_finished": sleep_finished,
            "excitation_ad_repeat_cnt": self.excitation_ad_repeat_cnt,
            "next_open_treasure_box": self.next_open_treasure_box,
            "title": title
        }
        new_userList.append ( temp )

if __name__ == "__main__":
        user_cookie = cookies.split ( '\n' )
        print(f"番茄阅读共获取到{len(user_cookie)}个账号")

        i = 0
        for cookie in user_cookie:
            print(f"=========开始第{i + 1}个账号=========")
            tomato(cookie).run(i)
            if i != len(user_cookie) - 1:
                i += 1
                wait_time = random.randint(60, 200)
                print(f'等待{wait_time}s')
                time.sleep(wait_time)

                # 执行结束 写回文件
                new_userList_json = {
                    "userList": new_userList
                }
                writeFile(tomato_read_json_path, new_userList_json)