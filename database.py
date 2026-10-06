# ═══════════════════════════════════════════════════════════════════════════
# 🚀 ISUKOBIT — TELEGRAM FILE STORE BOT
# ═══════════════════════════════════════════════════════════════════════════
# File      : database.py (SQLite — Race-Safe Version)
# Purpose   : Local SQLite database — koi cloud nahi, koi server nahi
# Author    : Isukobit Team
# Version   : 2.0.1
# Python    : 3.10+
# Library   : aiosqlite (async SQLite)
# ═══════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════
# 📦 IMPORTS
# ═══════════════════════════════════════════════════════════════════════════

import asyncio
import json
import time
import os
from pathlib import Path
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any, Union, Tuple

try:
    import aiosqlite
except ImportError:
    print("❌ ERROR: aiosqlite install nahi hai!")
    print("   Solution: pip install aiosqlite")
    raise

from config import Constants, DEFAULT_SETTINGS, settings, log, Colors, Bootstrap


# ═══════════════════════════════════════════════════════════════════════════
# 🗄️ DATABASE CLASS — SQLite Version
# ═══════════════════════════════════════════════════════════════════════════

class Database:
    """SQLite database manager — async operations."""

    def __init__(self):
        db_path = os.getenv("DB_PATH", "data/isukobit.db")
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[aiosqlite.Connection] = None
        self._connected: bool = False
        self._lock = asyncio.Lock()
        log.debug(f"SQLite database path: {self.db_path}")

    async def connect(self) -> None:
        if self._connected and self.conn:
            return
        async with self._lock:
            if self._connected and self.conn:
                return
            try:
                self.conn = await aiosqlite.connect(str(self.db_path))
                self.conn.row_factory = aiosqlite.Row
                await self.conn.execute("PRAGMA journal_mode = WAL")
                await self.conn.execute("PRAGMA foreign_keys = ON")
                await self.conn.execute("PRAGMA synchronous = NORMAL")
                await self.conn.execute("PRAGMA cache_size = 10000")
                await self.conn.execute("PRAGMA temp_store = MEMORY")
                await self.conn.commit()
                self._connected = True
                log.info(f"{Colors.success('✅')} SQLite connected: {self.db_path}")
            except Exception as e:
                log.error(f"{Colors.error('❌')} SQLite connection failed: {e}")
                raise

    async def disconnect(self) -> None:
        if self.conn:
            try:
                await self.conn.close()
            except Exception:
                pass
            self.conn = None
            self._connected = False
            log.info(f"{Colors.warning('🔌')} Database disconnected")

    async def reconnect(self, max_attempts: int = 5) -> bool:
        for attempt in range(1, max_attempts + 1):
            try:
                log.info(f"Reconnect attempt {attempt}/{max_attempts}...")
                await self.disconnect()
                await asyncio.sleep(2 ** attempt)
                await self.connect()
                return True
            except Exception as e:
                log.warning(f"Reconnect attempt {attempt} failed: {e}")
        log.error(f"{Colors.error('❌')} All reconnect attempts failed")
        return False

    async def is_connected(self) -> bool:
        if not self.conn or not self._connected:
            return False
        try:
            async with self.conn.execute("SELECT 1") as cursor:
                await cursor.fetchone()
            return True
        except Exception:
            return False

    async def execute(self, query: str, params: Optional[Tuple] = None) -> int:
        if not self.conn:
            await self.connect()
        try:
            async with self._lock:
                cursor = await self.conn.execute(query, params or ())
                await self.conn.commit()
                return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
        except Exception as e:
            log.error(f"DB execute error: {e}\nQuery: {query[:200]}")
            raise

    async def fetchone(self, query: str, params: Optional[Tuple] = None) -> Optional[Dict[str, Any]]:
        if not self.conn:
            await self.connect()
        try:
            async with self.conn.execute(query, params or ()) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return None
                return dict(row)
        except Exception as e:
            log.error(f"DB fetchone error: {e}\nQuery: {query[:200]}")
            raise

    async def fetchall(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        if not self.conn:
            await self.connect()
        try:
            async with self.conn.execute(query, params or ()) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            log.error(f"DB fetchall error: {e}\nQuery: {query[:200]}")
            raise

    async def fetchval(self, query: str, params: Optional[Tuple] = None, column: int = 0) -> Any:
        row = await self.fetchone(query, params)
        if not row:
            return None
        return list(row.values())[column]

    async def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        if not self.conn:
            await self.connect()
        try:
            async with self._lock:
                cursor = await self.conn.executemany(query, params_list)
                await self.conn.commit()
                return cursor.rowcount
        except Exception as e:
            log.error(f"DB executemany error: {e}")
            raise

    async def create_tables(self) -> None:
        log.info(f"{Colors.info('🏗️')} Creating tables...")

        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT DEFAULT NULL,
                first_name TEXT DEFAULT NULL,
                last_name TEXT DEFAULT NULL,
                language TEXT DEFAULT 'hinglish',
                status TEXT DEFAULT 'active',
                is_premium INTEGER DEFAULT 0,
                premium_until TEXT DEFAULT NULL,
                is_admin INTEGER DEFAULT 0,
                is_owner INTEGER DEFAULT 0,
                total_files INTEGER DEFAULT 0,
                total_downloads INTEGER DEFAULT 0,
                total_uploads INTEGER DEFAULT 0,
                joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_activity TEXT DEFAULT CURRENT_TIMESTAMP,
                is_banned INTEGER DEFAULT 0,
                ban_reason TEXT DEFAULT NULL,
                banned_at TEXT DEFAULT NULL,
                banned_by INTEGER DEFAULT NULL,
                notes TEXT DEFAULT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_code TEXT UNIQUE NOT NULL,
                file_id TEXT NOT NULL,
                file_unique_id TEXT DEFAULT NULL,
                message_id INTEGER DEFAULT NULL,
                channel_id INTEGER DEFAULT NULL,
                backup_message_id INTEGER DEFAULT NULL,
                backup_channel_id INTEGER DEFAULT NULL,
                file_name TEXT DEFAULT NULL,
                file_size INTEGER DEFAULT 0,
                mime_type TEXT DEFAULT NULL,
                file_extension TEXT DEFAULT NULL,
                file_type TEXT DEFAULT NULL,
                caption TEXT DEFAULT NULL,
                file_hash TEXT DEFAULT NULL,
                uploader_id INTEGER NOT NULL,
                uploader_username TEXT DEFAULT NULL,
                folder_id INTEGER DEFAULT NULL,
                download_count INTEGER DEFAULT 0,
                last_accessed TEXT DEFAULT NULL,
                uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT DEFAULT NULL,
                is_deleted INTEGER DEFAULT 0,
                deleted_at TEXT DEFAULT NULL,
                deleted_by INTEGER DEFAULT NULL,
                is_public INTEGER DEFAULT 0,
                password_hash TEXT DEFAULT NULL,
                extra_data TEXT DEFAULT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folder_name TEXT NOT NULL,
                owner_id INTEGER NOT NULL,
                parent_id INTEGER DEFAULT NULL,
                files_count INTEGER DEFAULT 0,
                is_public INTEGER DEFAULT 0,
                share_code TEXT DEFAULT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER PRIMARY KEY,
                added_by INTEGER DEFAULT NULL,
                added_at TEXT DEFAULT CURRENT_TIMESTAMP,
                permissions TEXT DEFAULT NULL,
                notes TEXT DEFAULT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS banned_users (
                user_id INTEGER PRIMARY KEY,
                reason TEXT DEFAULT NULL,
                banned_by INTEGER DEFAULT NULL,
                banned_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT DEFAULT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS settings (
                key_name TEXT PRIMARY KEY,
                value TEXT DEFAULT NULL,
                value_type TEXT DEFAULT 'string',
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_by INTEGER DEFAULT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_type TEXT NOT NULL,
                user_id INTEGER DEFAULT NULL,
                file_id INTEGER DEFAULT NULL,
                action TEXT DEFAULT NULL,
                details TEXT DEFAULT NULL,
                ip_address TEXT DEFAULT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_type TEXT DEFAULT 'database',
                file_name TEXT DEFAULT NULL,
                file_size INTEGER DEFAULT 0,
                message_id INTEGER DEFAULT NULL,
                channel_id INTEGER DEFAULT NULL,
                backup_path TEXT DEFAULT NULL,
                status TEXT DEFAULT 'completed',
                error_message TEXT DEFAULT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS broadcasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                message_type TEXT DEFAULT 'text',
                message_text TEXT DEFAULT NULL,
                file_id TEXT DEFAULT NULL,
                total_users INTEGER DEFAULT 0,
                sent_count INTEGER DEFAULT 0,
                failed_count INTEGER DEFAULT 0,
                blocked_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                started_at TEXT DEFAULT CURRENT_TIMESTAMP,
                finished_at TEXT DEFAULT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                downloaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT DEFAULT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS error_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_type TEXT DEFAULT NULL,
                error_message TEXT DEFAULT NULL,
                traceback TEXT DEFAULT NULL,
                user_id INTEGER DEFAULT NULL,
                function_name TEXT DEFAULT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS rate_limits (
                user_id INTEGER PRIMARY KEY,
                request_count INTEGER DEFAULT 0,
                window_start TEXT DEFAULT CURRENT_TIMESTAMP,
                spam_warnings INTEGER DEFAULT 0,
                muted_until TEXT DEFAULT NULL,
                last_request TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS premium_users (
                user_id INTEGER PRIMARY KEY,
                plan TEXT DEFAULT 'basic',
                started_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT DEFAULT NULL,
                payment_id TEXT DEFAULT NULL,
                amount_paid REAL DEFAULT 0.0,
                currency TEXT DEFAULT 'INR',
                auto_renew INTEGER DEFAULT 0
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS daily_stats (
                stat_date TEXT PRIMARY KEY,
                new_users INTEGER DEFAULT 0,
                active_users INTEGER DEFAULT 0,
                uploads INTEGER DEFAULT 0,
                downloads INTEGER DEFAULT 0,
                total_files INTEGER DEFAULT 0,
                total_size INTEGER DEFAULT 0,
                errors INTEGER DEFAULT 0,
                backups INTEGER DEFAULT 0
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_code TEXT UNIQUE NOT NULL,
                uploader_id INTEGER NOT NULL,
                file_ids TEXT NOT NULL,
                download_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
        ]

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX IF NOT EXISTS idx_users_status ON users(status)",
            "CREATE INDEX IF NOT EXISTS idx_users_joined ON users(joined_at)",
            "CREATE INDEX IF NOT EXISTS idx_files_code ON files(file_code)",
            "CREATE INDEX IF NOT EXISTS idx_files_uploader ON files(uploader_id)",
            "CREATE INDEX IF NOT EXISTS idx_files_folder ON files(folder_id)",
            "CREATE INDEX IF NOT EXISTS idx_files_uploaded ON files(uploaded_at)",
            "CREATE INDEX IF NOT EXISTS idx_files_hash ON files(file_hash)",
            "CREATE INDEX IF NOT EXISTS idx_folders_owner ON folders(owner_id)",
            "CREATE INDEX IF NOT EXISTS idx_logs_type ON logs(log_type)",
            "CREATE INDEX IF NOT EXISTS idx_logs_created ON logs(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_downloads_user ON downloads(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_downloads_date ON downloads(downloaded_at)",
        ]

        for i, sql in enumerate(tables, 1):
            try:
                await self.conn.execute(sql)
            except Exception as e:
                log.error(f"Table {i} creation failed: {e}")
                raise

        for idx_sql in indexes:
            try:
                await self.conn.execute(idx_sql)
            except Exception as e:
                log.debug(f"Index creation skipped: {e}")

        await self.conn.commit()
        log.info(f"{Colors.success('✅')} All {len(tables)} tables + {len(indexes)} indexes ready")

    async def insert_default_settings(self) -> None:
        log.info(f"{Colors.info('⚙️')} Inserting default settings...")
        count = 0
        for key, value in DEFAULT_SETTINGS.items():
            existing = await self.fetchone(
                "SELECT key_name FROM settings WHERE key_name = ?", (key,)
            )
            if existing:
                continue
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value, ensure_ascii=False)
                value_type = "json"
            elif isinstance(value, bool):
                value_str = "true" if value else "false"
                value_type = "bool"
            elif isinstance(value, int):
                value_str = str(value)
                value_type = "int"
            elif isinstance(value, float):
                value_str = str(value)
                value_type = "float"
            else:
                value_str = str(value)
                value_type = "string"
            await self.execute(
                "INSERT INTO settings (key_name, value, value_type) VALUES (?, ?, ?)",
                (key, value_str, value_type)
            )
            count += 1
        if count > 0:
            log.info(f"{Colors.success('✅')} Inserted {count} default settings")

    async def load_settings(self) -> Dict[str, Any]:
        rows = await self.fetchall("SELECT key_name, value, value_type FROM settings")
        result = {}
        for row in rows:
            key = row["key_name"]
            value = row["value"]
            value_type = row["value_type"]
            try:
                if value_type == "json":
                    result[key] = json.loads(value) if value else None
                elif value_type == "bool":
                    result[key] = value.lower() in ("true", "1", "yes") if value else False
                elif value_type == "int":
                    result[key] = int(value) if value else 0
                elif value_type == "float":
                    result[key] = float(value) if value else 0.0
                else:
                    result[key] = value
            except (ValueError, json.JSONDecodeError):
                result[key] = value
        return result

    # ═══════════════════════════════════════════════════════════════════════
    # 👥 USER OPERATIONS — FIXED RACE-SAFE VERSION
    # ═══════════════════════════════════════════════════════════════════════

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        return await self.fetchone("SELECT * FROM users WHERE user_id = ?", (user_id,))

    async def user_exists(self, user_id: int) -> bool:
        row = await self.fetchone("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        return row is not None

    async def add_user(self, user_id: int, first_name: str = "", username: str = "",
                       last_name: str = "", language: str = None) -> bool:
        """Naya user add karta hai (race-safe version)"""
        try:
            existing = await self.get_user(user_id)

            if existing:
                await self.execute(
                    """
                    UPDATE users 
                    SET first_name = ?, username = ?, last_name = ?,
                        last_activity = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                    """,
                    (first_name or existing.get("first_name", ""),
                     username or existing.get("username", ""),
                     last_name or existing.get("last_name", ""),
                     user_id)
                )
                return False
            else:
                result = await self.execute(
                    """
                    INSERT OR IGNORE INTO users 
                    (user_id, first_name, username, last_name, language)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (user_id, first_name, username, last_name,
                     language or "hinglish")
                )
                if result:
                    await self.increment_daily_stat("new_users")
                    return True
                return False
        except Exception as e:
            log.error(f"add_user error: {e}")
            return False

    async def update_user_activity(self, user_id: int) -> None:
        await self.execute(
            "UPDATE users SET last_activity = CURRENT_TIMESTAMP WHERE user_id = ?",
            (user_id,)
        )

    async def set_user_language(self, user_id: int, language: str) -> None:
        await self.execute(
            "UPDATE users SET language = ? WHERE user_id = ?",
            (language, user_id)
        )

    async def get_user_language(self, user_id: int) -> str:
        lang = await self.fetchval(
            "SELECT language FROM users WHERE user_id = ?", (user_id,)
        )
        return lang or "hinglish"

    async def increment_user_files(self, user_id: int, count: int = 1) -> None:
        await self.execute(
            """
            UPDATE users 
            SET total_files = total_files + ?,
                total_uploads = total_uploads + ?
            WHERE user_id = ?
            """,
            (count, count, user_id)
        )

    async def increment_user_downloads(self, user_id: int, count: int = 1) -> None:
        await self.execute(
            "UPDATE users SET total_downloads = total_downloads + ? WHERE user_id = ?",
            (count, user_id)
        )

    async def ban_user(self, user_id: int, reason: str = "", banned_by: int = 0,
                       expires_at: Optional[datetime] = None) -> bool:
        try:
            expires_str = expires_at.isoformat() if expires_at else None
            await self.execute(
                """
                UPDATE users 
                SET is_banned = 1, ban_reason = ?, 
                    banned_at = CURRENT_TIMESTAMP, banned_by = ?
                WHERE user_id = ?
                """,
                (reason, banned_by, user_id)
            )
            await self.execute(
                """
                INSERT INTO banned_users (user_id, reason, banned_by, expires_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    reason = excluded.reason,
                    banned_by = excluded.banned_by,
                    banned_at = CURRENT_TIMESTAMP,
                    expires_at = excluded.expires_at
                """,
                (user_id, reason, banned_by, expires_str)
            )
            return True
        except Exception as e:
            log.error(f"ban_user error: {e}")
            return False

    async def unban_user(self, user_id: int) -> bool:
        try:
            await self.execute(
                """
                UPDATE users 
                SET is_banned = 0, ban_reason = NULL,
                    banned_at = NULL, banned_by = NULL
                WHERE user_id = ?
                """,
                (user_id,)
            )
            await self.execute("DELETE FROM banned_users WHERE user_id = ?", (user_id,))
            return True
        except Exception as e:
            log.error(f"unban_user error: {e}")
            return False

    async def is_user_banned(self, user_id: int) -> bool:
        row = await self.fetchone(
            "SELECT is_banned FROM users WHERE user_id = ?", (user_id,)
        )
        return bool(row["is_banned"]) if row else False

    async def get_user_count(self) -> int:
        count = await self.fetchval("SELECT COUNT(*) FROM users")
        return count or 0

    async def get_all_user_ids(self) -> List[int]:
        rows = await self.fetchall("SELECT user_id FROM users WHERE is_banned = 0")
        return [row["user_id"] for row in rows]

    async def get_users_paginated(self, page: int = 1, per_page: int = 10) -> Tuple[List[Dict], int]:
        offset = (page - 1) * per_page
        users = await self.fetchall(
            "SELECT * FROM users ORDER BY joined_at DESC LIMIT ? OFFSET ?",
            (per_page, offset)
        )
        total = await self.get_user_count()
        return users, total

    async def search_users(self, query: str, limit: int = 10) -> List[Dict]:
        search_pattern = f"%{query}%"
        return await self.fetchall(
            """
            SELECT * FROM users 
            WHERE first_name LIKE ? 
               OR username LIKE ? 
               OR CAST(user_id AS TEXT) LIKE ?
            LIMIT ?
            """,
            (search_pattern, search_pattern, search_pattern, limit)
        )

    # ═══════════════════════════════════════════════════════════════════════
    # 👑 ADMIN OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════

    async def is_admin(self, user_id: int) -> bool:
        if user_id == Bootstrap.OWNER_ID:
            return True
        if user_id in Bootstrap.ADMIN_IDS:
            return True
        row = await self.fetchone("SELECT user_id FROM admins WHERE user_id = ?", (user_id,))
        return row is not None

    async def is_owner(self, user_id: int) -> bool:
        return user_id == Bootstrap.OWNER_ID

    async def add_admin(self, user_id: int, added_by: int = 0,
                        permissions: List[str] = None, notes: str = "") -> bool:
        try:
            perms_str = json.dumps(permissions or [])
            await self.execute(
                """
                INSERT INTO admins (user_id, added_by, permissions, notes)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    permissions = excluded.permissions,
                    notes = excluded.notes
                """,
                (user_id, added_by, perms_str, notes)
            )
            await self.execute("UPDATE users SET is_admin = 1 WHERE user_id = ?", (user_id,))
            return True
        except Exception as e:
            log.error(f"add_admin error: {e}")
            return False

    async def remove_admin(self, user_id: int) -> bool:
        if user_id == Bootstrap.OWNER_ID:
            return False
        try:
            await self.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
            await self.execute("UPDATE users SET is_admin = 0 WHERE user_id = ?", (user_id,))
            return True
        except Exception as e:
            log.error(f"remove_admin error: {e}")
            return False

    async def get_all_admins(self) -> List[int]:
        rows = await self.fetchall("SELECT user_id FROM admins")
        admin_ids = [row["user_id"] for row in rows]
        if Bootstrap.OWNER_ID not in admin_ids:
            admin_ids.append(Bootstrap.OWNER_ID)
        for aid in Bootstrap.ADMIN_IDS:
            if aid not in admin_ids:
                admin_ids.append(aid)
        return admin_ids

    # ═══════════════════════════════════════════════════════════════════════
    # 📁 FILE OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════

    async def add_file(self, file_code: str, file_id: str, uploader_id: int,
                       file_name: str = "", file_size: int = 0, mime_type: str = "",
                       file_extension: str = "", file_type: str = "", caption: str = "",
                       message_id: int = 0, channel_id: int = 0, file_unique_id: str = "",
                       uploader_username: str = "", folder_id: Optional[int] = None,
                       file_hash: str = "", expires_at: Optional[datetime] = None,
                       password_hash: str = "") -> Optional[int]:
        try:
            expires_str = expires_at.isoformat() if expires_at else None
            file_db_id = await self.execute(
                """
                INSERT INTO files 
                (file_code, file_id, file_unique_id, message_id, channel_id,
                 file_name, file_size, mime_type, file_extension, file_type,
                 caption, file_hash, uploader_id, uploader_username,
                 folder_id, expires_at, password_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (file_code, file_id, file_unique_id, message_id, channel_id,
                 file_name, file_size, mime_type, file_extension, file_type,
                 caption, file_hash, uploader_id, uploader_username,
                 folder_id, expires_str, password_hash)
            )
            await self.increment_user_files(uploader_id)
            await self.increment_daily_stat("uploads")
            if folder_id:
                await self.execute(
                    "UPDATE folders SET files_count = files_count + 1 WHERE id = ?",
                    (folder_id,)
                )
            return file_db_id
        except Exception as e:
            log.error(f"add_file error: {e}")
            return None

    async def get_file_by_code(self, file_code: str) -> Optional[Dict[str, Any]]:
        return await self.fetchone(
            "SELECT * FROM files WHERE file_code = ? AND is_deleted = 0", (file_code,)
        )

    async def get_file_by_id(self, file_id: int) -> Optional[Dict[str, Any]]:
        return await self.fetchone(
            "SELECT * FROM files WHERE id = ? AND is_deleted = 0", (file_id,)
        )

    async def get_file_by_hash(self, file_hash: str) -> Optional[Dict[str, Any]]:
        return await self.fetchone(
            "SELECT * FROM files WHERE file_hash = ? AND is_deleted = 0", (file_hash,)
        )

    async def get_user_files(self, user_id: int, page: int = 1,
                             per_page: int = 10, folder_id: Optional[int] = None) -> Tuple[List[Dict], int]:
        offset = (page - 1) * per_page
        if folder_id is not None:
            where = "uploader_id = ? AND folder_id = ? AND is_deleted = 0"
            params = (user_id, folder_id)
        else:
            where = "uploader_id = ? AND is_deleted = 0"
            params = (user_id,)
        files = await self.fetchall(
            f"SELECT * FROM files WHERE {where} ORDER BY uploaded_at DESC LIMIT ? OFFSET ?",
            (*params, per_page, offset)
        )
        total = await self.fetchval(f"SELECT COUNT(*) FROM files WHERE {where}", params)
        return files, total or 0

    async def get_all_user_file_ids(self, user_id: int) -> List[int]:
        """User ki SAARI file IDs return karta hai (Select All ke liye)"""
        rows = await self.fetchall(
            "SELECT id FROM files WHERE uploader_id = ? AND is_deleted = 0",
            (user_id,)
        )
        return [r["id"] for r in rows]

    async def search_files(self, query: str, user_id: Optional[int] = None,
                           page: int = 1, per_page: int = 10,
                           search_own_only: bool = True) -> Tuple[List[Dict], int]:
        offset = (page - 1) * per_page
        pattern = f"%{query}%"
        if user_id and search_own_only:
            where = "uploader_id = ? AND is_deleted = 0"
            search_where = "AND (file_name LIKE ? OR file_code LIKE ? OR caption LIKE ? OR file_extension LIKE ?)"
            params = (user_id, pattern, pattern, pattern, pattern)
        else:
            where = "is_deleted = 0"
            search_where = "AND (file_name LIKE ? OR file_code LIKE ? OR caption LIKE ? OR file_extension LIKE ?)"
            params = (pattern, pattern, pattern, pattern)
        files = await self.fetchall(
            f"SELECT * FROM files WHERE {where} {search_where} ORDER BY uploaded_at DESC LIMIT ? OFFSET ?",
            (*params, per_page, offset)
        )
        total = await self.fetchval(
            f"SELECT COUNT(*) FROM files WHERE {where} {search_where}", params
        )
        return files, total or 0

    async def increment_download_count(self, file_id: int) -> None:
        await self.execute(
            """
            UPDATE files 
            SET download_count = download_count + 1,
                last_accessed = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (file_id,)
        )

    async def record_download(self, file_db_id: int, user_id: int, ip_address: str = "") -> None:
        await self.execute(
            "INSERT INTO downloads (file_id, user_id, ip_address) VALUES (?, ?, ?)",
            (file_db_id, user_id, ip_address)
        )
        await self.increment_user_downloads(user_id)
        await self.increment_daily_stat("downloads")

    async def delete_file(self, file_db_id: int, deleted_by: int = 0) -> bool:
        try:
            await self.execute(
                """
                UPDATE files 
                SET is_deleted = 1, 
                    deleted_at = CURRENT_TIMESTAMP,
                    deleted_by = ?
                WHERE id = ?
                """,
                (deleted_by, file_db_id)
            )
            return True
        except Exception as e:
            log.error(f"delete_file error: {e}")
            return False

    async def rename_file(self, file_db_id: int, new_name: str) -> bool:
        try:
            await self.execute(
                "UPDATE files SET file_name = ? WHERE id = ?",
                (new_name, file_db_id)
            )
            return True
        except Exception as e:
            log.error(f"rename_file error: {e}")
            return False

    async def get_total_files_count(self) -> int:
        count = await self.fetchval("SELECT COUNT(*) FROM files WHERE is_deleted = 0")
        return count or 0

    async def get_total_files_size(self) -> int:
        size = await self.fetchval(
            "SELECT COALESCE(SUM(file_size), 0) FROM files WHERE is_deleted = 0"
        )
        return int(size) if size else 0

    # ═══════════════════════════════════════════════════════════════════════
    # 📂 FOLDER OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════

    async def create_folder(self, name: str, owner_id: int, parent_id: Optional[int] = None) -> Optional[int]:
        try:
            return await self.execute(
                "INSERT INTO folders (folder_name, owner_id, parent_id) VALUES (?, ?, ?)",
                (name, owner_id, parent_id)
            )
        except Exception as e:
            log.error(f"create_folder error: {e}")
            return None

    async def get_folder(self, folder_id: int) -> Optional[Dict[str, Any]]:
        return await self.fetchone("SELECT * FROM folders WHERE id = ?", (folder_id,))

    async def get_user_folders(self, user_id: int, parent_id: Optional[int] = None) -> List[Dict[str, Any]]:
        if parent_id is None:
            return await self.fetchall(
                "SELECT * FROM folders WHERE owner_id = ? AND parent_id IS NULL ORDER BY created_at DESC",
                (user_id,)
            )
        else:
            return await self.fetchall(
                "SELECT * FROM folders WHERE owner_id = ? AND parent_id = ? ORDER BY created_at DESC",
                (user_id, parent_id)
            )

    async def delete_folder(self, folder_id: int) -> bool:
        try:
            await self.execute("UPDATE files SET folder_id = NULL WHERE folder_id = ?", (folder_id,))
            await self.execute("UPDATE folders SET parent_id = NULL WHERE parent_id = ?", (folder_id,))
            await self.execute("DELETE FROM folders WHERE id = ?", (folder_id,))
            return True
        except Exception as e:
            log.error(f"delete_folder error: {e}")
            return False

    async def rename_folder(self, folder_id: int, new_name: str) -> bool:
        try:
            await self.execute(
                "UPDATE folders SET folder_name = ? WHERE id = ?", (new_name, folder_id)
            )
            return True
        except Exception as e:
            log.error(f"rename_folder error: {e}")
            return False

    async def move_file_to_folder(self, file_db_id: int, folder_id: Optional[int]) -> bool:
        try:
            old_file = await self.get_file_by_id(file_db_id)
            if old_file and old_file.get("folder_id"):
                await self.execute(
                    "UPDATE folders SET files_count = MAX(files_count - 1, 0) WHERE id = ?",
                    (old_file["folder_id"],)
                )
            await self.execute("UPDATE files SET folder_id = ? WHERE id = ?", (folder_id, file_db_id))
            if folder_id:
                await self.execute(
                    "UPDATE folders SET files_count = files_count + 1 WHERE id = ?", (folder_id,)
                )
            return True
        except Exception as e:
            log.error(f"move_file_to_folder error: {e}")
            return False

    # ═══════════════════════════════════════════════════════════════════════
    # 📦 BATCH OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════

    async def create_batch(self, batch_code: str, uploader_id: int, file_ids: List[int]) -> bool:
        """Naya batch create karta hai"""
        try:
            await self.execute(
                "INSERT INTO batches (batch_code, uploader_id, file_ids) VALUES (?, ?, ?)",
                (batch_code, uploader_id, json.dumps(file_ids))
            )
            return True
        except Exception as e:
            log.error(f"create_batch error: {e}")
            return False

    async def get_batch_by_code(self, batch_code: str) -> Optional[Dict[str, Any]]:
        """Batch + uski saari files return karta hai"""
        batch = await self.fetchone("SELECT * FROM batches WHERE batch_code = ?", (batch_code,))
        if not batch:
            return None
        try:
            file_ids = json.loads(batch.get("file_ids") or "[]")
        except Exception:
            file_ids = []
        files = []
        for fid in file_ids:
            f = await self.get_file_by_id(fid)
            if f:
                files.append(f)
        batch["files"] = files
        return batch

    async def increment_batch_downloads(self, batch_code: str) -> None:
        await self.execute(
            "UPDATE batches SET download_count = download_count + 1 WHERE batch_code = ?",
            (batch_code,)
        )

    # ═══════════════════════════════════════════════════════════════════════
    # ⚙️ SETTINGS OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════

    async def get_setting(self, key: str) -> Any:
        row = await self.fetchone(
            "SELECT value, value_type FROM settings WHERE key_name = ?", (key,)
        )
        if not row:
            return DEFAULT_SETTINGS.get(key)
        value = row["value"]
        value_type = row["value_type"]
        try:
            if value_type == "json":
                return json.loads(value) if value else None
            elif value_type == "bool":
                return value.lower() in ("true", "1", "yes") if value else False
            elif value_type == "int":
                return int(value) if value else 0
            elif value_type == "float":
                return float(value) if value else 0.0
            else:
                return value
        except (ValueError, json.JSONDecodeError):
            return value

    async def set_setting(self, key: str, value: Any, updated_by: int = 0) -> bool:
        try:
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value, ensure_ascii=False)
                value_type = "json"
            elif isinstance(value, bool):
                value_str = "true" if value else "false"
                value_type = "bool"
            elif isinstance(value, int):
                value_str = str(value)
                value_type = "int"
            elif isinstance(value, float):
                value_str = str(value)
                value_type = "float"
            else:
                value_str = str(value)
                value_type = "string"
            await self.execute(
                """
                INSERT INTO settings (key_name, value, value_type, updated_by)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(key_name) DO UPDATE SET
                    value = excluded.value,
                    value_type = excluded.value_type,
                    updated_by = excluded.updated_by,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (key, value_str, value_type, updated_by)
            )
            settings.set(key, value)
            return True
        except Exception as e:
            log.error(f"set_setting error: {e}")
            return False

    async def get_all_settings(self) -> Dict[str, Any]:
        return await self.load_settings()

    # ═══════════════════════════════════════════════════════════════════════
    # 📝 LOG OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════

    async def add_log(self, log_type: str, user_id: Optional[int] = None,
                      file_id: Optional[int] = None, action: str = "",
                      details: str = "", ip_address: str = "") -> None:
        try:
            await self.execute(
                """
                INSERT INTO logs 
                (log_type, user_id, file_id, action, details, ip_address)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (log_type, user_id, file_id, action, details, ip_address)
            )
        except Exception as e:
            log.error(f"add_log error: {e}")

    async def get_logs(self, log_type: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        if log_type:
            return await self.fetchall(
                "SELECT * FROM logs WHERE log_type = ? ORDER BY created_at DESC LIMIT ?",
                (log_type, limit)
            )
        else:
            return await self.fetchall(
                "SELECT * FROM logs ORDER BY created_at DESC LIMIT ?", (limit,)
            )

    async def log_error(self, error_type: str, error_message: str, traceback_str: str = "",
                        user_id: Optional[int] = None, function_name: str = "") -> None:
        try:
            await self.execute(
                """
                INSERT INTO error_logs 
                (error_type, error_message, traceback, user_id, function_name)
                VALUES (?, ?, ?, ?, ?)
                """,
                (error_type, error_message[:5000], traceback_str[:10000],
                 user_id, function_name)
            )
            await self.increment_daily_stat("errors")
        except Exception as e:
            log.error(f"log_error failed: {e}")

    # ═══════════════════════════════════════════════════════════════════════
    # 💾 BACKUP OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════

    async def add_backup_record(self, file_name: str, file_size: int, message_id: int = 0,
                                channel_id: int = 0, status: str = "completed",
                                backup_type: str = "database",
                                error_message: str = "") -> Optional[int]:
        try:
            return await self.execute(
                """
                INSERT INTO backups 
                (backup_type, file_name, file_size, message_id, 
                 channel_id, status, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (backup_type, file_name, file_size, message_id,
                 channel_id, status, error_message)
            )
        except Exception as e:
            log.error(f"add_backup_record error: {e}")
            return None

    async def get_recent_backups(self, limit: int = 10) -> List[Dict[str, Any]]:
        return await self.fetchall(
            "SELECT * FROM backups ORDER BY created_at DESC LIMIT ?", (limit,)
        )

    async def cleanup_old_backups(self, keep: int = 7) -> int:
        try:
            result = await self.execute(
                """
                DELETE FROM backups 
                WHERE id NOT IN (
                    SELECT id FROM backups 
                    ORDER BY created_at DESC 
                    LIMIT ?
                )
                """,
                (keep,)
            )
            return result
        except Exception as e:
            log.error(f"cleanup_old_backups error: {e}")
            return 0

    # ═══════════════════════════════════════════════════════════════════════
    # 📣 BROADCAST OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════

    async def create_broadcast(self, admin_id: int, message_type: str = "text",
                               message_text: str = "", file_id: str = "",
                               total_users: int = 0) -> Optional[int]:
        try:
            return await self.execute(
                """
                INSERT INTO broadcasts 
                (admin_id, message_type, message_text, file_id, total_users)
                VALUES (?, ?, ?, ?, ?)
                """,
                (admin_id, message_type, message_text, file_id, total_users)
            )
        except Exception as e:
            log.error(f"create_broadcast error: {e}")
            return None

    async def update_broadcast_stats(self, broadcast_id: int, sent: int = 0,
                                     failed: int = 0, blocked: int = 0,
                                     status: str = "running") -> None:
        try:
            finished = "CURRENT_TIMESTAMP" if status in ("completed", "cancelled", "failed") else "NULL"
            await self.execute(
                f"""
                UPDATE broadcasts 
                SET sent_count = sent_count + ?,
                    failed_count = failed_count + ?,
                    blocked_count = blocked_count + ?,
                    status = ?,
                    finished_at = {finished}
                WHERE id = ?
                """,
                (sent, failed, blocked, status, broadcast_id)
            )
        except Exception as e:
            log.error(f"update_broadcast_stats error: {e}")

    # ═══════════════════════════════════════════════════════════════════════
    # 📊 STATISTICS OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════

    async def get_stats(self) -> Dict[str, Any]:
        try:
            stats = {}
            stats["total_users"] = await self.fetchval("SELECT COUNT(*) FROM users") or 0
            stats["active_users"] = await self.fetchval(
                "SELECT COUNT(*) FROM users WHERE last_activity > datetime('now', '-7 days')"
            ) or 0
            stats["banned_users"] = await self.fetchval(
                "SELECT COUNT(*) FROM users WHERE is_banned = 1"
            ) or 0
            stats["total_files"] = await self.fetchval(
                "SELECT COUNT(*) FROM files WHERE is_deleted = 0"
            ) or 0
            stats["total_size"] = await self.fetchval(
                "SELECT COALESCE(SUM(file_size), 0) FROM files WHERE is_deleted = 0"
            ) or 0
            stats["total_downloads"] = await self.fetchval("SELECT COUNT(*) FROM downloads") or 0
            stats["total_uploads"] = await self.fetchval("SELECT COUNT(*) FROM files") or 0
            stats["today_users"] = await self.fetchval(
                "SELECT COUNT(*) FROM users WHERE DATE(joined_at) = DATE('now')"
            ) or 0
            stats["today_uploads"] = await self.fetchval(
                "SELECT COUNT(*) FROM files WHERE DATE(uploaded_at) = DATE('now')"
            ) or 0
            stats["today_downloads"] = await self.fetchval(
                "SELECT COUNT(*) FROM downloads WHERE DATE(downloaded_at) = DATE('now')"
            ) or 0
            stats["total_errors"] = await self.fetchval("SELECT COUNT(*) FROM error_logs") or 0
            try:
                stats["db_size"] = self.db_path.stat().st_size if self.db_path.exists() else 0
            except Exception:
                stats["db_size"] = 0
            return stats
        except Exception as e:
            log.error(f"get_stats error: {e}")
            return {}

    async def increment_daily_stat(self, stat_name: str, amount: int = 1) -> None:
        allowed = ["new_users", "active_users", "uploads", "downloads",
                   "total_files", "total_size", "errors", "backups"]
        if stat_name not in allowed:
            return
        try:
            today = date.today().isoformat()
            existing = await self.fetchone(
                "SELECT * FROM daily_stats WHERE stat_date = ?", (today,)
            )
            if not existing:
                await self.execute(
                    f"INSERT INTO daily_stats (stat_date, {stat_name}) VALUES (?, ?)",
                    (today, amount)
                )
            else:
                await self.execute(
                    f"UPDATE daily_stats SET {stat_name} = {stat_name} + ? WHERE stat_date = ?",
                    (amount, today)
                )
        except Exception as e:
            log.error(f"increment_daily_stat error: {e}")

    async def get_daily_stats(self, days: int = 7) -> List[Dict[str, Any]]:
        return await self.fetchall(
            """
            SELECT * FROM daily_stats 
            WHERE stat_date >= date('now', '-' || ? || ' days')
            ORDER BY stat_date DESC
            """,
            (days,)
        )

    # ═══════════════════════════════════════════════════════════════════════
    # 🚦 RATE LIMIT OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════

    async def check_rate_limit(self, user_id: int, max_per_minute: int = 10) -> Tuple[bool, int]:
        try:
            row = await self.fetchone("SELECT * FROM rate_limits WHERE user_id = ?", (user_id,))
            if not row:
                await self.execute(
                    """
                    INSERT INTO rate_limits 
                    (user_id, request_count, window_start, last_request)
                    VALUES (?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """,
                    (user_id,)
                )
                return True, 0
            if row["muted_until"]:
                try:
                    muted_until = datetime.fromisoformat(row["muted_until"])
                    if muted_until > datetime.now():
                        remaining = int((muted_until - datetime.now()).total_seconds())
                        return False, remaining
                except Exception:
                    pass
            try:
                window_start = datetime.fromisoformat(row["window_start"])
            except Exception:
                try:
                    window_start = datetime.strptime(row["window_start"], "%Y-%m-%d %H:%M:%S")
                except Exception:
                    window_start = datetime.now()
            elapsed = (datetime.now() - window_start).total_seconds()
            if elapsed > 60:
                await self.execute(
                    """
                    UPDATE rate_limits 
                    SET request_count = 1,
                        window_start = CURRENT_TIMESTAMP,
                        last_request = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                    """,
                    (user_id,)
                )
                return True, 0
            if row["request_count"] >= max_per_minute:
                remaining = int(60 - elapsed)
                return False, max(remaining, 1)
            await self.execute(
                """
                UPDATE rate_limits 
                SET request_count = request_count + 1,
                    last_request = CURRENT_TIMESTAMP
                WHERE user_id = ?
                """,
                (user_id,)
            )
            return True, 0
        except Exception as e:
            log.error(f"check_rate_limit error: {e}")
            return True, 0

    async def add_spam_warning(self, user_id: int) -> int:
        try:
            await self.execute(
                """
                INSERT INTO rate_limits (user_id, spam_warnings)
                VALUES (?, 1)
                ON CONFLICT(user_id) DO UPDATE SET
                    spam_warnings = spam_warnings + 1
                """,
                (user_id,)
            )
            warnings = await self.fetchval(
                "SELECT spam_warnings FROM rate_limits WHERE user_id = ?", (user_id,)
            )
            return warnings or 0
        except Exception as e:
            log.error(f"add_spam_warning error: {e}")
            return 0

    async def mute_user(self, user_id: int, duration_seconds: int = 3600) -> None:
        try:
            muted_until = (datetime.now() + timedelta(seconds=duration_seconds)).isoformat()
            await self.execute(
                """
                INSERT INTO rate_limits (user_id, muted_until)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    muted_until = excluded.muted_until,
                    spam_warnings = 0
                """,
                (user_id, muted_until)
            )
        except Exception as e:
            log.error(f"mute_user error: {e}")

    # ═══════════════════════════════════════════════════════════════════════
    # 🧹 CLEANUP OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════

    async def cleanup_expired_files(self) -> int:
        try:
            result = await self.execute(
                """
                UPDATE files 
                SET is_deleted = 1, deleted_at = CURRENT_TIMESTAMP
                WHERE expires_at IS NOT NULL 
                  AND expires_at < datetime('now') 
                  AND is_deleted = 0
                """
            )
            if result > 0:
                log.info(f"Cleaned up {result} expired files")
            return result
        except Exception as e:
            log.error(f"cleanup_expired_files error: {e}")
            return 0

    async def cleanup_old_logs(self, days: int = 30) -> int:
        try:
            return await self.execute(
                "DELETE FROM logs WHERE created_at < datetime('now', '-' || ? || ' days')",
                (days,)
            )
        except Exception as e:
            log.error(f"cleanup_old_logs error: {e}")
            return 0

    async def cleanup_old_error_logs(self, days: int = 30) -> int:
        try:
            return await self.execute(
                "DELETE FROM error_logs WHERE created_at < datetime('now', '-' || ? || ' days')",
                (days,)
            )
        except Exception as e:
            log.error(f"cleanup_old_error_logs error: {e}")
            return 0

    async def cleanup_old_downloads(self, days: int = 90) -> int:
        try:
            return await self.execute(
                "DELETE FROM downloads WHERE downloaded_at < datetime('now', '-' || ? || ' days')",
                (days,)
            )
        except Exception as e:
            log.error(f"cleanup_old_downloads error: {e}")
            return 0

    async def cleanup_rate_limits(self) -> int:
        try:
            return await self.execute(
                """
                DELETE FROM rate_limits 
                WHERE last_request < datetime('now', '-1 hour')
                  AND (muted_until IS NULL OR muted_until < datetime('now'))
                """
            )
        except Exception as e:
            log.error(f"cleanup_rate_limits error: {e}")
            return 0

    async def run_full_cleanup(self) -> Dict[str, int]:
        log.info(f"{Colors.info('🧹')} Running full cleanup...")
        result = {
            "expired_files": await self.cleanup_expired_files(),
            "old_logs": await self.cleanup_old_logs(30),
            "old_errors": await self.cleanup_old_error_logs(30),
            "old_downloads": await self.cleanup_old_downloads(90),
            "rate_limits": await self.cleanup_rate_limits(),
        }
        total = sum(result.values())
        if total > 0:
            log.info(f"{Colors.success('✅')} Cleanup done: {result}")
        return result

    async def health_check(self) -> Dict[str, Any]:
        result = {"connected": False, "response_time_ms": 0, "db_size": 0, "error": None}
        try:
            start = time.time()
            await self.fetchval("SELECT 1")
            elapsed = (time.time() - start) * 1000
            result["connected"] = True
            result["response_time_ms"] = round(elapsed, 2)
            try:
                result["db_size"] = self.db_path.stat().st_size if self.db_path.exists() else 0
            except Exception:
                result["db_size"] = 0
        except Exception as e:
            result["error"] = str(e)
        return result


# ═══════════════════════════════════════════════════════════════════════════
# 🌍 GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

db = Database()


# ═══════════════════════════════════════════════════════════════════════════
# 🚀 INIT HELPER
# ═══════════════════════════════════════════════════════════════════════════

async def init_database() -> Database:
    log.info(f"{Colors.info('🚀')} Initializing SQLite database...")
    await db.connect()
    await db.create_tables()
    await db.insert_default_settings()
    loaded = await db.load_settings()
    settings.load_from_db(loaded)
    log.info(f"{Colors.success('✅')} SQLite database ready")
    return db


async def close_database() -> None:
    await db.disconnect()


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = ["Database", "db", "init_database", "close_database"]


if __name__ == "__main__":
    async def _test():
        await db.connect()
        await db.create_tables()
        await db.insert_default_settings()
        await db.disconnect()
        print("✅ Test complete")
    asyncio.run(_test())