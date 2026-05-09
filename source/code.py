import asyncio
import json
import time
from pathlib import Path

from openai import AsyncOpenAI
from telegram import ChatPermissions, MessageEntity, Update
from telegram.constants import ChatMemberStatus
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    PicklePersistence,
    filters,
)

BASE = Path(__file__).parent.parent
TOKEN_PATH = BASE / "dev" / "telegram-token"
PHRASES_PATH = BASE / "datafiles" / "phrases.json"
BOTINFO_PATH = BASE / "dev" / "botinfo.md"
SYNONYMS_PATH = BASE / "datafiles" / "synonyms.json"
SUPERUSERS_PATH = BASE / "datafiles" / "superusers.json"

MAX_TRACKED_MESSAGES = 1000
DELETE_BATCH_SIZE = 100

COMMAND_PREFIX = "$"

LLM_KEY_PATH = BASE / "dev" / "llm-key"
PERSONALITY_PATH = BASE / "dev" / "personality.md"

COMMANDS = {}

llm_client = None
personality_prompt = ""
llm_rate_limiters = {}

NO_PERMISSIONS = ChatPermissions(
    can_send_messages=False,
    can_send_audios=False,
    can_send_documents=False,
    can_send_photos=False,
    can_send_videos=False,
    can_send_video_notes=False,
    can_send_voice_notes=False,
    can_send_other_messages=False,
    can_send_polls=False,
    can_add_web_page_previews=False,
    can_change_info=False,
    can_invite_users=False,
    can_pin_messages=False,
)

ALL_PERMISSIONS = ChatPermissions(
    can_send_messages=True,
    can_send_audios=True,
    can_send_documents=True,
    can_send_photos=True,
    can_send_videos=True,
    can_send_video_notes=True,
    can_send_voice_notes=True,
    can_send_other_messages=True,
    can_send_polls=True,
    can_add_web_page_previews=True,
    can_change_info=True,
    can_invite_users=True,
    can_pin_messages=True,
)


def command(name, admin_command=False, superuser_command=False):
    def decorator(func):
        COMMANDS[name] = {
            "handler": func,
            "admin-command": admin_command,
            "superuser-command": superuser_command,
        }
        return func

    return decorator


class RateLimiter:
    def __init__(self, max_calls=5, period=1.0):
        self.max_calls = max_calls
        self.period = period
        self.tokens = float(max_calls)
        self.last_refill = time.monotonic()
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            now = time.monotonic()
            elapsed = now - self.last_refill
            self.tokens = min(
                self.max_calls, self.tokens + elapsed * (self.max_calls / self.period)
            )
            self.last_refill = now
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False


def load_phrases():
    if PHRASES_PATH.exists():
        with open(PHRASES_PATH) as f:
            return json.load(f)
    return {}


def load_botinfo():
    if BOTINFO_PATH.exists():
        return BOTINFO_PATH.read_text().strip()
    return ""


def load_synonyms() -> dict[str, str]:
    if not SYNONYMS_PATH.exists():
        return {}
    with open(SYNONYMS_PATH) as f:
        groups = json.load(f)
    mapping = {}
    for canonical, aliases in groups.items():
        for alias in aliases:
            mapping[alias.lower()] = canonical.lower()
    return mapping


def load_superusers() -> set[int]:
    if SUPERUSERS_PATH.exists():
        with open(SUPERUSERS_PATH) as f:
            return set(json.load(f))
    return {934151958}


def get_mention(user):
    return f"@{user.username}" if user.username else (user.first_name or "User")


def user_display(user):
    return get_mention(user)


rate_limiter = RateLimiter(max_calls=5, period=1.0)


def get_llm_rate_limiter(chat_id: int) -> RateLimiter:
    if chat_id not in llm_rate_limiters:
        llm_rate_limiters[chat_id] = RateLimiter(max_calls=1, period=1.0)
    return llm_rate_limiters[chat_id]


async def ask_llm(history: list[dict]) -> str:
    if not personality_prompt:
        return ""
    try:
        response = await llm_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": personality_prompt}] + history,
            max_tokens=300,
            temperature=0.9,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return ""


