import json
import os
from os import path
from typing import Callable

import aiofiles
import aiohttp
import ffmpeg
import requests
import wget
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.types import Voice
from pyrogram.errors import UserAlreadyParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from Python_ARQ import ARQ
from youtube_search import YoutubeSearch

from DaisyXMusic.config import ARQ_API_KEY
from DaisyXMusic.config import BOT_NAME as bn
from DaisyXMusic.config import DURATION_LIMIT
from DaisyXMusic.config import UPDATES_CHANNEL as updateschannel
from DaisyXMusic.config import que
from DaisyXMusic.function.admins import admins as a
from DaisyXMusic.helpers.admins import get_administrators
from DaisyXMusic.helpers.channelmusic import get_chat_id
from DaisyXMusic.helpers.errors import DurationLimitError
from DaisyXMusic.helpers.decorators import errors
from DaisyXMusic.helpers.decorators import authorized_users_only
from DaisyXMusic.helpers.filters import command, other_filters
from DaisyXMusic.helpers.gets import get_file_name
from DaisyXMusic.services.callsmusic import callsmusic, queues
from DaisyXMusic.services.callsmusic.callsmusic import client as USER
from DaisyXMusic.services.converter.converter import convert
from DaisyXMusic.services.downloaders import youtube

chat_id = None
arq = ARQ("https://thearq.tech", ARQ_API_KEY)


def cb_admin_check(func: Callable) -> Callable:
    async def decorator(client, cb):
        admemes = a.get(cb.message.chat.id)
        if cb.from_user.id in admemes:
            return await func(client, cb)
        else:
            await cb.answer("You ain't allowed!", show_alert=True)
            return

    return decorator


def transcode(filename):
    ffmpeg.input(filename).output(
        "input.raw", format="s16le", acodec="pcm_s16le", ac=2, ar="48k"
    ).overwrite_output().run()
    os.remove(filename)


# Convert seconds to mm:ss
def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))


# Change image size
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


async def generate_cover(requested_by, title, views, duration, thumbnail):
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open("background.png", mode="wb")
                await f.write(await resp.read())
                await f.close()

    image1 = Image.open("./background.png")
    image2 = Image.open("./etc/foreground.png")
    image3 = changeImageSize(1280, 720, image1)
    image4 = changeImageSize(1280, 720, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save("temp.png")
    img = Image.open("temp.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("etc/font.otf", 32)
    draw.text((205, 550), f"Title: {title}", (51, 215, 255), font=font)
    draw.text((205, 590), f"Duration: {duration}", (255, 255, 255), font=font)
    draw.text((205, 630), f"Views: {views}", (255, 255, 255), font=font)
    draw.text(
        (205, 670),
        f"Added By: {requested_by}",
        (255, 255, 255),
        font=font,
    )
    img.save("final.png")
    os.remove("temp.png")
    os.remove("background.png")


@Client.on_message(filters.command("ρℓαуℓιѕт") & filters.group & ~filters.edited)
async def ρℓαуℓιѕт(client, message):
    global que
    queue = que.get(message.chat.id)
    if not queue:
        await message.reply_text("ρℓαуєя ιѕ ι∂ℓє")
    temp = []
    for t in queue:
        temp.append(t)
    now_playing = temp[0][0]
    by = temp[0][1].mention(style="md")
    msg = "**ησω ρℓαуιηg** in {}".format(message.chat.title)
    msg += "\n- " + now_playing
    msg += "\n- яєq ву " + by
    temp.pop(0)
    if temp:
        msg += "\n\n"
        msg += "**qυєυє**"
        for song in temp:
            name = song[0]
            usr = song[1].mention(style="md")
            msg += f"\n- {name}"
            msg += f"\n- яєq ву {usr}\n"
    await message.reply_text(msg)


# ============================= Settings =========================================


def updated_stats(chat, queue, vol=100):
    if chat.id in callsmusic.pytgcalls.active_calls:
        # if chat.id in active_chats:
        stats = "Settings of **{}**".format(chat.title)
        if len(que) > 0:
            stats += "\n\n"
            stats += "νσℓυмє : {}%\n".format(vol)
            stats += "ѕσηgѕ ιη qυєυє : `{}`\n".format(len(que))
            stats += "ησω ρℓαуιηg : **{}**\n".format(queue[0][0])
            stats += "яєqυєѕтє∂ ву : {}".format(queue[0][1].mention)
    else:
        stats = None
    return stats


def r_ply(type_):
    if type_ == "play":
        pass
    else:
        pass
    mar = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⏹", "ℓєανє"),
                InlineKeyboardButton("⏸", "ρυѕє"),
                InlineKeyboardButton("▶️", "яєѕυмє"),
                InlineKeyboardButton("⏭", "ѕкιρ"),
            ],
            [
                InlineKeyboardButton("ρℓαуℓιѕт 📖", "ρℓαуℓιѕт"),
            ],
            [InlineKeyboardButton("❌ ¢ℓσѕє", "¢ℓѕ")],
        ]
    )
    return mar


