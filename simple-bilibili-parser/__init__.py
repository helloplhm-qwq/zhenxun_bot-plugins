from nonebot import on_command
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.adapters.onebot.v11.event import Event
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, Message
from services.log import logger
from nonebot.typing import T_State
from utils.http_utils import AsyncHttpx
from configs.config import NICKNAME
from nonebot import on_command
from nonebot.params import CommandArg
import requests
from bs4 import BeautifulSoup
bs=BeautifulSoup
try:
    import ujson as json
except:
    import json

__zx_plugin_name__ = "B站解析"
__plugin_usage__ = """
获取B站视频信息，播放链接等
usage：
    B站解析 https://www.bilibili.com/video/BV23333333
    B站解析 https://www.bilibili.com/video/av23333333
    B站解析 https://www.bilibili.com/bangumi/ss23333
    B站解析 BV23333333
    B站解析 av23333333
    ...
""".strip()
__plugin_des__ = "获取B站视频信息，播放链接等"
__plugin_type__ = ("一些工具",)
__plugin_cmd__ = ["B站解析"]
__plugin_version__ = 0.1
__plugin_author__ = "helloplhm_qwq"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["B站解析 [data]"],
}

biliparse = on_command("B站解析", block=True, priority=5)

class dts():
    class LINK():
        """链接形式"""
        pass
    class BV():
        """BV号形式"""
        pass
    class av():
        """av号形式"""
        pass
    class ss():
        pass
    class ep():
        pass

class vts():
    class VIDEO():
        """视频和番剧的获取方式不同，所以要区别开来"""
        pass
    class BANGUMI():
        pass
    class BANGUMI_MULTI():
        pass

@biliparse.handle()
async def handle_first_receive(state: T_State, arg: Message = CommandArg()):
    try:
        if args := arg.extract_plain_text().strip():
            state["data"],state['data'] = args
    except:
        if args := arg.extract_plain_text().strip():
            state["data"] = args

def cnt_to(MESSAGE: str):
    logger.info(f'connect_to: {MESSAGE}')

def get_loc(MESSAGE: str):
    logger.info(f'get_location: {MESSAGE}')

global link
global get_type
global bvid
global aid
global cid
global like
global coin
global danmaku
global favorite
global view
global share
global title
global first_frame_link
global vtype
global errmsg
global cover
link=None
get_type=None
bvid=None
aid=None
cid=None
like=None
coin=None
danmaku=None
favorite=None
view=None
share=None
title=None
first_frame_link=None
vtype=None
cover=None
errmsg=None
online=None
up_name=None
tags_list=[]
first_frame=None
bangumi_title=None
bangumi_desc=None
bangumi_cover=None
tags_str=None
ssurl=None

