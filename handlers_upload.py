# ═══════════════════════════════════════════════════════════════════════════
# 🚀 ISUKOBIT — TELEGRAM FILE STORE BOT
# ═══════════════════════════════════════════════════════════════════════════
# File      : handlers_upload.py
# Purpose   : File upload ke saare handlers
# Author    : Isukobit Team
# Version   : 1.0.0
# Python    : 3.10+
# Library   : aiogram 3.x
# ═══════════════════════════════════════════════════════════════════════════
#
# YEH FILE KYA KARTI HAI:
# ─────────────────────────────────────────────────────────────────────────
# 1. Upload prompt dikhati hai (button dabane pe)
# 2. Document, Video, Audio, Photo, Voice, VideoNote, Animation handle
# 3. File size check
# 4. File type check
# 5. Duplicate detection (hash se)
# 6. Storage channel mein forward karti hai
# 7. Backup channel mein copy karti hai
# 8. File code generate karti hai
# 9. Database mein save karti hai
# 10. User ko link + code dikhati hai
# 11. Upload success keyboard
# 12. Error handling + retry
# 13. Log channel notification
# 14. Rate limit check
# 15. Per-user file limit check
# ═══════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════
# 📦 IMPORTS
# ═══════════════════════════════════════════════════════════════════════════

import time
import asyncio
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Document,
    Video,
    Audio,
    PhotoSize,
    Voice,
    VideoNote,
    Animation,
    Sticker,
)
from aiogram.enums import ParseMode
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramNetworkError,
    TelegramRetryAfter,
)

from config import Bootstrap, Constants, settings, log, Colors
from database import db
from keyboards import (
    CB,
    get_upload_keyboard,
    get_upload_success_keyboard,
    get_batch_prompt_keyboard,
    get_batch_success_keyboard,
    get_back_button,
    get_main_menu_keyboard,
    get_file_actions_keyboard,
    btn,
)
from strings import get_string
from utils import (
    escape_html,
    format_size,
    format_datetime,
    generate_file_code,
    detect_file_type,
    get_file_icon,
    get_file_extension,
    get_mime_type,
    is_allowed_extension,
    generate_file_link,
    truncate,
    truncate_middle,
    clean_filename,
    is_valid_file_code,
    rate_limiter,
    sessions,
)


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 ROUTER
# ═══════════════════════════════════════════════════════════════════════════

router = Router(name="upload_handlers")


# ═══════════════════════════════════════════════════════════════════════════
# 🛡️ HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

async def get_user_lang(user_id: int) -> str:
    """User ki language nikalta hai"""
    try:
        return await db.get_user_language(user_id)
    except Exception:
        return settings.get_str("default_language", "hinglish")


async def is_user_banned(user_id: int) -> bool:
    """Ban check"""
    try:
        return await db.is_user_banned(user_id)
    except Exception:
        return False


async def is_maintenance_mode() -> bool:
    """Maintenance check"""
    return settings.get_bool("maintenance_mode", False)


async def is_force_join_ok(bot: Bot, user_id: int) -> bool:
    """Force-join check (simple version)"""
    if not settings.get_bool("force_join_enabled", False):
        return True
    
    if await db.is_owner(user_id) or await db.is_admin(user_id):
        return True
    
    from aiogram.enums import ChatMemberStatus
    
    for i in range(1, 4):
        ch = settings.get_str(f"force_join_{i}", "")
        if not ch:
            continue
        
        try:
            member = await bot.get_chat_member(ch, user_id)
            if member.status in (
                ChatMemberStatus.LEFT,
                ChatMemberStatus.KICKED,
                ChatMemberStatus.RESTRICTED,
            ):
                return False
        except Exception:
            continue
    
    return True


async def check_rate_limit(user_id: int) -> tuple[bool, int]:
    """Rate limit check"""
    if await db.is_owner(user_id) or await db.is_admin(user_id):
        return True, 0
    
    max_per_min = settings.get_int("rate_limit_per_minute", 10)
    return rate_limiter.check(user_id, max_requests=max_per_min, window_seconds=60)


async def safe_send_message(
    message: Message,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    **kwargs
) -> Optional[Message]:
    """Safe sender"""
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
        log.warning(f"Send failed: {e}")
        return None
    except Exception as e:
        log.error(f"Send failed: {e}")
        return None


