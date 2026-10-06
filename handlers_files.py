# ═══════════════════════════════════════════════════════════════════════════
# 🚀 ISUKOBIT — TELEGRAM FILE STORE BOT
# ═══════════════════════════════════════════════════════════════════════════
# File      : handlers_files.py (FULLY FIXED — Custom Filter)
# Purpose   : File management — My Files, Search, Download, Delete, Rename
# Author    : Isukobit Team
# Version   : 1.0.3
# Python    : 3.10+
# Library   : aiogram 3.x
# ═══════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════
# 📦 IMPORTS
# ═══════════════════════════════════════════════════════════════════════════

import io
import time
import asyncio
import qrcode
from typing import Optional, List, Dict, Any

from aiogram import Router, F, Bot
from aiogram.filters import Command, BaseFilter
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BufferedInputFile,
)
from aiogram.enums import ParseMode
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
)

from config import Bootstrap, Constants, settings, log, Colors
from database import db
from keyboards import (
    CB,
    get_my_files_keyboard,
    get_empty_files_keyboard,
    get_file_actions_keyboard,
    get_file_confirm_delete_keyboard,
    get_file_info_keyboard,
    get_search_keyboard,
    get_search_results_keyboard,
    get_no_results_keyboard,
    get_delete_selection_keyboard,
    get_bulk_confirm_keyboard,
    get_back_button,
    get_main_menu_keyboard,
    build_pagination_row,
    format_file_size,
    btn,
)
from strings import get_string
from utils import (
    escape_html,
    format_size,
    format_datetime,
    format_time_ago,
    generate_file_link,
    truncate,
    truncate_middle,
    get_file_icon,
    is_valid_file_code,
    rate_limiter,
    sessions,
)


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 ROUTER
# ═══════════════════════════════════════════════════════════════════════════

router = Router(name="files_handlers")


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 CUSTOM FILTER — Sirf session active hone pe match kare
# ═══════════════════════════════════════════════════════════════════════════

class HasFileSession(BaseFilter):
    """
    Yeh filter sirf tab True return karta hai jab user ka
    rename ya search session active ho.
    Warna False — message next router (admin) ko pass ho jayega.
    """
    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False
        uid = message.from_user.id
        return (
            sessions.has(uid, "renaming_file") or
            sessions.has(uid, "searching")
        )


# ═══════════════════════════════════════════════════════════════════════════
# 🛡️ HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

async def get_user_lang(user_id: int) -> str:
    try:
        return await db.get_user_language(user_id)
    except Exception:
        return settings.get_str("default_language", "hinglish")


async def is_user_banned(user_id: int) -> bool:
    try:
        return await db.is_user_banned(user_id)
    except Exception:
        return False


async def safe_send_message(
    message: Message,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
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


def get_files_per_page() -> int:
    return settings.get_int("search_results_per_page", 10)


# ═══════════════════════════════════════════════════════════════════════════
# 📁 MY FILES
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == CB.MY_FILES)
async def callback_my_files(callback: CallbackQuery):
    """My Files button"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    if await is_user_banned(user_id):
        await callback.answer("Banned!", show_alert=True)
        return

    await show_my_files(
        callback=callback,
        user_id=user_id,
        lang=lang,
        page=1,
        edit=True,
    )


@router.message(Command("myfiles"))
async def cmd_my_files(message: Message):
    """My Files command"""
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    if await is_user_banned(user_id):
        return

    await show_my_files(
        message=message,
        user_id=user_id,
        lang=lang,
        page=1,
        edit=False,
    )


@router.callback_query(F.data.startswith("myfiles:"))
async def callback_my_files_pagination(callback: CallbackQuery):
    """My Files pagination"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    parts = callback.data.split(":", 1)

    if len(parts) < 2:
        await callback.answer("Invalid", show_alert=True)
        return

    action = parts[1]

    if action == "refresh":
        page = 1
    else:
        try:
            page = int(action)
        except ValueError:
            page = 1

    await show_my_files(
        callback=callback,
        user_id=user_id,
        lang=lang,
        page=page,
        edit=True,
    )


