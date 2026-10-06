import os
import sys
import time
import signal
import asyncio
import traceback
from datetime import datetime, timedelta
from typing import Optional, Any, Callable, Awaitable

# aiogram core
from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode, ChatMemberStatus
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    BotCommand,
    BotCommandScopeDefault,
    BotCommandScopeAllPrivateChats,
    ErrorEvent,
    Message,
    CallbackQuery,
)
from aiogram.exceptions import (
    TelegramUnauthorizedError,
    TelegramNetworkError,
    TelegramRetryAfter,
    TelegramForbiddenError,
    TelegramBadRequest,
    TelegramConflictError,
    TelegramServerError,
)

# Local modules
from config import (
    Bootstrap,
    Constants,
    Colors,
    settings,
    log,
    validate_config,
    print_banner,
    print_config_summary,
)
from database import db, init_database, close_database
from strings import get_string
from utils import get_uptime, format_size

# Routers
from handlers_start import router as start_router
from handlers_upload import router as upload_router, start_upload_worker
from handlers_files import router as files_router
from handlers_admin import router as admin_router


# ═══════════════════════════════════════════════════════════════════════════
# 🌍 GLOBAL VARIABLES
# ═══════════════════════════════════════════════════════════════════════════

bot: Optional[Bot] = None
dp: Optional[Dispatcher] = None
background_tasks: list = []
shutting_down: bool = False
startup_time: float = 0.0
restart_count: int = 0


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 MAIN APPLICATION CLASS
# ═══════════════════════════════════════════════════════════════════════════