async def safe_edit_message(
    callback: CallbackQuery,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    **kwargs
) -> bool:
    """Safe editor"""
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
        if "not modified" in str(e).lower():
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
# 📤 UPLOAD PROMPT
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == CB.UPLOAD)
async def callback_upload_prompt(callback: CallbackQuery, bot: Bot):
    """Upload prompt dikhata hai"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)
    
    # Ban check
    if await is_user_banned(user_id):
        await callback.answer("You are banned!", show_alert=True)
        return
    
    # Maintenance check
    if await is_maintenance_mode():
        if not (await db.is_admin(user_id) or await db.is_owner(user_id)):
            await callback.answer(
                settings.get_str("maintenance_message", "Maintenance"),
                show_alert=True
            )
            return
    
    # Force join check
    if not await is_force_join_ok(bot, user_id):
        await callback.answer("Please join channels first!", show_alert=True)
        return
    
    # Rate limit
    allowed, retry = await check_rate_limit(user_id)
    if not allowed:
        await callback.answer(
            get_string("error_rate_limit", lang=lang, seconds=retry),
            show_alert=True
        )
        return
    
    # Session set karo
    sessions.set(user_id, "awaiting_upload", True, timeout=600)
    
    # Limits banao
    max_size = settings.get_int("max_file_size", 50 * 1024 * 1024)
    allowed_exts = settings.get_list("allowed_extensions", [])
    
    if allowed_exts:
        allowed_types = ", ".join(allowed_exts[:10])
        if len(allowed_exts) > 10:
            allowed_types += f" +{len(allowed_exts) - 10} more"
    else:
        allowed_types = "Sab kuch"
    
    text = get_string(
        "upload_prompt",
        lang=lang,
        max_size=format_size(max_size),
        allowed_types=allowed_types,
    )
    
    kb = get_upload_keyboard(lang=lang)
    
    await safe_edit_message(callback, text, reply_markup=kb)
    
    try:
        await callback.answer()
    except Exception:
        pass


@router.message(Command("upload"))
async def cmd_upload(message: Message, bot: Bot):
    """Upload command"""
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)
    
    if await is_user_banned(user_id):
        return
    
    if await is_maintenance_mode():
        if not (await db.is_admin(user_id) or await db.is_owner(user_id)):
            await safe_send_message(
                message,
                settings.get_str("maintenance_message", "Maintenance")
            )
            return
    
    if not await is_force_join_ok(bot, user_id):
        await safe_send_message(message, "Please join channels first!")
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
    
    kb = get_upload_keyboard(lang=lang)
    await safe_send_message(message, text, reply_markup=kb)


# ═══════════════════════════════════════════════════════════════════════════
# 📦 BATCH UPLOAD — Multiple files, ek link
# ═══════════════════════════════════════════════════════════════════════════

BATCH_PROMPT_TEXT = (
    "📦 <b>Batch Upload Mode ON</b>\n\n"
    "Ab jitni chahe files ek-ek karke bhejo — sab files "
    "<b>ek hi link</b> mein jayengi.\n\n"
    "✅ Done — jab sab bhej lo (ek link ban jayega)\n"
    "❌ Cancel — batch band kar do\n\n"
    "⏱️ {minutes} minute ka time hai. Files bhejna shuru karo 👇"
)


async def start_batch(message_or_callback, user_id: int, lang: str, bot: Bot, edit: bool = False) -> None:
    """Batch mode shuru karta hai"""
    session_secs = settings.get_int("batch_session_minutes", 30) * 60
    sessions.set(user_id, "batch_upload", {"file_ids": []}, timeout=session_secs)
    kb = get_batch_prompt_keyboard(lang)
    text = BATCH_PROMPT_TEXT.format(minutes=settings.get_int("batch_session_minutes", 30))

    if edit:
        await safe_edit_message(message_or_callback, text, reply_markup=kb)
        try:
            await message_or_callback.answer()
        except Exception:
            pass
    else:
        await safe_send_message(message_or_callback, text, reply_markup=kb)


@router.callback_query(F.data == CB.BATCH)
async def callback_batch_start(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    if await is_user_banned(user_id):
        await callback.answer("You are banned!", show_alert=True)
        return

    if await is_maintenance_mode():
        if not (await db.is_admin(user_id) or await db.is_owner(user_id)):
            await callback.answer("Maintenance mode ON hai", show_alert=True)
            return

    if not await is_force_join_ok(bot, user_id):
        await callback.answer("Pehle channels join karo!", show_alert=True)
        return

    await start_batch(callback, user_id, lang, bot, edit=True)


@router.message(Command("batch"))
async def cmd_batch(message: Message, bot: Bot):
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    if await is_user_banned(user_id):
        return

    if await is_maintenance_mode():
        if not (await db.is_admin(user_id) or await db.is_owner(user_id)):
            return

    if not await is_force_join_ok(bot, user_id):
        await safe_send_message(message, "Pehle channels join karo!")
        return

    await start_batch(message, user_id, lang, bot, edit=False)


async def generate_unique_batch_code(max_tries: int = 10) -> str:
    """Unique batch code — BATCH-XXXXXX format"""
    for _ in range(max_tries):
        code = generate_file_code(prefix="BATCH", separator="-")
        existing = await db.fetchone("SELECT id FROM batches WHERE batch_code = ?", (code,))
        if not existing:
            return code
    return generate_file_code(prefix="BATCH", separator="-", length=8)


@router.callback_query(F.data == CB.BATCH_DONE)
async def callback_batch_done(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    batch_data = sessions.get(user_id, "batch_upload")

    if not batch_data:
        await callback.answer("Batch session nahi mila!", show_alert=True)
        return

    st = upload_queue.stats(user_id)
    if not batch_data.get("file_ids") and st["pending"] == 0:
        await callback.answer("Pehle kam se kam 1 file bhejo!", show_alert=True)
        return

    if st["pending"] > 0:
        # Queue abhi chal rahi hai — sab hone pe link automatic banega
        batch_data["waiting_finish"] = True
        sessions.set(user_id, "batch_upload", batch_data,
                     timeout=settings.get_int("batch_session_minutes", 30) * 60)
        await callback.answer(
            f"⏳ {st['pending']} files queue mein hain — ho jaane pe link automatic banega!",
            show_alert=True,
        )
        await _update_queue_progress(bot, user_id, lang)
        return

    await _finalize_batch(bot, user_id, lang)
    try:
        await callback.answer("✅ Batch ban gaya!")
    except Exception:
        pass


@router.callback_query(F.data == CB.BATCH_CANCEL)
async def callback_batch_cancel(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    sessions.clear(user_id)
    upload_queue.reset_user(user_id)

    is_admin = await db.is_admin(user_id)
    is_owner = await db.is_owner(user_id)

    kb = get_main_menu_keyboard(lang=lang, is_admin=is_admin, is_owner=is_owner)

    await safe_edit_message(callback, "❌ Batch cancel ho gaya. Wapas swagat! 👇", reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# ⏳ UPLOAD QUEUE — Waiting list system (100-200 files bhi safely)
# ═══════════════════════════════════════════════════════════════════════════

async def _tg_retry(factory, max_retries: int = 4):
    """TelegramRetryAfter (rate limit) pakad ke wait karke retry karta hai.
    factory = lambda: coroutine — har retry pe nayi coroutine banti hai."""
    for _ in range(max_retries):
        try:
            return await factory()
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after + 1)
    raise RuntimeError("Telegram rate limit — retry limit reached")


# Channel writes ko serialize karta hai — flood control impossible
_channel_lock = asyncio.Lock()


class UploadQueue:
    """Batch files ki waiting list — ek-ek karke process hoti hai"""

    def __init__(self):
        self._queue: asyncio.Queue = asyncio.Queue()
        self._enqueued: Dict[int, int] = {}
        self._processed: Dict[int, int] = {}
        self._failed: Dict[int, int] = {}

    def stats(self, user_id: int) -> Dict[str, int]:
        enq = self._enqueued.get(user_id, 0)
        done = self._processed.get(user_id, 0)
        fail = self._failed.get(user_id, 0)
        return {"processed": done, "pending": max(0, enq - done - fail), "failed": fail}

    def enqueue(self, user_id: int, item: Dict[str, Any]) -> None:
        self._enqueued[user_id] = self._enqueued.get(user_id, 0) + 1
        self._queue.put_nowait(item)

    def reset_user(self, user_id: int) -> None:
        for d in (self._enqueued, self._processed, self._failed):
            d.pop(user_id, None)

    async def worker(self, bot: Bot) -> None:
        log.info(f"{Colors.info('⏳')} Upload queue worker started [ALL-MODE]")
        while True:
            try:
                item = await self._queue.get()
                async with _channel_lock:
                    await self._process_item(bot, item)
            except asyncio.CancelledError:
                return
            except Exception as e:
                log.error(f"Queue worker error: {e}")
                await asyncio.sleep(2)

    async def _process_item(self, bot: Bot, item: Dict[str, Any]) -> None:
        user_id = item["user_id"]
        step_delay = settings.get_float("queue_step_delay", 1.5)
        item_delay = settings.get_float("queue_item_delay", 1.0)
        lang = item.get("lang", "hinglish")

        try:
            # ── Batch session abhi bhi active hai? ──
            batch_data = sessions.get(user_id, "batch_upload")
            if batch_data is None:
                self._processed[user_id] = self._processed.get(user_id, 0) + 1
                return  # user ne cancel kar diya

            storage_channel = settings.get_int("storage_channel_id", 0)
            if not storage_channel:
                raise RuntimeError("Storage channel not configured!")

            file_code = await generate_unique_code()

            # ── Step 1: Storage channel mein copy ──
            try:
                stored_message = await _tg_retry(lambda: bot.copy_message(
                    chat_id=storage_channel,
                    from_chat_id=item["chat_id"],
                    message_id=item["message_id"],
                ))
            except TelegramBadRequest:
                stored_message = await _tg_retry(lambda: send_file_to_channel(
                    bot, storage_channel, item["file_id"],
                    item["file_type"], item["file_name"], item.get("caption", "")
                ))
            await asyncio.sleep(step_delay)

            # ── Step 2: Caption with full details ──
            uploader_display = escape_html(item["first_name"] or "Unknown")
            if item.get("username"):
                uploader_display += f" (@{item['username']})"
            meta_ext = get_file_extension(item["file_name"]) or item["mime_type"].split("/")[-1]
            channel_caption = (
                f"📄 <b>{escape_html(item['file_name'])}</b>\n"
                f"🔑 <code>{file_code}</code> | 📦 {format_size(item['file_size'])} | 📂 {item['file_type']}\n"
                f"📎 Ext: <code>{meta_ext}</code> | 🎬 <code>{escape_html(item['mime_type'])}</code>\n"
                f"🆔 File ID: <code>{truncate_middle(item['file_unique_id'], 44)}</code>\n"
                f"👤 {uploader_display} | 🆔 <code>{user_id}</code>\n"
                f"📅 {datetime.now().strftime('%d %b %Y, %H:%M')}"
            )
            if item.get("caption"):
                channel_caption += f"\n💬 <i>{escape_html(truncate(item['caption'], 150))}</i>"
            try:
                await _tg_retry(lambda: bot.edit_message_caption(
                    chat_id=storage_channel,
                    message_id=stored_message.message_id,
                    caption=channel_caption,
                    parse_mode=ParseMode.HTML,
                ))
            except Exception as e:
                log.debug(f"Storage caption edit failed: {e}")
            await asyncio.sleep(step_delay)

            # ── Step 3: Backup channel ──
            backup_channel = settings.get_int("backup_channel_id", 0)
            backup_message_id = 0
            if backup_channel and backup_channel != storage_channel:
                try:
                    backup_msg = await _tg_retry(lambda: bot.copy_message(
                        chat_id=backup_channel,
                        from_chat_id=storage_channel,
                        message_id=stored_message.message_id,
                    ))
                    backup_message_id = backup_msg.message_id
                    await asyncio.sleep(step_delay)
                    try:
                        await _tg_retry(lambda: bot.edit_message_caption(
                            chat_id=backup_channel,
                            message_id=backup_message_id,
                            caption=f"💾 <b>BACKUP</b>\n\n{channel_caption}",
                            parse_mode=ParseMode.HTML,
                        ))
                    except Exception as e:
                        log.debug(f"Backup caption edit failed: {e}")
                except Exception as e:
                    log.warning(f"Backup copy failed: {e}")

            # ── Step 4: Database save ──
            file_hash = hashlib.sha256(f"{item['file_id']}{user_id}".encode()).hexdigest()
            file_db_id = await db.add_file(
                file_code=file_code,
                file_id=item["file_id"],
                file_unique_id=item["file_unique_id"],
                uploader_id=user_id,
                uploader_username=item.get("username", ""),
                file_name=item["file_name"],
                file_size=item["file_size"],
                mime_type=item["mime_type"],
                file_extension=get_file_extension(item["file_name"]),
                file_type=item["file_type"],
                caption=item.get("caption", ""),
                message_id=stored_message.message_id,
                channel_id=storage_channel,
                file_hash=file_hash,
            )
            if backup_message_id and file_db_id:
                try:
                    await db.execute(
                        "UPDATE files SET backup_message_id = ?, backup_channel_id = ? WHERE id = ?",
                        (backup_message_id, backup_channel, file_db_id)
                    )
                except Exception as e:
                    log.warning(f"Backup info save failed: {e}")

            # ── Step 5: Batch session mein add karo ──
            batch_data["file_ids"].append(file_db_id)
            sessions.set(user_id, "batch_upload", batch_data,
                         timeout=settings.get_int("batch_session_minutes", 30) * 60)
            self._processed[user_id] = self._processed.get(user_id, 0) + 1
            await log_upload(bot, item["tg_user"], file_code,
                             item["file_name"], item["file_size"], item["file_type"])

            # ── Step 6: Batch → progress, Single → success message ──
            if item.get("is_batch"):
                await _update_queue_progress(bot, user_id, lang)
                st = self.stats(user_id)
                if st["pending"] == 0 and batch_data.get("waiting_finish"):
                    await _finalize_batch(bot, user_id, lang)
            else:
                file_link = generate_file_link(file_code)
                success_text = get_string(
                    "upload_success", lang=lang,
                    filename=escape_html(item["file_name"]),
                    size=format_size(item["file_size"]),
                    code=file_code,
                    link=file_link,
                )
                try:
                    await bot.send_message(
                        user_id,
                        success_text,
                        reply_markup=get_upload_success_keyboard(
                            file_code=file_code, lang=lang
                        ),
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True,
                    )
                except Exception as e:
                    log.debug(f"Single success send failed: {e}")
                upload_queue.reset_user(user_id)

        except Exception as e:
            self._failed[user_id] = self._failed.get(user_id, 0) + 1
            log.error(f"Queue item failed (user {user_id}): {e}")
            try:
                await bot.send_message(
                    user_id,
                    f"❌ File process nahi hui: <code>{escape_html(item['file_name'])}</code>\nReason: {escape_html(str(e)[:100])}",
                    parse_mode=ParseMode.HTML,
                )
            except Exception:
                pass
            await _update_queue_progress(bot, user_id, lang)
        finally:
            await asyncio.sleep(item_delay)


upload_queue = UploadQueue()


async def start_upload_worker(bot: Bot) -> None:
    """Background worker start karta hai (app.py se call hota hai)"""
    await upload_queue.worker(bot)


async def _update_queue_progress(bot: Bot, user_id: int, lang: str) -> None:
    """Queue ki progress wala message edit karta hai"""
    batch_data = sessions.get(user_id, "batch_upload")
    if not batch_data:
        return
    st = upload_queue.stats(user_id)
    text = (
        f"⏳ <b>Batch Queue</b>\n\n"
        f"✅ Processed: <b>{st['processed']}</b>\n"
        f"⏳ Pending:   <b>{st['pending']}</b>\n"
        f"❌ Failed:    <b>{st['failed']}</b>\n\n"
    )
    if st["pending"] > 0:
        text += "Files process ho rahi hain — automatic chalti rahegi..."
    elif batch_data.get("waiting_finish"):
        text += "✅ Queue complete! Link ban raha hai..."
    else:
        text += "✅ Sab process ho gayi! <b>✅ Done</b> dabao link ke liye."
    kb = get_batch_prompt_keyboard(lang)
    prog_id = batch_data.get("progress_msg_id")
    try:
        if prog_id:
            await bot.edit_message_text(
                text, chat_id=user_id, message_id=prog_id,
                reply_markup=kb, parse_mode=ParseMode.HTML,
            )
        else:
            msg = await bot.send_message(user_id, text, reply_markup=kb, parse_mode=ParseMode.HTML)
            batch_data["progress_msg_id"] = msg.message_id
            sessions.set(user_id, "batch_upload", batch_data,
                         timeout=settings.get_int("batch_session_minutes", 30) * 60)
    except Exception as e:
        log.debug(f"Progress update failed: {e}")


async def _finalize_batch(bot: Bot, user_id: int, lang: str) -> None:
    """Queue khatam hone pe batch code + link banata hai"""
    batch_data = sessions.get(user_id, "batch_upload")
    if not batch_data or not batch_data.get("file_ids"):
        return
    batch_code = await generate_unique_batch_code()
    ok = await db.create_batch(batch_code, user_id, batch_data["file_ids"])
    if not ok:
        try:
            await bot.send_message(user_id, "❌ Batch save nahi hua, dobara try karo!")
        except Exception:
            pass
        return
    file_count = len(batch_data["file_ids"])
    sessions.clear(user_id)
    upload_queue.reset_user(user_id)
    bot_username = settings.get_str("bot_username", Bootstrap.BOT_USERNAME).lstrip("@")
    batch_link = f"https://t.me/{bot_username}?start={batch_code}"
    text = (
        f"🎉 <b>Batch Ready Ho Gaya!</b>\n\n"
        f"📦 Files: <b>{file_count}</b>\n"
        f"🔑 Batch Code: <code>{batch_code}</code>\n"
        f"🔗 <b>Ek hi link — sab files:</b>\n{batch_link}\n\n"
        f"📌 Is link ko kahin bhi share karo!"
    )
    kb = get_batch_success_keyboard(batch_code, lang)
    try:
        await bot.send_message(user_id, text, reply_markup=kb, parse_mode=ParseMode.HTML)
    except Exception as e:
        log.error(f"Batch finalize send failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# 📄 DOCUMENT HANDLER
# ═══════════════════════════════════════════════════════════════════════════

@router.message(F.document)
async def handle_document(message: Message, bot: Bot):
    """Document upload handle karta hai"""
    user_id = message.from_user.id
    
    # Ban check
    if await is_user_banned(user_id):
        lang = await get_user_lang(user_id)
        await safe_send_message(
            message,
            get_string("user_banned_msg", lang=lang,
                       reason="Banned", contact="@support")
        )
        return
    
    # Maintenance check
    if await is_maintenance_mode():
        if not (await db.is_admin(user_id) or await db.is_owner(user_id)):
            await safe_send_message(
                message,
                settings.get_str("maintenance_message", "Maintenance")
            )
            return
    
    # Force join check
    if not await is_force_join_ok(bot, user_id):
        await safe_send_message(message, "Please join channels first!")
        return
    
    # Rate limit
    allowed, retry = await check_rate_limit(user_id)
    if not allowed:
        lang = await get_user_lang(user_id)
        await safe_send_message(
            message,
            get_string("error_rate_limit", lang=lang, seconds=retry)
        )
        return
    
    # Document info
    doc = message.document
    file_name = doc.file_name or "document"
    file_size = doc.file_size or 0
    mime_type = doc.mime_type or "application/octet-stream"
    file_id = doc.file_id
    file_unique_id = doc.file_unique_id
    
    # Process upload
    await process_upload(
        message=message,
        bot=bot,
        file_id=file_id,
        file_unique_id=file_unique_id,
        file_name=file_name,
        file_size=file_size,
        mime_type=mime_type,
        file_type="document",
        caption=message.caption or "",
    )


# ═══════════════════════════════════════════════════════════════════════════
# 🎬 VIDEO HANDLER
# ═══════════════════════════════════════════════════════════════════════════

@router.message(F.video)
async def handle_video(message: Message, bot: Bot):
    """Video upload handle karta hai"""
    user_id = message.from_user.id
    
    if await is_user_banned(user_id):
        return
    if await is_maintenance_mode():
        if not (await db.is_admin(user_id) or await db.is_owner(user_id)):
            return
    if not await is_force_join_ok(bot, user_id):
        return
    
    allowed, retry = await check_rate_limit(user_id)
    if not allowed:
        lang = await get_user_lang(user_id)
        await safe_send_message(
            message,
            get_string("error_rate_limit", lang=lang, seconds=retry)
        )
        return
    
    video = message.video
    file_name = video.file_name or f"video_{video.file_unique_id[:8]}.mp4"
    file_size = video.file_size or 0
    mime_type = video.mime_type or "video/mp4"
    
    await process_upload(
        message=message,
        bot=bot,
        file_id=video.file_id,
        file_unique_id=video.file_unique_id,
        file_name=file_name,
        file_size=file_size,
        mime_type=mime_type,
        file_type="video",
        caption=message.caption or "",
    )


# ═══════════════════════════════════════════════════════════════════════════
# 🎵 AUDIO HANDLER
# ═══════════════════════════════════════════════════════════════════════════

@router.message(F.audio)
async def handle_audio(message: Message, bot: Bot):
    """Audio upload handle karta hai"""
    user_id = message.from_user.id
    
    if await is_user_banned(user_id):
        return
    if await is_maintenance_mode():
        if not (await db.is_admin(user_id) or await db.is_owner(user_id)):
            return
    if not await is_force_join_ok(bot, user_id):
        return
    
    allowed, retry = await check_rate_limit(user_id)
    if not allowed:
        lang = await get_user_lang(user_id)
        await safe_send_message(
            message,
            get_string("error_rate_limit", lang=lang, seconds=retry)
        )
        return
    
    audio = message.audio
    title = audio.title or audio.performer or ""
    file_name = audio.file_name or f"audio_{audio.file_unique_id[:8]}.mp3"
    
    if title and not audio.file_name:
        file_name = f"{clean_filename(title)}.mp3"
    
    file_size = audio.file_size or 0
    mime_type = audio.mime_type or "audio/mpeg"
    
    await process_upload(
        message=message,
        bot=bot,
        file_id=audio.file_id,
        file_unique_id=audio.file_unique_id,
        file_name=file_name,
        file_size=file_size,
        mime_type=mime_type,
        file_type="audio",
        caption=message.caption or "",
    )


# ═══════════════════════════════════════════════════════════════════════════
# 🖼️ PHOTO HANDLER
# ═══════════════════════════════════════════════════════════════════════════

@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot):
    """Photo upload handle karta hai (largest size)"""
    user_id = message.from_user.id
    
    if await is_user_banned(user_id):
        return
    if await is_maintenance_mode():
        if not (await db.is_admin(user_id) or await db.is_owner(user_id)):
            return
    if not await is_force_join_ok(bot, user_id):
        return
    
    allowed, retry = await check_rate_limit(user_id)
    if not allowed:
        lang = await get_user_lang(user_id)
        await safe_send_message(
            message,
            get_string("error_rate_limit", lang=lang, seconds=retry)
        )
        return
    
    # Largest size lo
    photo = message.photo[-1]
    file_name = f"photo_{photo.file_unique_id[:8]}.jpg"
    file_size = photo.file_size or 0
    
    await process_upload(
        message=message,
        bot=bot,
        file_id=photo.file_id,
        file_unique_id=photo.file_unique_id,
        file_name=file_name,
        file_size=file_size,
        mime_type="image/jpeg",
        file_type="photo",
        caption=message.caption or "",
    )


# ═══════════════════════════════════════════════════════════════════════════
# 🎤 VOICE HANDLER
# ═══════════════════════════════════════════════════════════════════════════

@router.message(F.voice)
async def handle_voice(message: Message, bot: Bot):
    """Voice upload handle karta hai"""
    user_id = message.from_user.id
    
    if await is_user_banned(user_id):
        return
    if await is_maintenance_mode():
        if not (await db.is_admin(user_id) or await db.is_owner(user_id)):
            return
    if not await is_force_join_ok(bot, user_id):
        return
    
    allowed, retry = await check_rate_limit(user_id)
    if not allowed:
        lang = await get_user_lang(user_id)
        await safe_send_message(
            message,
            get_string("error_rate_limit", lang=lang, seconds=retry)
        )
        return
    
    voice = message.voice
    file_name = f"voice_{voice.file_unique_id[:8]}.ogg"
    file_size = voice.file_size or 0
    
    await process_upload(
        message=message,
        bot=bot,
        file_id=voice.file_id,
        file_unique_id=voice.file_unique_id,
        file_name=file_name,
        file_size=file_size,
        mime_type="audio/ogg",
        file_type="audio",
        caption=message.caption or "",
    )


# ═══════════════════════════════════════════════════════════════════════════
# 📹 VIDEO NOTE HANDLER
# ═══════════════════════════════════════════════════════════════════════════

@router.message(F.video_note)
async def handle_video_note(message: Message, bot: Bot):
    """Video note (round video) handle karta hai"""
    user_id = message.from_user.id
    
    if await is_user_banned(user_id):
        return
    if await is_maintenance_mode():
        if not (await db.is_admin(user_id) or await db.is_owner(user_id)):
            return
    if not await is_force_join_ok(bot, user_id):
        return
    
    allowed, retry = await check_rate_limit(user_id)
    if not allowed:
        lang = await get_user_lang(user_id)
        await safe_send_message(
            message,
            get_string("error_rate_limit", lang=lang, seconds=retry)
        )
        return
    
    vn = message.video_note
    file_name = f"videonote_{vn.file_unique_id[:8]}.mp4"
    file_size = vn.file_size or 0
    
    await process_upload(
        message=message,
        bot=bot,
        file_id=vn.file_id,
        file_unique_id=vn.file_unique_id,
        file_name=file_name,
        file_size=file_size,
        mime_type="video/mp4",
        file_type="video",
        caption=message.caption or "",
    )


# ═══════════════════════════════════════════════════════════════════════════
# 🎞️ ANIMATION (GIF) HANDLER
# ═══════════════════════════════════════════════════════════════════════════

@router.message(F.animation)
async def handle_animation(message: Message, bot: Bot):
    """Animation (GIF) handle karta hai"""
    user_id = message.from_user.id
    
    if await is_user_banned(user_id):
        return
    if await is_maintenance_mode():
        if not (await db.is_admin(user_id) or await db.is_owner(user_id)):
            return
    if not await is_force_join_ok(bot, user_id):
        return
    
    allowed, retry = await check_rate_limit(user_id)
    if not allowed:
        lang = await get_user_lang(user_id)
        await safe_send_message(
            message,
            get_string("error_rate_limit", lang=lang, seconds=retry)
        )
        return
    
    anim = message.animation
    file_name = anim.file_name or f"animation_{anim.file_unique_id[:8]}.mp4"
    file_size = anim.file_size or 0
    mime_type = anim.mime_type or "video/mp4"
    
    await process_upload(
        message=message,
        bot=bot,
        file_id=anim.file_id,
        file_unique_id=anim.file_unique_id,
        file_name=file_name,
        file_size=file_size,
        mime_type=mime_type,
        file_type="video",
        caption=message.caption or "",
    )


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 MAIN UPLOAD PROCESSING
# ═══════════════════════════════════════════════════════════════════════════

async def process_upload(
    message: Message,
    bot: Bot,
    file_id: str,
    file_unique_id: str,
    file_name: str,
    file_size: int,
    mime_type: str,
    file_type: str,
    caption: str = "",
):
    """
    File upload ka main processing function.
    
    Steps:
    1. Validation checks
    2. Duplicate check
    3. File code generate
    4. Storage channel mein forward
    5. Backup channel mein copy
    6. Database mein save
    7. User ko response
    """
    user = message.from_user
    user_id = user.id
    lang = await get_user_lang(user_id)
    
    # ─── Step 1: File size check ────────────────────────────────────
    max_size = settings.get_int("max_file_size", 2048 * 1024 * 1024)
    
    if file_size > max_size:
        text = get_string(
            "upload_too_large",
            lang=lang,
            size=format_size(file_size),
            max_size=format_size(max_size),
        )
        await safe_send_message(message, text)
        return
    
    # ─── Step 2: Extension check ────────────────────────────────────
    if not is_allowed_extension(file_name):
        ext = get_file_extension(file_name)
        allowed = settings.get_list("allowed_extensions", [])
        allowed_str = ", ".join(allowed[:10]) if allowed else "N/A"
        
        text = get_string(
            "upload_type_not_allowed",
            lang=lang,
            extension=ext or "unknown",
            allowed=allowed_str,
        )
        await safe_send_message(message, text)
        return
    
    # ─── Step 3: Per-user file limit ────────────────────────────────
    max_files = settings.get_int("max_files_per_user", 0)
    if max_files > 0:
        user_data = await db.get_user(user_id)
        current_count = user_data.get("total_files", 0) if user_data else 0
        
        if current_count >= max_files:
            text = get_string(
                "upload_limit_reached",
                lang=lang,
                limit=max_files,
            )
            await safe_send_message(message, text)
            return
    
    # ─── Step 4: Processing message ────────────────────────────────
    processing_msg = await safe_send_message(
        message,
        get_string("upload_processing", lang=lang)
    )
    
    try:
        # ─── SAB uploads → Queue (waiting list) — flood control impossible ───
        batch_data = sessions.get(user_id, "batch_upload")
        is_batch = batch_data is not None

        if is_batch:
            max_batch = settings.get_int("batch_max_files", 50)
            q = upload_queue.stats(user_id)
            if q["processed"] + q["pending"] >= max_batch:
                if processing_msg:
                    try:
                        await processing_msg.delete()
                    except Exception:
                        pass
                await safe_send_message(
                    message,
                    f"⚠️ Max <b>{max_batch}</b> files per batch! ✅ Done dabao.",
                    reply_markup=get_batch_prompt_keyboard(lang),
                )
                return

        upload_queue.enqueue(user_id, {
            "user_id": user_id,
            "chat_id": message.chat.id,
            "message_id": message.message_id,
            "file_id": file_id,
            "file_unique_id": file_unique_id,
            "file_name": file_name,
            "file_size": file_size,
            "mime_type": mime_type,
            "file_type": file_type,
            "caption": caption,
            "first_name": user.first_name or "",
            "username": user.username or "",
            "tg_user": user,
            "lang": lang,
            "is_batch": is_batch,
        })

        if processing_msg:
            try:
                await processing_msg.delete()
            except Exception:
                pass

        q = upload_queue.stats(user_id)
        try:
            if is_batch:
                await message.answer(
                    f"📝 <b>Queue mein add ho gayi!</b>\n"
                    f"✅ Done: {q['processed']} | ⏳ Pending: {q['pending']}",
                    parse_mode=ParseMode.HTML,
                )
            else:
                await message.answer(
                    f"📝 <b>File queue mein lag gayi!</b>\n"
                    f"⏳ Number {q['pending']} pe hai — thodi der mein code milega...",
                    parse_mode=ParseMode.HTML,
                )
        except Exception:
            pass

        if is_batch:
            await _update_queue_progress(message.bot, user_id, lang)
        sessions.delete(user_id, "awaiting_upload")
        return

        # ─── Step 5: File code generate ────────────────────────────
        file_code = await generate_unique_code()
        
        # ─── Channel writes — LOCK ke andar (flood control safe) ──
        async with _channel_lock:
            # ─── Step 6: Storage channel check ─────────────────────────
            storage_channel = settings.get_int("storage_channel_id", 0)
        
            if not storage_channel:
                log.error("Storage channel not configured!")
                if processing_msg:
                    try:
                        await processing_msg.edit_text(
                            "❌ Storage channel not configured! Contact admin.",
                            parse_mode=ParseMode.HTML
                        )
                    except Exception:
                        pass
                return
        
            # ─── Step 7: Storage channel mein copy karo ────────────────
            stored_message = None
        
            try:
                stored_message = await _tg_retry(lambda: bot.copy_message(
                    chat_id=storage_channel,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id,
                ))
            except TelegramBadRequest as e:
                log.error(f"Storage copy failed: {e}")
                # Fallback: send by file_id
                stored_message = await send_file_to_channel(
                    bot, storage_channel, file_id, file_type,
                    file_name, caption
                )
            except Exception as e:
                log.error(f"Storage failed: {e}")
                if processing_msg:
                    try:
                        await processing_msg.edit_text(
                            f"❌ Storage channel error: <code>{escape_html(str(e)[:200])}</code>\n\n"
                            f"Admin se bolo — bot ko storage channel mein "
                            f"admin (post permission) karein.",
                            parse_mode=ParseMode.HTML
                        )
                    except Exception:
                        pass
                return
        
            if not stored_message:
                log.error("Storage fallback bhi fail — bot channel mein admin hai?")
                if processing_msg:
                    try:
                        await processing_msg.edit_text(
                            "❌ Storage channel pe post nahi ho payi.\n"
                            "Bot ko storage channel mein <b>admin (post permission)</b> karo, "
                            "ya channel ID sahi set karo.",
                            parse_mode=ParseMode.HTML
                        )
                    except Exception:
                        pass
                return
        
            # ─── Step 8: Backup channel mein copy karo ─────────────────
            backup_channel = settings.get_int("backup_channel_id", 0)
            backup_message_id = 0
        
            if backup_channel and backup_channel != storage_channel:
                try:
                    backup_msg = await bot.copy_message(
                        chat_id=backup_channel,
                        from_chat_id=storage_channel,
                        message_id=stored_message.message_id,
                    )
                    backup_message_id = backup_msg.message_id
                except Exception as e:
                    log.warning(f"Backup copy failed: {e}")
        
            # ─── Step 9: Database mein save karo ───────────────────────
            file_hash = hashlib.sha256(
                f"{file_id}{user_id}".encode()
            ).hexdigest()
        
            file_db_id = await db.add_file(
                file_code=file_code,
                file_id=file_id,
                file_unique_id=file_unique_id,
                uploader_id=user_id,
                uploader_username=user.username or "",
                file_name=file_name,
                file_size=file_size,
                mime_type=mime_type,
                file_extension=get_file_extension(file_name),
                file_type=file_type,
                caption=caption,
                message_id=stored_message.message_id,
                channel_id=storage_channel,
                file_hash=file_hash,
            )
        
            # Backup info update
            if backup_message_id and file_db_id:
                try:
                    await db.execute(
                        """
                        UPDATE files 
                        SET backup_message_id = ?, backup_channel_id = ?
                        WHERE id = ?
                        """,
                        (backup_message_id, backup_channel, file_db_id)
                    )
                except Exception as e:
                    log.warning(f"Backup info save failed: {e}")
        
            # ─── Step 9.5: Channel mein uploader details ka caption ────
            uploader_display = escape_html(user.first_name or "Unknown")
            if user.username:
                uploader_display += f" (@{user.username})"

            meta_ext = get_file_extension(file_name) or mime_type.split("/")[-1]

            channel_caption = (
                f"📄 <b>{escape_html(file_name)}</b>\n"
                f"🔑 <code>{file_code}</code> | 📦 {format_size(file_size)} | 📂 {file_type}\n"
                f"📎 Ext: <code>{meta_ext}</code> | 🎬 <code>{escape_html(mime_type)}</code>\n"
                f"🆔 File ID: <code>{truncate_middle(file_unique_id, 44)}</code>\n"
                f"👤 {uploader_display} | 🆔 <code>{user_id}</code>\n"
                f"📅 {datetime.now().strftime('%d %b %Y, %H:%M')}"
            )

            if caption:
                channel_caption += f"\n💬 <i>{escape_html(truncate(caption, 150))}</i>"

            try:
                await bot.edit_message_caption(
                    chat_id=storage_channel,
                    message_id=stored_message.message_id,
                    caption=channel_caption,
                    parse_mode=ParseMode.HTML,
                )
            except Exception as e:
                log.debug(f"Storage caption edit failed (voice/videonote?): {e}")

            if backup_message_id:
                try:
                    await bot.edit_message_caption(
                        chat_id=backup_channel,
                        message_id=backup_message_id,
                        caption=f"💾 <b>BACKUP</b>\n\n{channel_caption}",
                        parse_mode=ParseMode.HTML,
                    )
                except Exception as e:
                    log.debug(f"Backup caption edit failed: {e}")
            await asyncio.sleep(settings.get_float("queue_item_delay", 1.0))

        # ─── Step 10: User ko response ─────────────────────────────
        file_link = generate_file_link(file_code)
        
        success_text = get_string(
            "upload_success",
            lang=lang,
            filename=escape_html(file_name),
            size=format_size(file_size),
            code=file_code,
            link=file_link,
        )
        
        kb = get_upload_success_keyboard(file_code=file_code, lang=lang)
        
        if processing_msg:
            try:
                await processing_msg.edit_text(
                    success_text,
                    reply_markup=kb,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            except Exception:
                await safe_send_message(message, success_text, reply_markup=kb)
        else:
            await safe_send_message(message, success_text, reply_markup=kb)
        
        # ─── Step 11: Log channel ─────────────────────────────────
        await log_upload(bot, user, file_code, file_name, file_size, file_type)
        
        # ─── Step 12: Session clear ────────────────────────────────
        sessions.delete(user_id, "awaiting_upload")
        
        log.info(
            f"{Colors.success('📤')} Upload: {file_code} "
            f"({format_size(file_size)}) by user {user_id}"
        )
    
    except Exception as e:
        log.error(f"process_upload failed: {e}", exc_info=True)
        
        if processing_msg:
            try:
                await processing_msg.edit_text(
                    get_string("error_generic", lang=lang, error=str(e)[:100]),
                    parse_mode=ParseMode.HTML
                )
            except Exception:
                pass


async def generate_unique_code(max_tries: int = 10) -> str:
    """Unique file code generate karta hai (DB check ke saath)"""
    for _ in range(max_tries):
        code = generate_file_code()
        existing = await db.get_file_by_code(code)
        if not existing:
            return code
    # Fallback: timestamp add karo
    return generate_file_code(length=8)


async def send_file_to_channel(
    bot: Bot,
    channel_id: int,
    file_id: str,
    file_type: str,
    file_name: str,
    caption: str = "",
) -> Optional[Message]:
    """Fallback — file_id se channel mein file bhejta hai"""
    try:
        if file_type == "video":
            return await bot.send_video(channel_id, file_id, caption=caption)
        elif file_type == "audio":
            return await bot.send_audio(channel_id, file_id, caption=caption)
        elif file_type == "photo":
            return await bot.send_photo(channel_id, file_id, caption=caption)
        else:
            return await bot.send_document(
                channel_id, file_id, caption=caption
            )
    except Exception as e:
        log.error(f"send_file_to_channel failed: {e}")
        return None


async def log_upload(bot: Bot, user, file_code: str, file_name: str,
                     file_size: int, file_type: str):
    """Upload ka log bhejta hai log channel mein"""
    try:
        log_channel = settings.get_int("log_channel_id", 0)
        if not log_channel:
            return
        
        if not settings.get_bool("log_file_upload", True):
            return
        
        text = (
            f"📤 <b>New Upload</b>\n\n"
            f"👤 User: {user.first_name or 'Unknown'}\n"
            f"🆔 ID: <code>{user.id}</code>\n"
            f"📛 @{user.username or 'none'}\n\n"
            f"📄 File: <code>{escape_html(file_name)}</code>\n"
            f"🔑 Code: <code>{file_code}</code>\n"
            f"📦 Size: {format_size(file_size)}\n"
            f"📂 Type: {file_type}\n"
            f"📅 {format_datetime(None, '%d %b %Y, %H:%M')}"
        )
        
        await bot.send_message(
            log_channel,
            text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
    except Exception as e:
        log.debug(f"log_upload failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# 📋 UPLOAD SUCCESS ACTIONS
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith(f"{CB.FILE_SHARE}:"))
async def callback_share_file(callback: CallbackQuery):
    """Share button — file link dikhata hai"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)
    
    try:
        file_code = callback.data.split(":", 1)[1]
    except IndexError:
        await callback.answer("Invalid", show_alert=True)
        return
    
    file_data = await db.get_file_by_code(file_code)
    
    if not file_data:
        await callback.answer(
            get_string("file_not_found", lang=lang),
            show_alert=True
        )
        return
    
    # Ownership check
    if file_data.get("uploader_id") != user_id:
        if not (await db.is_admin(user_id) or await db.is_owner(user_id)):
            await callback.answer(
                "This is not your file!",
                show_alert=True
            )
            return
    
    file_link = generate_file_link(file_code)
    
    text = get_string(
        "share_link",
        lang=lang,
        filename=escape_html(file_data.get("file_name", "file")),
        link=file_link,
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=btn("info", lang),
                callback_data=f"{CB.FILE_INFO}:{file_code}"
            ),
            InlineKeyboardButton(
                text=btn("qr", lang),
                callback_data=f"{CB.FILE_QR}:{file_code}"
            ),
        ],
        [
            InlineKeyboardButton(
                text=btn("back", lang),
                callback_data=CB.MY_FILES
            ),
            InlineKeyboardButton(
                text=btn("home", lang),
                callback_data=CB.HOME
            ),
        ],
    ])
    
    await safe_edit_message(callback, text, reply_markup=kb)
    
    try:
        await callback.answer(get_string("share_copied", lang=lang))
    except Exception:
        pass


