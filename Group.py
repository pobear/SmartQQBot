# -*- coding: utf-8 -*-

import json
import time
import random

from Configs import *
from Msg import *
from HttpClient import *


class Group:

    def __init__(self, operator, ip, use_global_config=True):
        if isinstance(ip, (int, long, str)):
            # 使用uin初始化
            self.guin = ip
            self.gid = ""
        elif isinstance(ip, GroupMsg):
            self.guin = ip.from_uin
            self.gid = ip.info_seq
        self.msg_id = int(random.uniform(20000, 50000))
        self.__operator = operator
        self.member_list = []
        self.msg_list = []
        # TODO:消息历史保存功能
        self.follow_list = []
        self.tucao_dict = {}
        self.global_config = DefaultConfigs()
        self.private_config = GroupConfig(self)
        if use_global_config:
            self.config = self.global_config
        else:
            self.config = self.private_config
        self.process_order = [
            "repeat",
            "callout",
        ]

        print str(self.gid) + "群已激活, 当前执行顺序："
        print self.process_order

    def handle(self, msg):
        self.config.update()
        print "msg handling."
        # 仅关注消息内容进行处理 Only do the operation of handle the msg content
        for func in self.process_order:
            try:
                if bool(self.config.conf.getint("group", func)):
                    print "evaling " + func
                    if eval("self." + func)(msg):
                        return func
            except ConfigParser.NoOptionError as er:
                print er, "没有找到" + func + "功能的对应设置，请检查共有配置文件是否正确设置功能参数"
        print "finished."

    def reply(self, reply_content, fail_times=0):
        last_fail_times = fail_times

        fix_content = str(reply_content.replace("\\", "\\\\\\\\").replace("\n", "\\\\n").replace("\t", "\\\\t")).decode("utf-8")
        rsp = ""
        try:
            req_url = "http://d.web2.qq.com/channel/send_qun_msg2"
            data = (
                ('r', '{{"group_uin":{0}, "face":564,"content":"[\\"{4}\\",[\\"font\\",{{\\"name\\":\\"Arial\\",\\"size\\":\\"10\\",\\"style\\":[0,0,0],\\"color\\":\\"000000\\"}}]]","clientid":"{1}","msg_id":{2},"psessionid":"{3}"}}'.format(self.guin, self.__operator.ClientID, self.msg_id + 1, self.__operator.PSessionID, fix_content)),
                ('clientid', self.__operator.ClientID),
                ('psessionid', self.__operator.PSessionID)
            )
            rsp = HttpClient().Post(req_url, data, self.__operator.nowConfig.conf.get("global", "connect_referer"))
            rsp_json = json.loads(rsp)
            if rsp_json['retcode'] != 0:
                raise ValueError("reply pmchat error" + str(rsp_json['retcode']))
            print "Reply response: " + str(rsp_json)
            self.msg_id += 1
            return rsp_json
        except:
            if last_fail_times < 5:
                # loggin.error("Response Error.Wait for 2s and Retrying."+str(lastFailTimes))
                # logging.info(rsp)
                print "Response Error.Wait for 2s and Retrying." + str(last_fail_times)
                print rsp
                last_fail_times += 1
                time.sleep(2)
                self.reply(reply_content, last_fail_times + 1)
            else:
                print "Response Error over 5 times.Exit."
                print "Content:" + str(reply_content)
                # logging.error("Response Error over 5 times.Exit.")
                # raise ValueError(rsp)
                return False

    def callout(self, msg):
        if "智障机器人" in msg.content:
            print "calling out, trying to reply...."
            self.reply("干嘛（‘·д·）")
            print str(self.gid) + "有人叫我"
            return True
        return False

    def repeat(self, msg):
        if len(self.msg_list) > 0 and self.msg_list[-1].content == msg.content:
            if str(msg.content).strip() not in ("", " ", "[图片]", "[表情]"):
                print "repeating, trying to reply..."
                self.reply(msg.content)
                print "群" + str(self.gid) + "已复读：{" + str(msg.content) + "}"
                return True
        return False