async def show_my_files(
    user_id: int,
    lang: str,
    page: int = 1,
    edit: bool = False,
    callback: Optional[CallbackQuery] = None,
    message: Optional[Message] = None,
):
    """My Files display"""
    per_page = get_files_per_page()

    try:
        files, total = await db.get_user_files(
            user_id=user_id,
            page=page,
            per_page=per_page,
        )
    except Exception as e:
        log.error(f"get_user_files failed: {e}")
        files, total = [], 0

    if not files and page == 1:
        text = get_string("my_files_empty", lang=lang)
        kb = get_empty_files_keyboard(lang=lang)

        if edit and callback:
            await safe_edit_message(callback, text, reply_markup=kb)
            try:
                await callback.answer()
            except Exception:
                pass
        elif message:
            await safe_send_message(message, text, reply_markup=kb)
        return

    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))

    text = get_string(
        "my_files_header",
        lang=lang,
        count=total,
        page=page,
        total_pages=total_pages,
    )

    kb = get_my_files_keyboard(
        files=files,
        page=page,
        total_pages=total_pages,
        lang=lang,
        has_folder_support=settings.get_bool("folders_enabled", True),
    )

    if edit and callback:
        await safe_edit_message(callback, text, reply_markup=kb)
        try:
            await callback.answer()
        except Exception:
            pass
    elif message:
        await safe_send_message(message, text, reply_markup=kb)