@biliparse.got("data", prompt="网址呢？")
async def _(bot: Bot, ev: Event, state: T_State):
    global link
    global get_type
    global bvid
    global aid
    global cid
    global like
    global coin
    global danmaku
    global favorite
    global view
    global share
    global title
    global first_frame_link
    global vtype
    global errmsg
    global first_frame
    global cover
    global online
    global up_name
    global tags_str
    global tags_list
    global bangumi_title
    global bangumi_desc
    global bangumi_cover
    global ssurl
    try:
        parse_data=state['data']
        if parse_data.startswith('https://') or parse_data.startswith('http://'):
            if 'b23.tv' in parse_data:
                logger.info(f'link: {parse_data}')
                get_loc(parse_data)
                cnt_to(parse_data)
                urlreq=requests.get(parse_data,allow_redirects=False)
                headers=urlreq.headers
                location=headers['Location']
                logger.info(f'Share_target_link: {location}')
                link=location
                get_type=dts.LINK()
            elif 'bilibili.com' in parse_data:
                logger.info(f'link: {parse_data}')
                link=parse_data
                get_type=dts.LINK()
            else:
                logger.info(f'{ev.user_id}发送了一个不支持的链接')
                return
        elif parse_data.startswith('BV'):
            bvid=parse_data
            get_type=dts.BV()
        elif parse_data.startswith('av'):
            aid=parse_data.replace('av','')
            get_type=dts.av()
        elif parse_data.startswith('ss'):
            ssid=parse_data
            get_type=dts.ss()
        elif parse_data.startswith('ep'):
            epid=parse_data
            get_type=dts.ep()
        else:
            bot.send(event=ev,message='未知的B站信息')
            logger.info('未知的B站信息')
            return
        #parse finished
        taskresid,msg = await pre_get(vt=get_type)
        logger.info(f'结果id：{taskresid},消息：{msg}')
        if taskresid != 200 and taskresid != 301:
            return await bot.send(event=ev,message=f'出错了，{msg}')
        if taskresid==301:
            bangumi_pre_get(vt=get_type)
            return await bot.send(event=ev,message=f'暂时不支持的功能：{msg}')
        if type(vtype) is vts.VIDEO:
            sendtargetmsg=MessageSegment.image(cover)
            sendtargetmsg+=MessageSegment.text('视频首帧截图')
            sendtargetmsg+=MessageSegment.image(first_frame)
            sendtargetmsg+=MessageSegment.text(f'''
视频信息
标题：{title}
BV：{bvid}
av：av{aid}
cid：{cid}
up：{up_name}
观看数：{view}
点赞数：{like}
投币数：{coin}
收藏数：{favorite}
当前有{online}个人正在观看，已装填{danmaku}条弹幕
视频文件链接：还没做
音频文件链接：还没做
指向文件的链接为支持的最高清晰度
                '''.strip())
            await bot.send(event=ev,message=sendtargetmsg)
            return
        elif type(vtype) is vts.BANGUMI:
            sendtargetmsg=MessageSegment.image(cover)
            sendtargetmsg+=MessageSegment.text(bangumi_title+'\n')
            sendtargetmsg+=MessageSegment.text(bangumi_desc+'\n')
            sendtargetmsg+=MessageSegment.text(ssurl+'\n')
            sendtargetmsg+=MessageSegment.text(f'''
番剧信息
标题：{title}
BV：{bvid}
av：av{aid}
cid：{cid}
观看数：{view}
点赞数：{like}
投币数：{coin}
收藏数：{favorite}
当前有{online}个人正在观看，已装填{danmaku}条弹幕
视频文件链接：还没做
音频文件链接：还没做
指向文件的链接为支持的最高清晰度
'''.strip())
            await bot.send(event=ev,message=sendtargetmsg)
            return
    except Exception as error:
        await bot.send(event=ev,message='似乎出了点问题...')
        logger.error('出现错误！')
        raise error

