import json
import os
from pyrogram import Client, filters

# ── Config ──────────────────────────────────────────────

api_id = 37041319
api_hash = "7d9fd7836b2e153466431854a1927c67"
bot_token = "8692086821:AAGRARsUwO-66o2VCKweLXolnCXrQNgPPCE" 
ADMIN_ID = 6097379424 

# ── Client ──────────────────────────────────────────────

bot = Client(
    "searchbot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

# ── Persistent Storage ──────────────────────────────────

DB_FILE = "files.json"

def load_files():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

def save_files(files):
    with open(DB_FILE, "w") as f:
        json.dump(files, f, indent=2)

files = load_files()

# ── Save File Handler ───────────────────────────────────

@bot.on_message(filters.document)
async def save_file(client, message):

    if message.from_user.id != ADMIN_ID:
        await message.reply("❌ Only admin can upload files.")
        return

    file = message.document

    # Skip if no filename
    if not file.file_name:
        await message.reply("⚠️ File has no name, skipping.")
        return

    # Duplicate check
    if any(f["file_unique_id"] == file.file_unique_id for f in files):
        await message.reply(f"⚠️ {file.file_name} is already saved.")
        return

    files.append({
        "name": file.file_name,
        "file_id": file.file_id,
        "file_unique_id": file.file_unique_id
    })

    save_files(files)

    await message.reply(f"✅ Saved: {file.file_name}")
    print(f"[+] Saved: {file.file_name}")

# ── Search File Handler ─────────────────────────────────

@bot.on_message(filters.text)
async def search_file(client, message):
    query = message.text.strip().lower()

    if not query:
        await message.reply("⚠️ Please enter a search term.")
        return

    results = [
        f for f in files
        if query in f["name"].lower()
    ]

    if not results:
        await message.reply("❌ No file found.")
        return

    await message.reply(f"🔍 Found {len(results)} result(s):")

    for f in results:
        try:
            await message.reply_document(
                f["file_id"],
                caption=f["name"]
            )
        except Exception as e:
            await message.reply(
                f"⚠️ Could not send {f['name']}: {e}"
            )

# ── Start Command ───────────────────────────────────────

@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply(
        "👋 File Search Bot\n\n"
        "📁 Send me any file to save it.\n"
        "🔍 Type a filename to search for it."
    )

# ── List Command ────────────────────────────────────────

@bot.on_message(filters.command("list"))
async def list_files(client, message):

    if not files:
        await message.reply("📂 No files saved yet.")
        return

    names = "\n".join(
        f"• {f['name']}" for f in files
    )

    await message.reply(
        f"📂 Saved Files ({len(files)}):\n\n{names}"
    )

# ── Run ─────────────────────────────────────────────────

print("Bot is running...")
bot.run()