# ═══════════════════════════════════════════════════════════════════════════
# 📄 FILE DETAILS / ACTIONS
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith(f"{CB.FILE}:"))
async def callback_file_view(callback: CallbackQuery):
    """File details"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    try:
        file_id_str = callback.data.split(":", 1)[1]
        file_db_id = int(file_id_str)
    except (IndexError, ValueError):
        await callback.answer("Invalid file", show_alert=True)
        return

    file_data = await db.get_file_by_id(file_db_id)

    if not file_data:
        await callback.answer(
            get_string("file_not_found", lang=lang),
            show_alert=True
        )
        return

    is_owner_of_file = file_data.get("uploader_id") == user_id
    is_admin = await db.is_admin(user_id) or await db.is_owner(user_id)

    if not is_owner_of_file and not is_admin:
        await callback.answer(
            "Yeh file aapki nahi hai!",
            show_alert=True
        )
        return

    file_name = file_data.get("file_name", "file")
    file_size = file_data.get("file_size", 0)
    file_code = file_data.get("file_code", "")
    uploaded_at = file_data.get("uploaded_at")
    downloads = file_data.get("download_count", 0)

    icon = get_file_icon(file_name)

    uploader_data = await db.get_user(file_data.get("uploader_id"))
    uploader_name = "Unknown"
    if uploader_data:
        if uploader_data.get("username"):
            uploader_name = f"@{uploader_data['username']}"
        elif uploader_data.get("first_name"):
            uploader_name = uploader_data["first_name"]

    text = (
        f"{icon} <b>File Details</b>\n\n"
        f"📝 <b>Name:</b> <code>{escape_html(file_name)}</code>\n"
        f"🔑 <b>Code:</b> <code>{file_code}</code>\n"
        f"📦 <b>Size:</b> {format_size(file_size)}\n"
        f"📅 <b>Uploaded:</b> {format_datetime(uploaded_at, '%d %b %Y, %H:%M')}\n"
        f"👤 <b>Uploader:</b> {escape_html(uploader_name)}\n"
        f"📥 <b>Downloads:</b> {downloads}\n"
    )

    if file_data.get("caption"):
        caption_preview = truncate(file_data["caption"], 100)
        text += f"\n💬 <b>Caption:</b> {escape_html(caption_preview)}"

    kb = get_file_actions_keyboard(
        file_code=file_code,
        is_owner=is_owner_of_file,
        lang=lang,
    )

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# 📥 DOWNLOAD
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith(f"{CB.FILE_DL}:"))
async def callback_file_download(callback: CallbackQuery, bot: Bot):
    """File download"""
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

    if file_data.get("uploader_id") != user_id:
        if not (await db.is_admin(user_id) or await db.is_owner(user_id)):
            await callback.answer("Yeh file aapki nahi hai!", show_alert=True)
            return

    try:
        await callback.answer("📤 File bheji ja rahi hai...")
    except Exception:
        pass

    await send_file_by_code(
        bot=bot,
        chat_id=user_id,
        file_data=file_data,
        lang=lang,
    )


async def send_file_by_code(
    bot: Bot,
    chat_id: int,
    file_data: Dict[str, Any],
    lang: str,
):
    """
    File ko chat mein bhejta hai.
    
    IMPORTANT: copy_message use karta hai (50 MB limit bypass).
    Agar file_id wala method use kare toh 50 MB pe block hoga.
    """
    file_id = file_data.get("file_id")
    file_name = file_data.get("file_name", "file")
    file_size = file_data.get("file_size", 0)
    file_code = file_data.get("file_code", "")
    file_type = file_data.get("file_type", "document")
    caption_text = file_data.get("caption", "")

    # Storage channel info (copy_message ke liye zaroori)
    storage_channel = file_data.get("channel_id")
    message_id = file_data.get("message_id")

    caption = (
        f"📄 <b>{escape_html(file_name)}</b>\n\n"
        f"📦 Size: {format_size(file_size)}\n"
        f"🔑 Code: <code>{file_code}</code>"
    )

    if caption_text:
        caption = f"{escape_html(caption_text)}\n\n{caption}"

    try:
        # ─── Naya method: copy_message (koi size limit nahi) ───────
        if storage_channel and message_id:
            try:
                await bot.copy_message(
                    chat_id=chat_id,
                    from_chat_id=storage_channel,
                    message_id=message_id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                )
                log.info(f"File copied (copy_message): {file_code} to {chat_id}")
            except TelegramBadRequest as e:
                # Agar caption nahi lag sakta toh bina caption try karo
                log.warning(f"copy_message with caption failed: {e}, trying without caption")
                await bot.copy_message(
                    chat_id=chat_id,
                    from_chat_id=storage_channel,
                    message_id=message_id,
                )
                log.info(f"File copied (no caption): {file_code} to {chat_id}")
        else:
            # ─── Fallback: purana method (50 MB tak hi kaam karega) ─
            log.warning(f"No channel_id/message_id for {file_code}, using send_document")
            
            if file_type == "video":
                await bot.send_video(
                    chat_id, file_id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                )
            elif file_type == "audio":
                await bot.send_audio(
                    chat_id, file_id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                )
            elif file_type == "photo":
                await bot.send_photo(
                    chat_id, file_id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                )
            elif file_type == "animation":
                await bot.send_animation(
                    chat_id, file_id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                )
            elif file_type == "voice":
                await bot.send_voice(
                    chat_id, file_id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                )
            else:
                await bot.send_document(
                    chat_id, file_id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                )

        # Counts update
        try:
            await db.increment_download_count(file_data.get("id"))
            await db.record_download(file_data.get("id"), chat_id)
        except Exception as e:
            log.warning(f"Download count update failed: {e}")

    except TelegramBadRequest as e:
        log.error(f"Send file failed: {e}")
        try:
            await bot.send_message(
                chat_id,
                get_string("file_send_failed", lang=lang),
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            pass
    except Exception as e:
        log.error(f"Send file failed: {e}")
        try:
            await bot.send_message(
                chat_id,
                get_string("error_generic", lang=lang, error=str(e)[:100]),
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════════════
# 🗑️ DELETE
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith(f"{CB.FILE_DEL}:"))
async def callback_file_delete(callback: CallbackQuery):
    """Delete confirmation"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    try:
        file_code = callback.data.split(":", 1)[1]
    except IndexError:
        await callback.answer("Invalid", show_alert=True)
        return

    file_data = await db.get_file_by_code(file_code)

    if not file_data:
        await callback.answer("File not found!", show_alert=True)
        return

    if file_data.get("uploader_id") != user_id:
        if not (await db.is_admin(user_id) or await db.is_owner(user_id)):
            await callback.answer("Not your file!", show_alert=True)
            return

    text = get_string(
        "file_delete_confirm",
        lang=lang,
        filename=escape_html(file_data.get("file_name", "file")),
        code=file_code,
    )

    kb = get_file_confirm_delete_keyboard(file_code=file_code, lang=lang)

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