async def pre_get(vt):
    global link
    global get_type
    global bvid
    global aid
    global cid
    global like
    global coin
    global bangumi_title
    global danmaku
    global favorite
    global view
    global share
    global title
    global cover
    global first_frame_link
    global vtype
    global errmsg
    global first_frame
    global online
    global tags_str
    global tags_list
    global up_name
    global bangumi_desc
    global ssurl
    logger.info(f'{type(vt)}')
    if type(vt) is dts.LINK:
        logger.info(f'{link}')
        #link parse
        if link.endswith('/'):
            link=link[0:-1]
        _id_=link.replace('/?','?').split('/')[-1].split('?')[0]
        logger.info(f'id_parsed:{_id_}')
        if _id_.startswith('BV'):
            vtype=vts.VIDEO()
            bvid=_id_
            bvinfo=await bili_html_parse(f'https://www.bilibili.com/video/{bvid}')
            cover_link=bvinfo['videoData']['pic']
            up_name=bvinfo['videoData']['owner']['name']
            cnt_to(f'https://api.bilibili.com/x/web-interface/archive/stat?bvid={_id_}')
            aidreq=await AsyncHttpx.get(f'https://api.bilibili.com/x/web-interface/archive/stat?bvid={_id_}')
            aidjson=json.loads(aidreq.content)
            aid=aidjson['data']['aid']
            like=aidjson['data']['like']
            danmaku=aidjson['data']['danmaku']
            favorite=aidjson['data']['favorite']
            coin=aidjson['data']['coin']
            view=aidjson['data']['view']
            share=aidjson['data']['share']
            cnt_to(f'https://api.bilibili.com/x/player/pagelist?bvid={_id_}&jsonp=jsonp')
            cidreq=await AsyncHttpx.get(f'https://api.bilibili.com/x/player/pagelist?bvid={_id_}&jsonp=jsonp')
            cidjson=json.loads(cidreq.content)
            cid=cidjson['data'][0]['cid']
            title=cidjson['data'][0]['part']
            cnt_to(f'https://api.bilibili.com/x/player/online/total?aid={aid}&cid={cid}&bvid={bvid}')
            onlinereq=await AsyncHttpx.get(f'https://api.bilibili.com/x/player/online/total?aid={aid}&cid={cid}&bvid={bvid}')
            onlinejson=json.loads(onlinereq.content)
            online=onlinejson['data']['count']
            try:
                first_frame_link=cidjson['data'][-1]['first_frame']
            except:
                logger.warning('找不到封面地址')
                first_frame_link='https://cn.bing.com/th?id=1'
            first_frame=requests.get(first_frame_link).content
        elif _id_.startswith('av'):
            vtype=vts.VIDEO()
            aid=_id_.replace('av','')
            cnt_to(f'''https://api.bilibili.com/x/web-interface/archive/stat?aid={_id_.replace('av','')}''')
            bvidreq=await AsyncHttpx.get(f'''https://api.bilibili.com/x/web-interface/archive/stat?aid={_id_.replace('av','')}''')
            bvidjson=json.loads(bvidreq.content)
            bvid=bvidjson['data']['bvid']
            bvinfo=await bili_html_parse(f'https://www.bilibili.com/video/{bvid}')
            cover_link=bvinfo['videoData']['pic']
            up_name=bvinfo['videoData']['owner']['name']
            like=bvidjson['data']['like']
            danmaku=bvidjson['data']['danmaku']
            favorite=bvidjson['data']['favorite']
            coin=bvidjson['data']['coin']
            view=bvidjson['data']['view']
            share=bvidjson['data']['share']
            cnt_to(f'https://api.bilibili.com/x/player/pagelist?bvid={bvid}&jsonp=jsonp')
            cidreq=await AsyncHttpx.get(f'https://api.bilibili.com/x/player/pagelist?bvid={bvid}&jsonp=jsonp')
            cidjson=json.loads(cidreq.content)
            cid=cidjson['data'][0]['cid']
            title=cidjson['data'][0]['part']
            cnt_to(f'https://api.bilibili.com/x/player/online/total?aid={aid}&cid={cid}&bvid={bvid}')
            onlinereq=await AsyncHttpx.get(f'https://api.bilibili.com/x/player/online/total?aid={aid}&cid={cid}&bvid={bvid}')
            onlinejson=json.loads(onlinereq.content)
            online=onlinejson['data']['count']
            try:
                first_frame_link=cidjson['data'][-1]['first_frame']
            except:
                logger.warning('找不到首帧地址')
                first_frame_link='https://cn.bing.com/th?id=1'
            first_frame=requests.get(first_frame_link).content
        elif _id_.startswith('ss'):
            vtype=vts.BANGUMI
            return 301,'番剧剧集'
        elif _id_.startswith('ep'):
            vtype=vts.BANGUMI
            epinfo=await bili_html_parse('https://www.bilibili.com/bangumi/play/'+str(_id_))
            logger.info(f'{epinfo}')
            bvid=epinfo['epInfo']['bvid']
            title=epinfo['epInfo']['share_copy']
            bangumi_desc=epinfo['mediaInfo']['evaluate']
            bangumi_title=epinfo['mediaInfo']['season_title']
            cover_link='https:'+epinfo['mediaInfo']['cover']
            ssurl=epinfo['mediaInfo']['share_url']
            cnt_to(f'https://api.bilibili.com/x/web-interface/archive/stat?bvid={bvid}')
            aidreq=await AsyncHttpx.get(f'https://api.bilibili.com/x/web-interface/archive/stat?bvid={bvid}')
            aidjson=json.loads(aidreq.content)
            aid=aidjson['data']['aid']
            like=aidjson['data']['like']
            danmaku=aidjson['data']['danmaku']
            favorite=aidjson['data']['favorite']
            coin=aidjson['data']['coin']
            view=aidjson['data']['view']
            share=aidjson['data']['share']
            cnt_to(f'https://api.bilibili.com/x/player/pagelist?bvid={bvid}&jsonp=jsonp')
            cidreq=await AsyncHttpx.get(f'https://api.bilibili.com/x/player/pagelist?bvid={bvid}&jsonp=jsonp')
            cidjson=json.loads(cidreq.content)
            cid=cidjson['data'][0]['cid']
            cnt_to(f'https://api.bilibili.com/x/player/online/total?aid={aid}&cid={cid}&bvid={bvid}')
            onlinereq=await AsyncHttpx.get(f'https://api.bilibili.com/x/player/online/total?aid={aid}&cid={cid}&bvid={bvid}')
            onlinejson=json.loads(onlinereq.content)
            online=onlinejson['data']['count']
        else:
            return 400,'未知的指向id'
    elif type(vt) is dts.BV:
        cnt_to(f'https://api.bilibili.com/x/web-interface/archive/stat?bvid={bvid}')
        aidreq=await AsyncHttpx.get(f'https://api.bilibili.com/x/web-interface/archive/stat?bvid={bvid}')
        aidjson=json.loads(aidreq.content)
        bvinfo=await bili_html_parse(f'https://www.bilibili.com/video/{bvid}')
        cover_link=bvinfo['videoData']['pic']
        aid=aidjson['data']['aid']
        like=aidjson['data']['like']
        danmaku=aidjson['data']['danmaku']
        favorite=aidjson['data']['favorite']
        coin=aidjson['data']['coin']
        view=aidjson['data']['view']
        share=aidjson['data']['share']
        cnt_to(f'https://api.bilibili.com/x/player/pagelist?bvid={bvid}&jsonp=jsonp')
        cidreq=await AsyncHttpx.get(f'https://api.bilibili.com/x/player/pagelist?bvid={bvid}&jsonp=jsonp')
        cidjson=json.loads(cidreq.content)
        cid=cidjson['data'][0]['cid']
        title=cidjson['data'][0]['part']
        cnt_to(f'https://api.bilibili.com/x/player/online/total?aid={aid}&cid={cid}&bvid={bvid}')
        onlinereq=await AsyncHttpx.get(f'https://api.bilibili.com/x/player/online/total?aid={aid}&cid={cid}&bvid={bvid}')
        onlinejson=json.loads(onlinereq.content)
        online=onlinejson['data']['count']
        try:
            first_frame_link=cidjson['data'][-1]['first_frame']
        except:
            logger.warning('找不到首帧地址')
            first_frame_link='https://cn.bing.com/th?id=1'
        first_frame=requests.get(first_frame_link).content
    elif type(vt) is dts.av:
        cnt_to(f'https://api.bilibili.com/x/web-interface/archive/stat?aid={aid}')
        bvidreq=await AsyncHttpx.get(f'https://api.bilibili.com/x/web-interface/archive/stat?aid={aid}')
        bvidjson=json.loads(bvidreq.content)
        bvid=bvidjson['data']['bvid']
        bvinfo=await bili_html_parse(f'https://www.bilibili.com/video/{bvid}')
        cover_link=bvinfo['videoData']['pic']
        like=bvidjson['data']['like']
        danmaku=bvidjson['data']['danmaku']
        favorite=bvidjson['data']['favorite']
        coin=bvidjson['data']['coin']
        view=bvidjson['data']['view']
        share=bvidjson['data']['share']
        cnt_to(f'https://api.bilibili.com/x/player/pagelist?bvid={bvid}&jsonp=jsonp')
        cidreq=await AsyncHttpx.get(f'https://api.bilibili.com/x/player/pagelist?bvid={bvid}&jsonp=jsonp')
        cidjson=json.loads(cidreq.content)
        cid=cidjson['data'][0]['cid']
        title=cidjson['data'][0]['part']
        cnt_to(f'https://api.bilibili.com/x/player/online/total?aid={aid}&cid={cid}&bvid={bvid}')
        onlinereq=await AsyncHttpx.get(f'https://api.bilibili.com/x/player/online/total?aid={aid}&cid={cid}&bvid={bvid}')
        onlinejson=json.loads(onlinereq.content)
        online=onlinejson['data']['count']
        try:
            first_frame_link=cidjson['data'][-1]['first_frame']
        except:
            logger.warning('找不到首帧地址')
            first_frame_link='https://cn.bing.com/th?id=1'
        first_frame=requests.get(first_frame_link).content
    else:
        return 400,'未知的指向id'
    cover=requests.get(cover_link).content
    return 200,'''成功'''

async def bangumi_pre_get(vt):
    if type(vt) is dts.ss:
        pass

async def bili_html_parse(url):
    cnt_to(f'{url}')
    htmlreq=requests.get(f'{url}')
    soup=bs(htmlreq.content,features='lxml')
    allres=soup.find_all('script')
    for iss in range(len(allres)):
        try:
            sdjson=str(allres[iss]).replace('<script>window.__INITIAL_STATE__=','').replace(';(function(){var s;(s=document.currentScript||document.scripts[document.scripts.length-1]).parentNode.removeChild(s);}());</script>','')
            sddata=json.loads(sdjson)
            sd=allres[iss]
        except Exception as e:
            continue
    sdjson=str(sd).replace('<script>window.__INITIAL_STATE__=','').replace(';(function(){var s;(s=document.currentScript||document.scripts[document.scripts.length-1]).parentNode.removeChild(s);}());</script>','')
    data=json.loads(sdjson)
    return data
