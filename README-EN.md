# Pibot — Telegram Chat Bot

Multifunctional Telegram bot with phrase responses, RP commands, AI integration, and moderation tools.

## Features

- **Phrase responses** — automatically replies to trigger phrases from `phrases.json`
- **RP commands** — interactive roleplay (hug, kiss, etc.) via reply
- **AI integration** — replies with context when the bot is @mentioned in a reply (Gemini or Groq)
- **Admin commands** — `$nuke`, `$mute`, `$unmute`
- **Superuser commands** — `$kick`, `$ban`, `$changeai`
- **Anti-spam** — rate limiter, age filter, trigger phrase spam protection, Telegram mute

## Structure

```
pibot/
├── bot-data/         # JSON data files (phrases, synonyms, rp-commands)
├── env/              # Config files (gitignored: .env, botinfo.txt, changelog.txt)
├── info/             # Documentation
├── source/code.py    # Main bot (~900 lines)
└── setup.sh          # Deployment script
```

## Setup

1. Copy the repository to the server
2. Create `env/.env` with `BOT_TOKEN`, `GEMINI_API_KEY`, `GROQ_API_KEY`, `GROQ_BASE_URL`, `SUPERUSER_IDS`
3. Optionally configure `env/botinfo.txt` and `env/changelog.txt`
4. Run `bash setup.sh` to install systemd service or run manually

## Commands

Full list in `info/command-list.md` or type `пибот команды` in chat.

## Dependencies

- python-telegram-bot (v20+)
- google-genai
- openai (AsyncOpenAI)
