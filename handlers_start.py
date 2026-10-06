# ═══════════════════════════════════════════════════════════════════════════
# 🚀 ISUKOBIT — TELEGRAM FILE STORE BOT
# ═══════════════════════════════════════════════════════════════════════════
# File      : handlers_start.py (BOTH Keyboards Working)
# Purpose   : /start, main menu, reply keyboard, inline keyboard — sab
# Author    : Isukobit Team
# Version   : 1.0.3
# Python    : 3.10+
# Library   : aiogram 3.x
# ═══════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════
# 📦 IMPORTS
# ═══════════════════════════════════════════════════════════════════════════

import time
import asyncio
from datetime import datetime
from typing import Optional

from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.enums import ChatMemberStatus, ParseMode
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)

from config import Bootstrap, Constants, settings, log, Colors
from database import db
from keyboards import (
    CB,
    get_main_menu_keyboard,
    get_main_menu_reply_keyboard,
    get_back_button,
    get_close_keyboard,
    get_settings_keyboard,
    get_language_selection_keyboard,
    get_help_keyboard,
    get_about_keyboard,
    get_profile_keyboard,
    get_stats_keyboard,
    get_force_join_keyboard,
    get_batch_view_keyboard,
    btn,
)
from strings import (
    get_string,
    get_language_flag,
    get_language_name,
    SUPPORTED_LANGUAGES,
)
from utils import (
    escape_html,
    format_size,
    format_datetime,
    format_time_ago,
    get_uptime,
    format_user_display,
    truncate,
    rate_limiter,
    sessions,
    is_valid_file_code,
)


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 ROUTER
# ═══════════════════════════════════════════════════════════════════════════

router = Router(name="start_handlers")


# ═══════════════════════════════════════════════════════════════════════════
# 🛡️ HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

async def is_user_banned(user_id: int) -> bool:
    try:
        return await db.is_user_banned(user_id)
    except Exception:
        return False


async def is_maintenance_mode() -> bool:
    return settings.get_bool("maintenance_mode", False)


async def get_user_lang(user_id: int) -> str:
    try:
        return await db.get_user_language(user_id)
    except Exception:
        return settings.get_str("default_language", "hinglish")


async def check_force_join(bot: Bot, user_id: int) -> tuple:
    if not settings.get_bool("force_join_enabled", False):
        return True, []
    if await db.is_owner(user_id) or await db.is_admin(user_id):
        return True, []

    channels = []
    for i in range(1, 4):
        ch = settings.get_str(f"force_join_{i}", "")
        name = settings.get_str(f"force_join_{i}_name", f"Channel {i}")
        if ch:
            channels.append({"id": ch, "name": name})

    if not channels:
        return True, []

    missing = []
    for ch in channels:
        try:
            member = await bot.get_chat_member(ch["id"], user_id)
            if member.status in (
                ChatMemberStatus.LEFT,
                ChatMemberStatus.KICKED,
                ChatMemberStatus.RESTRICTED,
            ):
                missing.append(ch)
        except TelegramBadRequest:
            continue
        except Exception:
            continue

    return len(missing) == 0, missing


async def check_rate_limit(user_id: int) -> tuple:
    if await db.is_owner(user_id) or await db.is_admin(user_id):
        return True, 0
    max_per_min = settings.get_int("rate_limit_per_minute", 10)
    return rate_limiter.check(user_id, max_requests=max_per_min, window_seconds=60)


async def safe_send_message(
    message: Message,
    text: str,
    reply_markup=None,
    **kwargs
) -> Optional[Message]:
    try:
        return await message.answer(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            **kwargs
        )
    except TelegramForbiddenError:
        return None
    except TelegramBadRequest as e:
        log.warning(f"Bad request: {e}")
        return None
    except Exception as e:
        log.error(f"Send message failed: {e}")
        return None


async def safe_edit_message(
    callback: CallbackQuery,
    text: str,
    reply_markup=None,
    **kwargs
) -> bool:
    try:
        await callback.message.edit_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            **kwargs
        )
        return True
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            return True
        try:
            await callback.message.delete()
            await callback.message.answer(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
                **kwargs
            )
            return True
        except Exception:
            return False
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════════════
# 🚀 /start COMMAND HANDLERS
# ═══════════════════════════════════════════════════════════════════════════

