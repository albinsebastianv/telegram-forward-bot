import os
import asyncio
from telethon import TelegramClient, events

api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']

source = int(os.environ['SOURCE'])
destination = int(os.environ['DESTINATION'])

client = TelegramClient('session', api_id, api_hash)

# SETTINGS
DELAY_BETWEEN_MSG = 25   # seconds (safe)

async def forward_old_videos():
    print("Starting old video forwarding...")

    count = 0

    async for msg in client.iter_messages(source, reverse=True):
        if msg.video:
            try:
                print("Downloading video...")
                file = await msg.download_media()
                print("Downloaded:", file)

                if not file:
                    print("Download failed, skipping...")
                    continue

                print("Sending video...")
                await client.send_file(destination, file, caption=msg.text)

                count += 1
                print(f"Sent video #{count}")

                await asyncio.sleep(DELAY_BETWEEN_MSG)

            except Exception as e:
                print("Error:", e)

    print("Old videos forwarding completed!")

@client.on(events.NewMessage(chats=source))
async def handler(event):
    if event.message.video:
        try:
            print("New video detected")

            file = await event.message.download_media()
            print("Downloaded new video:", file)

            if not file:
                print("Download failed")
                return

            await client.send_file(destination, file, caption=event.message.text)

            print("New video sent!")

        except Exception as e:
            print("Error:", e)

async def main():
    print("Bot started!")

    # ✅ Test message
    await client.send_message(destination, "Hi, bot started ✅")

    # Start forwarding
    await forward_old_videos()

    print("Now listening for new videos...")

with client:
    client.loop.run_until_complete(main())
    client.run_until_disconnected()