@router.callback_query(F.data.startswith(f"{CB.CONFIRM}:del:"))
async def callback_file_delete_confirm(callback: CallbackQuery, bot: Bot):
    """Delete confirm"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    try:
        file_code = callback.data.split(":", 2)[2]
    except IndexError:
        await callback.answer("Invalid", show_alert=True)
        return

    file_data = await db.get_file_by_code(file_code)

    if not file_data:
        await callback.answer("File not found!", show_alert=True)
        return

    if file_data.get("uploader_id") != user_id:
        if not (await db.is_admin(user_id) or await db.is_owner(user_id)):
            await callback.answer("Not your file!", show_alert=True)
            return

    try:
        await db.delete_file(file_data.get("id"), deleted_by=user_id)
    except Exception as e:
        log.error(f"Delete failed: {e}")
        await callback.answer("Delete failed!", show_alert=True)
        return

    # ─── Channels se sirf ADMIN/OWNER delete kare toh file ude ───
    # Normal user delete kare → sirf uska access hat-ta hai,
    # file owner ke storage + backup channels mein SAFE rehti hai
    is_privileged = await db.is_admin(user_id) or await db.is_owner(user_id)

    if is_privileged:
        try:
            channel_id = file_data.get("channel_id")
            message_id = file_data.get("message_id")

            if channel_id and message_id:
                try:
                    await bot.delete_message(channel_id, message_id)
                except Exception as e:
                    log.debug(f"Delete from storage failed: {e}")

            backup_channel = file_data.get("backup_channel_id")
            backup_msg_id = file_data.get("backup_message_id")

            if backup_channel and backup_msg_id:
                try:
                    await bot.delete_message(backup_channel, backup_msg_id)
                except Exception as e:
                    log.debug(f"Delete from backup failed: {e}")
        except Exception as e:
            log.debug(f"Telegram delete failed: {e}")
    else:
        log.info(
            f"User-delete (channels safe): {file_code} "
            f"by user {user_id}"
        )

    await log_delete(bot, callback.from_user, file_code, file_data.get("file_name", ""))

    await callback.answer(
        get_string("file_delete_success", lang=lang),
        show_alert=False
    )

    await show_my_files(
        callback=callback,
        user_id=user_id,
        lang=lang,
        page=1,
        edit=True,
    )


async def log_delete(bot: Bot, user, file_code: str, file_name: str):
    """Delete log"""
    try:
        log_channel = settings.get_int("log_channel_id", 0)
        if not log_channel:
            return
        if not settings.get_bool("log_file_delete", True):
            return

        text = (
            f"🗑️ <b>File Deleted</b>\n\n"
            f"👤 {user.first_name or 'Unknown'}\n"
            f"🆔 <code>{user.id}</code>\n"
            f"📄 {escape_html(file_name)}\n"
            f"🔑 <code>{file_code}</code>\n"
            f"📅 {format_datetime(None, '%d %b %Y, %H:%M')}"
        )

        await bot.send_message(
            log_channel, text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except Exception as e:
        log.debug(f"log_delete failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# ✏️ RENAME
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith(f"{CB.FILE_RENAME}:"))
async def callback_file_rename(callback: CallbackQuery):
    """Rename prompt"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    try:
        file_code = callback.data.split(":", 1)[1]
    except IndexError:
        await callback.answer("Invalid", show_alert=True)
        return

    file_data = await db.get_file_by_code(file_code)

    if not file_data:
        await callback.answer("File not found!", show_alert=True)
        return

    if file_data.get("uploader_id") != user_id:
        if not (await db.is_admin(user_id) or await db.is_owner(user_id)):
            await callback.answer("Not your file!", show_alert=True)
            return

    sessions.set(user_id, "renaming_file", file_code, timeout=300)

    text = (
        f"✏️ <b>Rename File</b>\n\n"
        f"📄 Current: <code>{escape_html(file_data.get('file_name', 'file'))}</code>\n\n"
        f"Naya naam bhejo (extension ke saath):\n"
        f"Example: <code>my_notes.pdf</code>\n\n"
        f"Cancel karne ke liye /cancel bhejo."
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=btn("cancel", lang),
                callback_data=f"{CB.FILE}:{file_data.get('id')}"
            ),
        ],
    ])

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


async def handle_rename_input(message: Message, bot: Bot, lang: str):
    """Rename input process"""
    user_id = message.from_user.id
    new_name = (message.text or "").strip()

    if not new_name or len(new_name) > 200:
        await safe_send_message(
            message,
            "❌ Invalid naam! 1-200 characters ka hona chahiye.",
        )
        return

    file_code = sessions.get(user_id, "renaming_file")

    if not file_code:
        sessions.clear(user_id)
        return

    file_data = await db.get_file_by_code(file_code)

    if not file_data:
        sessions.clear(user_id)
        await safe_send_message(message, "❌ File not found!")
        return

    try:
        await db.rename_file(file_data.get("id"), new_name)
    except Exception as e:
        log.error(f"Rename failed: {e}")
        await safe_send_message(message, "❌ Rename failed!")
        return

    sessions.clear(user_id)

    text = (
        f"✅ <b>File renamed!</b>\n\n"
        f"📄 New name: <code>{escape_html(new_name)}</code>\n"
        f"🔑 Code: <code>{file_code}</code>"
    )

    kb = get_file_actions_keyboard(
        file_code=file_code,
        is_owner=True,
        lang=lang,
    )

    await safe_send_message(message, text, reply_markup=kb)