@router.message(CommandStart(deep_link=True))
async def start_with_deep_link(
    message: Message,
    command: CommandObject,
    bot: Bot
):
    """Deep link start — /start ISU-XXXXX"""
    user = message.from_user
    args = command.args

    log.info(f"Deep link start: user={user.id}, args={args}")

    if await is_user_banned(user.id):
        lang = await get_user_lang(user.id)
        await safe_send_message(
            message,
            get_string("user_banned_msg", lang=lang,
                       reason="Banned by admin", contact="@support")
        )
        return

    if await is_maintenance_mode():
        if not (await db.is_admin(user.id) or await db.is_owner(user.id)):
            await safe_send_message(
                message,
                settings.get_str("maintenance_message",
                    get_string("error_maintenance", lang="hinglish"))
            )
            return

    joined, missing = await check_force_join(bot, user.id)
    if not joined:
        await send_force_join_message(message, missing)
        return

    is_new = await db.add_user(
        user_id=user.id,
        first_name=user.first_name or "",
        username=user.username or "",
        last_name=user.last_name or "",
    )

    if is_new:
        log.info(f"New user registered: {user.id} (@{user.username})")
        await log_new_user(bot, user)

    file_code = args.strip().upper() if args else ""

    if not file_code:
        await start_main_menu(message, user)
        return

    # Batch link? → BATCH-XXXXXX
    if file_code.upper().startswith("BATCH-"):
        await handle_batch_access(message, file_code.upper())
        return

    await handle_file_access(message, file_code)


@router.message(CommandStart())
async def start_command(message: Message, bot: Bot):
    """Simple /start command"""
    user = message.from_user
    log.debug(f"/start from user={user.id} (@{user.username})")

    if await is_user_banned(user.id):
        lang = await get_user_lang(user.id)
        await safe_send_message(
            message,
            get_string("user_banned_msg", lang=lang,
                       reason="Banned by admin", contact="@support")
        )
        return

    if await is_maintenance_mode():
        is_admin = await db.is_admin(user.id) or await db.is_owner(user.id)
        allow_admin = settings.get_bool("maintenance_allow_admins", True)
        if not (is_admin and allow_admin):
            await safe_send_message(
                message,
                settings.get_str("maintenance_message",
                    get_string("error_maintenance", lang="hinglish"))
            )
            return

    joined, missing = await check_force_join(bot, user.id)
    if not joined:
        await send_force_join_message(message, missing)
        return

    is_new = await db.add_user(
        user_id=user.id,
        first_name=user.first_name or "",
        username=user.username or "",
        last_name=user.last_name or "",
    )

    if is_new:
        log.info(f"New user registered: {user.id} (@{user.username})")
        await log_new_user(bot, user)

    await start_main_menu(message, user)


async def start_main_menu(message: Message, user):
    """Main menu — BOTH keyboards bhejta hai"""
    user_id = user.id
    lang = await get_user_lang(user_id)

    user_data = await db.get_user(user_id)
    is_new = False

    if user_data:
        joined_at = user_data.get("joined_at")
        if joined_at:
            try:
                if hasattr(joined_at, "timestamp"):
                    diff = time.time() - joined_at.timestamp()
                    is_new = diff < 10
                elif isinstance(joined_at, str):
                    joined_dt = datetime.strptime(joined_at, "%Y-%m-%d %H:%M:%S")
                    diff = time.time() - joined_dt.timestamp()
                    is_new = diff < 10
            except Exception:
                pass

    is_admin = await db.is_admin(user_id)
    is_owner = await db.is_owner(user_id)

    if is_new:
        welcome_text = get_string("welcome", lang=lang)
    else:
        welcome_text = get_string(
            "welcome_back",
            lang=lang,
            name=escape_html(user.first_name or "User")
        )

    inline_kb = get_main_menu_keyboard(
        lang=lang,
        is_admin=is_admin,
        is_owner=is_owner
    )

    # 1️⃣ Pehle reply keyboard bhejo (bottom buttons)
    reply_kb = get_main_menu_reply_keyboard(
        lang=lang,
        is_admin=is_admin or is_owner
    )

    try:
        await message.answer(
            "👇 Menu (niche se bhi choose kar sakte ho)",
            reply_markup=reply_kb
        )
    except Exception as e:
        log.debug(f"Reply keyboard send failed: {e}")

    # 2️⃣ Phir inline keyboard ke saath welcome message
    await safe_send_message(
        message,
        welcome_text,
        reply_markup=inline_kb,
        disable_web_page_preview=True,
    )

    try:
        await db.increment_daily_stat("active_users")
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# ⌨️ REPLY KEYBOARD BUTTON HANDLERS — YEH ACTUALLY KAAM KARENGE
# ═══════════════════════════════════════════════════════════════════════════

