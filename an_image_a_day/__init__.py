from nonebot import on_command
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.adapters.onebot.v11.event import Event
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent
from services.log import logger
from utils.http_utils import AsyncHttpx
import requests
import json
import os
import datetime
from . import config
#声明插件数据
__zx_plugin_name__ = "每日一图"
__plugin_usage__ = """
usage：
    每日一图
""".strip()
__plugin_des__ = "每日一图"
__plugin_type__ = ("一些工具",)
__plugin_cmd__ = ["每日一图"]
__plugin_version__ = 0.1
__plugin_author__ = "helloplhm_qwq"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["每日一图"],
}

#检查是否保存，如果保存则创建保存目录
if config.save:
  try:
      os.mkdir(config.save_dir)
  except Exception as e:
      pass

#声明命令
animgaday_ = on_command("每日一图", block=True, priority=1)

@animgaday_.handle()
async def animgaday(bot: Bot, ev: Event):
    try:
        logger.info(
            '尝试获取必应每日一图'
            f'(from USER {ev.user_id}, GROUP {ev.group_id if isinstance(ev, GroupMessageEvent) else "private"} ) '
            )
        #请求必应每日一图信息
        img_urlreq=requests.get('https://bird.limestart.cn/cache/bing.json')
        data=json.loads(img_urlreq.content.decode('utf-8'))
        logger.info(
            f'请求成功,resp_data:{data}'
            )
        #获取图片
        image_url=data['images'][0]['url']
        img = await AsyncHttpx().get(f'https://cn.bing.com/{image_url}')
        logger.info(
            '读取并发送图片...'
            )
        #保存图片
        if config.save:
          open(f'./{config.save_dir}/'+str(datetime.date.today())+'.jpg','wb').write(img.content)
    except Exception as e:
        logger.error('出现错误！')
        raise e
        return await bot.send(event=ev, message="获取图片错误，请查看日志")
    await bot.send(event=ev, message=MessageSegment.image(img.content))
