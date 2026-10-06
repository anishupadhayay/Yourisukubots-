# ═══════════════════════════════════════════════════════════════════════════
# 🚀 ISUKOBIT — TELEGRAM FILE STORE BOT
# ═══════════════════════════════════════════════════════════════════════════
# File      : handlers_admin.py (FULLY FIXED — Custom Filter)
# Purpose   : Admin panel ke saare handlers
# Author    : Isukobit Team
# Version   : 1.0.3
# Python    : 3.10+
# Library   : aiogram 3.x
# ═══════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════
# 📦 IMPORTS
# ═══════════════════════════════════════════════════════════════════════════

import os
import io
import time
import asyncio
import subprocess
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from aiogram import Router, F, Bot
from aiogram.filters import Command, BaseFilter
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BufferedInputFile,
    FSInputFile,
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
    get_admin_panel_keyboard,
    get_admin_stats_keyboard,
    get_admin_users_keyboard,
    get_admin_user_list_keyboard,
    get_admin_user_actions_keyboard,
    get_admin_files_keyboard,
    get_admin_broadcast_keyboard,
    get_broadcast_confirm_keyboard,
    get_admin_backup_keyboard,
    get_admin_channels_keyboard,
    get_admin_security_keyboard,
    get_admin_maintenance_keyboard,
    get_admin_logs_keyboard,
    get_admin_settings_keyboard,
    get_admin_danger_keyboard,
    get_back_button,
    get_main_menu_keyboard,
    build_pagination_row,
    btn,
)
from strings import get_string
from utils import (
    escape_html,
    format_size,
    format_datetime,
    format_time_ago,
    format_duration,
    get_uptime,
    humanize_number,
    truncate,
    rate_limiter,
    sessions,
    get_dir_size,
    cleanup_temp_files,
)


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 ROUTER
# ═══════════════════════════════════════════════════════════════════════════

router = Router(name="admin_handlers")


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 CUSTOM FILTERS
# ═══════════════════════════════════════════════════════════════════════════

async def admin_filter(event) -> bool:
    """Check karta hai ki user admin hai ya nahi"""
    user_id = event.from_user.id if event.from_user else 0
    try:
        return await db.is_admin(user_id) or await db.is_owner(user_id)
    except Exception:
        return False


class HasAdminSession(BaseFilter):
    """
    Yeh filter sirf tab True return karta hai jab user ka
    admin-related session active ho (editing_setting, changing_channel, etc.)
    
    Warna False — message next router ko pass ho jayega.
    """
    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False
        uid = message.from_user.id
        return any([
            sessions.has(uid, "editing_setting"),
            sessions.has(uid, "changing_channel"),
            sessions.has(uid, "banning_user"),
            sessions.has(uid, "banning_user_search"),
            sessions.has(uid, "unbanning_user_search"),
            sessions.has(uid, "admin_searching_user"),
            sessions.has(uid, "broadcasting"),
            sessions.has(uid, "broadcast_content"),
        ])


# Admin filter apply — all message/callback in this router must be from admin
router.message.filter(admin_filter)
router.callback_query.filter(admin_filter)


# ═══════════════════════════════════════════════════════════════════════════
# 🛡️ HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

async def get_user_lang(user_id: int) -> str:
    try:
        return await db.get_user_language(user_id)
    except Exception:
        return settings.get_str("default_language", "hinglish")


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


async def get_server_stats() -> Dict[str, Any]:
    """Server stats nikalta hai"""
    stats = {
        "ram_total": 0,
        "ram_used": 0,
        "ram_percent": 0,
        "disk_total": 0,
        "disk_used": 0,
        "disk_percent": 0,
        "cpu_percent": 0,
    }

    try:
        import psutil

        ram = psutil.virtual_memory()
        stats["ram_total"] = ram.total
        stats["ram_used"] = ram.used
        stats["ram_percent"] = ram.percent

        disk = psutil.disk_usage("/")
        stats["disk_total"] = disk.total
        stats["disk_used"] = disk.used
        stats["disk_percent"] = disk.percent

        stats["cpu_percent"] = psutil.cpu_percent(interval=0.1)
    except Exception as e:
        log.debug(f"psutil error: {e}")

    return stats


# ═══════════════════════════════════════════════════════════════════════════
# 👑 ADMIN PANEL MAIN
# ═══════════════════════════════════════════════════════════════════════════

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Admin panel command"""
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

    text = get_string(
        "admin_panel",
        lang=lang,
        name=escape_html(message.from_user.first_name or "Admin"),
    )

    kb = get_admin_panel_keyboard(lang=lang, is_owner=is_owner)

    await safe_send_message(message, text, reply_markup=kb)


@router.callback_query(F.data == CB.ADMIN)
async def callback_admin_panel(callback: CallbackQuery):
    """Admin panel button"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    is_owner = await db.is_owner(user_id)

    text = get_string(
        "admin_panel",
        lang=lang,
        name=escape_html(callback.from_user.first_name or "Admin"),
    )

    kb = get_admin_panel_keyboard(lang=lang, is_owner=is_owner)

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# 📊 ADMIN STATISTICS
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == CB.ADMIN_STATS)
async def callback_admin_stats(callback: CallbackQuery):
    """Admin statistics dashboard"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    try:
        await callback.answer("⏳ Loading stats...")
    except Exception:
        pass

    try:
        stats = await db.get_stats()
    except Exception as e:
        log.error(f"get_stats failed: {e}")
        stats = {}

    srv = await get_server_stats()
    uptime = get_uptime(settings.get_float("bot_start_time", 0))

    total_users = stats.get("total_users", 0)
    active_users = stats.get("active_users", 0)
    banned = stats.get("banned_users", 0)
    total_files = stats.get("total_files", 0)
    total_size = stats.get("total_size", 0)
    total_downloads = stats.get("total_downloads", 0)
    total_uploads = stats.get("total_uploads", 0)
    today_users = stats.get("today_users", 0)
    today_uploads = stats.get("today_uploads", 0)
    today_downloads = stats.get("today_downloads", 0)
    errors = stats.get("total_errors", 0)
    db_size = stats.get("db_size", 0)

    text = (
        f"📊 <b>Admin Statistics</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 <b>Users</b>\n"
        f"• Total: <b>{humanize_number(total_users)}</b>\n"
        f"• Active (7d): <b>{humanize_number(active_users)}</b>\n"
        f"• Banned: <b>{banned}</b>\n"
        f"• Today joined: <b>{today_users}</b>\n\n"
        f"📁 <b>Files</b>\n"
        f"• Total: <b>{humanize_number(total_files)}</b>\n"
        f"• Uploads: <b>{humanize_number(total_uploads)}</b>\n"
        f"• Downloads: <b>{humanize_number(total_downloads)}</b>\n"
        f"• Total size: <b>{format_size(total_size)}</b>\n"
        f"• Today uploads: <b>{today_uploads}</b>\n"
        f"• Today downloads: <b>{today_downloads}</b>\n\n"
        f"💾 <b>Database</b>\n"
        f"• Size: <b>{format_size(db_size)}</b>\n"
        f"• Errors: <b>{errors}</b>\n\n"
        f"🖥️ <b>Server</b>\n"
        f"• RAM: <b>{format_size(srv['ram_used'])} / {format_size(srv['ram_total'])}</b> ({srv['ram_percent']}%)\n"
        f"• Disk: <b>{format_size(srv['disk_used'])} / {format_size(srv['disk_total'])}</b> ({srv['disk_percent']}%)\n"
        f"• CPU: <b>{srv['cpu_percent']}%</b>\n\n"
        f"⏰ Uptime: <b>{uptime}</b>\n"
        f"📅 {format_datetime(None, '%d %b %Y, %H:%M')}"
    )

    kb = get_admin_stats_keyboard(lang=lang)

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# 👥 ADMIN — USER MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == CB.ADMIN_USERS)
async def callback_admin_users(callback: CallbackQuery):
    """Users menu"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    text = (
        f"👥 <b>User Management</b>\n\n"
        f"Kya karna chahte ho?\n"
        f"Neeche ke buttons se select karo 👇"
    )

    kb = get_admin_users_keyboard(lang=lang)

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