@router.message(F.text.in_([
    "📤 File Upload", "📤 Upload File", "📤 फाइल अपलोड", "📤 Immittere"
]))
async def reply_upload_button(message: Message, bot: Bot):
    """Reply keyboard — File Upload button"""
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    if await is_user_banned(user_id):
        await safe_send_message(
            message,
            get_string("user_banned_msg", lang=lang,
                       reason="Banned", contact="@support")
        )
        return

    if await is_maintenance_mode():
        if not (await db.is_admin(user_id) or await db.is_owner(user_id)):
            await safe_send_message(
                message,
                settings.get_str("maintenance_message", "Maintenance")
            )
            return

    joined, missing = await check_force_join(bot, user_id)
    if not joined:
        await send_force_join_message(message, missing)
        return

    allowed, retry = await check_rate_limit(user_id)
    if not allowed:
        await safe_send_message(
            message,
            get_string("error_rate_limit", lang=lang, seconds=retry)
        )
        return

    sessions.set(user_id, "awaiting_upload", True, timeout=600)

    max_size = settings.get_int("max_file_size", 50 * 1024 * 1024)
    allowed_exts = settings.get_list("allowed_extensions", [])
    allowed_types = ", ".join(allowed_exts[:10]) if allowed_exts else "Sab kuch"

    text = get_string(
        "upload_prompt",
        lang=lang,
        max_size=format_size(max_size),
        allowed_types=allowed_types,
    )

    from keyboards import get_upload_keyboard
    kb = get_upload_keyboard(lang=lang)

    await safe_send_message(message, text, reply_markup=kb)