# ═══════════════════════════════════════════════════════════════════════════
# 📱 QR CODE
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith(f"{CB.FILE_QR}:"))
async def callback_file_qr(callback: CallbackQuery, bot: Bot):
    """File QR code"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    try:
        file_code = callback.data.split(":", 1)[1]
    except IndexError:
        await callback.answer("Invalid", show_alert=True)
        return

    file_data = await db.get_file_by_code(file_code)

    if not file_data:
        await callback.answer("File not found!", show_alert=True)
        return

    if file_data.get("uploader_id") != user_id:
        if not (await db.is_admin(user_id) or await db.is_owner(user_id)):
            await callback.answer("Not your file!", show_alert=True)
            return

    try:
        await callback.answer("📱 QR ban raha hai...")
    except Exception:
        pass

    file_link = generate_file_link(file_code)

    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(file_link)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        qr_bytes = buf.getvalue()

        photo = BufferedInputFile(
            qr_bytes,
            filename=f"qr_{file_code}.png"
        )

        caption = (
            f"📱 <b>QR Code</b>\n\n"
            f"📄 File: <code>{escape_html(file_data.get('file_name', 'file'))}</code>\n"
            f"🔑 Code: <code>{file_code}</code>\n\n"
            f"🔗 Scan karke file access karo!"
        )

        await callback.message.answer_photo(
            photo,
            caption=caption,
            parse_mode=ParseMode.HTML,
        )

    except Exception as e:
        log.error(f"QR generation failed: {e}")
        try:
            await callback.answer("QR failed!", show_alert=True)
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════════════
# 🔍 SEARCH
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == CB.SEARCH)
async def callback_search_prompt(callback: CallbackQuery):
    """Search prompt"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    if not settings.get_bool("search_enabled", True):
        await callback.answer("Search disabled", show_alert=True)
        return

    sessions.set(user_id, "searching", True, timeout=300)

    text = get_string("search_prompt", lang=lang)
    kb = get_search_keyboard(lang=lang)

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


@router.message(Command("search"))
async def cmd_search(message: Message):
    """Search command"""
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    if await is_user_banned(user_id):
        return

    if not settings.get_bool("search_enabled", True):
        return

    sessions.set(user_id, "searching", True, timeout=300)

    text = get_string("search_prompt", lang=lang)
    kb = get_search_keyboard(lang=lang)

    await safe_send_message(message, text, reply_markup=kb)


async def handle_search_input(message: Message, bot: Bot, lang: str):
    """Search input process"""
    user_id = message.from_user.id
    query = (message.text or "").strip()

    min_length = settings.get_int("search_min_query_length", 2)

    if len(query) < min_length:
        text = get_string(
            "search_too_short",
            lang=lang,
            min_length=min_length,
        )
        await safe_send_message(message, text)
        return

    sessions.delete(user_id, "searching")

    await show_search_results(
        message=message,
        user_id=user_id,
        query=query,
        page=1,
        lang=lang,
    )


async def show_search_results(
    user_id: int,
    query: str,
    page: int,
    lang: str,
    message: Optional[Message] = None,
    callback: Optional[CallbackQuery] = None,
    edit: bool = False,
):
    """Search results"""
    per_page = get_files_per_page()

    try:
        files, total = await db.search_files(
            query=query,
            user_id=user_id,
            page=page,
            per_page=per_page,
            search_own_only=True,
        )
    except Exception as e:
        log.error(f"search_files failed: {e}")
        files, total = [], 0

    if not files:
        text = get_string(
            "search_no_results",
            lang=lang,
            query=escape_html(query),
        )
        kb = get_no_results_keyboard(lang=lang)

        if edit and callback:
            await safe_edit_message(callback, text, reply_markup=kb)
            try:
                await callback.answer()
            except Exception:
                pass
        elif message:
            await safe_send_message(message, text, reply_markup=kb)
        return

    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))

    text = get_string(
        "search_results",
        lang=lang,
        query=escape_html(query),
        count=total,
        page=page,
        total_pages=total_pages,
    )

    kb = get_search_results_keyboard(
        files=files,
        query=query,
        page=page,
        total_pages=total_pages,
        lang=lang,
    )

    if edit and callback:
        await safe_edit_message(callback, text, reply_markup=kb)
        try:
            await callback.answer()
        except Exception:
            pass
    elif message:
        await safe_send_message(message, text, reply_markup=kb)