@router.callback_query(F.data.startswith(f"{CB.ADMIN_USERS}:list"))
async def callback_user_list(callback: CallbackQuery):
    """User list paginated"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    parts = callback.data.split(":")
    page = 1
    if len(parts) >= 3:
        try:
            page = int(parts[2])
        except ValueError:
            page = 1

    per_page = 10

    users, total = await db.get_users_paginated(page, per_page)
    total_pages = max(1, (total + per_page - 1) // per_page)

    text = (
        f"👥 <b>User List</b>\n\n"
        f"Total: <b>{total}</b> users\n"
        f"Page: <b>{page}/{total_pages}</b>"
    )

    kb = get_admin_user_list_keyboard(
        users=users,
        page=page,
        total_pages=total_pages,
        lang=lang,
    )

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


@router.callback_query(F.data.startswith(f"{CB.ADMIN_USERS}:view:"))
async def callback_user_view(callback: CallbackQuery):
    """User details"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    try:
        target_id = int(callback.data.split(":")[2])
    except (IndexError, ValueError):
        await callback.answer("Invalid user", show_alert=True)
        return

    user_data = await db.get_user(target_id)

    if not user_data:
        await callback.answer("User not found!", show_alert=True)
        return

    if target_id == Bootstrap.OWNER_ID:
        status = "⭐ Owner"
    elif user_data.get("is_admin"):
        status = "👑 Admin"
    elif user_data.get("is_banned"):
        status = "🚫 Banned"
    elif user_data.get("is_premium"):
        status = "💎 Premium"
    else:
        status = "👤 User"

    name_parts = []
    if user_data.get("first_name"):
        name_parts.append(user_data["first_name"])
    if user_data.get("last_name"):
        name_parts.append(user_data["last_name"])
    name = " ".join(name_parts) or "Unknown"

    text = (
        f"👤 <b>User Info</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🆔 ID: <code>{target_id}</code>\n"
        f"📝 Name: {escape_html(name)}\n"
        f"📛 Username: @{user_data.get('username') or 'none'}\n"
        f"⭐ Status: {status}\n"
        f"📅 Joined: {format_datetime(user_data.get('joined_at'), '%d %b %Y')}\n"
        f"🕐 Last active: {format_time_ago(user_data.get('last_activity'))}\n\n"
        f"📁 Files: <b>{user_data.get('total_files', 0)}</b>\n"
        f"📥 Downloads: <b>{user_data.get('total_downloads', 0)}</b>\n"
    )

    if user_data.get("is_banned"):
        text += (
            f"\n🚫 <b>Ban Reason:</b> {user_data.get('ban_reason') or 'N/A'}\n"
            f"📅 Banned at: {format_datetime(user_data.get('banned_at'), '%d %b %Y')}"
        )

    kb = get_admin_user_actions_keyboard(
        user_id=target_id,
        is_banned=user_data.get("is_banned", False),
        is_admin=user_data.get("is_admin", False),
        lang=lang,
    )

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# 🚫 BAN / UNBAN
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith(f"{CB.ADMIN_BAN}:") & ~F.data.contains("search"))
async def callback_user_ban(callback: CallbackQuery):
    """User ban karta hai"""
    admin_id = callback.from_user.id
    lang = await get_user_lang(admin_id)

    try:
        target_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Invalid", show_alert=True)
        return

    if target_id == Bootstrap.OWNER_ID:
        await callback.answer("Owner ko ban nahi kar sakte!", show_alert=True)
        return

    if await db.is_admin(target_id):
        if not await db.is_owner(admin_id):
            await callback.answer("Admin ko ban nahi kar sakte!", show_alert=True)
            return

    sessions.set(admin_id, "banning_user", target_id, timeout=300)

    text = (
        f"🚫 <b>Ban User</b>\n\n"
        f"User ID: <code>{target_id}</code>\n\n"
        f"Ban reason bhejo (ya /skip bhejo):\n"
        f"Cancel karne ke liye /cancel bhejo."
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=btn("skip", lang),
                callback_data=f"ban:skip:{target_id}"
            ),
            InlineKeyboardButton(
                text=btn("cancel", lang),
                callback_data=f"{CB.ADMIN_USERS}:view:{target_id}"
            ),
        ],
    ])

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


@router.callback_query(F.data.startswith("ban:skip:"))
async def callback_ban_skip(callback: CallbackQuery, bot: Bot):
    """Skip reason — direct ban"""
    admin_id = callback.from_user.id
    lang = await get_user_lang(admin_id)

    try:
        target_id = int(callback.data.split(":")[2])
    except (IndexError, ValueError):
        await callback.answer("Invalid", show_alert=True)
        return

    sessions.clear(admin_id)

    await perform_ban(callback, bot, target_id, "No reason", lang)