@router.message(F.text.in_([
    "📁 Meri Files", "📁 My Files", "📁 मेरा फाइलहरू", "📁 Mei Fasciculi"
]))
async def reply_my_files_button(message: Message):
    """Reply keyboard — My Files button"""
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    if await is_user_banned(user_id):
        return

    per_page = settings.get_int("search_results_per_page", 10)

    try:
        files, total = await db.get_user_files(user_id, page=1, per_page=per_page)
    except Exception as e:
        log.error(f"get_user_files failed: {e}")
        files, total = [], 0

    if not files and total == 0:
        from keyboards import get_empty_files_keyboard
        await safe_send_message(
            message,
            get_string("my_files_empty", lang=lang),
            reply_markup=get_empty_files_keyboard(lang=lang)
        )
        return

    total_pages = max(1, (total + per_page - 1) // per_page)

    header = get_string(
        "my_files_header",
        lang=lang,
        count=total,
        page=1,
        total_pages=total_pages,
    )

    from keyboards import get_my_files_keyboard
    kb = get_my_files_keyboard(
        files=files,
        page=1,
        total_pages=total_pages,
        lang=lang,
        has_folder_support=settings.get_bool("folders_enabled", True),
    )

    await safe_send_message(message, header, reply_markup=kb)


@router.message(F.text.in_([
    "🔍 Search", "🔍 खोज", "🔍 Quaerere"
]))
async def reply_search_button(message: Message):
    """Reply keyboard — Search button"""
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    if await is_user_banned(user_id):
        return

    if not settings.get_bool("search_enabled", True):
        await safe_send_message(message, "❌ Search disabled")
        return

    sessions.set(user_id, "searching", True, timeout=300)

    await safe_send_message(
        message,
        get_string("search_prompt", lang=lang),
        reply_markup=get_back_button(lang, CB.HOME)
    )


@router.message(F.text.in_([
    "👤 Profile", "👤 प्रोफाइल", "👤 Profilum"
]))
async def reply_profile_button(message: Message):
    """Reply keyboard — Profile button"""
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    if await is_user_banned(user_id):
        return

    await show_profile(message, user_id, lang, edit=False)


@router.message(F.text.in_([
    "📊 Statistics", "📊 तथ्याङ्क", "📊 Statistica"
]))
async def reply_stats_button(message: Message):
    """Reply keyboard — Statistics button"""
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    if await is_user_banned(user_id):
        return

    user_data = await db.get_user(user_id)

    if await db.is_admin(user_id) or await db.is_owner(user_id):
        stats = await db.get_stats()
        text = get_string(
            "stats_header",
            lang=lang,
            total_users=stats.get("total_users", 0),
            total_files=stats.get("total_files", 0),
            total_downloads=stats.get("total_downloads", 0),
            total_uploads=stats.get("total_uploads", 0),
            total_size=format_size(stats.get("total_size", 0)),
            today_users=stats.get("today_users", 0),
            today_uploads=stats.get("today_uploads", 0),
            today_downloads=stats.get("today_downloads", 0),
            uptime=get_uptime(settings.get_float("bot_start_time", 0)),
        )
    else:
        text = get_string(
            "stats_user",
            lang=lang,
            files=user_data.get("total_files", 0) if user_data else 0,
            downloads=user_data.get("total_downloads", 0) if user_data else 0,
            size=format_size(0),
            joined=format_datetime(
                user_data.get("joined_at") if user_data else None,
                "%d %b %Y"
            ),
        )

    kb = get_stats_keyboard(lang=lang)
    await safe_send_message(message, text, reply_markup=kb)


@router.message(F.text.in_([
    "❓ Madad", "❓ Help", "❓ सहयोग", "❓ Auxilium"
]))
async def reply_help_button(message: Message):
    """Reply keyboard — Help button"""
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    if await is_user_banned(user_id):
        return

    support = settings.get_str("support_username", "")
    help_text = get_string("help", lang=lang, support=support or "Not set")
    kb = get_help_keyboard(lang=lang, support_username=support)

    await safe_send_message(message, help_text, reply_markup=kb)


@router.message(F.text.in_([
    "👑 Admin Panel", "👑 Admin", "👑 Owner Panel"
]))
async def reply_admin_button(message: Message):
    """Reply keyboard — Admin Panel button"""
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    is_admin = await db.is_admin(user_id)
    is_owner = await db.is_owner(user_id)

    if not (is_admin or is_owner):
        await safe_send_message(
            message,
            get_string("error_not_admin", lang=lang)
        )
        return

    from keyboards import get_admin_panel_keyboard
    text = get_string(
        "admin_panel",
        lang=lang,
        name=escape_html(message.from_user.first_name or "Admin"),
    )
    kb = get_admin_panel_keyboard(lang=lang, is_owner=is_owner)

    await safe_send_message(message, text, reply_markup=kb)


# ═══════════════════════════════════════════════════════════════════════════
# 🔗 FILE ACCESS VIA DEEP LINK
# ═══════════════════════════════════════════════════════════════════════════

async def handle_file_access(message: Message, file_code: str):
    """Deep link se file access"""
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    if not is_valid_file_code(file_code):
        await safe_send_message(
            message,
            get_string("link_invalid", lang=lang),
            reply_markup=get_back_button(lang)
        )
        return

    try:
        file_data = await db.get_file_by_code(file_code)
    except Exception as e:
        log.error(f"File lookup failed: {e}")
        file_data = None

    if not file_data:
        await safe_send_message(
            message,
            get_string("file_not_found", lang=lang),
            reply_markup=get_back_button(lang)
        )
        return

    user_locked = settings.get_bool("user_locked_links", True)

    if user_locked and file_data.get("uploader_id") != user_id:
        uploader = await db.get_user(file_data.get("uploader_id"))
        uploader_name = "Unknown"
        if uploader:
            uploader_name = (
                uploader.get("first_name")
                or (f"@{uploader.get('username')}" if uploader.get("username") else f"User {uploader.get('user_id')}")
            )

        if not (await db.is_admin(user_id) or await db.is_owner(user_id)):
            await safe_send_message(
                message,
                get_string("file_access_denied", lang=lang, owner=uploader_name),
                reply_markup=get_back_button(lang)
            )
            return

    await send_file_to_user(message, file_data, lang)


async def send_file_to_user(message: Message, file_data: dict, lang: str):
    """File ko user ko send karta hai"""
    try:
        file_id = file_data.get("file_id")
        file_name = file_data.get("file_name", "file")
        file_size = file_data.get("file_size", 0)
        file_code = file_data.get("file_code", "")
        file_type = file_data.get("file_type", "document")

        caption = (
            f"📄 <b>{escape_html(file_name)}</b>\n\n"
            f"📦 Size: {format_size(file_size)}\n"
            f"🔑 Code: <code>{file_code}</code>"
        )

        storage_channel = file_data.get("channel_id")
        storage_message_id = file_data.get("message_id")

        if storage_channel and storage_message_id:
            # copy_message — 50 MB re-send limit bypass
            try:
                await message.bot.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=storage_channel,
                    message_id=storage_message_id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                )
            except TelegramBadRequest:
                await message.bot.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=storage_channel,
                    message_id=storage_message_id,
                )
        elif file_type == "video":
            await message.answer_video(file_id, caption=caption, parse_mode=ParseMode.HTML)
        elif file_type == "audio":
            await message.answer_audio(file_id, caption=caption, parse_mode=ParseMode.HTML)
        elif file_type == "photo":
            await message.answer_photo(file_id, caption=caption, parse_mode=ParseMode.HTML)
        else:
            await message.answer_document(file_id, caption=caption, parse_mode=ParseMode.HTML)

        await db.increment_download_count(file_data.get("id"))
        await db.record_download(file_data.get("id"), message.from_user.id)
        log.info(f"File sent: {file_code} to user {message.from_user.id}")

    except TelegramBadRequest as e:
        log.error(f"File send failed: {e}")
        await safe_send_message(
            message,
            get_string("file_send_failed", lang=lang),
            reply_markup=get_back_button(lang)
        )
    except Exception as e:
        log.error(f"File send failed: {e}")
        await safe_send_message(
            message,
            get_string("error_generic", lang=lang, error=str(e)[:100]),
            reply_markup=get_back_button(lang)
        )


