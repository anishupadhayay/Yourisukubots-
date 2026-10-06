# Yourisukubots-
🤖 Isukobit — Telegram File Store Bot

[![Bot](https://img.shields.io/badge/Telegram-@yourisukubot-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/yourisukubot)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://docs.aiogram.dev)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-Private-red?style=for-the-badge)](LICENSE)

A powerful Telegram File Store Bot — upload, search, share. One link for multiple files, automatic backups, and a flood-proof queue system!

[🚀 Features](#-features) • [📸 Screenshots](#-screenshots) • [⚙️ Setup](#️-setup) • [📖 Commands](#-commands) • [👑 Admin Panel](#-admin-panel)

---

## ✨ Features

### 📁 File Management

| Feature | Description |
|---|---|
| 📤 File Upload | Documents, videos, audio, photos, voice — all supported |
| 🔗 Unique Links | Every file gets an `ISU-XXXXXX` code + shareable deep-link |
| 🔍 Smart Search | Find files by name, code, or keyword |
| 📱 QR Codes | Generate a QR for the file link — scan & share |
| ✏️ Rename / Move | Rename files, organize them |

### 📦 Batch System (Star Feature ⭐)

| Feature | Description |
|---|---|
| 📦 Batch Upload | Send 100-200 files, get a single link |
| ⏳ Waiting List (Queue) | Files are processed in a queue — flood-control errors become impossible |
| 📥 Download All | Download the whole batch in one tap |
| 🔄 Auto-Retry | If a rate limit occurs, the bot waits and retries automatically |

### 🛡️ Safety & Control

- 🔒 User-Locked Links — Only the uploader (or an admin) can access the file
- 🚫 Ban System — Ban/unban users with a reason
- ⏱️ Rate Limiting — Spam protection built-in
- 🗑️ Select & Delete — Select multiple files and delete them together
- 👤 Channel Metadata — Full uploader details in the storage/backup channel

### 👑 Admin Panel

- 📊 Live statistics (users, files, downloads, server RAM/CPU)
- 📣 Broadcast — Text, photo, video, document — to all users
- 💾 Auto Backup — Daily automatic database backup
- 🛠️ Maintenance Mode — Turn the bot off with a custom message
- 📢 Channel Management — Storage, backup, log channel settings
- 📝 Logs — Downloads, uploads, joins, errors — all tracked
- 🌍 Multi-Language — Hinglish, English, Nepali, Latin

---

## 📸 Screenshots

> Add bot screenshots here (drag & drop on GitHub)

| Main Menu | Batch Upload | Admin Panel |
|---|---|---|
| 📷 | 📷 | 📷 |

---

## 🗂️ Project Structure

```text
isukobit/
├── app.py              # 🚀 Main entry — bot start, workers, shutdown
├── config.py           # ⚙️ Config, settings, logging, validation
├── database.py         # 🗄️ SQLite — all tables & queries
├── handlers_start.py   # 🏠 /start, menus, force-join, deep links
├── handlers_upload.py  # 📤 Upload + ⏳ QUEUE SYSTEM (batch)
├── handlers_files.py   # 📁 My Files, search, delete, QR
├── handlers_admin.py   # 👑 Admin panel — all admin features
├── keyboards.py        # ⌨️ All buttons & keyboards (4 languages)
├── strings.py          # 🌍 Bot messages — Hinglish/English/Nepali/Latin
├── utils.py            # 🛠️ Helpers — encryption, formatting, sessions
├── .env                # 🔐 Secrets (in .gitignore!)
└── requirements.txt    # 📦 Dependencies
```

---

## ⚙️ Setup

### Step 1️⃣ — Install Python packages

```bash
pip install -r requirements.txt
```

### Step 2️⃣ — Create `.env` file

```bash
cp .env.example .env    # or create .env manually
```

```env
# ─── Required ───
BOT_TOKEN=1234567890:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx   # from @BotFather
API_ID=12345678                                             # from my.telegram.org
API_HASH=abcdef1234567890abcdef1234567890                   # from my.telegram.org
OWNER_ID=123456789                                          # from @userinfobot
DB_PASSWORD=anything123                                     # for SQLite validation
ENCRYPTION_KEY=generate_it                                  # see below

# ─── Optional ───
BOT_NAME=Isukobit
BOT_USERNAME=yourisukubot
LOG_LEVEL=INFO
```

Generate `ENCRYPTION_KEY`:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Step 3️⃣ — Create 3 channels

| Channel | Purpose | Bot role |
|---|---|---|
| 📥 Storage Channel | Files are stored here | Admin (Post Messages) — required! |
| 💾 Backup Channel | Backup copy of files | Admin (recommended) |
| 📝 Log Channel | Notifications & reports | Admin (recommended) |

> ⚠️ The bot will NOT work for uploads unless it is an admin in the Storage Channel!

To get a channel ID: forward any message from the channel to `@userinfobot`.

### Step 4️⃣ — Run the bot

```bash
python app.py
```

On startup, you should see:

```text
✅ Bot verified: @yourisukubot
✅ Storage channel OK: -100...
✅ Backup channel OK: -100...
✅ Log channel OK: -100...
⏳ Upload queue worker started [ALL-MODE]
✅ Bot startup complete!
```

### Step 5️⃣ — Link channels (Admin Panel)

Go to the bot → `/admin` → 📢 Channels → enter each channel ID

---

## ☁️ Deploy on Pterodactyl Panel (soFthost etc.)

1. Upload all `.py` files in the Files section
2. Create `.env` file (fill in values)
3. Startup command: `python app.py`
4. Press Start — logs will appear in the console
5. Clean shutdown via Stop button (no need to force kill!)

---

## 📖 Commands

| Command | Description |
|---|---|
| `/start` | Main menu |
| `/help` | Help & commands list |
| `/upload` | Start file upload |
| `/batch` | 📦 Batch mode — multiple files, one link |
| `/myfiles` | View your files |
| `/search` | Find a file |
| `/profile` | Your profile |
| `/stats` | Statistics |
| `/settings` | Bot settings |
| `/about` | About the bot |
| `/cancel` | Cancel current action |
| `/admin` | 👑 Admin panel (admin/owner only) |

---

## 👑 Admin Panel Guide

```text
/admin
├── 📊 Statistics      → Live bot + server stats
├── 👥 Users           → User list, search, ban/unban, admin add/remove
├── 📁 Files           → File management
├── 📣 Broadcast       → Send a message to all users
├── 💾 Backup          → Create/list database backups
├── ⚙️ Settings        → File limits, batch limits, queue delays
├── 📢 Channels        → Storage/backup/log channel IDs
├── 🔐 Security        → Anti-spam toggle, rate limits
├── 🛠️ Maintenance     → Maintenance mode ON/OFF
├── 📝 Logs            → Downloads/uploads/users/errors logs
├── 💚 Health Check    → Bot + DB + server health
└── 🔄 Restart         → Restart bot
```

### 🔧 Important Settings (Admin Panel → Settings → File)

| Setting | Default | Description |
|---|---|---|
| `max_file_size` | 50 MB | Max upload size (bytes) |
| `batch_max_files` | 50 | Max files per batch |
| `batch_session_minutes` | 30 | Batch session duration |
| `queue_step_delay` | 1.5 | Queue: gap between each step (sec) |
| `queue_item_delay` | 1.0 | Queue: gap between each file (sec) |
| `log_report_interval_seconds` | 300 | Log channel report interval |

---

## 🔄 How the Queue System Works

```text
User sends a file (single or batch)
        │
        ▼
📝 File added to "Waiting List" — INSTANT response
        │
        ▼
⏳ Background Worker — processes one by one:
   Storage Channel → Caption → Backup → Database
   (1.5 sec gap between each step)
        │
        ▼
✅ Success! Code + link received

❌ If Telegram rate limit occurs → bot waits and RETRIES
```

Result: Send 200 files — never get a "Flood Control" error! 🔒

---

## 🌐 Languages

| Language | Code |
|---|---|
| 🇮🇳 Hinglish (default) | `hinglish` |
| 🇬🇧 English | `english` |
| 🇳🇵 नेपाली | `nepali` |
| 🏛️ Latin | `latin` |

Change: `/settings` → 🌍 Language

---

## 🛡️ Security Notes

- 🔐 Never make `.env` public (check `.gitignore` before pushing to GitHub!)
- 🔑 Generate `ENCRYPTION_KEY` only once — if you change it later, old encrypted data will be corrupted
- 👑 `OWNER_ID` should be only your Telegram ID — this gives full control
- 🚫 If the bot token leaks, revoke it immediately from @BotFather

### `.gitignore` (make sure to add this!)

```gitignore
.env
*.db
__pycache__/
logs/
data/
backups/
sessions/
*.session
```

---

## ❓ FAQ

**Bot is not working for uploads.**
Make the bot admin again in the storage channel (Post Messages permission). Channel → Administrators → Add → @yourisukubot

**Flood Control error is coming.**
This is an error from the old code. The new code has a Queue System — all files go through the waiting list. Upload the latest `handlers_upload.py` and restart.

**Links are wrong / bot username is wrong.**
At startup, the bot automatically syncs its username from Telegram. Restart it — all links will be correct.

**What is the file size limit?**
Telegram limit: 2GB per file (4GB for Telegram Premium users). You can increase the bot's `max_file_size` setting from the admin panel.

---

## ⚠️ Disclaimer

> This bot was made for educational purposes. Users are responsible for their own files. Uploading copyright content or illegal material is strictly prohibited — the bot owner is not responsible for such content. [Terms & Conditions](https://your-username.github.io/isukobit-terms/)

---

⭐ If you like the project, don't forget to star it!

Made with ❤️ by Isukobit Team
