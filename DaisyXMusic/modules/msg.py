import os
from DaisyXMusic.config import SOURCE_CODE,ASSISTANT_NAME,PROJECT_NAME,SUPPORT_GROUP,UPDATES_CHANNEL
class Messages():
      START_MSG = "**нєℓℓσ 👋 [{}](tg://user?id={})!**\n\n🤖 ι αм αη α∂ναη¢є∂ вσт ¢яєαтє∂ ƒσя ρℓαуιηg мυѕι¢ ιη тнє νσι¢є ¢нαтѕ σƒ тєℓєgяαм gяσυρѕ & ¢нαηηєℓѕ.\n\n✅ ѕєη∂ мє /help ƒσя мσяє ιηƒσ."
      HELP_MSG = [
        ".",
f"""
**нєу 👋 ωєℓ¢σмє вα¢к тσ {PROJECT_NAME}
⚪️ {PROJECT_NAME} ¢αη ρℓαу мυѕι¢ ιη уσυя gяσυρ'ѕ νσι¢є ¢нαт αѕ ωєℓℓ αѕ ¢нαηηєℓ νσι¢є ¢нαтѕ
⚪️ αѕѕιѕтαηт ηαмє >> @{ASSISTANT_NAME}\n\n¢ℓι¢к ηєχт ƒσя ιηѕтяυ¢тισηѕ**
""",

f"""
**ѕєттιηg υρ**
1) 𝐌𝐚𝐤𝐞 𝐛𝐨𝐭 𝐚𝐝𝐦𝐢𝐧 (𝐆𝐫𝐨𝐮𝐩 𝐚𝐧𝐝 𝐢𝐧 𝐜𝐡𝐚𝐧𝐧𝐞𝐥 𝐢𝐟 𝐮𝐬𝐞 𝐜𝐩𝐥𝐚𝐲)
2) 𝐒𝐭𝐚𝐫𝐭 𝐚 𝐯𝐨𝐢𝐜𝐞 𝐜𝐡𝐚𝐭
3) 𝐓𝐫𝐲 /play [𝐬𝐨𝐧𝐠 𝐧𝐚𝐦𝐞] 𝐟𝐨𝐫 𝐭𝐡𝐞 𝐟𝐢𝐫𝐬𝐭 𝐭𝐢𝐦𝐞 𝐛𝐲 𝐚𝐧 𝐚𝐝𝐦𝐢𝐧
*) 𝐈𝐟 𝐮𝐬𝐞𝐫𝐛𝐨𝐭 𝐣𝐨𝐢𝐧𝐞𝐝 𝐞𝐧𝐣𝐨𝐲 𝐦𝐮𝐬𝐢𝐜, 𝐈𝐟 𝐧𝐨𝐭 𝐚𝐝𝐝 @{ASSISTANT_NAME} 𝐭𝐨 𝐲𝐨𝐮𝐫 𝐠𝐫𝐨𝐮𝐩 𝐚𝐧𝐝 𝐫𝐞𝐭𝐫𝐲
**ƒσя ¢нαηηєℓ мυѕι¢ ρℓαу**
1) 𝐌𝐚𝐤𝐞 𝐦𝐞 𝐚𝐝𝐦𝐢𝐧 𝐨𝐟 𝐲𝐨𝐮𝐫 𝐜𝐡𝐚𝐧𝐧𝐞𝐥
2) 𝐒𝐞𝐧𝐝 /userbotjoinchannel 𝐢𝐧 𝐥𝐢𝐧𝐤𝐞𝐝 𝐠𝐫𝐨𝐮𝐩
3) 𝐍𝐨𝐰 𝐬𝐞𝐧𝐝 𝐜𝐨𝐦𝐦𝐚𝐧𝐝𝐬 𝐢𝐧 𝐥𝐢𝐧𝐤𝐞𝐝 𝐠𝐫𝐨𝐮𝐩
**¢σммαη∂ѕ**
**=>> ѕσηg ρℓαуιηg🎧**
- /play: Play song using youtube music
- /play [yt url] : Play the given yt url
- /play [reply yo audio]: Play replied audio
- /dplay: Play song via deezer
- /splay: Play song via jio saavn
**=>> ρℓαувα¢к ⏯**
- /player: Open Settings menu of player
- /skip: Skips the current track
- /pause: Pause track
- /resume: Resumes the paused track
- /end: Stops media playback
- /current: Shows the current Playing track
- /playlist: Shows playlist
""",
        
f"""
**=>> 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 𝐌𝐮𝐬𝐢𝐜 𝐏𝐥𝐚𝐲 🛠**
⚪️ For linked group admins only:
- /cplay [song name] - play song you requested
- /cdplay [song name] - play song you requested via deezer
- /csplay [song name] - play song you requested via jio saavn
- /cplaylist - Show now playing list
- /cccurrent - Show now playing
- /cplayer - open music player settings panel
- /cpause - pause song play
- /cresume - resume song play
- /cskip - play next song
- /cend - stop music play
- /userbotjoinchannel - invite assistant to your chat
channel is also can be used instead of c ( /cplay = /channelplay )
⚪️ If you donlt like to play in linked group:
1) Get your channel ID.
2) Create a group with tittle: Channel Music: your_channel_id
3) Add bot as Channel admin with full perms
4) Add @{ASSISTANT_NAME} to the channel as an admin.
5) Simply send commands in your group.
""",

f"""
**=>> мσяє тσσℓѕ 🧑‍🔧**
- /admincache: Updates admin info of your group. Try if bot isn't recognize admin
- /userbotjoin: Invite @{ASSISTANT_NAME} Userbot to your chat
*Player cmd and all other cmds except /play, /current  and /playlist  are only for admins of the group.
"""
      ]