async def perform_ban(
    callback: CallbackQuery,
    bot: Bot,
    target_id: int,
    reason: str,
    lang: str,
):
    """Ban execute karta hai"""
    admin_id = callback.from_user.id

    try:
        await db.ban_user(
            user_id=target_id,
            reason=reason,
            banned_by=admin_id,
        )
    except Exception as e:
        log.error(f"ban_user failed: {e}")
        await callback.answer("Ban failed!", show_alert=True)
        return

    try:
        await bot.send_message(
            target_id,
            get_string(
                "user_banned_msg",
                lang="hinglish",
                reason=reason,
                contact="@support",
            ),
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        pass

    await log_admin_action(
        bot, admin_id, "ban_user", f"Banned {target_id}: {reason}"
    )

    await callback.answer("✅ User banned!", show_alert=True)

    callback.data = f"{CB.ADMIN_USERS}:view:{target_id}"
    await callback_user_view(callback)


async def perform_ban_message(
    message: Message,
    bot: Bot,
    target_id: int,
    reason: str,
    lang: str,
):
    """Ban execute karta hai (message se)"""
    admin_id = message.from_user.id

    try:
        await db.ban_user(
            user_id=target_id,
            reason=reason,
            banned_by=admin_id,
        )
    except Exception as e:
        log.error(f"ban_user failed: {e}")
        await safe_send_message(message, "❌ Ban failed!")
        return

    try:
        await bot.send_message(
            target_id,
            get_string(
                "user_banned_msg",
                lang="hinglish",
                reason=reason,
                contact="@support",
            ),
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        pass

    await log_admin_action(
        bot, admin_id, "ban_user", f"Banned {target_id}: {reason}"
    )

    text = (
        f"✅ <b>User Banned</b>\n\n"
        f"🆔 ID: <code>{target_id}</code>\n"
        f"📝 Reason: {escape_html(reason)}"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=btn("back", lang),
            callback_data=CB.ADMIN_USERS
        )],
    ])

    await safe_send_message(message, text, reply_markup=kb)


@router.callback_query(F.data.startswith(f"{CB.ADMIN_UNBAN}:") & ~F.data.contains("search"))
async def callback_user_unban(callback: CallbackQuery, bot: Bot):
    """User unban karta hai"""
    admin_id = callback.from_user.id
    lang = await get_user_lang(admin_id)

    try:
        target_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Invalid", show_alert=True)
        return

    try:
        await db.unban_user(target_id)
    except Exception as e:
        log.error(f"unban failed: {e}")
        await callback.answer("Unban failed!", show_alert=True)
        return

    try:
        await bot.send_message(
            target_id,
            "✅ <b>Aapka ban hata diya gaya hai!</b>\n\n"
            "Ab aap bot use kar sakte hain.",
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        pass

    await log_admin_action(
        bot, admin_id, "unban_user", f"Unbanned {target_id}"
    )

    await callback.answer("✅ User unbanned!", show_alert=True)

    callback.data = f"{CB.ADMIN_USERS}:view:{target_id}"
    await callback_user_view(callback)


# ═══════════════════════════════════════════════════════════════════════════
# 👑 ADD / REMOVE ADMIN (Owner only)
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith(f"{CB.ADMIN_ADD}:") & ~F.data.contains("search"))
async def callback_add_admin(callback: CallbackQuery):
    """Admin add karta hai (owner only)"""
    owner_id = callback.from_user.id
    lang = await get_user_lang(owner_id)

    if not await db.is_owner(owner_id):
        await callback.answer("Only owner!", show_alert=True)
        return

    try:
        target_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Invalid", show_alert=True)
        return

    if await db.is_admin(target_id):
        await callback.answer("Already admin!", show_alert=True)
        return

    try:
        await db.add_admin(target_id, added_by=owner_id)
    except Exception as e:
        log.error(f"add_admin failed: {e}")
        await callback.answer("Failed!", show_alert=True)
        return

    await callback.answer("✅ User is now admin!", show_alert=True)

    callback.data = f"{CB.ADMIN_USERS}:view:{target_id}"
    await callback_user_view(callback)


@router.callback_query(F.data.startswith(f"{CB.ADMIN_REMOVE}:") & ~F.data.contains("search"))
async def callback_remove_admin(callback: CallbackQuery, bot: Bot):
    """Admin remove karta hai (owner only)"""
    owner_id = callback.from_user.id
    lang = await get_user_lang(owner_id)

    if not await db.is_owner(owner_id):
        await callback.answer("Only owner!", show_alert=True)
        return

    try:
        target_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Invalid", show_alert=True)
        return

    if target_id == Bootstrap.OWNER_ID:
        await callback.answer("Cannot remove owner!", show_alert=True)
        return

    try:
        await db.remove_admin(target_id)
    except Exception as e:
        log.error(f"remove_admin failed: {e}")
        await callback.answer("Failed!", show_alert=True)
        return

    try:
        await bot.send_message(
            target_id,
            "ℹ️ Aapko admin se remove kar diya gaya hai.",
        )
    except Exception:
        pass

    await callback.answer("✅ Admin removed!", show_alert=True)

    callback.data = f"{CB.ADMIN_USERS}:view:{target_id}"
    await callback_user_view(callback)


# ═══════════════════════════════════════════════════════════════════════════
# 🔍 SEARCH USER / BAN / UNBAN PROMPTS
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == CB.ADMIN_SEARCH_USER)
async def callback_search_user_prompt(callback: CallbackQuery):
    """Search user prompt"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    sessions.set(user_id, "admin_searching_user", True, timeout=300)

    text = (
        f"🔍 <b>Search User</b>\n\n"
        f"User ka naam, username, ya ID bhejo.\n"
        f"Example: <code>Raj</code>, <code>@raj_123</code>, <code>123456789</code>\n\n"
        f"Cancel: /cancel"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=btn("cancel", lang),
            callback_data=CB.ADMIN_USERS
        )],
    ])

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


@router.callback_query(F.data == CB.ADMIN_BAN)
async def callback_ban_prompt(callback: CallbackQuery):
    """Ban user prompt"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    sessions.set(user_id, "banning_user_search", True, timeout=300)

    text = (
        f"🚫 <b>Ban User</b>\n\n"
        f"User ID ya username bhejo.\n"
        f"Example: <code>123456789</code> ya <code>@raj_123</code>\n\n"
        f"Cancel: /cancel"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=btn("cancel", lang),
            callback_data=CB.ADMIN_USERS
        )],
    ])

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


@router.callback_query(F.data == CB.ADMIN_UNBAN)
async def callback_unban_prompt(callback: CallbackQuery):
    """Unban user prompt"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    sessions.set(user_id, "unbanning_user_search", True, timeout=300)

    text = (
        f"✅ <b>Unban User</b>\n\n"
        f"User ID ya username bhejo.\n\n"
        f"Cancel: /cancel"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=btn("cancel", lang),
            callback_data=CB.ADMIN_USERS
        )],
    ])

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# 📣 BROADCAST
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == CB.ADMIN_BROADCAST)
async def callback_broadcast_prompt(callback: CallbackQuery):
    """Broadcast prompt"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    sessions.set(user_id, "broadcasting", {"step": "content"}, timeout=600)

    text = get_string("broadcast_prompt", lang=lang)
    kb = get_admin_broadcast_keyboard(lang=lang)

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