class IsukobitBot:
    """Main bot application class."""

    def __init__(self):
        self.bot: Optional[Bot] = None
        self.dp: Optional[Dispatcher] = None
        self.running: bool = False
        self.start_time: float = 0.0
        self._stop_event = asyncio.Event()

    # ───────────────────────────────────────────────────────────────────────
    # 🚀 STARTUP
    # ───────────────────────────────────────────────────────────────────────

    async def startup(self) -> None:
        """Bot startup process"""
        global bot, dp, startup_time

        self.start_time = time.time()
        startup_time = self.start_time

        log.info("=" * 70)
        log.info(f"{Colors.BRIGHT_CYAN}🚀 ISUKOBIT starting up...{Colors.RESET}")
        log.info("=" * 70)

        # 1. Validate config
        log.info(f"{Colors.info('1️⃣')} Validating configuration...")
        if not validate_config():
            log.error(f"{Colors.error('❌')} Config validation failed!")
            sys.exit(1)
        log.info(f"{Colors.success('✅')} Config valid")

        # 2. Initialize database
        log.info(f"{Colors.info('2️⃣')} Initializing database...")
        try:
            await init_database()
        except Exception as e:
            log.error(f"{Colors.error('❌')} Database init failed: {e}")
            traceback.print_exc()
            sys.exit(1)
        log.info(f"{Colors.success('✅')} Database ready")

        # 3. Create Bot instance
        log.info(f"{Colors.info('3️⃣')} Creating bot instance...")
        try:
            self.bot = self._create_bot()
            bot = self.bot
        except Exception as e:
            log.error(f"{Colors.error('❌')} Bot creation failed: {e}")
            sys.exit(1)

        # 4. Verify bot token
        try:
            me = await self.bot.get_me()
            log.info(
                f"{Colors.success('✅')} Bot verified: "
                f"@{me.username} (ID: {me.id})"
            )
            # DB mein purana username ho toh bhi links hamesha sahi banenge
            if me.username:
                await db.set_setting("bot_username", me.username)
                settings.set("bot_username", me.username)
                log.info(
                    f"{Colors.success('✅')} Username synced: @{me.username}"
                )

            # Teenon channels ka health check
            for ch_name, ch_key in (
                ("Storage", "storage_channel_id"),
                ("Backup", "backup_channel_id"),
                ("Log", "log_channel_id"),
            ):
                try:
                    ch_id = settings.get_int(ch_key, 0)
                    if ch_id:
                        await self.bot.get_chat(ch_id)
                        log.info(
                            f"{Colors.success('✅')} {ch_name} channel OK: {ch_id}"
                        )
                    else:
                        log.warning(
                            f"{Colors.warning('⚠️')} {ch_name} channel ID "
                            f"set nahi hai (admin panel se set karo)"
                        )
                except Exception as e:
                    log.error(
                        f"{Colors.error('❌')} {ch_name} channel problem: {e}"
                    )
        except TelegramUnauthorizedError:
            log.error(f"{Colors.error('❌')} Invalid BOT_TOKEN!")
            sys.exit(1)
        except Exception as e:
            log.error(f"{Colors.error('❌')} Bot verification failed: {e}")
            sys.exit(1)

        # 5. Create Dispatcher
        log.info(f"{Colors.info('4️⃣')} Creating dispatcher...")
        self.dp = self._create_dispatcher()
        dp = self.dp
        log.info(f"{Colors.success('✅')} Dispatcher ready")

        # 6. Register middlewares
        log.info(f"{Colors.info('5️⃣')} Registering middlewares...")
        self._register_middlewares()
        log.info(f"{Colors.success('✅')} Middlewares registered")

        # 7. Register routers
        log.info(f"{Colors.info('6️⃣')} Registering routers...")
        self._register_routers()
        log.info(f"{Colors.success('✅')} Routers registered")

        # 8. Set bot commands
        log.info(f"{Colors.info('7️⃣')} Setting bot commands...")
        try:
            await self._set_bot_commands()
            log.info(f"{Colors.success('✅')} Commands set")
        except Exception as e:
            log.warning(f"{Colors.warning('⚠️')} Commands failed: {e}")

        # 9. Start background tasks
        log.info(f"{Colors.info('8️⃣')} Starting background tasks...")
        self._start_background_tasks()
        log.info(f"{Colors.success('✅')} Background tasks started")

        # 10. Notify admins
        log.info(f"{Colors.info('9️⃣')} Notifying admins...")
        try:
            await self._notify_startup()
            log.info(f"{Colors.success('✅')} Admins notified")
        except Exception as e:
            log.debug(f"Startup notification failed: {e}")

        # 11. Save start time
        try:
            await db.set_setting("bot_start_time", self.start_time)
            settings.set("bot_start_time", self.start_time)
        except Exception as e:
            log.debug(f"Failed to save start time: {e}")

        self.running = True

        log.info("=" * 70)
        log.info(
            f"{Colors.BRIGHT_GREEN}✅ Bot startup complete! "
            f"Ready to receive updates.{Colors.RESET}"
        )
        log.info("=" * 70)

    # ───────────────────────────────────────────────────────────────────────
    # 🤖 BOT CREATION
    # ───────────────────────────────────────────────────────────────────────

    def _create_bot(self) -> Bot:
        """Bot instance banata hai"""
        api_server_url = os.getenv("API_SERVER_URL", "").strip()

        if api_server_url:
            log.info(f"Using custom API server: {api_server_url}")
            api_server = TelegramAPIServer.from_base(api_server_url)
            session = AiohttpSession(api=api_server)
        else:
            session = AiohttpSession(timeout=120)

        bot = Bot(
            token=Bootstrap.BOT_TOKEN,
            session=session,
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML,
                link_preview_is_disabled=True,
            ),
        )

        return bot

    # ───────────────────────────────────────────────────────────────────────
    # 🎛️ DISPATCHER CREATION
    # ───────────────────────────────────────────────────────────────────────

    def _create_dispatcher(self) -> Dispatcher:
        """Dispatcher instance banata hai"""
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        return dp

    # ───────────────────────────────────────────────────────────────────────
    # 🎯 MIDDLEWARES
    # ───────────────────────────────────────────────────────────────────────

    def _register_middlewares(self) -> None:
        """Middlewares register karta hai"""

        # ─── Logging middleware ──────────────────────────────────────
        @self.dp.update.outer_middleware()
        async def logging_middleware(handler, event, data):
            start = time.time()
            try:
                result = await handler(event, data)
                elapsed = (time.time() - start) * 1000
                if elapsed > 1000:
                    log.debug(f"Slow handler: {elapsed:.0f}ms")
                return result
            except Exception as e:
                elapsed = (time.time() - start) * 1000
                log.error(f"Handler error ({elapsed:.0f}ms): {e}")
                raise

        # ─── Ban check middleware ────────────────────────────────────
        @self.dp.message.middleware()
        @self.dp.callback_query.middleware()
        async def ban_middleware(handler, event, data):
            try:
                user_id = event.from_user.id if event.from_user else None
                if not user_id:
                    return await handler(event, data)

                if user_id == Bootstrap.OWNER_ID:
                    return await handler(event, data)

                if await db.is_admin(user_id):
                    return await handler(event, data)

                if await db.is_user_banned(user_id):
                    return

                return await handler(event, data)
            except Exception as e:
                log.debug(f"Ban middleware error: {e}")
                return await handler(event, data)

        # ─── Maintenance middleware (NEW — full block) ───────────────
        @self.dp.message.middleware()
        @self.dp.callback_query.middleware()
        async def maintenance_middleware(handler, event, data):
            """Maintenance mode — saare handlers se pehle check"""
            try:
                # Maintenance off — normal chalne do
                if not settings.get_bool("maintenance_mode", False):
                    return await handler(event, data)

                user_id = event.from_user.id if event.from_user else None
                if not user_id:
                    return await handler(event, data)

                # Owner & Admin ko bypass do
                if user_id == Bootstrap.OWNER_ID:
                    return await handler(event, data)

                if await db.is_admin(user_id):
                    return await handler(event, data)

                # /start ko allow karo
                text = getattr(event, "text", "") or ""
                if text.startswith("/start"):
                    return await handler(event, data)

                # Verify button ko allow karo
                cb_data = getattr(event, "data", "") or ""
                if cb_data == "verify":
                    return await handler(event, data)

                # Admin panel button ko allow karo (agar koi admin hai)
                if cb_data == "admin":
                    return await handler(event, data)

                # Baaki sab block karo
                msg = settings.get_str(
                    "maintenance_message",
                    "🛠️ <b>Bot abhi maintenance mein hai</b>"
                )

                # Callback query
                if isinstance(event, CallbackQuery):
                    try:
                        await event.answer(
                            "🛠️ Bot maintenance mein hai",
                            show_alert=True
                        )
                    except Exception:
                        pass
                    return

                # Message
                if isinstance(event, Message):
                    try:
                        await event.answer(
                            msg,
                            parse_mode=ParseMode.HTML
                        )
                    except Exception:
                        pass
                    return

                return

            except Exception as e:
                log.debug(f"Maintenance middleware error: {e}")
                return await handler(event, data)

        log.debug("Middlewares registered")

    # ───────────────────────────────────────────────────────────────────────
    # 🛣️ ROUTERS
    # ───────────────────────────────────────────────────────────────────────

    def _register_routers(self) -> None:
        """Saare routers register karta hai"""
        # Order matters:
        # 1. Admin panel PEHLE (taaki admin ke commands aur callbacks pehle match ho)
        #    Actually nahi — start pehle chahiye, phir upload, phir files, phir admin
        #    Lekin admin callbacks ko conflict na ho isliye specific ordering
        
        self.dp.include_router(start_router)
        log.debug("✅ start_router registered")

        self.dp.include_router(upload_router)
        log.debug("✅ upload_router registered")

        self.dp.include_router(files_router)
        log.debug("✅ files_router registered")

        self.dp.include_router(admin_router)
        log.debug("✅ admin_router registered")

    # ───────────────────────────────────────────────────────────────────────
    # 📋 BOT COMMANDS
    # ───────────────────────────────────────────────────────────────────────

    async def _set_bot_commands(self) -> None:
        """Bot ke commands set karta hai"""
        commands = [
            BotCommand(command="start", description="🏠 Main menu"),
            BotCommand(command="help", description="❓ Help"),
            BotCommand(command="upload", description="📤 Upload file"),
            BotCommand(command="myfiles", description="📁 My files"),
            BotCommand(command="search", description="🔍 Search files"),
            BotCommand(command="profile", description="👤 My profile"),
            BotCommand(command="stats", description="📊 Statistics"),
            BotCommand(command="settings", description="⚙️ Settings"),
            BotCommand(command="about", description="ℹ️ About bot"),
        ]

        try:
            await self.bot.set_my_commands(
                commands=commands,
                scope=BotCommandScopeDefault()
            )
            await self.bot.set_my_commands(
                commands=commands,
                scope=BotCommandScopeAllPrivateChats()
            )
        except Exception as e:
            log.warning(f"Set commands failed: {e}")

    # ───────────────────────────────────────────────────────────────────────
    # 🔄 BACKGROUND TASKS
    # ───────────────────────────────────────────────────────────────────────

    def _start_background_tasks(self) -> None:
        """Saare background tasks start karta hai"""
        global background_tasks

        if settings.get_bool("backup_enabled", True):
            task = asyncio.create_task(self._auto_backup_loop())
            background_tasks.append(task)
            log.debug("📅 Auto-backup task started")

        task = asyncio.create_task(self._cleanup_loop())
        background_tasks.append(task)
        log.debug("🧹 Cleanup task started")

        task = asyncio.create_task(self._daily_stats_loop())
        background_tasks.append(task)
        log.debug("📊 Daily stats task started")

        task = asyncio.create_task(self._health_check_loop())
        background_tasks.append(task)
        log.debug("💚 Health check task started")

        task = asyncio.create_task(self._session_cleanup_loop())
        background_tasks.append(task)
        log.debug("🗂️ Session cleanup task started")

        task = asyncio.create_task(start_upload_worker(self.bot))
        background_tasks.append(task)
        log.debug("⏳ Upload queue worker started")

        task = asyncio.create_task(self._log_report_loop())
        background_tasks.append(task)
        log.debug("📋 Log report task started")

    async def _auto_backup_loop(self) -> None:
        """Auto backup loop"""
        await asyncio.sleep(300)

        while not self._stop_event.is_set():
            try:
                interval_hours = settings.get_int("backup_interval_hours", 24)
                interval_seconds = interval_hours * 3600

                log.info(f"{Colors.info('💾')} Running auto-backup...")
                await self._do_backup()
                log.info(
                    f"{Colors.success('✅')} Auto-backup complete. "
                    f"Next in {interval_hours}h"
                )

                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(),
                        timeout=interval_seconds
                    )
                    return
                except asyncio.TimeoutError:
                    continue

            except asyncio.CancelledError:
                log.debug("Auto-backup task cancelled")
                return
            except Exception as e:
                log.error(f"Auto-backup error: {e}")
                await asyncio.sleep(3600)

    async def _do_backup(self) -> None:
        """Backup execute karta hai"""
        try:
            from handlers_admin import create_db_backup

            backup_file = await create_db_backup()

            if not backup_file:
                log.error("Backup creation failed")
                return

            backup_channel = settings.get_int("backup_channel_id", 0)

            if backup_channel:
                from aiogram.types import FSInputFile
                file_input = FSInputFile(
                    backup_file,
                    filename=os.path.basename(backup_file)
                )
                await self.bot.send_document(
                    backup_channel,
                    file_input,
                    caption=(
                        f"💾 <b>Auto Backup</b>\n\n"
                        f"📅 {datetime.now().strftime('%d %b %Y, %H:%M')}\n"
                        f"📦 Size: {os.path.getsize(backup_file) / 1024:.1f} KB"
                    ),
                    parse_mode=ParseMode.HTML,
                )

            await db.cleanup_old_backups(keep=settings.get_int("backup_retention", 7))

            try:
                if os.path.exists(backup_file):
                    os.remove(backup_file)
            except Exception:
                pass

            await db.add_log(
                log_type="backup",
                action="auto_backup",
                details=f"Backup completed: {os.path.basename(backup_file)}"
            )

        except Exception as e:
            log.error(f"do_backup failed: {e}")
            traceback.print_exc()

    async def _cleanup_loop(self) -> None:
        """Cleanup loop — hourly"""
        await asyncio.sleep(600)

        while not self._stop_event.is_set():
            try:
                log.debug("🧹 Running cleanup...")

                try:
                    expired = await db.cleanup_expired_files()
                    if expired > 0:
                        log.info(f"Cleaned {expired} expired files")
                except Exception as e:
                    log.debug(f"Expired files cleanup failed: {e}")

                try:
                    await db.cleanup_old_logs(days=30)
                except Exception:
                    pass

                try:
                    await db.cleanup_old_error_logs(days=30)
                except Exception:
                    pass

                try:
                    await db.cleanup_old_downloads(days=90)
                except Exception:
                    pass

                try:
                    await db.cleanup_rate_limits()
                except Exception:
                    pass

                try:
                    from utils import cleanup_temp_files
                    cleanup_temp_files(older_than_hours=24)
                except Exception:
                    pass

                try:
                    from utils import rate_limiter
                    rate_limiter.cleanup(older_than_seconds=3600)
                except Exception:
                    pass

                log.debug("🧹 Cleanup done")

                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(),
                        timeout=3600
                    )
                    return
                except asyncio.TimeoutError:
                    continue

            except asyncio.CancelledError:
                return
            except Exception as e:
                log.error(f"Cleanup error: {e}")
                await asyncio.sleep(600)

    async def _daily_stats_loop(self) -> None:
        """Daily stats update loop"""
        await asyncio.sleep(1800)

        while not self._stop_event.is_set():
            try:
                try:
                    stats = await db.get_stats()
                    settings.set("total_users_count", stats.get("total_users", 0))
                    settings.set("total_files_count", stats.get("total_files", 0))
                    settings.set("total_downloads_count", stats.get("total_downloads", 0))
                except Exception as e:
                    log.debug(f"Stats update failed: {e}")

                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(),
                        timeout=300
                    )
                    return
                except asyncio.TimeoutError:
                    continue

            except asyncio.CancelledError:
                return
            except Exception as e:
                log.debug(f"Daily stats error: {e}")
                await asyncio.sleep(300)

    async def _health_check_loop(self) -> None:
        """Health check loop"""
        await asyncio.sleep(900)
        consecutive_failures = 0

        while not self._stop_event.is_set():
            try:
                health = await db.health_check()

                if not health.get("connected"):
                    consecutive_failures += 1
                    log.warning(
                        f"DB health failed (#{consecutive_failures}): "
                        f"{health.get('error')}"
                    )

                    if consecutive_failures >= 3:
                        log.error("3 consecutive DB failures. Attempting reconnect...")
                        success = await db.reconnect(max_attempts=3)
                        if success:
                            consecutive_failures = 0
                            log.info("Reconnected successfully")
                else:
                    if consecutive_failures > 0:
                        log.info("DB health restored")
                    consecutive_failures = 0

                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(),
                        timeout=900
                    )
                    return
                except asyncio.TimeoutError:
                    continue

            except asyncio.CancelledError:
                return
            except Exception as e:
                log.debug(f"Health check error: {e}")
                await asyncio.sleep(900)

    async def _session_cleanup_loop(self) -> None:
        """Session cleanup loop"""
        await asyncio.sleep(600)

        while not self._stop_event.is_set():
            try:
                from utils import sessions
                cleaned = sessions.cleanup()
                if cleaned > 0:
                    log.debug(f"Cleaned {cleaned} expired sessions")

                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(),
                        timeout=600
                    )
                    return
                except asyncio.TimeoutError:
                    continue

            except asyncio.CancelledError:
                return
            except Exception as e:
                log.debug(f"Session cleanup error: {e}")
                await asyncio.sleep(600)

    async def _log_report_loop(self) -> None:
        """Har interval pe log channel mein status report bhejta hai"""
        await asyncio.sleep(60)

        while not self._stop_event.is_set():
            try:
                await self._send_log_report()

                interval = settings.get_int("log_report_interval_seconds", 300)
                if interval <= 0:
                    interval = 300

                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(),
                        timeout=interval
                    )
                    return
                except asyncio.TimeoutError:
                    continue

            except asyncio.CancelledError:
                return
            except Exception as e:
                log.debug(f"Log report error: {e}")
                await asyncio.sleep(60)

    async def _send_log_report(self) -> None:
        """Log channel mein stats snapshot bhejta hai"""
        log_channel = settings.get_int("log_channel_id", 0)
        if not log_channel:
            return

        try:
            stats = await db.get_stats()
        except Exception:
            stats = {}

        try:
            text = (
                f"📋 <b>Bot Status Report</b>\n\n"
                f"⏰ Uptime: <b>{get_uptime(settings.get_float('bot_start_time', 0))}</b>\n"
                f"👥 Users: <b>{stats.get('total_users', 0)}</b> "
                f"(+{stats.get('today_users', 0)} today)\n"
                f"📁 Files: <b>{stats.get('total_files', 0)}</b> | "
                f"📥 Downloads: <b>{stats.get('total_downloads', 0)}</b>\n"
                f"📅 Today: {stats.get('today_uploads', 0)} uploads, "
                f"{stats.get('today_downloads', 0)} downloads\n"
                f"🚫 Banned: <b>{stats.get('banned_users', 0)}</b> | "
                f"⚠️ Errors: <b>{stats.get('total_errors', 0)}</b>\n"
                f"🗄️ DB Size: <b>{format_size(stats.get('db_size', 0))}</b>\n\n"
                f"🕐 {datetime.now().strftime('%d %b %Y, %H:%M:%S')}"
            )

            await self.bot.send_message(
                log_channel,
                text,
                parse_mode=ParseMode.HTML,
            )
        except Exception as e:
            log.debug(f"Log report send failed: {e}")

    # ───────────────────────────────────────────────────────────────────────
    # 📢 STARTUP NOTIFICATION
    # ───────────────────────────────────────────────────────────────────────

    async def _notify_startup(self) -> None:
        """Admins ko startup notification bhejta hai"""
        try:
            log_channel = settings.get_int("log_channel_id", 0)
            if not log_channel:
                return

            me = await self.bot.get_me()

            text = (
                f"🚀 <b>Bot Started</b>\n\n"
                f"🤖 @{me.username}\n"
                f"📦 v{Bootstrap.BOT_VERSION}\n"
                f"📅 {datetime.now().strftime('%d %b %Y, %H:%M')}"
            )

            await self.bot.send_message(
                log_channel,
                text,
                parse_mode=ParseMode.HTML,
            )
        except Exception as e:
            log.debug(f"Notify startup failed: {e}")

    # ───────────────────────────────────────────────────────────────────────
    # 🛑 SHUTDOWN
    # ───────────────────────────────────────────────────────────────────────

    async def shutdown(self) -> None:
        """Bot shutdown process"""
        global shutting_down

        if shutting_down:
            return

        shutting_down = True
        self.running = False
        self._stop_event.set()

        log.info("=" * 70)
        log.info(f"{Colors.warning('🛑')} Shutting down...")
        log.info("=" * 70)

        log.info("Cancelling background tasks...")
        for task in background_tasks:
            if not task.done():
                task.cancel()

        if background_tasks:
            await asyncio.gather(*background_tasks, return_exceptions=True)
        log.info(f"{Colors.success('✅')} Tasks cancelled")

        try:
            log_channel = settings.get_int("log_channel_id", 0)
            if log_channel and self.bot:
                await self.bot.send_message(
                    log_channel,
                    "🛑 <b>Bot shutting down</b>",
                    parse_mode=ParseMode.HTML,
                )
        except Exception:
            pass

        if self.bot:
            try:
                await self.bot.session.close()
                log.info(f"{Colors.success('✅')} Bot session closed")
            except Exception as e:
                log.warning(f"Bot close failed: {e}")

        try:
            await close_database()
            log.info(f"{Colors.success('✅')} Database closed")
        except Exception as e:
            log.warning(f"DB close failed: {e}")

        log.info("=" * 70)
        log.info(f"{Colors.success('✅')} Shutdown complete")
        log.info("=" * 70)

        # ─── Panel ke liye: process guaranteed exit ────────────────
        await asyncio.sleep(1)
        os._exit(0)

    # ───────────────────────────────────────────────────────────────────────
    # ▶️ RUN
    # ───────────────────────────────────────────────────────────────────────

    async def run(self) -> None:
        """Bot ko chalata hai"""
        try:
            await self.startup()

            try:
                await self.bot.delete_webhook(drop_pending_updates=False)
            except Exception as e:
                log.debug(f"Delete webhook failed: {e}")

            log.info(f"{Colors.BRIGHT_CYAN}🎧 Starting polling...{Colors.RESET}")

            await self.dp.start_polling(
                self.bot,
                allowed_updates=self.dp.resolve_used_update_types(),
                drop_pending_updates=False,
                handle_signals=False,
            )

        except Exception as e:
            log.error(f"Run error: {e}")
            traceback.print_exc()
            raise
        finally:
            await self.shutdown()