# ═══════════════════════════════════════════════════════════════════════════
# 📦 BATCH ACCESS — Ek link, multiple files
# ═══════════════════════════════════════════════════════════════════════════

async def handle_batch_access(message: Message, batch_code: str):
    """Batch link se saari files dikhata hai"""
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    batch = await db.get_batch_by_code(batch_code)

    if not batch or not batch.get("files"):
        await safe_send_message(
            message,
            get_string("file_not_found", lang=lang),
            reply_markup=get_back_button(lang)
        )
        return

    user_locked = settings.get_bool("user_locked_links", True)
    if user_locked and batch.get("uploader_id") != user_id:
        if not (await db.is_admin(user_id) or await db.is_owner(user_id)):
            await safe_send_message(
                message,
                get_string("file_access_denied", lang=lang, owner="batch owner"),
                reply_markup=get_back_button(lang)
            )
            return

    total_size = sum(f.get("file_size", 0) for f in batch["files"])

    text = (
        f"📦 <b>Batch Files</b>\n\n"
        f"🔑 Code: <code>{batch_code}</code>\n"
        f"📂 Files: <b>{len(batch['files'])}</b>\n"
        f"💾 Total Size: <b>{format_size(total_size)}</b>\n\n"
        f"Neeche se file choose karo ya sab download karo 👇"
    )

    kb = get_batch_view_keyboard(batch["files"], batch_code, lang)
    await safe_send_message(message, text, reply_markup=kb)

    await db.increment_batch_downloads(batch_code)