async def handle_broadcast_content(message: Message, bot: Bot, lang: str):
    """Broadcast content receive karta hai"""
    user_id = message.from_user.id

    content = {
        "type": "text",
        "text": message.text or message.caption or "",
        "file_id": None,
        "message_id": message.message_id,
        "from_chat_id": message.chat.id,
    }

    if message.photo:
        content["type"] = "photo"
        content["file_id"] = message.photo[-1].file_id
    elif message.video:
        content["type"] = "video"
        content["file_id"] = message.video.file_id
    elif message.audio:
        content["type"] = "audio"
        content["file_id"] = message.audio.file_id
    elif message.document:
        content["type"] = "document"
        content["file_id"] = message.document.file_id
    elif message.animation:
        content["type"] = "animation"
        content["file_id"] = message.animation.file_id

    sessions.set(user_id, "broadcast_content", content, timeout=600)
    sessions.set(user_id, "broadcasting", {"step": "confirm"}, timeout=600)

    try:
        user_ids = await db.get_all_user_ids()
        total = len(user_ids)
    except Exception:
        total = 0

    text = get_string(
        "broadcast_confirm",
        lang=lang,
        count=total,
    )

    kb = get_broadcast_confirm_keyboard(lang=lang)

    await safe_send_message(message, text, reply_markup=kb)


@router.callback_query(F.data == CB.BC_CONFIRM)
async def callback_broadcast_confirm(callback: CallbackQuery, bot: Bot):
    """Broadcast confirm — send karta hai"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    content = sessions.get(user_id, "broadcast_content")

    if not content:
        await callback.answer("Session expired!", show_alert=True)
        sessions.clear(user_id)
        return

    sessions.clear(user_id)

    await callback.answer("🚀 Broadcast started!")

    await run_broadcast(bot, callback.from_user, content, lang, callback)


@router.callback_query(F.data == CB.BC_CANCEL)
async def callback_broadcast_cancel(callback: CallbackQuery):
    """Broadcast cancel"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    sessions.clear(user_id)

    await callback.answer(
        get_string("broadcast_cancelled", lang=lang),
        show_alert=True
    )

    callback.data = CB.ADMIN
    await callback_admin_panel(callback)


