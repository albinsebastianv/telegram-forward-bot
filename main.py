import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# =========================
# TELEGRAM API CONFIG
# =========================

api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
session_string = os.environ['SESSION']

destination = int(os.environ['DESTINATION'])

client = TelegramClient(
    StringSession(session_string),
    api_id,
    api_hash
)

# =========================
# SETTINGS
# =========================

DELAY_BETWEEN_MSG = 45  # safer delay (seconds)

# =========================
# SOURCE GROUPS CONTROL
# =========================

# These groups will send ALL old videos from beginning
FULL_HISTORY_SOURCES = [
    -1002835976219,
]

# These groups will SKIP old videos
# and only send NEW videos from now onward
NEW_ONLY_SOURCES = [
    -1002206382201,
]

# Combined list for new incoming video monitoring
ALL_SOURCES = FULL_HISTORY_SOURCES + NEW_ONLY_SOURCES

# =========================
# FORWARD OLD VIDEOS
# =========================

async def forward_old_videos():
    print("Starting old video forwarding...")

    for src in FULL_HISTORY_SOURCES:
        print(f"Processing FULL history source: {src}")

        while True:
            try:
                async for msg in client.iter_messages(src, reverse=True):

                    if msg.video:
                        try:
                            if not client.is_connected():
                                print("Reconnecting...")
                                await client.connect()

                            print(f"Downloading old video ID {msg.id}...")
                            file = await msg.download_media()

                            if not file:
                                continue

                            caption = msg.text or ""
                            caption = f"[Source: {src}]\n{caption}"

                            await client.send_file(
                                destination,
                                file,
                                caption=caption,
                                supports_streaming=True
                            )

                            print(f"Sent old video ID {msg.id}")

                            await asyncio.sleep(DELAY_BETWEEN_MSG)

                        except Exception as e:
                            print("Send Error:", e)

                break

            except Exception as e:
                print("Retrying due to error:", e)
                await asyncio.sleep(10)

    print("Old video forwarding completed!")

# =========================
# NEW VIDEOS ONLY
# =========================

@client.on(events.NewMessage(chats=ALL_SOURCES))
async def handler(event):
    if event.message.video:
        try:
            if not client.is_connected():
                print("Reconnecting...")
                await client.connect()

            print("New video detected")

            file = await event.message.download_media()

            if not file:
                return

            caption = event.message.text or ""
            caption = f"[Source: {event.chat_id}]\n{caption}"

            await client.send_file(
                destination,
                file,
                caption=caption,
                supports_streaming=True
            )

            print("New video sent!")

        except Exception as e:
            print("Error in new handler:", e)

# =========================
# MAIN
# =========================

async def main():
    print("Bot started!")

    await client.connect()

    if not await client.is_user_authorized():
        print("Session not authorized!")
        return

    try:
        await client.send_message(
            destination,
            "Hi, bot started ✅"
        )
    except Exception as e:
        print("Test message error:", e)

    await forward_old_videos()

    print("Now listening for new videos only...")

with client:
    client.loop.run_until_complete(main())
    client.run_until_disconnected()
