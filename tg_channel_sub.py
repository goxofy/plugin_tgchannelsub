#import re
#import requests
import schedule
import threading
import feedparser
import time
from bs4 import BeautifulSoup
#from lxml import etree
from plugins import register, Plugin, Event, logger, Reply, ReplyType
from utils.api import send_txt

@register
class TgChannelSub(Plugin):
    name = "tgchannelsub"

    def __init__(self, config: dict):
        super().__init__(config)
        # 获取rss地址
        self.rss_url = self.config.get("rssurl")  # 将 rss_url 作为实例变量
        # 存储rss已有项目的链接
        self.processed_links = set()
        # 获取初始的 RSS 订阅内容，跳过处理
        feed = feedparser.parse(self.rss_url)
        #print(feed)
        for entry in feed.entries:
            self.processed_links.add(entry.link)
            print(entry.link)
        
        scheduler_thread = threading.Thread(target=self.start_schedule)
        scheduler_thread.start()

    def did_receive_message(self, event: Event):
        pass

    def will_generate_reply(self, event: Event):
        pass

    def will_decorate_reply(self, event: Event):
        pass

    def will_send_reply(self, event: Event):
        pass

    def help(self, **kwargs) -> str:
        return "TG 频道订阅"

    def start_schedule(self):
        schedule.every().minute.do(self.auto_send)
        #while True:
        #    schedule.run_pending()
        #    time.sleep(600)

    def auto_send(self):
        logger.info("Start TG Channel Sub Auto Send")
        single_chat_list = self.config.get("single_chat_list", [])
        group_chat_list = self.config.get("group_chat_list", [])
        content = self.tg_channel_msg()
        for single_chat in single_chat_list:
            send_txt(content, single_chat)
            time.sleep(1)
        for group_chat in group_chat_list:
            send_txt(content, group_chat)
            time.sleep(1)

    def tg_channel_msg(self) -> str:
        
        formatted_msg = ""
        
        try:
            # 解析 RSS 订阅
            feed = feedparser.parse(self.rss_url)
    
            # 遍历订阅的条目，获取最新的消息
            for entry in feed.entries:
                # 获取消息链接
                entry_link = entry.link
    
                # 如果链接不在已获取消息的集合中，处理消息并添加到集合中
                if entry_link not in self.processed_links:
                    self.processed_links.add(entry.link)  # 使用成员变量
                    print(f"{entry.link} added to the processed list")
    
                    # 获取消息标题和描述
                    entry_title = entry.title
                    entry_description = BeautifulSoup(entry.description, 'html.parser').get_text()
    
                    # 打印消息标题和描述
                    #print("标题:", entry_title)
                    #print("描述:", entry_description)
                    #print("=" * 40)
                    formatted_msg += f"{entry_title} : {entry_description} \n\n\n"
                    print(formatted_msg)

        except Exception as e:
            logger.error(f"Error occurred while fetching tg channel msg: {str(e)}")
        return formatted_msg