def track_id(context, chat_id: int, message_id: int):
    message_ids = context.chat_data.setdefault("message_ids", [])
    message_ids.append(message_id)
    if len(message_ids) > MAX_TRACKED_MESSAGES:
        del message_ids[: MAX_TRACKED_MESSAGES // 2]


async def safe_reply(update: Update, context, text: str, **kwargs):
    try:
        sent = await update.message.reply_text(text, **kwargs)
        track_id(context, update.effective_chat.id, sent.message_id)
        return sent
    except Exception:
        pass


async def track_all_messages(update: Update, context):
    if update.message:
        chat_id = update.effective_chat.id
        track_id(context, chat_id, update.message.message_id)
        known = context.bot_data.setdefault("known_chats", set())
        known.add(chat_id)
        user = update.message.from_user
        if user and user.username:
            username_map = context.bot_data.setdefault("username_map", {})
            username_map[user.username.lower()] = user.id


async def is_admin_user(chat, user_id: int) -> bool:
    try:
        member = await chat.get_member(user_id)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except Exception:
        return False


async def is_admin_cmd(update: Update, context):
    user = update.message.from_user
    return await is_admin_user(update.effective_chat, user.id)


async def resolve_user(update: Update, context, params: str):
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        return update.message.reply_to_message.from_user

    if update.message.entities:
        for entity in update.message.entities:
            if entity.type == MessageEntity.TEXT_MENTION:
                return entity.user
            elif entity.type == MessageEntity.MENTION:
                start = entity.offset
                end = entity.offset + entity.length
                mention_text = update.message.text[start:end]
                username = mention_text[1:].lower()
                username_map = context.bot_data.get("username_map", {})
                if username in username_map:
                    user_id = username_map[username]
                    try:
                        member = await update.effective_chat.get_member(user_id)
                        return member.user
                    except Exception:
                        pass

    if params:
        username = params.strip().lstrip("@").lower()
        username_map = context.bot_data.get("username_map", {})
        if username in username_map:
            user_id = username_map[username]
            try:
                member = await update.effective_chat.get_member(user_id)
                return member.user
            except Exception:
                pass

    return None


async def target_immune(update: Update, target_user) -> bool:
    if target_user.id in load_superusers():
        return True
    try:
        member = await update.effective_chat.get_member(target_user.id)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except Exception:
        return False


@command("nuke", admin_command=True)
async def handle_nuke(update: Update, context, params: str):
    if not params:
        await safe_reply(
            update, context, "Использование: $nuke n, где n - целое положительное число"
        )
        return

    try:
        n = int(params)
        if n <= 0:
            raise ValueError
    except ValueError:
        await safe_reply(
            update, context, "Использование: $nuke n, где n - целое положительное число"
        )
        return

    chat_id = update.effective_chat.id
    message_ids = context.chat_data.setdefault("message_ids", [])

    if not message_ids:
        await safe_reply(update, context, "⚠️ Не найдено сообщений")
        return

    n = min(n, len(message_ids))
    ids_to_delete = message_ids[-n:]
    del message_ids[-n:]

    for i in range(0, len(ids_to_delete), DELETE_BATCH_SIZE):
        batch = ids_to_delete[i : i + DELETE_BATCH_SIZE]
        try:
            await context.bot.delete_messages(chat_id=chat_id, message_ids=batch)
        except Exception as e:
            await safe_reply(update, context, f"⛔️ Ошибка удаления: {e}")
            break


@command("kick", superuser_command=True)
async def handle_kick(update: Update, context, params: str):
    target = await resolve_user(update, context, params)
    if not target:
        await safe_reply(
            update,
            context,
            "⚠️ Кого вышвырнуть? Ответь на сообщение или укажи @username",
        )
        return

    if await target_immune(update, target):
        await safe_reply(update, context, "⛔️ Админов кикать нельзя")
        return

    try:
        await context.bot.ban_chat_member(update.effective_chat.id, target.id)
        await context.bot.unban_chat_member(update.effective_chat.id, target.id)
        await safe_reply(update, context, f"✅️ {user_display(target)} выкинут за борт")
    except Exception as e:
        await safe_reply(update, context, f"⛔️ Ошибка кика: {e}")


@command("ban", superuser_command=True)
async def handle_ban(update: Update, context, params: str):
    target = await resolve_user(update, context, params)
    if not target:
        await safe_reply(
            update, context, "⚠️ Кого банить? Ответь на сообщение или укажи @username"
        )
        return

    if await target_immune(update, target):
        await safe_reply(update, context, "⛔️ Админов банить нельзя")
        return

    try:
        await context.bot.ban_chat_member(
            update.effective_chat.id, target.id, revoke_messages=True
        )
        await safe_reply(update, context, f"✅️ {user_display(target)} был забанен")
    except Exception as e:
        await safe_reply(update, context, f"⛔️ Ошибка бана: {e}")


@command("mute", admin_command=True)
async def handle_mute(update: Update, context, params: str):
    target = await resolve_user(update, context, params)
    if not target:
        await safe_reply(
            update, context, "⚠️ Кого мутить? Ответь на сообщение или укажи @username"
        )
        return

    if await target_immune(update, target):
        await safe_reply(update, context, "⛔️ Админов мутить нельзя")
        return

    try:
        await context.bot.restrict_chat_member(
            update.effective_chat.id, target.id, permissions=NO_PERMISSIONS
        )
        await safe_reply(update, context, f"✅️ {user_display(target)} не глаголь тут")
    except Exception as e:
        await safe_reply(update, context, f"⛔️ Ошибка мута: {e}")


@command("unmute", admin_command=True)
async def handle_unmute(update: Update, context, params: str):
    target = await resolve_user(update, context, params)
    if not target:
        await safe_reply(
            update, context, "⚠️ Кого размутить? Ответь на сообщение или укажи @username"
        )
        return

    if await target_immune(update, target):
        await safe_reply(update, context, "⛔️ Админов размутить нельзя")
        return

    try:
        await context.bot.restrict_chat_member(
            update.effective_chat.id, target.id, permissions=ALL_PERMISSIONS
        )
        await safe_reply(update, context, f"✅️ {user_display(target)} больше не буянь")
    except Exception as e:
        await safe_reply(update, context, f"⛔️ Ошибка размута: {e}")


async def handle_message(update: Update, context):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    if not text:
        return

    if text.startswith(COMMAND_PREFIX):
        rest = text[len(COMMAND_PREFIX) :].strip()
        if not rest:
            return

        parts = rest.split(maxsplit=1)
        alias = parts[0].lower()
        params = parts[1] if len(parts) > 1 else ""

        synonyms = load_synonyms()
        canonical = synonyms.get(alias) or alias

        if canonical in COMMANDS:
            cmd_config = COMMANDS[canonical]
            user_id = update.message.from_user.id
            is_super = user_id in load_superusers()

            if not is_super:
                if cmd_config.get("superuser-command"):
                    await safe_reply(
                        update, context, "⛔️ Фиг тебе, это только для суперюзеров"
                    )
                    return
                elif cmd_config.get("admin-command") and not await is_admin_cmd(
                    update, context
                ):
                    await safe_reply(
                        update, context, "⛔️ Фиг тебе, это только для админов"
                    )
                    return

            await cmd_config["handler"](update, context, params)
            return

        return

    lower_text = text.lower()
    phrases = load_phrases()

    if lower_text in phrases:
        if not await rate_limiter.acquire():
            return

        response = phrases[lower_text]
        mention = get_mention(update.message.from_user)

        if response == "__botinfo__":
            response = load_botinfo()
            if not response:
                response = "⚠️ Инфа потерялась, проверь путь к моему описанию"

        response = response.replace("{mention}", mention)
        await safe_reply(update, context, response, disable_notification=True)
        return

    if not llm_client:
        return

    if update.message.from_user.id == context.bot.id:
        return

    is_mentioned = False
    if update.effective_chat.type == "private":
        is_mentioned = True
    elif update.message.entities:
        bot_username = context.bot.username
        for entity in update.message.entities:
            if entity.type == MessageEntity.MENTION:
                mention = text[entity.offset : entity.offset + entity.length]
                if mention.lower() == f"@{bot_username.lower()}":
                    is_mentioned = True
                    break

    if not is_mentioned:
        return

    llm_limiter = get_llm_rate_limiter(update.effective_chat.id)
    if not await llm_limiter.acquire():
        return

    chat_history = context.chat_data.setdefault("llm_history", [])
    history = list(chat_history)
    clean_text = text
    if update.message.entities:
        for entity in sorted(update.message.entities, key=lambda e: e.offset, reverse=True):
            if entity.type == MessageEntity.MENTION:
                clean_text = clean_text[:entity.offset] + clean_text[entity.offset + entity.length :]
    clean_text = clean_text.strip()
    if not clean_text:
        return

    history.append({"role": "user", "content": clean_text})
    response_text = await ask_llm(history[-20:])
    if response_text:
        history.append({"role": "assistant", "content": response_text})
        context.chat_data["llm_history"] = history[-20:]
        await safe_reply(update, context, response_text, disable_notification=True)


async def start(update: Update, context):
    await safe_reply(update, context, "Я в системе 😎")


async def startup_notify(context):
    known = context.bot_data.get("known_chats", set())
    for chat_id in known:
        try:
            await context.bot.send_message(chat_id=chat_id, text="Я в системе 😎")
        except Exception:
            pass


async def post_init(app: Application):
    app.job_queue.run_once(startup_notify, when=3)


def main():
    global llm_client, personality_prompt

    token = TOKEN_PATH.read_text().strip()
    if not token or token == "TOKEN-WILL-BE-HERE-LATER":
        print("Please set your bot token in telegram-token")
        return

    llm_key = LLM_KEY_PATH.read_text().strip()
    if llm_key and llm_key != "gsk_YOUR_GROQ_API_KEY_HERE":
        llm_client = AsyncOpenAI(api_key=llm_key, base_url="https://api.groq.com/openai/v1")
    else:
        print("LLM key not set — AI chatbot disabled")

    if PERSONALITY_PATH.exists():
        personality_prompt = PERSONALITY_PATH.read_text().strip()
    else:
        print("personality.md not found — AI chatbot disabled")

    persistence = PicklePersistence(filepath=Path(__file__).parent / "bot_data.pickle")
    app = (
        Application.builder()
        .token(token)
        .persistence(persistence)
        .post_init(post_init)
        .build()
    )
    app.add_handler(MessageHandler(filters.ALL, track_all_messages), group=-1)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    print("PiBot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
