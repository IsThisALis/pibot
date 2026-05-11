# 🤖 PiBot

🛩️ Telegram group moderation and interactive response bot. Supports English and Russian.

## ⚙️ Features

- **Phrase responses** — exact (case-insensitive) trigger phrases with customizable replies
- **Moderation commands** — `$kick`, `$ban`, `$mute`, `$unmute` with permission levels
- **NUKE** — `$nuke n` deletes last `n` messages
- **Command aliases** — synonyms in `synonyms.json` (e.g. `$nuke` / `$burn`)
- **Permission system** — superusers, group admins, and regular users
- **Persistence** — state survives restarts via PicklePersistence

## 🚀 Quick start

```bash
git clone https://github.com/deltashrimp/pibot.git
cd pibot
./setup.sh
# edit dev/telegram-token — paste your bot token
# edit datafiles/superusers.json — add your Telegram user ID
./launchbot.sh
```
### ➕️ Create new bot

**BEFORE RUNNING `./launchbot.sh`**

Search for botfather in telegram and send it `/newbot`.

After a quick setup, it will provide you with a bot token. Copy and paste it inside telegram-token file.

### ➕️ Add bot to a groupchat
Find your bot in telegram and add it to a groupchat from it's profile.

## 🛠️ Commands

| Command | Who can use |
|---------|------------|
| `$nuke n` | group admin | 
| `$kick @user` | superuser | 
| `$ban @user` | superuser | 
| `$mute @user` | group admin | 
| `$unmute @user` | group admin | 

Target users by: **reply** to their message or **@mention**.

## 🌳 Structure

```
pibot/
├── source/code.py              # main bot logic
├── datafiles/
│   ├── synonyms.json           # command aliases
│   ├── public-phrases.json     # example trigger phrases
│   └── public-superusers.json  # template superuser list
├── dev/
│   └── public-botinfo.md       # template bot info
├── launchbot.sh                # start script
└── setup.sh                    # first-time setup
```
_setup.sh will add private versions of public files_

## 📃 License

GNU General Public License v3.0

## 👨‍💻 Devs and helpers
Main developers: deltashrimp, opencode/big-pickle