@Client.on_message(filters.command("current") & filters.group & ~filters.edited)
async def ee(client, message):
    queue = que.get(message.chat.id)
    stats = updated_stats(message.chat, queue)
    if stats:
        await message.reply(stats)
    else:
        await message.reply("ησ ν¢ ιηѕтαη¢єѕ яυηηιηg ιη тнιѕ ¢нαт")


@Client.on_message(filters.command("player") & filters.group & ~filters.edited)
@authorized_users_only
async def settings(client, message):
    playing = None
    chat_id = get_chat_id(message.chat)
    if chat_id in callsmusic.pytgcalls.active_calls:
        playing = True
    queue = que.get(chat_id)
    stats = updated_stats(message.chat, queue)
    if stats:
        if playing:
            await message.reply(stats, reply_markup=r_ply("pause"))

        else:
            await message.reply(stats, reply_markup=r_ply("play"))
    else:
        await message.reply("ησ ν¢ ιηѕтαη¢єѕ яυηηιηg ιη тнιѕ ¢нαт")


@Client.on_callback_query(filters.regex(pattern=r"^(playlist)$"))
async def p_cb(b, cb):
    global que
    que.get(cb.message.chat.id)
    type_ = cb.matches[0].group(1)
    cb.message.chat.id
    cb.message.chat
    cb.message.reply_markup.inline_keyboard[1][0].callback_data
    if type_ == "playlist":
        queue = que.get(cb.message.chat.id)
        if not queue:
            await cb.message.edit("ρℓαуєя ιѕ ι∂ℓє")
        temp = []
        for t in queue:
            temp.append(t)
        now_playing = temp[0][0]
        by = temp[0][1].mention(style="md")
        msg = "**ησω ρℓαуιηg** in {}".format(cb.message.chat.title)
        msg += "\n- " + now_playing
        msg += "\n- яєq ву " + by
        temp.pop(0)
        if temp:
            msg += "\n\n"
            msg += "**qυєυє**"
            for song in temp:
                name = song[0]
                usr = song[1].mention(style="md")
                msg += f"\n- {name}"
                msg += f"\n- яєq ву {usr}\n"
        await cb.message.edit(msg)


