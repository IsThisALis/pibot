# PiBot

Telegram group moderation and interactive response bot. Supports English and Russian.

## Features

- **Phrase responses** — exact (case-insensitive) trigger phrases with customizable replies
- **Moderation commands** — `$kick`, `$ban`, `$mute`, `$unmute` with permission levels
- **NUKE** — `$nuke n` deletes last `n` messages
- **Command aliases** — synonyms in `synonyms.json` (e.g. `$nuke` / `$burn`)
- **Permission system** — superusers, group admins, and regular users
- **Immunity** — superusers and admins cannot be moderated
- **Rate limited** — 5 responses/second token bucket
- **Persistence** — state survives restarts via PicklePersistence

## Quick start

```bash
git clone <repo>
cd pibot
./setup.sh
# edit dev/telegram-token — paste your bot token
# edit datafiles/superusers.json — add your Telegram user ID
./launchbot.sh
```

## Commands

| Command | Who can use | Action |
|---------|------------|--------|
| `$nuke n` | group admin | Delete last n messages |
| `$kick @user` | superuser | Kick user from chat |
| `$ban @user` | superuser | Ban user permanently |
| `$mute @user` | group admin | Restrict user from sending |
| `$unmute @user` | group admin | Restore user permissions |

Target users by: **reply** to their message, **@mention**, or **plain username**.

## Structure

```
pibot/
├── source/code.py              # main bot logic
├── datafiles/
│   ├── synonyms.json           # command aliases
│   ├── public-phrases.json     # example trigger phrases
│   ├── public-superusers.json  # template superuser list
│   ├── phrases.json            # personal (gitignored)
│   └── superusers.json         # personal (gitignored)
├── dev/
│   ├── telegram-token          # personal (gitignored)
│   ├── botinfo.md              # personal (gitignored)
│   └── public-botinfo.md       # template bot info
├── launchbot.sh                # start script
└── setup.sh                    # first-time setup
```

## Requirements

- Python 3.10+
- python-telegram-bot at least 22.x

## License

GNU General Public License v3.0

## Devs and helpers
Main developers: deltashrimp, opencode/big-pickle
