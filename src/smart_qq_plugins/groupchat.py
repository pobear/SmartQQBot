# -*- coding: utf-8 -*-
import json
import logging
import datetime
import requests
from smart_qq_bot.signals import on_group_message

__author__ = 'pobear'


@on_group_message(name='groupchat')
def record_message(msg, bot):
    group_info = bot.get_group_info_ext(msg.group_code)
    sender_info = bot.get_friend_info(msg.send_uin)
    nickname = ''
    for user in group_info.get('minfo'):
        if user['uin'] == msg.send_uin:
            nickname = user['nick']
            break
    record = {
        'group_name': group_info.get('ginfo', {}).get('name'),
        'qq': sender_info['account'],
        'nickname': nickname,
        'content': msg.content,
        'send_time': '@%s' % msg.time
    }

    logging.info(json.dumps(record, ensure_ascii=False))

    url = 'http://api.jzb.io:8888/events/qqchats/'
    r = requests.post(url, data=json.dumps(record))
    print(r.json())
