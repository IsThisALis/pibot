# Pibot — Telegram Chat Bot

Multifunctional Telegram bot with phrase responses, RP commands, AI integration (Groq Llama), and moderation tools.

## Features

- **Phrase responses** — automatically replies to trigger phrases from `phrases.json`
- **RP commands** — interactive roleplay (hug, kiss, etc.) via reply
- **AI integration** — responds with context when the bot is @mentioned (Groq Llama 3.3 70B via OpenAI SDK)
- **Admin commands** — `nuke`, `mute`, `unmute`
- **Superuser commands** — `kick`, `ban`, `block`
- **Anti-spam** — rate limiter, age filter, trigger phrase spam protection, Telegram mute
- **Rank system** — 4-level access (Owner, Admin+, Admin, Member)

## Structure

```
pibot/
├── bot-data/         # JSON/MD data files (phrases, rp-commands, personality)
├── env/              # Config files (gitignored: tokens, keys, dev IDs)
├── info/             # Documentation and help files
├── important/        # Logging setup and internal tooling (gitignored)
├── source/
│   ├── pibot.py      # Main bot class (~1120 lines)
│   └── persistence.py # SQLite persistence
├── setup.sh          # Deployment script
└── launchbot.sh      # Launch script
```

## Setup

1. Clone the repository to your server
2. Run `bash setup.sh` — creates config files, venv, and installs dependencies
3. Fill in `env/telegram-token` with your bot token (from BotFather)
4. Fill in `env/groq-key` with your Groq API key
5. Optionally edit `bot-data/personality.md` and `bot-data/botinfo.md`
6. Run `./launchbot.sh`

## Commands

Full list in `info/command-list.md` or type `пибот команды` in chat.

## Dependencies

- python-telegram-bot (v22+, with job-queue)
- openai (AsyncOpenAI for Groq API)
