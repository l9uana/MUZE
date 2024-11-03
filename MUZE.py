import discord
from discord.ext import commands
import yt_dlp
import asyncio

TOKEN = '아 섹스하고싶다'  # 실제 토큰으로 바꿔주세요

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)  # 원하는 프리픽스로 바꿔주세요 ('$', '!' 등등)

ydl_format = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

DEBUG = True  # 디버그 모드 설정
TYPE = "auto"  # 음성채널 입장 모드를 선택해주세요
VOICE_CHANNEL_ID = 6974892  # (fixed만 해당) 원하는 음성채널 ID로 설정해주세요
CHANNEL_NAME = "🎵MUZE"  # 원하는 채널 이름으로 설정해주세요

queue = []
current_song = None

@bot.event
async def on_ready():
    print(f'{bot.user} is ready!')

    guild = discord.utils.get(bot.guilds)  # 서버 가져오기
    channel = discord.utils.get(guild.text_channels, name=CHANNEL_NAME)  # 서버에 봇 메세지 채널 있는지 확인
    
    if channel is None:
        # 없으면 새로 파기
        channel = await guild.create_text_channel(CHANNEL_NAME)
        await channel.send('M!044 [MUZE 준비 완료-옷!!]') if DEBUG else await channel.send('MUZE 준비 완료-옷!!')
    else:
        await channel.send('M!046 [MUZE 준비 완료-옷!! (메세지 채널이 이미 존재합니다)]') if DEBUG else await channel.send('MUZE 준비 완료-옷!! (메세지 채널이 이미 존재합니다)')

@bot.command()
async def 재생(ctx, *, url):
    global queue, current_song

    if TYPE == "fixed":
        channel = bot.get_channel(VOICE_CHANNEL_ID)
    elif TYPE == "auto":
        channel = ctx.author.voice.channel if ctx.author.voice else None
    else:
        await ctx.send("M!057 [EXC057 - TYPE 변수가 잘못되었습니다. 'fixed' 또는 'auto'로 설정되어있는지 확인 바랍니다.]") if DEBUG else await ctx.send("EXC057 오류가 발생했습니다!")
        return

    if channel and isinstance(channel, discord.VoiceChannel):
        if ctx.voice_client is None:
            voice_client = await channel.connect()
        else:
            voice_client = ctx.voice_client

            if voice_client.channel != channel:
                await voice_client.move_to(channel)

        with yt_dlp.YoutubeDL(ydl_format) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                audio_url = info['url']
                title = info['title']

                queue.append((audio_url, title))

                embed = discord.Embed(title="대기열에 추가되었습니다!", description=title, color=0x5B33FF)
                embed.set_image(url=info.get('thumbnail'))
                embed.set_author(name="MUZE", icon_url=bot.user.avatar.url)

                await ctx.send(f'M!081 [{title}이 대기열에 추가되었습니다.]') if DEBUG else await ctx.send(embed=embed)

                if not voice_client.is_playing():
                    await play_next_song(voice_client, ctx)

            except Exception as e:
                await ctx.send(f"M!087 [EXC087 - {str(e)}]") if DEBUG else await ctx.send("EXC087 오류가 발생했습니다!")
    else:
        if TYPE == "auto":
            await ctx.send("M!090 [EXC090 - 유저가 음성 채널에 없습니다.]") if DEBUG else await ctx.send("EXC090 오류가 발생했습니다!")
        else:
            await ctx.send("M!092 [EXC092 - 잘못된 음성 채널 ID입니다.]") if DEBUG else await ctx.send("EXC092 오류가 발생했습니다!")

@bot.command()
async def 정지(ctx):
    if ctx.voice_client and ctx.voice_client.is_connected():
        queue.clear()
        await ctx.voice_client.disconnect()
        await ctx.send("M!099 [재생을 종료하고 대기열을 초기화했습니다!]") if DEBUG else await ctx.send('재생을 종료하고 대기열을 초기화했습니다!')
    else:
        await ctx.send("M!101 [EXC101 - 이미 음성 채널을 나가있습니다.]") if DEBUG else await ctx.send("EXC101 오류가 발생했습니다!")

async def play_next_song(voice_client, ctx):
    global queue, current_song
    if queue:
        current_song = queue[0]
        audio_url, title = current_song
        
        # Play the next song in the queue
        voice_client.play(discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS), after=lambda e: bot.loop.create_task(play_next_song(voice_client, ctx)))
        await ctx.send(f"M!111 [현재 재생 중: **{title}**]") if DEBUG else await ctx.send(f"현재 재생 중: **{title}**")
        
        queue.pop(0)
    else:
        await ctx.send("M!115 [대기열이 비어있습니다, 재생을 종료합니다.]") if DEBUG else await ctx.send("대기열이 비어있습니다, 재생을 종료합니다.")
        await voice_client.disconnect()
        
@bot.command()
async def 대기열(ctx):
    if queue:
        description = "\n".join([f"{idx + 1}. {title}" for idx, (_, title) in enumerate(queue)])
        if DEBUG:
            await ctx.send(f'M!123 대기열 목록:\n{description}')
        else:
            embed = discord.Embed(title="대기열 목록", description=description, color=0x5B33FF)
            embed.set_author(name="MUZE", icon_url=bot.user.avatar.url)
            await ctx.send(embed=embed)
    else:
        await ctx.send("M!129 [대기열이 비어있습니다.]") if DEBUG else await ctx.send("대기열이 비어있습니다.")

@bot.command()
async def 스킵(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("M!135 [현재 곡을 건너뜁니다...]") if DEBUG else await ctx.send("현재 곡을 건너뜁니다...")
        await play_next_song(ctx.voice_client, ctx)
    else:
        await ctx.send("M!138 [EXC138 - 재생 중인 곡이 없습니다.]") if DEBUG else await ctx.send("재생 중인 곡이 없습니다.")

bot.run(TOKEN)