@Client.on_callback_query(
    filters.regex(pattern=r"^(play|pause|skip|leave|puse|resume|menu|cls)$")
)
@cb_admin_check
async def m_cb(b, cb):
    global que
    if (
        cb.message.chat.title.startswith("Channel Music: ")
        and chat.title[14:].isnumeric()
    ):
        chet_id = int(chat.title[13:])
    else:
        chet_id = cb.message.chat.id
    qeue = que.get(chet_id)
    type_ = cb.matches[0].group(1)
    cb.message.chat.id
    m_chat = cb.message.chat

    the_data = cb.message.reply_markup.inline_keyboard[1][0].callback_data
    if type_ == "pause":
        if (chet_id not in callsmusic.pytgcalls.active_calls) or (
            callsmusic.pytgcalls.active_calls[chet_id] == "paused"
        ):
            await cb.answer("¢нαт ιѕ ησт ¢σηηє¢тє∂!", show_alert=True)
        else:
            callsmusic.pytgcalls.pause_stream(chet_id)

            await cb.answer("мυѕι¢ ραυѕє∂!")
            await cb.message.edit(
                updated_stats(m_chat, qeue), reply_markup=r_ply("play")
            )

    elif type_ == "play":
        if (chet_id not in callsmusic.pytgcalls.active_calls) or (
            callsmusic.pytgcalls.active_calls[chet_id] == "playing"
        ):
            await cb.answer("¢нαт ιѕ ησт ¢σηηє¢тє∂!", show_alert=True)
        else:
            callsmusic.pytgcalls.яєѕυмє_stream(chet_id)
            await cb.answer("мυѕι¢ яєѕυмєd!")
            await cb.message.edit(
                updated_stats(m_chat, qeue), reply_markup=r_ply("pause")
            )

    elif type_ == "ρℓαуℓιѕт":
        queue = que.get(cb.message.chat.id)
        if not queue:
            await cb.message.edit("ρℓαуєя ιѕ ι∂ℓє")
        temp = []
        for t in queue:
            temp.append(t)
        now_playing = temp[0][0]
        by = temp[0][1].mention(style="md")
        msg = "**ησω ρℓαуιηg** in {}".format(cb.message.chat.title)
        msg += "\n- " + now_playing
        msg += "\n- яєq ву " + by
        temp.pop(0)
        if temp:
            msg += "\n\n"
            msg += "**qυєυє**"
            for song in temp:
                name = song[0]
                usr = song[1].mention(style="md")
                msg += f"\n- {name}"
                msg += f"\n- яєq ву {usr}\n"
        await cb.message.edit(msg)

    elif type_ == "яєѕυмє":
        if (chet_id not in callsmusic.pytgcalls.active_calls) or (
            callsmusic.pytgcalls.active_calls[chet_id] == "playing"
        ):
            await cb.answer("¢нαт ιѕ ησт ¢σηηє¢тє∂ σя αℓяєα∂у ρℓαуηg", show_alert=True)
        else:
            callsmusic.pytgcalls.яєѕυмє_stream(chet_id)
            await cb.answer("Music яєѕυмєd!")
    elif type_ == "ρυѕє":
        if (chet_id not in callsmusic.pytgcalls.active_calls) or (
            callsmusic.pytgcalls.active_calls[chet_id] == "paused"
        ):
            await cb.answer("¢нαт ιѕ ησт ¢σηηє¢тє∂ σя αℓяєα∂у ραυѕє∂", show_alert=True)
        else:
            callsmusic.pytgcalls.pause_stream(chet_id)

            await cb.answer("мυѕι¢ ραυѕє∂!")
    elif type_ == "cls":
        await cb.answer("¢ℓσѕєd мєηυ")
        await cb.message.delete()

    elif type_ == "menu":
        stats = updated_stats(cb.message.chat, qeue)
        await cb.answer("мєηυ σρєηє∂")
        marr = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⏹", "ℓєανє"),
                    InlineKeyboardButton("⏸", "ρυѕє"),
                    InlineKeyboardButton("▶️", "яєѕυмє"),
                    InlineKeyboardButton("⏭", "ѕкιρ"),
                ],
                [
                    InlineKeyboardButton("ρℓαуℓιѕт 📖", "ρℓαуℓιѕт"),
                ],
                [InlineKeyboardButton("❌ ¢ℓσѕє", "cls")],
            ]
        )
        await cb.message.edit(stats, reply_markup=marr)
    elif type_ == "skip":
        if qeue:
            qeue.pop(0)
        if chet_id not in callsmusic.pytgcalls.active_calls:
            await cb.answer("¢нαт ιѕ ησт ¢σηηє¢тє∂!", show_alert=True)
        else:
            callsmusic.queues.task_done(chet_id)

            if callsmusic.queues.is_empty(chet_id):
                callsmusic.pytgcalls.ℓєανє_group_call(chet_id)

                await cb.message.edit("- No More ρℓαуℓιѕт..\n- ℓєανιηg ν¢!")
            else:
                callsmusic.pytgcalls.change_stream(
                    chet_id, callsmusic.queues.get(chet_id)["file"]
                )
                await cb.answer("ѕкιρped")
                await cb.message.edit((m_chat, qeue), reply_markup=r_ply(the_data))
                await cb.message.reply_text(
                    f"- ѕкιρped тяα¢к\n- ησω ρℓαуιηg **{qeue[0][0]}**"
                )

    else:
        if chet_id in callsmusic.pytgcalls.active_calls:
            try:
                callsmusic.queues.clear(chet_id)
            except QueueEmpty:
                pass

            callsmusic.pytgcalls.ℓєανє_group_call(chet_id)
            await cb.message.edit("ѕυ¢¢єѕѕƒυℓℓу ℓєƒт тнє ¢нαт!")
        else:
            await cb.answer("¢нαт ιѕ ησт ¢σηηє¢тє∂!", show_alert=True)


