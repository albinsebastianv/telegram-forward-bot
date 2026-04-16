import os
import asyncio
from telethon import TelegramClient, events

api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']

source = int(os.environ['SOURCE'])
destination = int(os.environ['DESTINATION'])

client = TelegramClient('session', api_id, api_hash)

# SETTINGS
BATCH_SIZE = 40                # 30–50 recommended
DELAY_BETWEEN_BATCH = 1800    # 30 minutes
DELAY_BETWEEN_MSG = 10        # 10 seconds between each video

async def forward_old_videos():
    print("Starting old video forwarding...")

    videos = []
    async for msg in client.iter_messages(source, reverse=True):
        if msg.video:
            videos.append(msg)

    print(f"Total videos found: {len(videos)}")

    for i in range(0, len(videos), BATCH_SIZE):
        batch = videos[i:i+BATCH_SIZE]

        print(f"Sending batch {i//BATCH_SIZE + 1}")

        for msg in batch:
            try:
                file = await msg.download_media()
                await client.send_file(destination, file, caption=msg.text)
                await asyncio.sleep(DELAY_BETWEEN_MSG)
            except Exception as e:
                print("Error:", e)

        print("Batch done. Waiting before next batch...")
        await asyncio.sleep(DELAY_BETWEEN_BATCH)

    print("Old videos forwarding completed!")

@client.on(events.NewMessage(chats=source))
async def handler(event):
    if event.message.video:
        try:
            file = await event.message.download_media()
            await client.send_file(destination, file, caption=event.message.text)
        except Exception as e:
            print("Error:", e)

async def main():
    await forward_old_videos()
    print("Now listening for new videos...")

with client:
    client.loop.run_until_complete(main())
    client.run_until_disconnected()