@router.callback_query(F.data.startswith("srch:"))
async def callback_search_pagination(callback: CallbackQuery):
    """Search pagination"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    try:
        parts = callback.data.split(":", 2)
        query = parts[1]
        page = int(parts[2])
    except (IndexError, ValueError):
        await callback.answer("Invalid", show_alert=True)
        return

    await show_search_results(
        user_id=user_id,
        query=query,
        page=page,
        lang=lang,
        callback=callback,
        edit=True,
    )


# ═══════════════════════════════════════════════════════════════════════════
# 🚫 CANCEL
# ═══════════════════════════════════════════════════════════════════════════

@router.message(Command("cancel"))
async def cmd_cancel(message: Message):
    """Cancel session"""
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    sessions.clear(user_id)

    is_admin = await db.is_admin(user_id)
    is_owner = await db.is_owner(user_id)

    kb = get_main_menu_keyboard(
        lang=lang,
        is_admin=is_admin,
        is_owner=is_owner,
    )

    welcome_text = get_string(
        "welcome_back",
        lang=lang,
        name=escape_html(message.from_user.first_name or "User"),
    )

    await safe_send_message(message, welcome_text, reply_markup=kb)


# ═══════════════════════════════════════════════════════════════════════════
# 📋 FILE INFO ALIAS
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("finfo:"))
async def callback_finfo(callback: CallbackQuery):
    """Short alias for file info"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    file_code = callback.data.split(":", 1)[1]
    file_data = await db.get_file_by_code(file_code)

    if not file_data:
        await callback.answer("Not found!", show_alert=True)
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
        lang=lang,
    )

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# 🗑️ BULK DELETE — Select & Delete / Delete All
# ═══════════════════════════════════════════════════════════════════════════

async def _delete_one_file(bot: Bot, file_data: Dict[str, Any], deleted_by: int) -> bool:
    """User delete → sirf DB (channels safe). Admin/Owner delete → channels se bhi."""
    try:
        await db.delete_file(file_data.get("id"), deleted_by=deleted_by)
    except Exception:
        return False

    is_privileged = await db.is_admin(deleted_by) or await db.is_owner(deleted_by)

    if is_privileged:
        ch, mid = file_data.get("channel_id"), file_data.get("message_id")
        if ch and mid:
            try:
                await bot.delete_message(ch, mid)
            except Exception:
                pass

        bch, bmid = file_data.get("backup_channel_id"), file_data.get("backup_message_id")
        if bch and bmid:
            try:
                await bot.delete_message(bch, bmid)
            except Exception:
                pass
    else:
        log.info(
            f"Bulk user-delete (channels safe): file_id={file_data.get('id')} "
            f"by user {deleted_by}"
        )
    return True


async def show_delete_selection(
    user_id: int,
    lang: str,
    page: int = 1,
    edit: bool = False,
    callback: Optional[CallbackQuery] = None,
    message: Optional[Message] = None,
):
    """Selection mode dikhata hai"""
    per_page = 10

    try:
        files, total = await db.get_user_files(user_id, page=page, per_page=per_page)
    except Exception as e:
        log.error(f"get_user_files failed: {e}")
        files, total = [], 0

    sel = sessions.get(user_id, "delete_select") or {"selected": []}
    selected_ids = sel.get("selected", [])

    if not files and page == 1:
        text = "📂 Koi files nahi hain!"
        kb = get_empty_files_keyboard(lang=lang)
        if edit and callback:
            await safe_edit_message(callback, text, reply_markup=kb)
            try: await callback.answer()
            except Exception: pass
        elif message:
            await safe_send_message(message, text, reply_markup=kb)
        return

    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))

    text = (
        f"🗑️ <b>Select &amp; Delete</b>\n\n"
        f"⬜ File pe tap karo → select/deselect\n"
        f"☑️ Selected: <b>{len(selected_ids)}</b> / {total} files\n\n"
        f"Page: <b>{page}/{total_pages}</b>"
    )

    kb = get_delete_selection_keyboard(files, selected_ids, page, total_pages, total, lang)

    if edit and callback:
        await safe_edit_message(callback, text, reply_markup=kb)
        try: await callback.answer()
        except Exception: pass
    elif message:
        await safe_send_message(message, text, reply_markup=kb)


