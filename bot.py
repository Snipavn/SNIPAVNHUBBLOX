import os
import re
import time
import threading
import requests
import logging
import discord
import asyncio
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# Load token từ .env
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger("discord_bot")

# Thông tin chiến dịch
QUEST_INFO = {
    "m88": {
        "url": "https://bet88ec.com/cach-danh-bai-sam-loc",
        "traffic": "https://bet88ec.com/",
        "codexn": "taodeptrai"
    },
    "fb88": {
        "url": "https://fb88mg.com/ty-le-cuoc-hong-kong-la-gi",
        "traffic": "https://fb88mg.com/",
        "codexn": "taodeptrai"
    },
    "188bet": {
        "url": "https://88betag.com/cach-choi-game-bai-pok-deng",
        "traffic": "https://88betag.com/",
        "codexn": "taodeptrailamnhe"
    },
    "w88": {
        "url": "https://188.166.185.213/tim-hieu-khai-niem-3-bet-trong-poker-la-gi",
        "traffic": "https://188.166.185.213/",
        "codexn": "taodeptrai"
    },
    "v9bet": {
        "url": "https://v9betxa.com/cach-choi-craps",
        "traffic": "https://v9betxa.com/",
        "codexn": "taodeptrai"
    }
}

# Kênh cho phép sử dụng lệnh
ALLOWED_CHANNEL_ID = 1393820443151962242  # ← Thay bằng ID kênh thật của bạn

# Khởi tạo bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logger.info(f'Bot đã online!! {bot.user.name}#{bot.user.discriminator} (ID: {bot.user.id})')
    
    try:
        synced = await bot.tree.sync()
        logger.info(f'Đã đồng bộ lệnh: {len(synced)} lệnh đã được đăng ký.')
        for command in synced:
            logger.info(f' - {command.name}: {command.description}')
    except Exception as e:
        logger.error(f'Lỗi khi đồng bộ lệnh: {e}')
    
    await bot.change_presence(
        activity=discord.Game(name="Hiha như con cặc!"),
        status=discord.Status.idle
    )
    logger.info('Bot đã sẵn sàng để dùng lệnh.')

# Hàm xử lý đếm ngược và gửi mã
def process_yeumoney_step(interaction: discord.Interaction, message_id: int, code: str):
    for remaining in range(75, 0, -5):
        try:
            asyncio.run_coroutine_threadsafe(
                interaction.edit_original_response(
                    content=f"⏳ Đang xử lý... vui lòng chờ {remaining} giây."
                ),
                bot.loop
            )
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật tin nhắn: {e}")
        time.sleep(5)

    asyncio.run_coroutine_threadsafe(
        interaction.edit_original_response(
            content=f"» **Mã của bạn là:**\n```{code}```\n🎉 Hãy nhập mã để anbatocom \nBot By [SNIPA VN](https://youtube.com/@snipavn205)."
        ),
        bot.loop
    )

# Tạo danh sách Choice từ QUEST_INFO
choices_list = [
    app_commands.Choice(name=name, value=name)
    for name in QUEST_INFO.keys()
]

# Slash command
@bot.tree.command(name="bypass_yeumoney", description="Nhập từ khoá như 188bet,m88,v9net,fb88,w88 để lấy mã")
@app_commands.describe(keyword="Chọn từ khoá 188bet,m88,v9net,fb88,w88 để lấy mã")
@app_commands.choices(keyword=choices_list)
async def bypass_yeumoney(interaction: discord.Interaction, keyword: app_commands.Choice[str]):
    if interaction.channel_id != ALLOWED_CHANNEL_ID:
        await interaction.response.send_message("❌ Lệnh này chỉ được dùng trong kênh <#1393820443151962242>.", ephemeral=True)
        return

    await interaction.response.defer(thinking=True)

    key = keyword.value
    info = QUEST_INFO.get(key)

    if not info:
        embed = discord.Embed(
            title="❌ Không thể lấy mã!",
            description='Từ khoá không hợp lệ. Vui lòng thử: 188bet, fb88, w88, v9bet...',
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        logger.warning(f"Từ khoá không hợp lệ: {key}")
        return

    try:
        response = requests.post(
            "https://traffic-user.net/GET_MA.php",
            params={
                "codexn": info["codexn"],
                "url": info["url"],
                "loai_traffic": info["traffic"],
                "clk": 1000
            }
        )

        match = re.search(r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>', response.text)
        if match:
            code = match.group(1)
            await interaction.followup.send(content="⏳ Đang xử lý... Vui lòng chờ!")
            threading.Thread(
                target=process_yeumoney_step,
                args=(interaction, interaction.id, code),
                daemon=True
            ).start()
        else:
            await interaction.followup.send("⚠️ Không tìm thấy mã.")
    except Exception as e:
        logger.error(f"Lỗi khi gửi yêu cầu: {e}")
        await interaction.followup.send(f"⚠️ Đã xảy ra lỗi: {e}")

# Khởi chạy bot
if __name__ == "__main__":
    if DISCORD_BOT_TOKEN:
        try:
            bot.run(DISCORD_BOT_TOKEN)
        except Exception as e:
            logger.critical(f"Không thể khởi chạy bot: {e}")
    else:
        logger.critical("Không tìm thấy DISCORD_BOT_TOKEN trong .env")