async def run_broadcast(
    bot: Bot,
    admin,
    content: dict,
    lang: str,
    callback: CallbackQuery,
):
    """Broadcast run karta hai"""
    try:
        user_ids = await db.get_all_user_ids()
    except Exception as e:
        log.error(f"get_all_user_ids failed: {e}")
        return

    total = len(user_ids)

    if total == 0:
        return

    try:
        bc_id = await db.create_broadcast(
            admin_id=admin.id,
            message_type=content.get("type", "text"),
            message_text=content.get("text", ""),
            file_id=content.get("file_id") or "",
            total_users=total,
        )
    except Exception:
        bc_id = None

    sent = 0
    failed = 0
    blocked = 0

    batch_size = 25
    delay_between_batches = 1.0

    for i in range(0, total, batch_size):
        batch = user_ids[i:i + batch_size]

        for uid in batch:
            try:
                await send_broadcast_message(bot, uid, content)
                sent += 1
            except TelegramForbiddenError:
                blocked += 1
            except TelegramBadRequest as e:
                log.debug(f"Broadcast to {uid} failed: {e}")
                failed += 1
            except Exception as e:
                log.debug(f"Broadcast to {uid} failed: {e}")
                failed += 1

        if bc_id:
            try:
                await db.update_broadcast_stats(bc_id, sent=0, status="running")
            except Exception:
                pass

        await asyncio.sleep(delay_between_batches)

    if bc_id:
        try:
            await db.update_broadcast_stats(
                bc_id, sent=sent, failed=failed, blocked=blocked, status="completed"
            )
        except Exception:
            pass

    try:
        report_text = (
            f"✅ <b>Broadcast Complete!</b>\n\n"
            f"✅ Sent: <b>{sent}</b>\n"
            f"❌ Failed: <b>{failed}</b>\n"
            f"🚫 Blocked: <b>{blocked}</b>\n"
            f"📊 Total: <b>{total}</b>"
        )

        await callback.message.answer(
            report_text,
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        pass

    await log_admin_action(
        bot, admin.id, "broadcast",
        f"Sent to {sent}, failed: {failed}, blocked: {blocked}"
    )


async def send_broadcast_message(bot: Bot, chat_id: int, content: dict):
    """Ek user ko broadcast bhejta hai"""
    ctype = content.get("type", "text")
    text = content.get("text", "")
    file_id = content.get("file_id")

    if ctype == "photo" and file_id:
        await bot.send_photo(chat_id, file_id, caption=text or None, parse_mode=ParseMode.HTML)
    elif ctype == "video" and file_id:
        await bot.send_video(chat_id, file_id, caption=text or None, parse_mode=ParseMode.HTML)
    elif ctype == "audio" and file_id:
        await bot.send_audio(chat_id, file_id, caption=text or None, parse_mode=ParseMode.HTML)
    elif ctype == "document" and file_id:
        await bot.send_document(chat_id, file_id, caption=text or None, parse_mode=ParseMode.HTML)
    elif ctype == "animation" and file_id:
        await bot.send_animation(chat_id, file_id, caption=text or None, parse_mode=ParseMode.HTML)
    else:
        await bot.send_message(chat_id, text or ".", parse_mode=ParseMode.HTML)


# ═══════════════════════════════════════════════════════════════════════════
# 💾 BACKUP
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == CB.ADMIN_BACKUP)
async def callback_backup_menu(callback: CallbackQuery):
    """Backup menu"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    text = (
        f"💾 <b>Backup Management</b>\n\n"
        f"Database backup aur restore options 👇"
    )

    kb = get_admin_backup_keyboard(lang=lang)

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


@router.callback_query(F.data == f"{CB.ADMIN_BACKUP}:create")
async def callback_backup_create(callback: CallbackQuery, bot: Bot):
    """Backup create karta hai"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    await callback.answer("💾 Backup shuru...")

    status_msg = await callback.message.answer(
        "💾 <b>Creating backup...</b>",
        parse_mode=ParseMode.HTML,
    )

    try:
        backup_file = await create_db_backup()

        if not backup_file:
            await status_msg.edit_text(
                "❌ Backup failed!",
                parse_mode=ParseMode.HTML,
            )
            return

        backup_channel = settings.get_int("backup_channel_id", 0)

        if backup_channel:
            try:
                file_input = FSInputFile(backup_file, filename=os.path.basename(backup_file))

                sent = await bot.send_document(
                    backup_channel,
                    file_input,
                    caption=(
                        f"💾 <b>Database Backup</b>\n\n"
                        f"📅 {format_datetime(None, '%d %b %Y, %H:%M')}\n"
                        f"📦 Size: {format_size(os.path.getsize(backup_file))}"
                    ),
                    parse_mode=ParseMode.HTML,
                )

                await db.add_backup_record(
                    file_name=os.path.basename(backup_file),
                    file_size=os.path.getsize(backup_file),
                    message_id=sent.message_id,
                    channel_id=backup_channel,
                    status="completed",
                )

                await status_msg.edit_text(
                    f"✅ <b>Backup Complete!</b>\n\n"
                    f"📦 Size: {format_size(os.path.getsize(backup_file))}\n"
                    f"📁 Sent to backup channel",
                    parse_mode=ParseMode.HTML,
                )
            except Exception as e:
                log.error(f"Backup upload failed: {e}")
                await status_msg.edit_text(
                    f"⚠️ Backup created but upload failed: {e}",
                    parse_mode=ParseMode.HTML,
                )
        else:
            await status_msg.edit_text(
                f"✅ Backup created: {backup_file}\n"
                f"⚠️ Backup channel not configured",
                parse_mode=ParseMode.HTML,
            )

        await cleanup_old_backups()

    except Exception as e:
        log.error(f"Backup failed: {e}")
        try:
            await status_msg.edit_text(
                f"❌ Backup failed: {str(e)[:200]}",
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            pass


async def create_db_backup() -> Optional[str]:
    """SQLite database ka backup banata hai"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Constants.BACKUP_TEMP_DIR
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # SQLite database path
        db_path_str = os.getenv("DB_PATH", "data/isukobit.db")
        db_path = Path(db_path_str)
        
        if not db_path.exists():
            log.error(f"Database file not found: {db_path}")
            return None
        
        # Backup file name
        backup_file = backup_dir / f"backup_{timestamp}.db"
        
        # Copy database file
        shutil.copy2(db_path, backup_file)
        
        # Compress
        import gzip
        compressed = str(backup_file) + ".gz"
        with open(backup_file, "rb") as f_in:
            with gzip.open(compressed, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        os.remove(backup_file)
        
        return compressed

    except Exception as e:
        log.error(f"create_db_backup failed: {e}")
        return None


async def cleanup_old_backups():
    """Purane backups delete karta hai"""
    try:
        retention = settings.get_int("backup_retention", 7)
        await db.cleanup_old_backups(keep=retention)
    except Exception as e:
        log.error(f"cleanup_old_backups failed: {e}")


@router.callback_query(F.data == f"{CB.ADMIN_BACKUP}:list")
async def callback_backup_list(callback: CallbackQuery):
    """Backup list"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    try:
        backups = await db.get_recent_backups(limit=10)
    except Exception:
        backups = []

    if not backups:
        text = "💾 <b>No backups found</b>"
    else:
        text = f"💾 <b>Recent Backups</b>\n\n"
        for b in backups:
            text += (
                f"📁 <code>{escape_html(b.get('file_name', 'backup'))}</code>\n"
                f"   📦 {format_size(b.get('file_size', 0))} | "
                f"📅 {format_datetime(b.get('created_at'), '%d %b %H:%M')}\n\n"
            )

    kb = get_admin_backup_keyboard(lang=lang)

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


@router.callback_query(F.data == f"{CB.ADMIN_BACKUP}:cleanup")
async def callback_backup_cleanup(callback: CallbackQuery):
    """Backup cleanup"""
    await callback.answer("🧹 Cleaning up...")

    try:
        count = await db.cleanup_old_backups(keep=3)
        await callback.answer(f"✅ Deleted {count} old backups", show_alert=True)
    except Exception as e:
        await callback.answer(f"❌ {e}", show_alert=True)


# ═══════════════════════════════════════════════════════════════════════════
# 📢 CHANNELS
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == CB.ADMIN_CHANNELS)
async def callback_channels_menu(callback: CallbackQuery):
    """Channels menu"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    storage = settings.get_int("storage_channel_id", 0)
    backup = settings.get_int("backup_channel_id", 0)
    log_ch = settings.get_int("log_channel_id", 0)

    text = (
        f"📢 <b>Channel Settings</b>\n\n"
        f"📥 Storage: <code>{storage or 'Not set'}</code>\n"
        f"💾 Backup: <code>{backup or 'Not set'}</code>\n"
        f"📝 Log: <code>{log_ch or 'Not set'}</code>\n\n"
        f"Change karne ke liye button dabao."
    )

    kb = get_admin_channels_keyboard(lang=lang)

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


@router.callback_query(F.data.startswith(f"{CB.ADMIN_CHANNELS}:"))
async def callback_channel_change(callback: CallbackQuery):
    """Channel change prompt"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    channel_type = callback.data.split(":")[1]

    if channel_type == "force_join":
        text = (
            f"📢 <b>Force Join Channels</b>\n\n"
            f"Current:\n"
            f"1. {settings.get_str('force_join_1', 'Not set')}\n"
            f"2. {settings.get_str('force_join_2', 'Not set')}\n"
            f"3. {settings.get_str('force_join_3', 'Not set')}\n\n"
            f"Set karne ke liye bot ke through command use karo:\n"
            f"<code>/set_force_join 1 @channel_name</code>"
        )
        await callback.answer("Use /set_force_join command", show_alert=True)
        return

    sessions.set(user_id, "changing_channel", channel_type, timeout=300)

    text = (
        f"📢 <b>Change {channel_type.title()} Channel</b>\n\n"
        f"New channel ID bhejo.\n"
        f"Example: <code>-1001234567890</code>\n\n"
        f"Bot channel admin hona chahiye.\n\n"
        f"Cancel: /cancel"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=btn("cancel", lang),
            callback_data=CB.ADMIN_CHANNELS
        )],
    ])

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# 🔐 SECURITY
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == CB.ADMIN_SECURITY)
async def callback_security_menu(callback: CallbackQuery):
    """Security menu"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    anti_spam = settings.get_bool("anti_spam_enabled", True)
    rate_limit = settings.get_int("rate_limit_per_minute", 10)
    user_lock = settings.get_bool("user_locked_links", True)

    text = (
        f"🔐 <b>Security Settings</b>\n\n"
        f"🛡️ Anti-Spam: {'✅ ON' if anti_spam else '❌ OFF'}\n"
        f"⏱️ Rate Limit: <b>{rate_limit}</b> req/min\n"
        f"🔒 User-Locked Links: {'✅ ON' if user_lock else '❌ OFF'}"
    )

    kb = get_admin_security_keyboard(
        anti_spam=anti_spam,
        lang=lang,
    )

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


@router.callback_query(F.data == f"{CB.ADMIN_SECURITY}:toggle_spam")
async def callback_toggle_spam(callback: CallbackQuery):
    """Anti-spam toggle"""
    user_id = callback.from_user.id

    current = settings.get_bool("anti_spam_enabled", True)
    new_value = not current

    await db.set_setting("anti_spam_enabled", new_value, user_id)

    status = "ON" if new_value else "OFF"
    await callback.answer(f"✅ Anti-spam {status}", show_alert=False)

    await callback_security_menu(callback)


@router.callback_query(F.data == f"{CB.ADMIN_SECURITY}:rate_limit")
async def callback_rate_limit_edit(callback: CallbackQuery):
    """Rate limit edit prompt"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    sessions.set(user_id, "editing_setting", "rate_limit_per_minute", timeout=300)

    current = settings.get_int("rate_limit_per_minute", 10)

    text = (
        f"⏱️ <b>Rate Limit</b>\n\n"
        f"Current: <b>{current}</b> requests/minute\n\n"
        f"New value bhejo (1-1000):"
    )

    await safe_edit_message(callback, text, reply_markup=get_back_button(lang, CB.ADMIN_SECURITY))

    try:
        await callback.answer()
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# 🛠️ MAINTENANCE
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == CB.ADMIN_MAINTENANCE)
async def callback_maintenance_menu(callback: CallbackQuery):
    """Maintenance menu"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    is_on = settings.get_bool("maintenance_mode", False)

    text = (
        f"🛠️ <b>Maintenance Mode</b>\n\n"
        f"Status: {'🟢 ON' if is_on else '🔴 OFF'}\n\n"
        f"Jab ON ho:\n"
        f"• Normal users bot use nahi kar sakte\n"
        f"• Admins/Owner bypass kar sakte hain"
    )

    kb = get_admin_maintenance_keyboard(is_on=is_on, lang=lang)

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


@router.callback_query(F.data == f"{CB.ADMIN_MAINTENANCE}:toggle")
async def callback_maintenance_toggle(callback: CallbackQuery):
    """Maintenance toggle"""
    user_id = callback.from_user.id

    current = settings.get_bool("maintenance_mode", False)
    new_value = not current

    await db.set_setting("maintenance_mode", new_value, user_id)

    status = "ON" if new_value else "OFF"
    await callback.answer(f"🛠️ Maintenance {status}", show_alert=True)

    await callback_maintenance_menu(callback)


@router.callback_query(F.data == f"{CB.ADMIN_MAINTENANCE}:edit")
async def callback_maintenance_edit(callback: CallbackQuery):
    """Maintenance message edit"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    sessions.set(user_id, "editing_setting", "maintenance_message", timeout=300)

    current = settings.get_str("maintenance_message", "")

    text = (
        f"✏️ <b>Edit Maintenance Message</b>\n\n"
        f"Current:\n<code>{escape_html(truncate(current, 200))}</code>\n\n"
        f"Naya message bhejo:"
    )

    await safe_edit_message(callback, text, reply_markup=get_back_button(lang, CB.ADMIN_MAINTENANCE))

    try:
        await callback.answer()
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# 📝 LOGS
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == CB.ADMIN_LOGS)
async def callback_logs_menu(callback: CallbackQuery):
    """Logs menu"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    text = (
        f"📝 <b>Logs</b>\n\n"
        f"Konsa log dekhna hai? 👇"
    )

    kb = get_admin_logs_keyboard(lang=lang)

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


@router.callback_query(F.data.startswith(f"{CB.ADMIN_LOGS}:"))
async def callback_logs_view(callback: CallbackQuery):
    """Specific log view"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    log_type = callback.data.split(":")[1]

    type_map = {
        "downloads": "file_download",
        "uploads": "file_upload",
        "users": "user_joined",
        "errors": "error",
        "all": None,
    }

    filter_type = type_map.get(log_type, None)

    try:
        logs = await db.get_logs(log_type=filter_type, limit=20)
    except Exception:
        logs = []

    if not logs:
        text = f"📝 <b>No logs found</b>"
    else:
        text = f"📝 <b>{log_type.title()} Logs</b> (last 20)\n\n"
        for entry in logs[:20]:
            ts = format_datetime(entry.get("created_at"), "%d %b %H:%M")
            action = entry.get("action", "")
            uid = entry.get("user_id", "")
            text += f"• <code>{ts}</code> | {action} | {uid}\n"

    kb = get_back_button(lang, CB.ADMIN_LOGS)

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# 💚 HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == CB.ADMIN_HEALTH)
async def callback_health_check(callback: CallbackQuery, bot: Bot):
    """Health check"""
    await callback.answer("💚 Checking...")

    db_health = await db.health_check()
    srv = await get_server_stats()

    try:
        me = await bot.get_me()
        bot_info = f"@{me.username}"
    except Exception:
        bot_info = "Error"

    uptime = get_uptime(settings.get_float("bot_start_time", 0))

    temp_size = get_dir_size(Constants.TEMP_DIR)
    backup_size = get_dir_size(Constants.BACKUP_TEMP_DIR)

    text = (
        f"💚 <b>Health Check</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🗄️ <b>Database</b>\n"
        f"• Connected: {'✅' if db_health.get('connected') else '❌'}\n"
        f"• Response: {db_health.get('response_time_ms', 0)} ms\n"
        f"• Size: {format_size(db_health.get('db_size', 0))}\n\n"
        f"🤖 <b>Bot</b>\n"
        f"• Info: {bot_info}\n"
        f"• Uptime: {uptime}\n\n"
        f"🖥️ <b>Server</b>\n"
        f"• RAM: {srv['ram_percent']}%\n"
        f"• CPU: {srv['cpu_percent']}%\n"
        f"• Disk: {srv['disk_percent']}%\n\n"
        f"📁 <b>Storage</b>\n"
        f"• Temp: {format_size(temp_size)}\n"
        f"• Backups: {format_size(backup_size)}"
    )

    kb = get_back_button("hinglish", CB.ADMIN)

    await safe_edit_message(callback, text, reply_markup=kb)


