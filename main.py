import os
import asyncio
import json
from telethon import TelegramClient, events

api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']

sources = [int(x.strip()) for x in os.environ['SOURCE'].split(',')]
destination = int(os.environ['DESTINATION'])

client = TelegramClient('session', api_id, api_hash)

# SETTINGS
DELAY_BETWEEN_MSG = 40  # safer delay

PROGRESS_FILE = "progress.json"

# ---------------- LOAD / SAVE PROGRESS ---------------- #

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_progress(data):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f)

# ---------------- OLD VIDEOS ---------------- #

async def forward_old_videos():
    print("Starting old video forwarding...")

    progress = load_progress()

    for src in sources:
        print(f"Processing source: {src}")

        last_id = progress.get(str(src), 0)

        while True:
            try:
                async for msg in client.iter_messages(src, reverse=True):
                    
                    # Skip already processed
                    if msg.id <= last_id:
                        continue

                    if msg.video:
                        try:
                            print(f"Downloading video ID {msg.id}...")
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

                            print(f"Sent video ID {msg.id}")

                            # Save progress
                            progress[str(src)] = msg.id
                            save_progress(progress)

                            await asyncio.sleep(DELAY_BETWEEN_MSG)

                        except Exception as e:
                            print("Send Error:", e)

                break

            except Exception as e:
                print("Retrying due to error:", e)
                await asyncio.sleep(10)

    print("Old videos forwarding completed!")

# ---------------- NEW VIDEOS ---------------- #

@client.on(events.NewMessage(chats=sources))
async def handler(event):
    if event.message.video:
        try:
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

# ---------------- MAIN ---------------- #

async def main():
    print("Bot started!")

    await client.send_message(destination, "Hi, bot started ✅")

    await forward_old_videos()

    print("Now listening for new videos...")

with client:
    client.loop.run_until_complete(main())
    client.run_until_disconnected()
