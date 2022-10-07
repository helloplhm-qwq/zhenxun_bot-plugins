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
from . import config

__zx_plugin_name__ = "pixiv随机图片"
__plugin_usage__ = """
usage：
    pixiv随机图片
""".strip()
__plugin_des__ = "pixiv随机图片"
__plugin_type__ = ("一些工具",)
__plugin_cmd__ = ["pixiv随机图片"]
__plugin_version__ = 0.1
__plugin_author__ = "helloplhm_qwq"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["pixiv随机图片"],
}

ig = on_command("pixiv随机图片", block=True, priority=5)

if config.save:
  try:
      os.mkdir(f'{config.save_dir}')
  except:
      pass

@ig.handle()
async def pixrandomimg(bot: Bot, ev: Event):
    try:
        logger.info(
            '尝试获取pixiv随机图片'
            f'(from USER {ev.user_id}, GROUP {ev.group_id if isinstance(ev, GroupMessageEvent) else "private"} ) '
            )
        img_urlreq=requests.get('https://px2.rainchan.win/random',allow_redirects=False)
        header=img_urlreq.headers
        image_url=header['Location']
        logger.info(
            f'请求成功,resp_header:{header}'
            )
        img = await AsyncHttpx().get(f'https://px2.rainchan.win{image_url}'.replace('small',f'{config.quality}'))
        logger.info(
            '读取并发送图片...'
            )
        if config.save:
            image_id=image_url.split('/')[-1]
            open(config.save_dir+image_id+'.png','wb').write(img.content)
    except Exception as e:
        logger.error('出现错误！')
        raise e
        return await bot.send(event=ev, message="获取图片错误，请查看日志")
    await bot.send(event=ev, message=MessageSegment.image(img.content))