# ═══════════════════════════════════════════════════════════════════════════
# 🚨 ERROR HANDLER
# ═══════════════════════════════════════════════════════════════════════════

async def global_error_handler(event: ErrorEvent) -> bool:
    """Global error handler"""
    exception = event.exception
    update = event.update

    if isinstance(exception, TelegramConflictError):
        log.error(
            "⚠️ Bot conflict! Ek hi token se do jagah chal raha hai. "
            "Dusra instance band karo!"
        )
        return True

    if isinstance(exception, TelegramForbiddenError):
        log.debug(f"User blocked bot: {exception}")
        return True

    if isinstance(exception, TelegramRetryAfter):
        wait = exception.retry_after
        log.warning(f"Rate limited by Telegram. Waiting {wait}s...")
        await asyncio.sleep(wait + 1)
        return True

    if isinstance(exception, TelegramBadRequest):
        log.warning(f"Bad request: {exception}")
        return True

    if isinstance(exception, TelegramNetworkError):
        log.warning(f"Network error: {exception}")
        return True

    log.error("=" * 70)
    log.error(f"{Colors.error('❌ UNHANDLED EXCEPTION')}")
    log.error("=" * 70)
    log.error(f"Exception: {type(exception).__name__}")
    log.error(f"Message: {exception}")
    log.error(f"Update ID: {update.update_id if update else 'N/A'}")

    tb_str = "".join(traceback.format_tb(exception.__traceback__))
    log.error(f"Traceback:\n{tb_str}")
    log.error("=" * 70)

    try:
        await db.log_error(
            error_type=type(exception).__name__,
            error_message=str(exception)[:5000],
            traceback_str=tb_str[:10000],
            function_name="global_error_handler",
        )
    except Exception:
        pass

    try:
        await _notify_error(exception, update)
    except Exception:
        pass

    return True