@router.callback_query(F.data == CB.FILE_BULK)
async def callback_bulk_delete_menu(callback: CallbackQuery):
    """Select & Delete mode khulta hai"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    if await is_user_banned(user_id):
        await callback.answer("Banned!", show_alert=True)
        return

    if not sessions.has(user_id, "delete_select"):
        sessions.set(user_id, "delete_select", {"selected": [], "page": 1}, timeout=600)

    await show_delete_selection(user_id, lang, page=1, edit=True, callback=callback)


@router.callback_query(F.data.startswith(f"{CB.DSEL}:"))
async def callback_dsel_toggle(callback: CallbackQuery):
    """File select/deselect toggle"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    try:
        fid = int(callback.data.split(":", 1)[1])
    except (IndexError, ValueError):
        await callback.answer("Invalid", show_alert=True)
        return

    sel = sessions.get(user_id, "delete_select")
    if not sel:
        sessions.set(user_id, "delete_select", {"selected": [], "page": 1}, timeout=600)
        sel = sessions.get(user_id, "delete_select")

    if fid in sel["selected"]:
        sel["selected"].remove(fid)
    else:
        sel["selected"].append(fid)
    sessions.set(user_id, "delete_select", sel, timeout=600)

    page = sel.get("page", 1)
    await show_delete_selection(user_id, lang, page=page, edit=True, callback=callback)


@router.callback_query(F.data.startswith(f"{CB.DSEL_PAGE}:"))
async def callback_dsel_page(callback: CallbackQuery):
    """Selection mode pagination"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    try:
        page = int(callback.data.split(":", 1)[1])
    except (IndexError, ValueError):
        page = 1

    sel = sessions.get(user_id, "delete_select") or {"selected": []}
    sel["page"] = page
    sessions.set(user_id, "delete_select", sel, timeout=600)

    await show_delete_selection(user_id, lang, page=page, edit=True, callback=callback)


@router.callback_query(F.data == CB.DSEL_ALL)
async def callback_dsel_all(callback: CallbackQuery):
    """Sab files select karo"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    ids = await db.get_all_user_file_ids(user_id)
    sel = sessions.get(user_id, "delete_select") or {"selected": [], "page": 1}
    sel["selected"] = ids
    sessions.set(user_id, "delete_select", sel, timeout=600)

    try:
        await callback.answer(f"✅ {len(ids)} files selected!")
    except Exception:
        pass

    await show_delete_selection(user_id, lang, page=sel.get("page", 1), edit=True, callback=callback)


@router.callback_query(F.data == CB.DSEL_DEL)
async def callback_dsel_delete(callback: CallbackQuery):
    """Delete selected — confirmation"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    sel = sessions.get(user_id, "delete_select")
    if not sel or not sel.get("selected"):
        await callback.answer("Pehle files select karo! ⬜ pe tap karo", show_alert=True)
        return

    count = len(sel["selected"])
    text = (
        f"⚠️ <b>Pakka delete karni hain?</b>\n\n"
        f"🗑️ Files: <b>{count}</b>\n\n"
        f"❗ Yeh action UNDO nahi ho sakta!"
    )
    kb = get_bulk_confirm_keyboard(CB.DSEL_CONF, CB.FILE_BULK, count, lang)
    await safe_edit_message(callback, text, reply_markup=kb)

    try: await callback.answer()
    except Exception: pass


@router.callback_query(F.data == CB.DSEL_CONF)
async def callback_dsel_confirm(callback: CallbackQuery, bot: Bot):
    """Selected files delete karta hai"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    sel = sessions.get(user_id, "delete_select")
    if not sel or not sel.get("selected"):
        await callback.answer("Session expire ho gaya!", show_alert=True)
        return

    ids = list(sel["selected"])
    await callback.answer(f"🗑️ {len(ids)} files delete ho rahi hain...")

    deleted, failed = 0, 0
    for fid in ids:
        fdata = await db.get_file_by_id(fid)
        if not fdata:
            continue
        if fdata.get("uploader_id") != user_id:
            if not (await db.is_admin(user_id) or await db.is_owner(user_id)):
                continue
        if await _delete_one_file(bot, fdata, user_id):
            deleted += 1
        else:
            failed += 1
        await asyncio.sleep(0.4)

    sessions.delete(user_id, "delete_select")

    text = (
        f"🗑️ <b>Delete Complete!</b>\n\n"
        f"✅ Deleted: <b>{deleted}</b>\n"
        f"❌ Failed: <b>{failed}</b>"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=btn("my_files", lang), callback_data=CB.MY_FILES)],
        [InlineKeyboardButton(text=btn("home", lang), callback_data=CB.HOME)],
    ])
    await safe_send_message(callback.message, text, reply_markup=kb)