# ═══════════════════════════════════════════════════════════════════════════
# 🔄 RESTART
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == CB.ADMIN_RESTART)
async def callback_restart_confirm(callback: CallbackQuery):
    """Restart confirm"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    text = (
        f"🔄 <b>Restart Bot</b>\n\n"
        f"⚠️ Bot restart ho jayega. Sure ho?"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=btn("yes", lang),
                callback_data="restart:confirm"
            ),
            InlineKeyboardButton(
                text=btn("no", lang),
                callback_data=CB.ADMIN
            ),
        ],
    ])

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


@router.callback_query(F.data == "restart:confirm")
async def callback_restart(callback: CallbackQuery, bot: Bot):
    """Restart execute karta hai"""
    user_id = callback.from_user.id

    if not await db.is_owner(user_id):
        await callback.answer("Only owner can restart!", show_alert=True)
        return

    await callback.answer("🔄 Restarting...", show_alert=True)

    try:
        await callback.message.answer(
            "🔄 Bot restarting... (systemd auto-restart karega)",
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        pass

    await log_admin_action(bot, user_id, "restart", "Bot restart requested")

    await asyncio.sleep(2)
    os._exit(0)


# ═══════════════════════════════════════════════════════════════════════════
# ⚙️ SETTINGS MENU
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == CB.ADMIN_SETTINGS)
async def callback_settings_menu(callback: CallbackQuery):
    """Admin settings menu"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    text = (
        f"⚙️ <b>Bot Settings</b>\n\n"
        f"Konsi category edit karni hai? 👇"
    )

    kb = get_admin_settings_keyboard(lang=lang)

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