async def _notify_error(exception: Exception, update: Any) -> None:
    """Admins ko error notification bhejta hai"""
    try:
        if not settings.get_bool("notify_admin_on_error", True):
            return

        log_channel = settings.get_int("log_channel_id", 0)
        if not log_channel or not bot:
            return

        throttle_seconds = settings.get_int("error_throttle_seconds", 60)
        now = time.time()
        key = f"_last_error_{type(exception).__name__}"

        last = getattr(_notify_error, key, 0)
        if now - last < throttle_seconds:
            return

        setattr(_notify_error, key, now)

        text = (
            f"🚨 <b>Bot Error</b>\n\n"
            f"⚠️ Type: <code>{type(exception).__name__}</code>\n"
            f"📝 Message: <code>{str(exception)[:300]}</code>\n"
            f"📅 {datetime.now().strftime('%d %b %Y, %H:%M')}"
        )

        await bot.send_message(
            log_channel,
            text,
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# 🔔 SIGNAL HANDLERS
# ═══════════════════════════════════════════════════════════════════════════

async def _graceful_stop(app: "IsukobitBot") -> None:
    """Panel ke Stop/Restart pe polling band karke exit karta hai"""
    try:
        if app.dp and hasattr(app.dp, "stop_polling"):
            await app.dp.stop_polling()
    except Exception as e:
        log.debug(f"stop_polling failed: {e}")

    try:
        if app.bot:
            await app.bot.session.close()
    except Exception:
        pass

    # Agar 10 second mein process exit na ho to force exit
    # (taaki panel ko Force Kill na karna pade)
    await asyncio.sleep(10)
    log.warning("Graceful exit timeout — forcing exit")
    os._exit(0)


def register_signal_handlers(app: IsukobitBot, loop: asyncio.AbstractEventLoop) -> None:
    """Signal handlers register karta hai"""
    def _handler(sig):
        log.info(f"Received signal: {sig.name}")
        loop.create_task(_graceful_stop(app))

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, _handler, sig)
        except NotImplementedError:
            signal.signal(sig, lambda s, f: loop.create_task(_graceful_stop(app)))


