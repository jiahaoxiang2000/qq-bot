from ncatbot.core import BotClient
from ncatbot.core.message import GroupMessage, PrivateMessage
from ncatbot.utils.config import config
from ncatbot.utils.logger import get_log
import os
from dotenv import load_dotenv
from utils.spam_filter import is_advertising_in_segments

# Load environment variables from .env file if present
load_dotenv()

_log = get_log()

# Get configuration from environment variables with defaults
bot_uin = os.getenv("BOT_UIN", "123456")  # 设置 bot qq 号 (必填)
ws_uri = os.getenv("WS_URI", "ws://localhost:3001")  # 设置 napcat websocket server 地址
token = os.getenv("BOT_TOKEN", "")  # 设置 token (napcat 服务器的 token)

config.set_bot_uin(bot_uin)
config.set_ws_uri(ws_uri)
config.set_token(token)

bot = BotClient()


@bot.group_event()
async def on_group_message(msg: GroupMessage):
    """Asynchronous handler for group messages.

    Processes messages received in groups where the bot is present.

    Parameters
    ----------
    msg : GroupMessage
        The received group message containing:
        - `sender`: Information about who sent the message, have the user_id, nickname, etc.
        - `content`: The actual message content
        - `message`: array of message segments, for meeting the OneBot11 standard
        - `group_id`: The group where the message was sent
        - And other metadata

    Notes
    -----
    See the official documentation for complete message structure:
    https://docs.ncatbot.xyz/guide/iloveseu/#%E5%9B%9E%E8%B0%83%E5%87%BD%E6%95%B0%E5%8F%82%E6%95%B0
    """
    _log.info(msg)

    # Check for advertising in message segments
    if hasattr(msg, "message") and is_advertising_in_segments(msg.message):
        _log.warning(
            f"Detected advertising in group {msg.group_id} from {msg.sender.user_id}. Deleting message."
        )
        await bot.api.delete_msg(msg.message_id)

        # Optionally, you can send a warning to the group
        await bot.api.post_group_msg(msg.group_id, text="请不要发送广告内容⚡️")

        # Optionally, you can kick the user if they're persistent
        # await bot.api.kick_group_member(msg.group_id, msg.sender.user_id)

        return


@bot.private_event()
async def on_private_message(msg: PrivateMessage):
    _log.info(msg)
    if msg.raw_message == "测试":
        await bot.api.post_private_msg(msg.user_id, text="Bot Isomo is work ~^~")


# async def on_notice_message(msg):
#     _log.info(msg)

# async def on_request_message(msg):
#     _log.info(msg)

# bot.notice_event(on_notice_message)
# bot.request_event(on_request_message)

if __name__ == "__main__":
    bot.run()