@router.callback_query(F.data == CB.DEL_ALL)
async def callback_del_all(callback: CallbackQuery):
    """Delete ALL — confirmation"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    ids = await db.get_all_user_file_ids(user_id)
    if not ids:
        await callback.answer("Koi files nahi hain!", show_alert=True)
        return

    count = len(ids)
    text = (
        f"💣 <b>SARI {count} files delete karni hain?</b>\n\n"
        f"⚠️⚠️ DANGER: Yeh sab kuch HAMESHA ke liye delete hoga!\n"
        f"❗ UNDO possible NAHI hai!\n\n"
        f"Soch samajh ke dabao 👇"
    )
    kb = get_bulk_confirm_keyboard(CB.DEL_ALL_CONF, CB.FILE_BULK, count, lang)
    await safe_edit_message(callback, text, reply_markup=kb)

    try: await callback.answer()
    except Exception: pass


@router.callback_query(F.data == CB.DEL_ALL_CONF)
async def callback_del_all_confirm(callback: CallbackQuery, bot: Bot):
    """SAARI files delete karta hai"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    ids = await db.get_all_user_file_ids(user_id)
    if not ids:
        await callback.answer("Koi files nahi hain!", show_alert=True)
        return

    await callback.answer(f"💣 {len(ids)} files delete ho rahi hain...")

    deleted, failed = 0, 0
    for fid in ids:
        fdata = await db.get_file_by_id(fid)
        if not fdata:
            continue
        if await _delete_one_file(bot, fdata, user_id):
            deleted += 1
        else:
            failed += 1
        await asyncio.sleep(0.4)

    sessions.delete(user_id, "delete_select")

    text = (
        f"💣 <b>Sab Delete Ho Gaya!</b>\n\n"
        f"✅ Deleted: <b>{deleted}</b>\n"
        f"❌ Failed: <b>{failed}</b>\n\n"
        f"📂 Ab tumhari file list khaali hai."
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=btn("upload", lang), callback_data=CB.UPLOAD)],
        [InlineKeyboardButton(text=btn("home", lang), callback_data=CB.HOME)],
    ])
    await safe_send_message(callback.message, text, reply_markup=kb)


@router.callback_query(F.data == CB.DSEL_CANCEL)
async def callback_dsel_cancel(callback: CallbackQuery):
    """Selection mode band"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    sessions.delete(user_id, "delete_select")

    await callback.answer("❌ Selection cancel")

    callback.data = "myfiles:1"
    await callback_my_files_pagination(callback)


# ═══════════════════════════════════════════════════════════════════════════
# 📝 TEXT INPUT HANDLER — FIXED (Custom Filter)
# ═══════════════════════════════════════════════════════════════════════════

@router.message(F.text & ~F.text.startswith("/"), HasFileSession())
async def handle_text_input(message: Message, bot: Bot):
    """
    Text messages handle karta hai — SIRF jab user ka file session active ho.
    
    Filter ki madad se yeh handler tab hi match karega jab:
    - User rename kar raha ho, YA
    - User search kar raha ho
    
    Warna handler skip ho jayega aur message next router (admin) ko jayega.
    Isliye admin settings jaise 'max_file_size' value yahan atak nahi rahi.
    """
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    if await is_user_banned(user_id):
        return

    # ─── Rename session ──────────────────────────────────────────
    if sessions.has(user_id, "renaming_file"):
        await handle_rename_input(message, bot, lang)
        return

    # ─── Search session ──────────────────────────────────────────
    if sessions.has(user_id, "searching"):
        await handle_search_input(message, bot, lang)
        return


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "router",
    "HasFileSession",
    "callback_my_files",
    "cmd_my_files",
    "show_my_files",
    "callback_file_view",
    "callback_file_download",
    "callback_file_delete",
    "callback_file_delete_confirm",
    "callback_file_rename",
    "callback_file_qr",
    "callback_search_prompt",
    "cmd_search",
    "show_search_results",
    "send_file_by_code",
    "callback_bulk_delete_menu",
    "show_delete_selection",
]


# ═══════════════════════════════════════════════════════════════════════════
# 📖 END OF FILE
# ═══════════════════════════════════════════════════════════════════════════