from asyncio import QueueEmpty
from pyrogram import Client
from pyrogram import filters
from pyrogram.types import Message

from DaisyXMusic.config import que
from DaisyXMusic.function.admins import set
from DaisyXMusic.helpers.channelmusic import get_chat_id
from DaisyXMusic.helpers.decorators import authorized_users_only
from DaisyXMusic.helpers.decorators import errors
from DaisyXMusic.helpers.filters import command 
from DaisyXMusic.helpers.filters import other_filters
from DaisyXMusic.services.callsmusic import callsmusic
from DaisyXMusic.services.callsmusic.queues import queues


@Client.on_message(filters.command(["channelpause","cpause"]) & filters.group & ~filters.edited)
@errors
@authorized_users_only
async def pause(_, message: Message):
    try:
      conchat = await _.get_chat(message.chat.id)
      conid = conchat.linked_chat.id
      chid = conid
    except:
      await message.reply("ιѕ ¢нαт єνєη ℓιηкє∂")
      return    
    chat_id = chid
    if (chat_id not in callsmusic.active_chats) or (
        callsmusic.active_chats[chat_id] == "paused"
    ):
        await message.reply_text("❗ ησтнιηg ιѕ ѕтяєαмιηg!")
    else:
        callsmusic.pause(chat_id)
        await message.reply_text("▶️ ραυѕє∂!")


@Client.on_message(filters.command(["channelresume","cresume"]) & filters.group & ~filters.edited)
@errors
@authorized_users_only
async def resume(_, message: Message):
    try:
      conchat = await _.get_chat(message.chat.id)
      conid = conchat.linked_chat.id
      chid = conid
    except:
      await message.reply("ιѕ ¢нαт єνєη ℓιηкє∂")
      return    
    chat_id = chid
    if (chat_id not in callsmusic.active_chats) or (
        callsmusic.active_chats[chat_id] == "playing"
    ):
        await message.reply_text("❗ ησтнιηg ιѕ ραυѕє∂!")
    else:
        callsmusic.resume(chat_id)
        await message.reply_text("⏸ яєѕυмє∂!")


@Client.on_message(filters.command(["channelend","cend"]) & filters.group & ~filters.edited)
@errors
@authorized_users_only
async def stop(_, message: Message):
    try:
      conchat = await _.get_chat(message.chat.id)
      conid = conchat.linked_chat.id
      chid = conid
    except:
      await message.reply("ιѕ ¢нαт єνєη ℓιηкє∂")
      return    
    chat_id = chid
    if chat_id not in callsmusic.active_chats:
        await message.reply_text("❗ ησтнιηg ιѕ ѕтяєαмιηg!")
    else:
        try:
            queues.clear(chat_id)
        except QueueEmpty:
            pass

        await callsmusic.stop(chat_id)
        await message.reply_text("❌ ѕтσρρє∂ ѕтяєαмιηg!")


@Client.on_message(filters.command(["channelskip","cskip"]) & filters.group & ~filters.edited)
@errors
@authorized_users_only
async def skip(_, message: Message):
    global que
    try:
      conchat = await _.get_chat(message.chat.id)
      conid = conchat.linked_chat.id
      chid = conid
    except:
      await message.reply("ιѕ ¢нαт єνєη ℓιηкє∂")
      return    
    chat_id = chid
    if chat_id not in callsmusic.active_chats:
        await message.reply_text("❗ ησтнιηg ιѕ ρℓαуιηg тσ ѕкιρ!")
    else:
        queues.task_done(chat_id)

        if queues.is_empty(chat_id):
            await callsmusic.stop(chat_id)
        else:
            await callsmusic.set_stream(
                chat_id, 
                queues.get(chat_id)["file"]
            )

    qeue = que.get(chat_id)
    if qeue:
        skip = qeue.pop(0)
    if not qeue:
        return
    await message.reply_text(f"- Skipped **{skip[0]}**\n- Now Playing **{qeue[0][0]}**")


@Client.on_message(filters.command("channeladmincache"))
@errors
async def admincache(client, message: Message):
    try:
      conchat = await client.get_chat(message.chat.id)
      conid = conchat.linked_chat.id
      chid = conid
    except:
      await message.reply("ιѕ ¢нαт єνєη ℓιηкє∂")
      return
    set(
        chid,
        [
            member.user
            for member in await conchat.linked_chat.get_members(filter="administrators")
        ],
    )
    await message.reply_text("一═デ︻ ❇️ α∂мιη ¢α¢нє яєƒяєѕнє∂! ︻デ═一")