@Client.on_message(command("play") & other_filters)
async def play(_, message: Message):
    global que
    lel = await message.reply("🔄 **ρяσ¢єѕѕιηg**")
    administrators = await get_administrators(message.chat)
    chid = message.chat.id

    try:
        user = await USER.get_me()
    except:
        user.first_name = "helper"
    usar = user
    wew = usar.id
    try:
        # chatdetails = await USER.get_chat(chid)
        await _.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message.from_user.id:
                if message.chat.title.startswith("Channel Music: "):
                    await lel.edit(
                        "<b>яємємвєя тσ α∂∂ нєℓρєя тσ уσυя ¢нαηηєℓ</b>",
                    )
                    pass
                try:
                    invitelink = await _.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "<b>α∂∂ мє αѕ α∂мιη σƒ уσя gяσυρ ƒιяѕт</b>",
                    )
                    return

                try:
                    await USER.join_chat(invitelink)
                    await USER.send_message(
                        message.chat.id, "ι נσιηє∂ тнιѕ gяσυρ ƒσя ρℓαуιηg мυѕι¢ ιη ν¢"
                    )
                    await lel.edit(
                        "<b>нєℓρєя υѕєявσт נσιηє∂ уσυя ¢нαт</b>",
                    )

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    # print(e)
                    await lel.edit(
                        f"<b>🔴 ƒℓσσ∂ ωαιт єяяσя 🔴 \ηυѕєя [Userbot](https://t.me/lightningmujik) ¢συℓ∂η'т נσιη уσυя gяσυρ ∂υє тσ нєανу яєqυєѕтѕ ƒσя υѕєявσт! мαкє ѕυяє υѕєя ιѕ ησт вαηηє∂ ιη gяσυρ."                         
                        "\η\ησя мαηυαℓℓу α∂∂ αѕѕιѕтαηт тσ уσυя gяσυρ αη∂ тяу αgαιη</b>",
                    )
    try:
        await USER.get_chat(chid)
        # lmoa = await client.get_chat_member(chid,wew)
    except:
        await lel.edit(
            f"<i> {user.first_name} υѕєявσт ησт ιη тнιѕ ¢нαт, αѕк α∂мιη тσ ѕєη∂ /υѕєявσтנσιη ¢σммαη∂ ƒσя ƒιяѕт тιмє σя α∂∂ [𝕌𝕤𝕖𝕣𝕓𝕠𝕥](https://t.me/lightningmujik) мαηυαℓℓу</i>"
        )
        return
    message.from_user.id
    message.from_user.first_name
    await lel.edit("🔎 **ƒιη∂ιηg**")
    message.from_user.id
    user_id = message.from_user.id
    message.from_user.first_name
    user_name = message.from_user.first_name
    rpk = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    audio = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"❌ νι∂єσѕ ℓσηgєя тнαη {DURATION_LIMIT} мιηυтє(ѕ) αяєη'т αℓℓσωє∂ тσ ρℓαу!"
            )
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📖 ρℓαуℓιѕт", callback_data="ρℓαуℓιѕт"),
                    InlineKeyboardButton("Menu ⏯ ", callback_data="мєηυ"),
                ],
                [InlineKeyboardButton(text="❌ ¢ℓσѕє", callback_data="cls")],
            ]
        )
        file_name = get_file_name(audio)
        title = file_name
        thumb_name = "https://telegra.ph/file/b0c914fae86cb425793c3.jpg"
        thumbnail = thumb_name
        duration = round(audio.duration / 60)
        views = "Locally added"
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await converter.convert(
            (await message.reply_to_message.download(file_name))
            if not path.isfile(path.join("downloads", file_name))
            else file_name
        )
    else:
        query = ""
        for i in message.command[1:]:
            query += " " + str(i)
        print(query)
        await lel.edit("🎵 **ρяσ¢єѕѕιηg**")
        ydl_opts = {"format": "bestaudio[ext=m4a]"}
        try:
            results = YoutubeSearch(query, max_results=1).to_dict()
            url = f"https://youtube.com{results[0]['url_suffix']}"
            # print(results)
            title = results[0]["title"][:40]
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f"thumb{title}.jpg"
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)
            duration = results[0]["duration"]
            results[0]["url_suffix"]
            views = results[0]["views"]

        except Exception as e:
            await lel.edit(
                "ѕσηg ησт ƒσυη∂.тяу αησтнєя ѕσηg σя мαувє ѕρєℓℓ ιт ρяσρєяℓу."
            )
            print(str(e))
            return

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📖 ρℓαуℓιѕт", callback_data="ρℓαуℓιѕт"),
                    InlineKeyboardButton("мєηυ ⏯ ", callback_data="menu"),
                ],
                [InlineKeyboardButton(text="Watch On YouTube 🎬", url=f"{url}")],
                [InlineKeyboardButton(text="❌ ¢ℓσѕє", callback_data="cls")],
            ]
        )
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await convert(youtube.download(url))
    chat_id = get_chat_id(message.chat)
    if chat_id in callsmusic.pytgcalls.active_calls:
        position = await queues.put(chat_id, file=file_path)
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        await message.reply_photo(
            photo="final.png",
            caption=f"#⃣ уσυя яєqυєѕтє∂ ѕσηg **qυєυє∂** αт ρσѕιтιση {position}!",
            reply_markup=keyboard,
        )
        os.remove("final.png")
        return await lel.delete()
    else:
        chat_id = get_chat_id(message.chat)
        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        try:
            callsmusic.pytgcalls.join_group_call(chat_id, file_path)
        except:
            message.reply("gяσυρ ¢αℓℓ ιѕ ησт ¢σηηє¢тє∂ σя ι ¢αη'т נσιη ιт")
            return
        await message.reply_photo(
            photo="final.png",
            reply_markup=keyboard,
            caption="▶️ **ρℓαуιηg** нєяє тнє ѕσηg яєqυєѕтє∂ ву {} νια уσυтυвє мυѕι¢ 😜".format(
                message.from_user.mention()
            ),
        )
        os.remove("final.png")
        return await lel.delete()


