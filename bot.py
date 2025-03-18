import logging
from telethon import TelegramClient, events
from telethon.tl.types import PeerUser

# ================== 用户配置区域 ==================
API_ID = 20442170  # 在此填入你的API_ID
API_HASH = 'f53931d13b7c71549c5ab8ac83639095'  # 在此填入你的API_HASH
KEYWORDS = ["群发", "代发", "助手"]  # 触发关键词列表
RESPONSE_TEXT = '''您好，24小时全天群聊监听机器人
请联系三元 @sanyuan2004 获取免费试用资格
回复【STOP】取消订阅'''  # 私信内容
# ================== 配置结束 ======================

# 初始化日志系统
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('monitor.log')
    ]
)
logger = logging.getLogger('TG-Monitor')

class BotManager:
    def __init__(self):
        self.client = TelegramClient(
            session='monitor_session',
            api_id=API_ID,
            api_hash=API_HASH
        )
        self.keywords = [kw.lower() for kw in KEYWORDS]
        self.sent_users = set()  # 已发送用户记录

        # 注册事件处理器
        self.client.add_event_handler(
            self.message_handler,
            events.NewMessage(incoming=True)
        )

    async def message_handler(self, event):
        # 排除非群组消息和自身消息
        if not event.is_group or event.out:
            return

        # 消息预处理
        msg = event.message.text.lower().strip()
        sender = await event.get_sender()
        
        # 关键词匹配检查
        if any(kw in msg for kw in self.keywords):
            logger.info(f"检测到关键词触发 - 用户ID: {sender.id}")

            # 防止重复发送
            if sender.id in self.sent_users:
                return

            try:
                # 发送私信
                await self.client.send_message(
                    entity=sender.id,
                    message=RESPONSE_TEXT
                )
                self.sent_users.add(sender.id)
                logger.info(f"成功发送私信至用户 {sender.id}")

            except Exception as e:
                logger.error(f"发送失败: {str(e)}")
                if "隐私设置" in str(e):
                    logger.warning("该用户禁止陌生人消息")

    async def start(self):
        await self.client.start()
        logger.info("""
        ====================================
        监听程序已启动！
        登录账号: {} (ID: {})
        监听关键词: {}
        ====================================
        """.format(
            (await self.client.get_me()).username,
            (await self.client.get_me()).id,
            ', '.join(KEYWORDS)
        ))
        await self.client.run_until_disconnected()

if __name__ == '__main__':
    bot = BotManager()
    try:
        bot.client.loop.run_until_complete(bot.start())
    except KeyboardInterrupt:
        logger.info("程序已手动终止")
    except Exception as e:
        logger.error(f"致命错误: {str(e)}")