# ═══════════════════════════════════════════════════════════════════════════
# 🎬 MAIN ENTRY
# ═══════════════════════════════════════════════════════════════════════════

async def main_async() -> None:
    """Async main function"""
    global restart_count

    print_banner()
    print_config_summary()

    app = IsukobitBot()

    loop = asyncio.get_event_loop()
    register_signal_handlers(app, loop)

    try:
        await app.run()
    except KeyboardInterrupt:
        log.info("Keyboard interrupt received")
        await app.shutdown()
    except TelegramUnauthorizedError:
        log.error("Invalid bot token!")
        sys.exit(1)
    except Exception as e:
        log.error(f"Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)


def main() -> None:
    """Sync main entry point"""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n👋 Bot band kar diya gaya.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════
# 📌 ERROR HANDLER REGISTER (post-startup)
# ═══════════════════════════════════════════════════════════════════════════

def _register_error_handler_after_startup(app: IsukobitBot) -> None:
    """Error handler register karta hai startup ke baad"""
    if app.dp:
        app.dp.errors.register(global_error_handler)


_original_startup = IsukobitBot.startup


async def _patched_startup(self):
    await _original_startup(self)
    _register_error_handler_after_startup(self)


IsukobitBot.startup = _patched_startup


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "IsukobitBot",
    "main",
    "main_async",
    "global_error_handler",
    "bot",
    "dp",
]


# ═══════════════════════════════════════════════════════════════════════════
# 🚀 ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()