@Client.on_message(filters.command("dplay") & filters.group & ~filters.edited)
async def deezer(client: Client, message_: Message):
    global que
    lel = await message_.reply("🔄 **ρяσ¢єѕѕιηg**")
    administrators = await get_administrators(message_.chat)
    chid = message_.chat.id
    try:
        user = await USER.get_me()
    except:
        user.first_name = "[𝕌𝕤𝕖𝕣𝕓𝕠𝕥](https://t.me/lightningmujik)"
    usar = user
    wew = usar.id
    try:
        # chatdetails = await USER.get_chat(chid)
        await client.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message_.from_user.id:
                if message_.chat.title.startswith("Channel Music: "):
                    await lel.edit(
                        "<b>яємємвєя тσ α∂∂ нєℓρєя тσ уσυя ¢нαηηєℓ</b>",
                    )
                    pass
                try:
                    invitelink = await client.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "<b>α∂∂ мє αѕ α∂мιη σƒ уσя gяσυρ ƒιяѕт</b>",
                    )
                    return

                try:
                    await USER.join_chat(invitelink)
                    await USER.send_message(
                        message_.chat.id, "ι נσιηє∂ тнιѕ gяσυρ ƒσя ρℓαуιηg мυѕι¢ ιη ν¢"
                    )
                    await lel.edit(
                        "<b>нєℓρєя υѕєявσт נσιηє∂ уσυя ¢нαт</b>",
                    )

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    # print(e)
                    await lel.edit(
                        f"<b>🔴 ƒℓσσ∂ ωαιт єяяσя 🔴 \ηυѕєя {user.first_name} ¢συℓ∂η'т נσιη уσυя gяσυρ ∂υє тσ нєανу яєqυєѕтѕ ƒσя υѕєявσт! мαкє ѕυяє υѕєя ιѕ ησт вαηηє∂ ιη gяσυρ."                         
                        "\η\ησя мαηυαℓℓу α∂∂ αѕѕιѕтαηт тσ уσυя gяσυρ αη∂ тяу αgαιη</b>",
                    )
    try:
        await USER.get_chat(chid)
        # lmoa = await client.get_chat_member(chid,wew)
    except:
        await lel.edit(
            f"<i> {user.first_name} υѕєявσт ησт ιη тнιѕ ¢нαт, αѕк α∂мιη тσ ѕєη∂ /υѕєявσтנσιη ¢σммαη∂ ƒσя ƒιяѕт тιмє σя α∂∂ {user.first_name} мαηυαℓℓу</i>"
        )
        return
    requested_by = message_.from_user.first_name

    text = message_.text.split(" ", 1)
    queryy = text[1]
    res = lel
    await res.edit(f"ѕєαя¢нιηg 👀👀👀 ƒσя __{queryy}__ ση ∂єєzєя")
    try:
        songs = await arq.deezer(query=queryy, limit=1)
        if not songs.ok:
            await message_.reply_text(songs.result)
            return
        title = songs.result[0].title
        url = songs.result[0].url
        artist = songs.result[0].artist
        duration = int(songs.result[0].duration)
        thumbnail = songs.result[0].thumbnail

    except:
        await res.edit("ƒσυη∂ ℓιтєяαℓℓу ησтнιηg, уσυ ѕнσυℓ∂ ωσяк ση уσυя єηgℓιѕн!")
        return
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📖 ρℓαуℓιѕт", callback_data="ρℓαуℓιѕт"),
                InlineKeyboardButton("Menu ⏯ ", callback_data="menu"),
            ],
            [InlineKeyboardButton(text="Listen ση ∂єєzєя 🎬", url=f"{url}")],
            [InlineKeyboardButton(text="❌ ¢ℓσѕє", callback_data="cls")],
        ]
    )
    file_path = await convert(wget.download(url))
    await res.edit("gєηєяαтιηg тнυмвηαιℓ")
    await generate_cover(requested_by, title, artist, duration, thumbnail)
    chat_id = get_chat_id(message_.chat)
    if chat_id in callsmusic.pytgcalls.active_calls:
        await res.edit("α∂∂ιηg ιη qυєυє")
        position = await queues.put(chat_id, file=file_path)
        qeue = que.get(chat_id)
        s_name = title
        r_by = message_.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        await res.edit_text(f"✯{bn}✯= #️⃣ qυєυє∂ αт ρσѕιтιση {position}")
    else:
        await res.edit_text(f"✯{bn}✯=▶️ ρℓαуιηg.....")

        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = title
        r_by = message_.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        try:
            callsmusic.pytgcalls.join_group_call(chat_id, file_path)
        except:
            res.edit("gяσυρ ¢αℓℓ ιѕ ησт ¢σηηє¢тє∂ σƒ ι ¢αη'т נσιη ιт")
            return

    await res.delete()

    m = await client.send_photo(
        chat_id=message_.chat.id,
        reply_markup=keyboard,
        photo="final.png",
        caption=f"ρℓαуιηg [{title}]({url})νια ∂єєzєя",
    )
    os.remove("final.png")