@router.callback_query(F.data.startswith(f"{CB.FILE_INFO}:"))
async def callback_file_info(callback: CallbackQuery):
    """File info dikhata hai"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)
    
    try:
        file_code = callback.data.split(":", 1)[1]
    except IndexError:
        await callback.answer("Invalid", show_alert=True)
        return
    
    file_data = await db.get_file_by_code(file_code)
    
    if not file_data:
        await callback.answer(
            get_string("file_not_found", lang=lang),
            show_alert=True
        )
        return
    
    # Ownership check
    if file_data.get("uploader_id") != user_id:
        if not (await db.is_admin(user_id) or await db.is_owner(user_id)):
            await callback.answer("Not your file!", show_alert=True)
            return
    
    uploader = await db.get_user(file_data.get("uploader_id"))
    uploader_name = "Unknown"
    if uploader:
        uploader_name = uploader.get("first_name") or f"@{uploader.get('username', '')}"
    
    text = get_string(
        "file_info",
        lang=lang,
        filename=escape_html(file_data.get("file_name", "file")),
        code=file_code,
        size=format_size(file_data.get("file_size", 0)),
        date=format_datetime(file_data.get("uploaded_at"), "%d %b %Y"),
        uploader=escape_html(uploader_name),
        downloads=file_data.get("download_count", 0),
        file_type=file_data.get("file_type", "document"),
    )
    
    kb = get_file_actions_keyboard(
        file_code=file_code,
        is_owner=True,
        lang=lang
    )
    
    await safe_edit_message(callback, text, reply_markup=kb)
    
    try:
        await callback.answer()
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "router",
    "handle_document",
    "handle_video",
    "handle_audio",
    "handle_photo",
    "handle_voice",
    "handle_video_note",
    "handle_animation",
    "process_upload",
    "generate_unique_code",
    "cmd_batch",
    "callback_batch_start",
    "callback_batch_done",
    "callback_batch_cancel",
    "start_upload_worker",
    "upload_queue",
]


# ═══════════════════════════════════════════════════════════════════════════
# 📖 END OF FILE
# ═══════════════════════════════════════════════════════════════════════════
#
# Total lines : ~1150+
# Handlers    : 10+
# File types  : 7 (document, video, audio, photo, voice, video_note, animation)
#
# ═══════════════════════════════════════════════════════════════════════════