@router.callback_query(F.data.startswith(f"{CB.ADMIN_SETTINGS}:"))
async def callback_settings_category(callback: CallbackQuery):
    """Settings category view"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    category = callback.data.split(":")[1]

    category_map = {
        "file": [
            ("Max file size", "max_file_size", format_size),
            ("File code prefix", "file_code_prefix", str),
            ("Max files/user", "max_files_per_user", str),
            ("Batch max files", "batch_max_files", str),
            ("Batch session (min)", "batch_session_minutes", str),
            ("Queue step delay", "queue_step_delay", str),
            ("Queue item delay", "queue_item_delay", str),
            ("Log report interval (sec)", "log_report_interval_seconds", str),
            ("Link expiry (hrs)", "link_expiry_hours", str),
            ("User locked", "user_locked_links", str),
        ],
        "ui": [
            ("Bot name", "bot_name", str),
            ("Default language", "default_language", str),
            ("Buttons style", "buttons_style", str),
            ("Theme", "theme", str),
        ],
        "premium": [
            ("Premium enabled", "premium_enabled", str),
            ("Premium price", "premium_price_stars", str),
            ("Duration (days)", "premium_duration_days", str),
        ],
        "lang": [],
        "terms": [
            ("Terms URL", "terms_url", str),
            ("Privacy URL", "privacy_url", str),
            ("Support", "support_username", str),
        ],
    }

    settings_list = category_map.get(category, [])

    if not settings_list:
        text = f"⚙️ <b>{category.title()} Settings</b>\n\nNo editable settings yet."
        kb = get_back_button(lang, CB.ADMIN_SETTINGS)
        await safe_edit_message(callback, text, reply_markup=kb)
        return

    text = f"⚙️ <b>{category.title()} Settings</b>\n\n"
    buttons = []

    for label, key, formatter in settings_list:
        value = settings.get(key, "N/A")
        try:
            display = formatter(value) if callable(formatter) else str(value)
        except Exception:
            display = str(value)

        text += f"• {label}: <code>{display}</code>\n"
        buttons.append([InlineKeyboardButton(
            text=f"✏️ {label}",
            callback_data=f"editset:{key}"
        )])

    buttons.append([InlineKeyboardButton(
        text=btn("back", lang),
        callback_data=CB.ADMIN_SETTINGS
    )])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


@router.callback_query(F.data.startswith("editset:"))
async def callback_edit_setting(callback: CallbackQuery):
    """Setting edit prompt"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    setting_key = callback.data.split(":", 1)[1]

    sessions.set(user_id, "editing_setting", setting_key, timeout=300)

    current = settings.get(setting_key, "N/A")

    text = (
        f"✏️ <b>Edit Setting</b>\n\n"
        f"Setting: <code>{setting_key}</code>\n"
        f"Current: <code>{current}</code>\n\n"
        f"Naya value bhejo:"
    )

    kb = get_back_button(lang, CB.ADMIN_SETTINGS)

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# ⚠️ DANGER ZONE
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == CB.ADMIN_DANGER)
async def callback_danger_menu(callback: CallbackQuery):
    """Danger zone menu"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    if not await db.is_owner(user_id):
        await callback.answer("Only owner!", show_alert=True)
        return

    text = (
        f"⚠️ <b>Danger Zone</b>\n\n"
        f"Yeh actions irreversible hain. Dhyan se use karo!"
    )

    kb = get_admin_danger_keyboard(lang=lang)

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


@router.callback_query(F.data.startswith(f"{CB.ADMIN_DANGER}:"))
async def callback_danger_action(callback: CallbackQuery, bot: Bot):
    """Danger action execute"""
    user_id = callback.from_user.id

    if not await db.is_owner(user_id):
        await callback.answer("Only owner!", show_alert=True)
        return

    action = callback.data.split(":")[1]

    if action == "clear_logs":
        count = await db.cleanup_old_logs(days=7)
        await callback.answer(f"✅ Cleared {count} old logs", show_alert=True)

    elif action == "cleanup_files":
        count = await db.cleanup_expired_files()
        await callback.answer(f"✅ Cleaned {count} expired files", show_alert=True)

    elif action == "reset_settings":
        await callback.answer("⚠️ Use /reset_settings command", show_alert=True)

    elif action == "full_reset":
        await callback.answer("⚠️ Use /full_reset (dangerous!)", show_alert=True)


# ═══════════════════════════════════════════════════════════════════════════
# 📁 ADMIN FILE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == CB.ADMIN_FILES)
async def callback_admin_files(callback: CallbackQuery):
    """Admin files menu"""
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)

    total = await db.get_total_files_count()
    total_size = await db.get_total_files_size()

    text = (
        f"📁 <b>File Management</b>\n\n"
        f"📊 Total files: <b>{humanize_number(total)}</b>\n"
        f"💾 Total size: <b>{format_size(total_size)}</b>"
    )

    kb = get_admin_files_keyboard(lang=lang)

    await safe_edit_message(callback, text, reply_markup=kb)

    try:
        await callback.answer()
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# 📝 TEXT INPUT HANDLER — FIXED (Custom Filter)
# ═══════════════════════════════════════════════════════════════════════════

@router.message(F.text & ~F.text.startswith("/"), HasAdminSession())
async def handle_settings_input(message: Message, bot: Bot):
    """
    Admin text input handle karta hai — SIRF jab admin session active ho.
    
    Filter ki madad se yeh handler tab hi match karega jab:
    - Admin setting edit kar raha ho, YA
    - Admin channel change kar raha ho, YA
    - Admin user search/ban/unban kar raha ho, YA
    - Admin broadcast bhej raha ho
    
    Warna handler skip ho jayega aur message next router ko jayega.
    """
    user_id = message.from_user.id

    if not (await db.is_admin(user_id) or await db.is_owner(user_id)):
        return

    lang = await get_user_lang(user_id)
    new_value_str = (message.text or "").strip()

    # ─── Setting edit ────────────────────────────────────────────
    if sessions.has(user_id, "editing_setting"):
        setting_key = sessions.get(user_id, "editing_setting")
        sessions.clear(user_id)

        current = settings.get(setting_key)
        parsed_value = new_value_str

        try:
            if isinstance(current, bool):
                parsed_value = new_value_str.lower() in ("true", "1", "yes", "on", "haan")
            elif isinstance(current, int):
                parsed_value = int(new_value_str)
            elif isinstance(current, float):
                parsed_value = float(new_value_str)
            elif isinstance(current, list):
                parsed_value = [x.strip() for x in new_value_str.split(",") if x.strip()]
        except (ValueError, TypeError) as e:
            await safe_send_message(
                message,
                f"❌ Invalid value: {e}"
            )
            return

        try:
            await db.set_setting(setting_key, parsed_value, user_id)
        except Exception as e:
            log.error(f"set_setting failed: {e}")
            await safe_send_message(message, f"❌ Save failed: {e}")
            return

        await log_admin_action(
            bot, user_id, "edit_setting",
            f"{setting_key} = {parsed_value}"
        )

        text = (
            f"✅ <b>Setting Updated</b>\n\n"
            f"🔑 {setting_key}\n"
            f"📝 New value: <code>{parsed_value}</code>"
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=btn("back", lang),
                callback_data=CB.ADMIN_SETTINGS
            )],
        ])

        await safe_send_message(message, text, reply_markup=kb)
        return

    # ─── Channel change ──────────────────────────────────────────
    if sessions.has(user_id, "changing_channel"):
        channel_type = sessions.get(user_id, "changing_channel")
        sessions.clear(user_id)

        try:
            channel_id = int(new_value_str)
        except ValueError:
            await safe_send_message(message, "❌ Invalid channel ID")
            return

        setting_key = f"{channel_type}_channel_id"
        await db.set_setting(setting_key, channel_id, user_id)

        text = (
            f"✅ <b>Channel Updated</b>\n\n"
            f"📢 {channel_type.title()}: <code>{channel_id}</code>"
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=btn("back", lang),
                callback_data=CB.ADMIN_CHANNELS
            )],
        ])

        await safe_send_message(message, text, reply_markup=kb)
        return

    # ─── Admin search user ───────────────────────────────────────
    if sessions.has(user_id, "admin_searching_user"):
        sessions.clear(user_id)

        query = new_value_str.lstrip("@")

        try:
            if query.isdigit():
                users = [await db.get_user(int(query))]
                users = [u for u in users if u]
            else:
                users = await db.search_users(query, limit=10)
        except Exception:
            users = []

        if not users:
            await safe_send_message(message, "❌ No users found")
            return

        text = f"🔍 <b>Search Results</b> ({len(users)})\n\n"
        buttons = []

        for u in users:
            name = u.get("first_name", "Unknown")
            uid = u.get("user_id")
            buttons.append([InlineKeyboardButton(
                text=f"👤 {name} [{uid}]",
                callback_data=f"{CB.ADMIN_USERS}:view:{uid}"
            )])

        buttons.append([InlineKeyboardButton(
            text=btn("back", lang),
            callback_data=CB.ADMIN_USERS
        )])

        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await safe_send_message(message, text, reply_markup=kb)
        return

    # ─── Ban user search ─────────────────────────────────────────
    if sessions.has(user_id, "banning_user_search"):
        sessions.clear(user_id)

        query = new_value_str.lstrip("@")
        target_id = None

        try:
            if query.isdigit():
                target_id = int(query)
            else:
                users = await db.search_users(query, limit=1)
                if users:
                    target_id = users[0].get("user_id")
        except Exception:
            pass

        if not target_id:
            await safe_send_message(message, "❌ User not found")
            return

        sessions.set(user_id, "banning_user", target_id, timeout=300)

        text = (
            f"🚫 <b>Ban User</b>\n\n"
            f"ID: <code>{target_id}</code>\n\n"
            f"Reason bhejo (ya /skip):"
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=btn("skip", lang),
                callback_data=f"ban:skip:{target_id}"
            )],
        ])

        await safe_send_message(message, text, reply_markup=kb)
        return

    # ─── Unban user search ───────────────────────────────────────
    if sessions.has(user_id, "unbanning_user_search"):
        sessions.clear(user_id)

        query = new_value_str.lstrip("@")
        target_id = None

        try:
            if query.isdigit():
                target_id = int(query)
            else:
                users = await db.search_users(query, limit=1)
                if users:
                    target_id = users[0].get("user_id")
        except Exception:
            pass

        if not target_id:
            await safe_send_message(message, "❌ User not found")
            return

        await db.unban_user(target_id)

        text = f"✅ User <code>{target_id}</code> unbanned!"
        kb = get_back_button(lang, CB.ADMIN_USERS)

        await safe_send_message(message, text, reply_markup=kb)
        return

    # ─── Ban reason input ────────────────────────────────────────
    if sessions.has(user_id, "banning_user"):
        target_id = sessions.get(user_id, "banning_user")
        reason = new_value_str[:200] or "No reason"
        sessions.clear(user_id)

        await perform_ban_message(message, bot, target_id, reason, lang)
        return

    # ─── Broadcast content ───────────────────────────────────────
    if sessions.has(user_id, "broadcasting"):
        bc_data = sessions.get(user_id, "broadcasting")
        if isinstance(bc_data, dict) and bc_data.get("step") == "content":
            await handle_broadcast_content(message, bot, lang)
            return


# ═══════════════════════════════════════════════════════════════════════════
# 📝 ADMIN ACTION LOGGER
# ═══════════════════════════════════════════════════════════════════════════

async def log_admin_action(
    bot: Bot,
    admin_id: int,
    action: str,
    details: str = "",
):
    """Admin action log karta hai"""
    try:
        await db.add_log(
            log_type="admin_action",
            user_id=admin_id,
            action=action,
            details=details,
        )

        log_channel = settings.get_int("log_channel_id", 0)
        if not log_channel:
            return

        if not settings.get_bool("log_admin_actions", True):
            return

        admin_data = await db.get_user(admin_id)
        admin_name = "Admin"
        if admin_data:
            admin_name = admin_data.get("first_name") or f"@{admin_data.get('username', '')}"

        text = (
            f"👑 <b>Admin Action</b>\n\n"
            f"👤 {escape_html(admin_name)}\n"
            f"🆔 <code>{admin_id}</code>\n\n"
            f"⚡ Action: <code>{action}</code>\n"
            f"📝 {escape_html(truncate(details, 200))}\n"
            f"📅 {format_datetime(None, '%d %b %Y, %H:%M')}"
        )

        await bot.send_message(
            log_channel, text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except Exception as e:
        log.debug(f"log_admin_action failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "router",
    "HasAdminSession",
    "cmd_admin",
    "callback_admin_panel",
    "callback_admin_stats",
    "callback_admin_users",
    "callback_user_view",
    "callback_user_ban",
    "callback_user_unban",
    "callback_add_admin",
    "callback_remove_admin",
    "callback_broadcast_prompt",
    "run_broadcast",
    "create_db_backup",
    "log_admin_action",
]


# ═══════════════════════════════════════════════════════════════════════════
# 📖 END OF FILE
# ═══════════════════════════════════════════════════════════════════════════