@Client.on_message(filters.command("splay") & filters.group & ~filters.edited)
async def jiosaavn(client: Client, message_: Message):
    global que
    lel = await message_.reply("🔄 **ρяσ¢єѕѕιηg**")
    administrators = await get_administrators(message_.chat)
    chid = message_.chat.id
    try:
        user = await USER.get_me()
    except:
        user.first_name = "Lightningmujik"
    usar = user
    wew = usar.id
    try:
        # chatdetails = await USER.get_chat(chid)
        await client.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message_.from_user.id:
                if message_.chat.title.startswith("Channel Music: "):
                    await lel.edit(
                        "<b>яємємвєя тσ α∂∂ нєℓρєя тσ уσυя ¢нαηηєℓ</b>",
                    )
                    pass
                try:
                    invitelink = await client.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "<b>α∂∂ мє αѕ α∂мιη σƒ уσя gяσυρ ƒιяѕт</b>",
                    )
                    return

                try:
                    await USER.join_chat(invitelink)
                    await USER.send_message(
                        message_.chat.id, "ι נσιηє∂ тнιѕ gяσυρ ƒσя ρℓαуιηg мυѕι¢ ιη ν¢"
                    )
                    await lel.edit(
                        "<b>нєℓρєя υѕєявσт נσιηє∂ уσυя ¢нαт</b>",
                    )

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    # print(e)
                    await lel.edit(
                        f"<b>🔴 ƒℓσσ∂ ωαιт єяяσя 🔴 \ηυѕєя {user.firstname} ¢συℓ∂η'т נσιη уσυя gяσυρ ∂υє тσ нєανу яєqυєѕтѕ ƒσя υѕєявσт! мαкє ѕυяє υѕєя ιѕ ησт вαηηє∂ ιη gяσυρ."                         
                        "\η\ησя мαηυαℓℓу α∂∂ αѕѕιѕтαηт тσ уσυя gяσυρ αη∂ тяу αgαιη</b>",
                    )
    try:
        await USER.get_chat(chid)
        # lmoa = await client.get_chat_member(chid,wew)
    except:
        await lel.edit(
            "<i> нєℓρєя υѕєявσт ησт ιη тнιѕ ¢нαт, αѕк α∂мιη тσ ѕєη∂ /ρℓαу ¢σммαη∂ ƒσя ƒιяѕт тιмє σя α∂∂ αѕѕιѕтαηт мαηυαℓℓу</i>"
        )
        return
    requested_by = message_.from_user.first_name
    chat_id = message_.chat.id
    text = message_.text.split(" ", 1)
    query = text[1]
    res = lel
    await res.edit(f"ѕєαя¢нιηg 👀👀👀 ƒσя `{query}` ση נισ ѕαανη")
    try:
        songs = await arq.saavn(query)
        if not songs.ok:
            await message_.reply_text(songs.result)
            return
        sname = songs.result[0].song
        slink = songs.result[0].media_url
        ssingers = songs.result[0].singers
        sthumb = songs.result[0].image
        sduration = int(songs.result[0].duration)
    except Exception as e:
        await res.edit("ƒσυη∂ ℓιтєяαℓℓу ησтнιηg!, уσυ ѕнσυℓ∂ ωσяк ση уσυя єηgℓιѕн.")
        print(str(e))
        return
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📖 ρℓαуℓιѕт", callback_data="ρℓαуℓιѕт"),
                InlineKeyboardButton("Menu ⏯ ", callback_data="menu"),
            ],
            [
                InlineKeyboardButton(
                    text="נσιη υρ∂αтєѕ ¢нαηηєℓ", url=f"{updateschannel}"
                )
            ],
            [InlineKeyboardButton(text="❌ ¢ℓσѕє", callback_data="cls")],
        ]
    )
    file_path = await convert(wget.download(slink))
    chat_id = get_chat_id(message_.chat)
    if chat_id in callsmusic.pytgcalls.active_calls:
        position = await queues.put(chat_id, file=file_path)
        qeue = que.get(chat_id)
        s_name = sname
        r_by = message_.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        await res.delete()
        m = await client.send_photo(
            chat_id=message_.chat.id,
            reply_markup=keyboard,
            photo="final.png",
            caption=f"✯{bn}✯=#️⃣ qυєυє∂ αт ρσѕιтιση {position}",
        )

    else:
        await res.edit_text(f"{bn}=▶️ ρℓαуιηg.....")
        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = sname
        r_by = message_.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        try:
            callsmusic.pytgcalls.join_group_call(chat_id, file_path)
        except:
            res.edit("gяσυρ ¢αℓℓ ιѕ ησт ¢σηηє¢тє∂ σƒ ι ¢αη'т נσιη ιт")
            return
    await res.edit("gєηєяαтιηg тнυмвηαιℓ.")
    await generate_cover(requested_by, sname, ssingers, sduration, sthumb)
    await res.delete()
    m = await client.send_photo(
        chat_id=message_.chat.id,
        reply_markup=keyboard,
        photo="final.png",
        caption=f"ρℓαуιηg {sname} ση נισ ѕαανη",
    )
    os.remove("final.png")