@router.callback_query(F.data.startswith(f"{CB.BATCH_DL_ALL}:"))
async def callback_batch_download_all(callback: CallbackQuery, bot: Bot):
    """Batch ki sab files ek-ek karke bhejta hai"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    batch_code = callback.data.split(":", 1)[1]
    batch = await db.get_batch_by_code(batch_code)

    if not batch or not batch.get("files"):
        await callback.answer("Batch nahi mila!", show_alert=True)
        return

    user_locked = settings.get_bool("user_locked_links", True)
    if user_locked and batch.get("uploader_id") != user_id:
        if not (await db.is_admin(user_id) or await db.is_owner(user_id)):
            await callback.answer("Yeh batch aapka nahi hai!", show_alert=True)
            return

    try:
        await callback.answer("📥 Sab files bheji ja rahi hain...")
    except Exception:
        pass

    from handlers_files import send_file_by_code

    for f in batch["files"]:
        try:
            await send_file_by_code(bot=bot, chat_id=user_id, file_data=f, lang=lang)
            await asyncio.sleep(1.0)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after + 1)
            try:
                await send_file_by_code(bot=bot, chat_id=user_id, file_data=f, lang=lang)
                await asyncio.sleep(1.0)
            except Exception as e2:
                log.error(f"Batch download retry failed ({f.get('file_code')}): {e2}")
        except Exception as e:
            log.error(f"Batch download failed ({f.get('file_code')}): {e}")

    await db.increment_batch_downloads(batch_code)


# ═══════════════════════════════════════════════════════════════════════════
# 📢 FORCE JOIN
# ═══════════════════════════════════════════════════════════════════════════

async def send_force_join_message(message: Message, missing_channels: list):
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    channels_data = []
    for ch in missing_channels:
        channel_id = ch.get("id", "")
        name = ch.get("name", "Channel")

        url = ""
        if str(channel_id).startswith("@") or not str(channel_id).startswith("-"):
            url = f"https://t.me/{str(channel_id).lstrip('@')}"
        elif str(channel_id).startswith("-100"):
            try:
                chat = await message.bot.get_chat(channel_id)
                if chat.invite_link:
                    url = chat.invite_link
            except Exception:
                pass

        if url:
            channels_data.append({"name": name, "url": url})

    text = get_string("force_join", lang=lang)

    if channels_data:
        kb = get_force_join_keyboard(channels_data, lang=lang)
    else:
        kb = get_close_keyboard(lang)

    await safe_send_message(message, text, reply_markup=kb)


@router.callback_query(F.data == CB.VERIFY)
async def verify_force_join(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    joined, missing = await check_force_join(bot, user_id)

    if not joined:
        try:
            await callback.answer(
                get_string("force_join_not_verified", lang=lang),
                show_alert=True
            )
        except Exception:
            pass
        return

    try:
        await callback.answer(
            get_string("force_join_verified", lang=lang),
            show_alert=False
        )
    except Exception:
        pass

    user = callback.from_user
    is_admin = await db.is_admin(user_id)
    is_owner = await db.is_owner(user_id)

    kb = get_main_menu_keyboard(
        lang=lang, is_admin=is_admin, is_owner=is_owner
    )

    welcome_text = get_string(
        "welcome_back", lang=lang,
        name=escape_html(user.first_name or "User")
    )

    await safe_edit_message(callback, welcome_text, reply_markup=kb)


# ═══════════════════════════════════════════════════════════════════════════
# 🏠 MAIN MENU CALLBACKS (INLINE BUTTONS)
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == CB.HOME)
async def callback_home(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    if await is_user_banned(user_id):
        try:
            await callback.answer("You are banned!", show_alert=True)
        except Exception:
            pass
        return

    joined, missing = await check_force_join(bot, user_id)
    if not joined:
        await send_force_join_message(callback.message, missing)
        return

    is_admin = await db.is_admin(user_id)
    is_owner = await db.is_owner(user_id)

    kb = get_main_menu_keyboard(
        lang=lang, is_admin=is_admin, is_owner=is_owner
    )

    welcome_text = get_string(
        "welcome_back", lang=lang,
        name=escape_html(callback.from_user.first_name or "User")
    )

    await safe_edit_message(callback, welcome_text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


@router.callback_query(F.data == CB.MENU)
async def callback_menu(callback: CallbackQuery, bot: Bot):
    await callback_home(callback, bot)


@router.callback_query(F.data == CB.CLOSE)
async def callback_close(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except Exception:
        pass
    try:
        await callback.answer()
    except Exception:
        pass


@router.callback_query(F.data == CB.NOOP)
async def callback_noop(callback: CallbackQuery):
    try:
        await callback.answer()
    except Exception:
        pass


@router.callback_query(F.data == CB.CANCEL)
async def callback_cancel(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)
    sessions.clear(user_id)
    try:
        await callback.answer(get_string("upload_cancelled", lang=lang))
    except Exception:
        pass
    await callback_home(callback, bot)


@router.callback_query(F.data == CB.BACK)
async def callback_back(callback: CallbackQuery, bot: Bot):
    await callback_home(callback, bot)


# ═══════════════════════════════════════════════════════════════════════════
# ❓ /help COMMAND
# ═══════════════════════════════════════════════════════════════════════════

@router.message(Command("help"))
async def help_command(message: Message):
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    if await is_user_banned(user_id):
        return

    support = settings.get_str("support_username", "")
    help_text = get_string("help", lang=lang, support=support or "Not set")
    kb = get_help_keyboard(lang=lang, support_username=support)

    await safe_send_message(message, help_text, reply_markup=kb)


@router.callback_query(F.data == CB.HELP)
async def callback_help(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    support = settings.get_str("support_username", "")
    help_text = get_string("help", lang=lang, support=support or "Not set")
    kb = get_help_keyboard(lang=lang, support_username=support)

    await safe_edit_message(callback, help_text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# ℹ️ /about COMMAND
# ═══════════════════════════════════════════════════════════════════════════

@router.message(Command("about"))
async def about_command(message: Message):
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    if await is_user_banned(user_id):
        return

    await show_about(message, lang, edit=False)


@router.callback_query(F.data == CB.ABOUT)
async def callback_about(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    await show_about(callback.message, lang, edit=True, callback=callback)


async def show_about(message, lang: str, edit: bool = False, callback=None):
    bot_name = settings.get_str("bot_name", Bootstrap.BOT_NAME)
    bot_version = Bootstrap.BOT_VERSION

    owner_id = Bootstrap.OWNER_ID
    owner_data = await db.get_user(owner_id)
    owner_name = f"ID: {owner_id}"
    if owner_data:
        if owner_data.get("username"):
            owner_name = f"@{owner_data['username']}"
        elif owner_data.get("first_name"):
            owner_name = owner_data["first_name"]

    languages = "🌍 Hinglish, English, Nepali, Latin"

    server_info = "Local"
    try:
        import psutil
        ram = psutil.virtual_memory()
        server_info = f"{ram.percent}% RAM used"
    except Exception:
        pass

    support = settings.get_str("support_username", "")
    update_channel = settings.get_str("update_channel", "")

    text = get_string(
        "about", lang=lang,
        bot_name=bot_name, version=bot_version, owner=owner_name,
        languages=languages, server=server_info,
        support=support or "N/A", updates=update_channel or "N/A",
    )

    kb = get_about_keyboard(lang=lang, update_channel=update_channel)

    if edit and callback:
        await safe_edit_message(callback, text, reply_markup=kb)
        try:
            await callback.answer()
        except Exception:
            pass
    else:
        await safe_send_message(message, text, reply_markup=kb)


# ═══════════════════════════════════════════════════════════════════════════
# 👤 /profile COMMAND
# ═══════════════════════════════════════════════════════════════════════════

@router.message(Command("profile"))
async def profile_command(message: Message):
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    if await is_user_banned(user_id):
        return

    await show_profile(message, user_id, lang)


@router.callback_query(F.data == CB.PROFILE)
async def callback_profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)
    await show_profile(callback.message, user_id, lang, edit=True, callback=callback)


async def show_profile(message, user_id: int, lang: str, edit: bool = False, callback=None):
    user_data = await db.get_user(user_id)

    if not user_data:
        await safe_send_message(
            message,
            get_string("user_not_registered", lang=lang)
        )
        return

    if await db.is_owner(user_id):
        status = "⭐ Owner"
    elif await db.is_admin(user_id):
        status = "👑 Admin"
    elif user_data.get("is_banned"):
        status = "🚫 Banned"
    elif user_data.get("is_premium"):
        status = "💎 Premium"
    else:
        status = "👤 User"

    premium_until = user_data.get("premium_until")
    premium_str = "No"
    if user_data.get("is_premium"):
        if premium_until:
            premium_str = f"Yes (until {format_datetime(premium_until, '%d %b %Y')})"
        else:
            premium_str = "Yes"

    name_parts = []
    if user_data.get("first_name"):
        name_parts.append(user_data["first_name"])
    if user_data.get("last_name"):
        name_parts.append(user_data["last_name"])
    name = " ".join(name_parts) or "Unknown"

    text = get_string(
        "my_profile", lang=lang,
        name=escape_html(name), user_id=user_id,
        username=user_data.get("username") or "none",
        join_date=format_datetime(user_data.get("joined_at"), "%d %b %Y"),
        total_files=user_data.get("total_files", 0),
        total_downloads=user_data.get("total_downloads", 0),
        status=status, premium=premium_str,
    )

    kb = get_profile_keyboard(lang=lang)

    if edit and callback:
        await safe_edit_message(callback, text, reply_markup=kb)
        try:
            await callback.answer()
        except Exception:
            pass
    else:
        await safe_send_message(message, text, reply_markup=kb)


# ═══════════════════════════════════════════════════════════════════════════
# 📊 /stats COMMAND
# ═══════════════════════════════════════════════════════════════════════════

@router.message(Command("stats"))
async def stats_command(message: Message):
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    if await is_user_banned(user_id):
        return

    user_data = await db.get_user(user_id)

    if await db.is_admin(user_id) or await db.is_owner(user_id):
        stats = await db.get_stats()
        text = get_string(
            "stats_header", lang=lang,
            total_users=stats.get("total_users", 0),
            total_files=stats.get("total_files", 0),
            total_downloads=stats.get("total_downloads", 0),
            total_uploads=stats.get("total_uploads", 0),
            total_size=format_size(stats.get("total_size", 0)),
            today_users=stats.get("today_users", 0),
            today_uploads=stats.get("today_uploads", 0),
            today_downloads=stats.get("today_downloads", 0),
            uptime=get_uptime(settings.get_float("bot_start_time", 0)),
        )
    else:
        text = get_string(
            "stats_user", lang=lang,
            files=user_data.get("total_files", 0) if user_data else 0,
            downloads=user_data.get("total_downloads", 0) if user_data else 0,
            size=format_size(0),
            joined=format_datetime(
                user_data.get("joined_at") if user_data else None, "%d %b %Y"
            ),
        )

    kb = get_stats_keyboard(lang=lang)
    await safe_send_message(message, text, reply_markup=kb)


@router.callback_query(F.data == CB.STATS)
async def callback_stats(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)
    user_data = await db.get_user(user_id)

    if await db.is_admin(user_id) or await db.is_owner(user_id):
        stats = await db.get_stats()
        text = get_string(
            "stats_header", lang=lang,
            total_users=stats.get("total_users", 0),
            total_files=stats.get("total_files", 0),
            total_downloads=stats.get("total_downloads", 0),
            total_uploads=stats.get("total_uploads", 0),
            total_size=format_size(stats.get("total_size", 0)),
            today_users=stats.get("today_users", 0),
            today_uploads=stats.get("today_uploads", 0),
            today_downloads=stats.get("today_downloads", 0),
            uptime=get_uptime(settings.get_float("bot_start_time", 0)),
        )
    else:
        text = get_string(
            "stats_user", lang=lang,
            files=user_data.get("total_files", 0) if user_data else 0,
            downloads=user_data.get("total_downloads", 0) if user_data else 0,
            size=format_size(0),
            joined=format_datetime(
                user_data.get("joined_at") if user_data else None, "%d %b %Y"
            ),
        )

    kb = get_stats_keyboard(lang=lang)
    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# ⚙️ /settings COMMAND
# ═══════════════════════════════════════════════════════════════════════════

@router.message(Command("settings"))
async def settings_command(message: Message):
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    if await is_user_banned(user_id):
        return

    text = get_string("settings_menu", lang=lang)
    kb = get_settings_keyboard(user_lang=lang, lang=lang)

    await safe_send_message(message, text, reply_markup=kb)


@router.callback_query(F.data == CB.SETTINGS)
async def callback_settings(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    text = get_string("settings_menu", lang=lang)
    kb = get_settings_keyboard(user_lang=lang, lang=lang)

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# 🌍 LANGUAGE SELECTION
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == CB.LANG)
async def callback_language(callback: CallbackQuery):
    user_id = callback.from_user.id
    current_lang = await get_user_lang(user_id)

    text = (
        "🌍 <b>Choose Language</b>\n"
        "🌍 <b>Apni bhasha chuno</b>\n"
        "🌍 <b>आफ्नो भाषा छान्नुहोस्</b>\n\n"
        "Select your preferred language:"
    )

    kb = get_language_selection_keyboard(current_lang=current_lang)
    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


@router.callback_query(F.data.startswith(f"{CB.LANG_SET}:"))
async def callback_language_set(callback: CallbackQuery):
    user_id = callback.from_user.id

    try:
        new_lang = callback.data.split(":", 1)[1]
    except IndexError:
        await callback.answer("Invalid language", show_alert=True)
        return

    if new_lang not in SUPPORTED_LANGUAGES:
        await callback.answer("Unsupported language", show_alert=True)
        return

    await db.set_user_language(user_id, new_lang)

    flag = get_language_flag(new_lang)
    name = get_language_name(new_lang, native=True)

    await callback.answer(
        f"✅ Language set: {flag} {name}",
        show_alert=False
    )

    text = get_string("settings_menu", lang=new_lang)
    kb = get_settings_keyboard(user_lang=new_lang, lang=new_lang)
    await safe_edit_message(callback, text, reply_markup=kb)


# ═══════════════════════════════════════════════════════════════════════════
# 📝 LOG NEW USER
# ═══════════════════════════════════════════════════════════════════════════

async def log_new_user(bot: Bot, user):
    try:
        log_channel = settings.get_int("log_channel_id", 0)
        if not log_channel:
            return
        if not settings.get_bool("log_new_user", True):
            return

        user_display = format_user_display(
            user.id, user.first_name or "", user.username or ""
        )

        total_users = await db.get_user_count()

        text = (
            f"🆕 <b>New User</b>\n\n"
            f"👤 {user_display}\n"
            f"🆔 <code>{user.id}</code>\n"
            f"📛 @{user.username or 'none'}\n"
            f"📅 {format_datetime(None, '%d %b %Y, %H:%M')}\n\n"
            f"📊 Total Users: <b>{total_users}</b>"
        )

        await bot.send_message(
            log_channel, text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
    except Exception as e:
        log.debug(f"Log new user failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "router",
    "start_command",
    "start_with_deep_link",
    "help_command",
    "about_command",
    "profile_command",
    "stats_command",
    "settings_command",
    "get_user_lang",
    "check_force_join",
    "is_user_banned",
    "is_maintenance_mode",
]


# ═══════════════════════════════════════════════════════════════════════════
# 📖 END OF FILE
# ═══════════════════════════════════════════════════════════════════════════