import os
import sys
import json
import time
import logging
import platform
import subprocess
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Union, List, Dict, Tuple
from functools import lru_cache

# Third-party
try:
    from dotenv import load_dotenv
except ImportError:
    print("❌ ERROR: python-dotenv install nahi hai!")
    print("   Solution: pip install python-dotenv")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════
# 📂 PATHS SETUP
# ═══════════════════════════════════════════════════════════════════════════

# Base directory — jahan yeh config.py file hai
BASE_DIR: Path = Path(__file__).resolve().parent

# .env file ka path
ENV_FILE: Path = BASE_DIR / ".env"

# .env.example file ka path (reference ke liye)
ENV_EXAMPLE_FILE: Path = BASE_DIR / ".env.example"

# Logs folder
LOGS_DIR: Path = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True, parents=True)

# Backups temp folder
BACKUP_TEMP_DIR: Path = BASE_DIR / "backups"
BACKUP_TEMP_DIR.mkdir(exist_ok=True, parents=True)

# Downloads temp folder
DOWNLOADS_TEMP_DIR: Path = BASE_DIR / "downloads"
DOWNLOADS_TEMP_DIR.mkdir(exist_ok=True, parents=True)

# Cache folder
CACHE_DIR: Path = BASE_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True, parents=True)

# Data folder (SQLite, JSON files ke liye)
DATA_DIR: Path = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True, parents=True)

# Sessions folder (agar Pyrogram/Telethon use karo)
SESSIONS_DIR: Path = BASE_DIR / "sessions"
SESSIONS_DIR.mkdir(exist_ok=True, parents=True)

# Temp folder
TEMP_DIR: Path = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True, parents=True)


# ═══════════════════════════════════════════════════════════════════════════
# 🔄 LOAD .env FILE
# ═══════════════════════════════════════════════════════════════════════════

if not ENV_FILE.exists():
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  ❌  ERROR: .env file nahi mili!                         ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print(f"  Expected path : {ENV_FILE}")
    print()
    print("  SOLUTION:")
    print("  1. Terminal mein jao: cd " + str(BASE_DIR))
    print("  2. Command chalao: cp .env.example .env")
    print("  3. .env file kholo aur apni values bharo")
    print("  4. Phir bot start karo")
    print()
    sys.exit(1)

# .env file load karo (override=True matlab .env ki values system env ko override karengi)
load_dotenv(dotenv_path=ENV_FILE, override=True)


# ═══════════════════════════════════════════════════════════════════════════
# 🛠️ HELPER FUNCTIONS — Env values safely nikalne ke liye
# ═══════════════════════════════════════════════════════════════════════════

def get_env(
    key: str,
    default: Optional[str] = None,
    required: bool = False,
    strip: bool = True
) -> Optional[str]:
    """
    .env se string value nikalta hai.
    
    Parameters
    ----------
    key : str
        Environment variable ka naam (e.g. "BOT_TOKEN")
    default : str, optional
        Agar value nahi mili toh yeh return karega
    required : bool
        True hone pe agar value nahi mili toh program exit ho jayega
    strip : bool
        True hone pe value ke aage-peeche ke spaces hata dega
    
    Returns
    -------
    str or None
    
    Examples
    --------
    >>> get_env("BOT_TOKEN")
    '123456:ABC...'
    
    >>> get_env("MISSING_KEY", "default_value")
    'default_value'
    
    >>> get_env("CRITICAL_KEY", required=True)
    [Program exits if not found]
    """
    value = os.getenv(key, default)
    
    if value is not None and strip and isinstance(value, str):
        value = value.strip()
    
    if required and (value is None or value == ""):
        print()
        print("╔══════════════════════════════════════════════════════════╗")
        print(f"║  ❌  FATAL: Required env variable missing                 ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print()
        print(f"  Variable : {key}")
        print(f"  File     : {ENV_FILE}")
        print()
        print(f"  SOLUTION: .env file mein '{key}=...' add karo")
        print()
        sys.exit(1)
    
    return value


def get_int(
    key: str,
    default: int = 0,
    required: bool = False,
    min_val: Optional[int] = None,
    max_val: Optional[int] = None
) -> int:
    """
    Env variable ko integer mein convert karta hai.
    
    Parameters
    ----------
    key : str
        Environment variable ka naam
    default : int
        Agar value nahi mili toh yeh return karega
    required : bool
        True hone pe value zaroori hai
    min_val : int, optional
        Minimum allowed value
    max_val : int, optional
        Maximum allowed value
    
    Returns
    -------
    int
    """
    value = get_env(key, None, required)
    
    if value is None or value == "":
        return default
    
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        print(f"⚠️  WARNING: '{key}' ka value integer nahi hai: '{value}'")
        print(f"   Default use kar raha hoon: {default}")
        return default
    
    if min_val is not None and int_value < min_val:
        print(f"⚠️  WARNING: '{key}' value {int_value} < min {min_val}")
        print(f"   Min value use kar raha hoon: {min_val}")
        return min_val
    
    if max_val is not None and int_value > max_val:
        print(f"⚠️  WARNING: '{key}' value {int_value} > max {max_val}")
        print(f"   Max value use kar raha hoon: {max_val}")
        return max_val
    
    return int_value


def get_float(
    key: str,
    default: float = 0.0,
    required: bool = False
) -> float:
    """Env variable ko float mein convert karta hai"""
    value = get_env(key, None, required)
    
    if value is None or value == "":
        return default
    
    try:
        return float(value)
    except (ValueError, TypeError):
        print(f"⚠️  WARNING: '{key}' ka value float nahi hai: '{value}'")
        print(f"   Default use kar raha hoon: {default}")
        return default


def get_bool(key: str, default: bool = False) -> bool:
    """
    Env variable ko boolean mein convert karta hai.
    
    True values  : true, 1, yes, on, haan, ha, y, t
    False values : false, 0, no, off, nahi, na, n, f
    """
    value = get_env(key, None)
    
    if value is None or value == "":
        return default
    
    value_lower = value.lower().strip()
    
    true_values = ("true", "1", "yes", "on", "haan", "ha", "y", "t", "enable", "enabled")
    false_values = ("false", "0", "no", "off", "nahi", "na", "n", "f", "disable", "disabled")
    
    if value_lower in true_values:
        return True
    if value_lower in false_values:
        return False
    
    print(f"⚠️  WARNING: '{key}' ka value boolean nahi hai: '{value}'")
    print(f"   Default use kar raha hoon: {default}")
    return default


def get_list(
    key: str,
    separator: str = ",",
    default: Optional[List[str]] = None,
    strip: bool = True
) -> List[str]:
    """
    Env variable ko list mein convert karta hai.
    
    Examples
    --------
    .env: ALLOWED_EXTENSIONS=pdf,zip,rar,apk
    >>> get_list("ALLOWED_EXTENSIONS")
    ['pdf', 'zip', 'rar', 'apk']
    """
    value = get_env(key, None)
    
    if value is None or value == "":
        return default or []
    
    items = value.split(separator)
    
    if strip:
        items = [item.strip() for item in items]
    
    # Empty strings hata do
    items = [item for item in items if item]
    
    return items


def get_int_list(
    key: str,
    separator: str = ",",
    default: Optional[List[int]] = None
) -> List[int]:
    """Env variable ko integer list mein convert karta hai"""
    items = get_list(key, separator)
    
    if not items:
        return default or []
    
    result = []
    for item in items:
        try:
            result.append(int(item))
        except ValueError:
            print(f"⚠️  WARNING: '{item}' integer nahi hai, skip kar raha hoon")
    
    return result


def get_json(
    key: str,
    default: Optional[Any] = None
) -> Any:
    """Env variable ko JSON parse karta hai"""
    value = get_env(key, None)
    
    if value is None or value == "":
        return default
    
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        print(f"⚠️  WARNING: '{key}' ka JSON invalid hai: {e}")
        print(f"   Default use kar raha hoon: {default}")
        return default


# ═══════════════════════════════════════════════════════════════════════════
# 🔐 BOOTSTRAP CONFIG — Yeh .env se aati hain (bot start hone se pehle chahiye)
# ═══════════════════════════════════════════════════════════════════════════

class Bootstrap:
    """
    Bootstrap settings — sirf woh cheezein jo bot start hone se pehle chahiye.
    
    Yeh settings bot ke andar se CHANGE NAHI ho sakti.
    Kyunki:
    1. Bot Token — bot isi se start hota hai
    2. API ID/Hash — Telegram se connect hone ke liye
    3. DB credentials — database se connect hone ke liye
    4. Owner ID — pehla admin kaun hai
    5. Encryption Key — sensitive data ke liye
    
    Baaki saari settings DATABASE mein hain — admin panel se change hongi.
    """
    
    # ─────────────────────────────────────────────────────────────────────
    # 🤖 BOT INFORMATION
    # ─────────────────────────────────────────────────────────────────────
    
    # @BotFather se milta hai
    BOT_TOKEN: str = get_env("BOT_TOKEN", required=True)
    
    # Bot ka display name (default)
    BOT_NAME: str = get_env("BOT_NAME", "Isukobit")
    
    # Bot ka username (@ ke bina)
    BOT_USERNAME: str = get_env("BOT_USERNAME", "IsukobitBot")
    
    # Bot ki version
    BOT_VERSION: str = "1.0.0"
    
    # ─────────────────────────────────────────────────────────────────────
    # 🔐 TELEGRAM API CREDENTIALS
    # ─────────────────────────────────────────────────────────────────────
    
    # my.telegram.org se milta hai
    API_ID: int = get_int("API_ID", 0, required=True, min_val=1)
    API_HASH: str = get_env("API_HASH", required=True)
    
    # Session name (agar Pyrogram/Telethon use karo)
    SESSION_NAME: str = get_env("SESSION_NAME", "isukobit_session")
    
    # ─────────────────────────────────────────────────────────────────────
    # 👑 OWNER & ADMIN
    # ─────────────────────────────────────────────────────────────────────
    
    # Owner ka Telegram numeric ID
    OWNER_ID: int = get_int("OWNER_ID", 0, required=True, min_val=1)
    
    # Extra admins ke IDs (baad mein admin panel se bhi add kar sakte ho)
    ADMIN_IDS: List[int] = get_int_list("ADMIN_IDS", default=[])
    
    # ─────────────────────────────────────────────────────────────────────
    # 🗄️ DATABASE
    # ─────────────────────────────────────────────────────────────────────
    
    DB_HOST: str = get_env("DB_HOST", "localhost")
    DB_PORT: int = get_int("DB_PORT", 3306, min_val=1, max_val=65535)
    DB_NAME: str = get_env("DB_NAME", "isukobit_db")
    DB_USER: str = get_env("DB_USER", "isukobit_user")
    DB_PASSWORD: str = get_env("DB_PASSWORD", required=True)
    
    # Connection pool settings
    DB_POOL_SIZE: int = get_int("DB_POOL_SIZE", 5, min_val=1, max_val=50)
    DB_MAX_OVERFLOW: int = get_int("DB_MAX_OVERFLOW", 10, min_val=0, max_val=100)
    DB_POOL_RECYCLE: int = get_int("DB_POOL_RECYCLE", 3600, min_val=60)
    DB_POOL_PRE_PING: bool = get_bool("DB_POOL_PRE_PING", True)
    DB_ECHO: bool = get_bool("DB_ECHO", False)
    
    # ─────────────────────────────────────────────────────────────────────
    # 🔐 ENCRYPTION
    # ─────────────────────────────────────────────────────────────────────
    
    # Fernet key — sensitive data encrypt karne ke liye
    ENCRYPTION_KEY: str = get_env("ENCRYPTION_KEY", required=True)
    
    # ─────────────────────────────────────────────────────────────────────
    # 📝 LOGGING
    # ─────────────────────────────────────────────────────────────────────
    
    LOG_LEVEL: str = get_env("LOG_LEVEL", "INFO").upper()
    LOG_FILE: str = get_env("LOG_FILE", str(LOGS_DIR / "isukobit.log"))
    LOG_MAX_SIZE: int = get_int("LOG_MAX_SIZE", 10 * 1024 * 1024)  # 10 MB
    LOG_BACKUP_COUNT: int = get_int("LOG_BACKUP_COUNT", 5)
    
    # ─────────────────────────────────────────────────────────────────────
    # 🌐 SERVER INFO
    # ─────────────────────────────────────────────────────────────────────
    
    @staticmethod
    def get_server_info() -> Dict[str, Any]:
        """Server ki info return karta hai"""
        try:
            import psutil
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            
            return {
                "platform": platform.system(),
                "platform_release": platform.release(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "hostname": platform.node(),
                "cpu_count": psutil.cpu_count(),
                "ram_total_gb": round(ram.total / (1024 ** 3), 2),
                "ram_available_gb": round(ram.available / (1024 ** 3), 2),
                "ram_percent": ram.percent,
                "disk_total_gb": round(disk.total / (1024 ** 3), 2),
                "disk_free_gb": round(disk.free / (1024 ** 3), 2),
                "disk_percent": disk.percent,
            }
        except ImportError:
            return {
                "platform": platform.system(),
                "python_version": platform.python_version(),
                "hostname": platform.node(),
            }
    
    @staticmethod
    def get_uptime() -> str:
        """Server ka uptime return karta hai"""
        try:
            with open("/proc/uptime", "r") as f:
                uptime_seconds = float(f.readline().split()[0])
            
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            parts = []
            if days > 0:
                parts.append(f"{days}d")
            if hours > 0:
                parts.append(f"{hours}h")
            parts.append(f"{minutes}m")
            
            return " ".join(parts)
        except Exception:
            return "Unknown"


# ═══════════════════════════════════════════════════════════════════════════
# ⚙️ DEFAULT SETTINGS — Yeh database mein store hongi
# ═══════════════════════════════════════════════════════════════════════════
#
# Yeh sirf DEFAULT values hain. Pehli baar bot start hone pe database mein
# daali jayengi. Uske baad ADMIN PANEL se change ho sakti hain.
#
# ═══════════════════════════════════════════════════════════════════════════

DEFAULT_SETTINGS: Dict[str, Any] = {
    
    # ─────────────────────────────────────────────────────────────────────
    # 🤖 BOT INFO
    # ─────────────────────────────────────────────────────────────────────
    "bot_name": Bootstrap.BOT_NAME,
    "bot_username": Bootstrap.BOT_USERNAME,
    "bot_version": "1.0.0",
    "bot_description": "Telegram File Store Bot",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📢 CHANNELS
    # ─────────────────────────────────────────────────────────────────────
    "storage_channel_id": 0,
    "storage_channel_name": "",
    "backup_channel_id": 0,
    "backup_channel_name": "",
    "log_channel_id": 0,
    "log_channel_name": "",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📢 FORCE JOIN
    # ─────────────────────────────────────────────────────────────────────
    "force_join_enabled": False,
    "force_join_1": "",
    "force_join_1_name": "",
    "force_join_2": "",
    "force_join_2_name": "",
    "force_join_3": "",
    "force_join_3_name": "",
    "force_join_verify_button": True,
    "force_join_message": (
        "🔒 <b>Access Denied!</b>\n\n"
        "Bot use karne ke liye pehle neeche diye gaye channels "
        "ko join karein, phir <b>✅ Verify</b> button dabayein.\n\n"
        "Join karne ke baad wapas aake verify karein."
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # 🎨 UI SETTINGS
    # ─────────────────────────────────────────────────────────────────────
    "default_language": "hinglish",
    "buttons_style": "both",              # inline / reply / both
    "theme": "modern",                    # modern / simple / professional / anime
    "show_emoji": True,
    "show_file_size": True,
    "show_upload_date": True,
    "show_download_count": True,
    "show_uploader_name": True,
    
    # ─────────────────────────────────────────────────────────────────────
    # 📁 FILE SETTINGS
    # ─────────────────────────────────────────────────────────────────────
    "max_file_size": 52428800,            # 50 MB in bytes
    "allowed_extensions": [],             # Khaali list = sab allowed
    "blocked_extensions": [],             # Yeh extensions block
    "file_code_prefix": "ISU",
    "file_code_length": 6,
    "max_files_per_user": 0,              # 0 = unlimited
    "max_files_per_day_per_user": 0,      # 0 = unlimited
    "batch_max_files": 50,                # Ek batch mein max files
    "batch_session_minutes": 30,          # Batch session ki duration (minutes)
    "queue_step_delay": 1.5,              # Queue: har Telegram step ke beech gap (sec)
    "queue_item_delay": 1.0,              # Queue: har file ke beech gap (sec)
    "link_expiry_hours": 0,               # 0 = never expire
    "user_locked_links": True,            # Sirf uploader download kar sake
    "allow_duplicate_files": False,
    "auto_delete_after_days": 0,          # 0 = never
    
    # ─────────────────────────────────────────────────────────────────────
    # 🔐 SECURITY
    # ─────────────────────────────────────────────────────────────────────
    "rate_limit_per_minute": 10,
    "rate_limit_upload_per_hour": 30,
    "rate_limit_download_per_hour": 100,
    "spam_warn_limit": 5,
    "spam_mute_duration": 3600,           # 1 hour in seconds
    "anti_spam_enabled": True,
    "anti_flood_enabled": True,
    "block_forward": True,                # File forward nahi kar sakte
    "protect_content": True,              # Content protection
    "require_join_for_download": True,
    
    # ─────────────────────────────────────────────────────────────────────
    # 💾 BACKUP
    # ─────────────────────────────────────────────────────────────────────
    "backup_enabled": True,
    "backup_interval_hours": 24,          # Daily
    "backup_retention": 7,                # Last 7 backups
    "backup_temp_dir": str(BACKUP_TEMP_DIR),
    "backup_include_files": False,        # Sirf DB dump
    "backup_compress": True,
    "backup_notify_admin": True,
    "backup_verify_after": True,
    
    # ─────────────────────────────────────────────────────────────────────
    # 🛠️ MAINTENANCE
    # ─────────────────────────────────────────────────────────────────────
    "maintenance_mode": False,
    "maintenance_message": (
        "🛠️ <b>Bot abhi maintenance mein hai</b>\n\n"
        "Thodi der baad try karein. Aapki patience ke liye shukriya! 🙏\n\n"
        "Updates ke liye join karein: @IsukobitUpdates"
    ),
    "maintenance_allow_admins": True,
    
    # ─────────────────────────────────────────────────────────────────────
    # 📜 TERMS & PRIVACY
    # ─────────────────────────────────────────────────────────────────────
    "terms_url": "",
    "privacy_url": "",
    "dmca_url": "",
    "show_terms_on_start": False,
    
    # ─────────────────────────────────────────────────────────────────────
    # 📞 CONTACT & SUPPORT
    # ─────────────────────────────────────────────────────────────────────
    "support_username": "",
    "update_channel": "",
    "owner_username": "",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🎁 WELCOME MESSAGES
    # ─────────────────────────────────────────────────────────────────────
    "welcome_sticker": "",
    "welcome_message": (
        "🎉 <b>Isukobit mein aapka swagat hai!</b>\n\n"
        "Main ek File Store Bot hoon. Aap mere through files "
        "upload, search aur download kar sakte hain.\n\n"
        "📌 <b>Quick Commands:</b>\n"
        "• /start — Main menu\n"
        "• /help — Madad\n"
        "• /upload — File upload karo\n"
        "• /myfiles — Apni files dekho\n"
        "• /search — File dhundho\n\n"
        "Neeche ke buttons se shuru karein 👇"
    ),
    "welcome_back_message": (
        "🎉 <b>Wapas swagat, {name}!</b>\n\n"
        "Aap kya karna chahte hain?\n"
        "Neeche ke buttons se select karein 👇"
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # 📊 STATISTICS
    # ─────────────────────────────────────────────────────────────────────
    "bot_start_time": 0,
    "total_users_count": 0,
    "total_files_count": 0,
    "total_downloads_count": 0,
    "total_uploads_count": 0,
    
    # ─────────────────────────────────────────────────────────────────────
    # 🚀 PERFORMANCE
    # ─────────────────────────────────────────────────────────────────────
    "workers": 1,
    "request_timeout": 30,
    "max_retries": 3,
    "retry_delay": 5,
    "cache_ttl": 300,
    "session_timeout": 1800,
    
    # ─────────────────────────────────────────────────────────────────────
    # 📂 FOLDER SYSTEM
    # ─────────────────────────────────────────────────────────────────────
    "folders_enabled": True,
    "max_folders_per_user": 50,
    "max_folder_depth": 5,
    "default_folder_name": "My Files",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🔍 SEARCH
    # ─────────────────────────────────────────────────────────────────────
    "search_enabled": True,
    "search_results_per_page": 10,
    "search_min_query_length": 2,
    "inline_search_enabled": True,
    
    # ─────────────────────────────────────────────────────────────────────
    # 💎 PREMIUM SYSTEM
    # ─────────────────────────────────────────────────────────────────────
    "premium_enabled": False,
    "premium_max_file_size": 2097152000,  # 2 GB
    "premium_unlimited_uploads": True,
    "premium_no_ads": True,
    "premium_price_stars": 100,
    "premium_duration_days": 30,
    
    # ─────────────────────────────────────────────────────────────────────
    # 📊 LOGGING
    # ─────────────────────────────────────────────────────────────────────
    "log_new_user": True,
    "log_file_upload": True,
    "log_file_delete": True,
    "log_file_download": True,
    "log_user_ban": True,
    "log_admin_actions": True,
    "log_errors": True,
    "log_backup": True,
    "log_report_interval_seconds": 300,   # Log channel mein report kitne sec pe (0/300=5min, 10=har 10 sec)
    
    # ─────────────────────────────────────────────────────────────────────
    # 🎛️ ADMIN PANEL
    # ─────────────────────────────────────────────────────────────────────
    "admin_page_size": 10,
    "broadcast_delay_seconds": 0.05,
    "broadcast_batch_size": 100,
    "broadcast_max_retries": 3,
    "allow_admin_add_files": True,
    "allow_admin_delete_any": True,
    
    # ─────────────────────────────────────────────────────────────────────
    # ⚡ ERROR & RECOVERY
    # ─────────────────────────────────────────────────────────────────────
    "auto_retry_failed": True,
    "db_reconnect_attempts": 5,
    "telegram_reconnect_attempts": 5,
    "notify_admin_on_error": True,
    "error_throttle_seconds": 60,
    
    # ─────────────────────────────────────────────────────────────────────
    # 🌐 EXTERNAL SERVICES
    # ─────────────────────────────────────────────────────────────────────
    "google_drive_enabled": False,
    "s3_enabled": False,
    "shortlink_enabled": False,
    "qr_code_enabled": True,
    "web_dashboard_enabled": False,
    "rest_api_enabled": False,
}


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 CONSTANTS — Fixed values jo code mein use hote hain
# ═══════════════════════════════════════════════════════════════════════════

class Constants:
    """Fixed constants jo kabhi change nahi hote"""
    
    # ─────────────────────────────────────────────────────────────────────
    # 📁 PATHS
    # ─────────────────────────────────────────────────────────────────────
    BASE_DIR = BASE_DIR
    LOGS_DIR = LOGS_DIR
    BACKUP_TEMP_DIR = BACKUP_TEMP_DIR
    DOWNLOADS_TEMP_DIR = DOWNLOADS_TEMP_DIR
    CACHE_DIR = CACHE_DIR
    DATA_DIR = DATA_DIR
    SESSIONS_DIR = SESSIONS_DIR
    TEMP_DIR = TEMP_DIR
    
    # ─────────────────────────────────────────────────────────────────────
    # 📏 FILE SIZES
    # ─────────────────────────────────────────────────────────────────────
    BYTE = 1
    KB = 1024
    MB = 1024 * 1024
    GB = 1024 * 1024 * 1024
    TB = 1024 * 1024 * 1024 * 1024
    
    # ─────────────────────────────────────────────────────────────────────
    # 📁 FOLDER NAMES
    # ─────────────────────────────────────────────────────────────────────
    DEFAULT_FOLDER = "root"
    TRASH_FOLDER = "_trash"
    TEMP_FOLDER = "_temp"
    
    # ─────────────────────────────────────────────────────────────────────
    # ⏱️ TIME CONSTANTS
    # ─────────────────────────────────────────────────────────────────────
    SECOND = 1
    MINUTE = 60
    HOUR = 3600
    DAY = 86400
    WEEK = 604800
    MONTH = 2592000
    YEAR = 31536000
    
    CACHE_TTL = 300
    SESSION_TIMEOUT = 1800
    RATE_LIMIT_WINDOW = 60
    
    # ─────────────────────────────────────────────────────────────────────
    # 🎨 EMOJIS — UI ke liye
    # ─────────────────────────────────────────────────────────────────────
    EMOJI_SUCCESS = "✅"
    EMOJI_ERROR = "❌"
    EMOJI_WARNING = "⚠️"
    EMOJI_INFO = "ℹ️"
    EMOJI_LOADING = "⏳"
    
    EMOJI_FILE = "📄"
    EMOJI_FOLDER = "📁"
    EMOJI_FILES = "📁"
    EMOJI_LOCK = "🔒"
    EMOJI_UNLOCK = "🔓"
    EMOJI_KEY = "🔑"
    
    EMOJI_SEARCH = "🔍"
    EMOJI_UPLOAD = "📤"
    EMOJI_DOWNLOAD = "📥"
    EMOJI_SHARE = "🔗"
    EMOJI_LINK = "🔗"
    EMOJI_QR = "📱"
    
    EMOJI_ADMIN = "👑"
    EMOJI_USER = "👤"
    EMOJI_USERS = "👥"
    EMOJI_STATS = "📊"
    EMOJI_CHART = "📈"
    
    EMOJI_BACKUP = "💾"
    EMOJI_SETTINGS = "⚙️"
    EMOJI_TOOLS = "🔧"
    EMOJI_SECURITY = "🛡️"
    
    EMOJI_STAR = "⭐"
    EMOJI_PREMIUM = "💎"
    EMOJI_GIFT = "🎁"
    EMOJI_ROCKET = "🚀"
    EMOJI_FIRE = "🔥"
    EMOJI_HEART = "❤️"
    EMOJI_THUMBSUP = "👍"
    
    EMOJI_CALENDAR = "📅"
    EMOJI_CLOCK = "🕐"
    EMOJI_TIME = "⏰"
    
    EMOJI_TRASH = "🗑️"
    EMOJI_RECYCLE = "♻️"
    EMOJI_RESTORE = "↩️"
    
    EMOJI_BACK = "⬅️"
    EMOJI_NEXT = "➡️"
    EMOJI_UP = "⬆️"
    EMOJI_DOWN = "⬇️"
    EMOJI_REFRESH = "🔄"
    EMOJI_CLOSE = "❌"
    EMOJI_CHECK = "✅"
    
    EMOJI_MENU = "📋"
    EMOJI_HOME = "🏠"
    EMOJI_HELP = "❓"
    EMOJI_ABOUT = "ℹ️"
    
    EMOJI_LANGUAGE = "🌍"
    EMOJI_TRANSLATE = "🔤"
    
    EMOJI_DATABASE = "🗄️"
    EMOJI_SERVER = "🖥️"
    EMOJI_CLOUD = "☁️"
    
    EMOJI_REPORT = "🚨"
    EMOJI_BAN = "🚫"
    EMOJI_WARN = "⚠️"
    EMOJI_MUTE = "🔇"
    
    EMOJI_CHANNEL = "📢"
    EMOJI_BROADCAST = "📣"
    EMOJI_NOTIFICATION = "🔔"
    
    EMOJI_PDF = "📕"
    EMOJI_DOC = "📘"
    EMOJI_XLS = "📗"
    EMOJI_PPT = "📙"
    EMOJI_ZIP = "🗜️"
    EMOJI_IMAGE = "🖼️"
    EMOJI_VIDEO = "🎬"
    EMOJI_AUDIO = "🎵"
    EMOJI_APK = "📦"
    EMOJI_CODE = "💻"
    EMOJI_TEXT = "📝"
    
    # ─────────────────────────────────────────────────────────────────────
    # 📊 DATABASE TABLE NAMES
    # ─────────────────────────────────────────────────────────────────────
    TABLE_USERS = "users"
    TABLE_FILES = "files"
    TABLE_FOLDERS = "folders"
    TABLE_ADMINS = "admins"
    TABLE_BANNED = "banned_users"
    TABLE_SETTINGS = "settings"
    TABLE_LOGS = "logs"
    TABLE_BACKUPS = "backups"
    TABLE_BROADCASTS = "broadcasts"
    TABLE_DOWNLOADS = "downloads"
    TABLE_ERRORS = "error_logs"
    TABLE_RATE_LIMITS = "rate_limits"
    TABLE_PREMIUM = "premium_users"
    TABLE_STATS = "daily_stats"
    
    # ─────────────────────────────────────────────────────────────────────
    # 🌍 LANGUAGES
    # ─────────────────────────────────────────────────────────────────────
    LANGUAGES = ["hinglish", "english", "nepali", "latin"]
    DEFAULT_LANGUAGE = "hinglish"
    
    LANGUAGE_FLAGS = {
        "hinglish": "🇮🇳",
        "english": "🇬🇧",
        "nepali": "🇳🇵",
        "latin": "🏛️",
    }
    
    LANGUAGE_NAMES = {
        "hinglish": "Hinglish",
        "english": "English",
        "nepali": "नेपाली",
        "latin": "Latina",
    }
    
    # ─────────────────────────────────────────────────────────────────────
    # 📄 FILE TYPES
    # ─────────────────────────────────────────────────────────────────────
    COMMON_EXTENSIONS = [
        # Documents
        "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
        "txt", "rtf", "odt", "ods", "odp", "csv",
        
        # Archives
        "zip", "rar", "7z", "tar", "gz", "bz2", "xz",
        
        # Applications
        "apk", "exe", "msi", "deb", "rpm", "dmg", "appimage",
        
        # Images
        "jpg", "jpeg", "png", "gif", "webp", "svg", "bmp",
        "tiff", "ico", "heic", "raw",
        
        # Videos
        "mp4", "mkv", "avi", "mov", "webm", "flv", "wmv",
        "m4v", "mpg", "mpeg", "3gp",
        
        # Audio
        "mp3", "wav", "ogg", "flac", "m4a", "aac", "wma", "opus",
        
        # Code
        "json", "xml", "html", "css", "js", "ts", "py", "java",
        "c", "cpp", "h", "php", "rb", "go", "rs", "sql", "sh",
        
        # Others
        "epub", "mobi", "azw3", "torrent", "iso", "img",
    ]
    
    FILE_TYPE_MAP = {
        # Documents
        "pdf": EMOJI_PDF,
        "doc": EMOJI_DOC,
        "docx": EMOJI_DOC,
        "xls": EMOJI_XLS,
        "xlsx": EMOJI_XLS,
        "ppt": EMOJI_PPT,
        "pptx": EMOJI_PPT,
        "txt": EMOJI_TEXT,
        "csv": EMOJI_TEXT,
        
        # Archives
        "zip": EMOJI_ZIP,
        "rar": EMOJI_ZIP,
        "7z": EMOJI_ZIP,
        "tar": EMOJI_ZIP,
        "gz": EMOJI_ZIP,
        
        # Media
        "jpg": EMOJI_IMAGE,
        "jpeg": EMOJI_IMAGE,
        "png": EMOJI_IMAGE,
        "gif": EMOJI_IMAGE,
        "webp": EMOJI_IMAGE,
        "mp4": EMOJI_VIDEO,
        "mkv": EMOJI_VIDEO,
        "avi": EMOJI_VIDEO,
        "mov": EMOJI_VIDEO,
        "mp3": EMOJI_AUDIO,
        "wav": EMOJI_AUDIO,
        "ogg": EMOJI_AUDIO,
        "flac": EMOJI_AUDIO,
        
        # Apps
        "apk": EMOJI_APK,
        "exe": EMOJI_APK,
        "msi": EMOJI_APK,
        
        # Code
        "py": EMOJI_CODE,
        "js": EMOJI_CODE,
        "html": EMOJI_CODE,
        "css": EMOJI_CODE,
        "json": EMOJI_CODE,
        "xml": EMOJI_CODE,
        "sql": EMOJI_CODE,
    }
    
    # ─────────────────────────────────────────────────────────────────────
    # 🎨 BUTTON TEXT LABELS
    # ─────────────────────────────────────────────────────────────────────
    BTN_UPLOAD = "📤 Upload File"
    BTN_MY_FILES = "📁 My Files"
    BTN_SEARCH = "🔍 Search"
    BTN_STATS = "📊 Statistics"
    BTN_SETTINGS = "⚙️ Settings"
    BTN_HELP = "❓ Help"
    BTN_ABOUT = "ℹ️ About"
    BTN_BACK = "⬅️ Back"
    BTN_HOME = "🏠 Home"
    BTN_CLOSE = "❌ Close"
    BTN_REFRESH = "🔄 Refresh"
    BTN_NEXT = "➡️ Next"
    BTN_PREV = "⬅️ Previous"
    BTN_VERIFY = "✅ Verify"
    BTN_JOIN = "📢 Join Channel"
    BTN_DOWNLOAD = "📥 Download"
    BTN_SHARE = "🔗 Share"
    BTN_DELETE = "🗑️ Delete"
    BTN_RENAME = "✏️ Rename"
    BTN_CANCEL = "❌ Cancel"
    BTN_CONFIRM = "✅ Confirm"
    
    # ─────────────────────────────────────────────────────────────────────
    # 🎯 CALLBACK DATA PATTERNS
    # ─────────────────────────────────────────────────────────────────────
    CB_MENU = "menu"
    CB_UPLOAD = "upload"
    CB_MY_FILES = "myfiles"
    CB_SEARCH = "search"
    CB_STATS = "stats"
    CB_HELP = "help"
    CB_ABOUT = "about"
    CB_BACK = "back"
    CB_HOME = "home"
    CB_CLOSE = "close"
    CB_REFRESH = "refresh"
    CB_VERIFY = "verify"
    CB_DOWNLOAD = "dl"
    CB_DELETE = "del"
    CB_CONFIRM = "confirm"
    CB_CANCEL = "cancel"
    CB_PAGE = "page"
    CB_FILE = "file"
    CB_FOLDER = "folder"
    CB_ADMIN = "admin"
    CB_SETTINGS = "settings"
    CB_LANGUAGE = "lang"
    CB_BAN = "ban"
    CB_UNBAN = "unban"
    CB_BROADCAST = "bc"
    CB_BACKUP = "backup"
    CB_MAINTENANCE = "maint"
    
    # ─────────────────────────────────────────────────────────────────────
    # 📝 REGEX PATTERNS
    # ─────────────────────────────────────────────────────────────────────
    import re as _re
    REGEX_FILE_CODE = _re.compile(r"^ISU-[A-Z0-9]{6}$")
    REGEX_USERNAME = _re.compile(r"^@[a-zA-Z0-9_]{5,32}$")
    REGEX_URL = _re.compile(r"^https?://.+")
    REGEX_TELEGRAM_LINK = _re.compile(r"^(https?://)?t\.me/.+")
    REGEX_CHANNEL_ID = _re.compile(r"^-100\d{10,}$")
    REGEX_USER_ID = _re.compile(r"^\d{6,15}$")
    del _re
    
    # ─────────────────────────────────────────────────────────────────────
    # ⚠️ ERROR MESSAGES (Internal use)
    # ─────────────────────────────────────────────────────────────────────
    ERR_FILE_TOO_LARGE = "File bahut badi hai"
    ERR_FILE_TYPE = "Yeh file type allowed nahi hai"
    ERR_RATE_LIMIT = "Aap bahut tez request bhej rahe hain"
    ERR_NOT_ADMIN = "Aap admin nahi hain"
    ERR_NOT_OWNER = "Yeh sirf owner ke liye hai"
    ERR_USER_BANNED = "Aap banned hain"
    ERR_FILE_NOT_FOUND = "File nahi mili"
    ERR_INVALID_CODE = "Invalid file code"
    ERR_ACCESS_DENIED = "Aap is file ko access nahi kar sakte"
    ERR_MAINTENANCE = "Bot maintenance mein hai"
    ERR_UNKNOWN = "Kuch gadbad ho gayi"


# ═══════════════════════════════════════════════════════════════════════════
# 🎨 COLORS — Terminal output colors
# ═══════════════════════════════════════════════════════════════════════════

class Colors:
    """Terminal colors — logs aur output ko readable banane ke liye"""
    
    # Reset
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    
    # Foreground
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright foreground
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Background
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    
    @staticmethod
    def colorize(text: str, color: str) -> str:
        """Text ko colorize karta hai"""
        return f"{color}{text}{Colors.RESET}"
    
    @staticmethod
    def success(text: str) -> str:
        return f"{Colors.BRIGHT_GREEN}{text}{Colors.RESET}"
    
    @staticmethod
    def error(text: str) -> str:
        return f"{Colors.BRIGHT_RED}{text}{Colors.RESET}"
    
    @staticmethod
    def warning(text: str) -> str:
        return f"{Colors.BRIGHT_YELLOW}{text}{Colors.RESET}"
    
    @staticmethod
    def info(text: str) -> str:
        return f"{Colors.BRIGHT_CYAN}{text}{Colors.RESET}"


# ═══════════════════════════════════════════════════════════════════════════
# 📝 LOGGING SETUP
# ═══════════════════════════════════════════════════════════════════════════

class ColorFormatter(logging.Formatter):
    """
    Custom log formatter jo console pe colorful output deta hai.
    """
    
    COLORS = {
        logging.DEBUG: Colors.BRIGHT_BLACK,
        logging.INFO: Colors.BRIGHT_CYAN,
        logging.WARNING: Colors.BRIGHT_YELLOW,
        logging.ERROR: Colors.BRIGHT_RED,
        logging.CRITICAL: Colors.BRIGHT_MAGENTA,
    }
    
    def format(self, record: logging.LogRecord) -> str:
        log_color = self.COLORS.get(record.levelno, Colors.RESET)
        
        # Time
        time_str = self.formatTime(record, "%H:%M:%S")
        
        # Level
        level_str = f"{log_color}{record.levelname:<8}{Colors.RESET}"
        
        # Name
        name_str = f"{Colors.DIM}{record.name}{Colors.RESET}"
        
        # Message
        msg = record.getMessage()
        
        # Return formatted
        return f"{Colors.CYAN}[{time_str}]{Colors.RESET} {level_str} {name_str}: {msg}"


def setup_logging() -> logging.Logger:
    """
    Bot ke liye complete logging setup karta hai.
    
    - Console pe colorful logs
    - File mein plain text logs (rotating)
    - Errors ke liye alag file
    
    Returns:
        logging.Logger
    """
    # Root logger
    logger = logging.getLogger("isukobit")
    logger.setLevel(getattr(logging, Bootstrap.LOG_LEVEL, logging.INFO))
    
    # Purane handlers clear karo
    logger.handlers.clear()
    
    # ─────────────────────────────────────────────────────────────────────
    # Console Handler
    # ─────────────────────────────────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(ColorFormatter())
    logger.addHandler(console_handler)
    
    # ─────────────────────────────────────────────────────────────────────
    # File Handler (Rotating)
    # ─────────────────────────────────────────────────────────────────────
    try:
        from logging.handlers import RotatingFileHandler
        
        log_path = Path(Bootstrap.LOG_FILE)
        log_path.parent.mkdir(exist_ok=True, parents=True)
        
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=Bootstrap.LOG_MAX_SIZE,
            backupCount=Bootstrap.LOG_BACKUP_COUNT,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        
        file_format = "[%(asctime)s] [%(levelname)-8s] [%(name)s] %(message)s"
        file_handler.setFormatter(logging.Formatter(file_format, datefmt="%Y-%m-%d %H:%M:%S"))
        
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"File logging setup failed: {e}")
    
    # ─────────────────────────────────────────────────────────────────────
    # Error File Handler (sirf errors)
    # ─────────────────────────────────────────────────────────────────────
    try:
        from logging.handlers import RotatingFileHandler
        
        error_log_path = LOGS_DIR / "errors.log"
        
        error_handler = RotatingFileHandler(
            error_log_path,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        
        error_format = "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] %(message)s"
        error_handler.setFormatter(logging.Formatter(error_format, datefmt="%Y-%m-%d %H:%M:%S"))
        
        logger.addHandler(error_handler)
    except Exception:
        pass  # Silent fail — error logging critical nahi hai
    
    return logger


# Global logger instance — saari files isko import karengi
log: logging.Logger = setup_logging()


# ═══════════════════════════════════════════════════════════════════════════
# ✅ VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

def validate_config() -> bool:
    """
    Saari bootstrap settings validate karta hai.
    
    Returns:
        True agar sab theek, warna False
    """
    errors: List[str] = []
    warnings: List[str] = []
    
    # ─────────────────────────────────────────────────────────────────────
    # 🤖 BOT TOKEN
    # ─────────────────────────────────────────────────────────────────────
    if not Bootstrap.BOT_TOKEN:
        errors.append("BOT_TOKEN missing — @BotFather se lo")
    elif ":" not in Bootstrap.BOT_TOKEN:
        errors.append("BOT_TOKEN format galat hai — should be '123456:ABC-DEF...'")
    elif len(Bootstrap.BOT_TOKEN) < 40:
        warnings.append("BOT_TOKEN chhota lag raha hai — check karo")
    
    # ─────────────────────────────────────────────────────────────────────
    # 🔐 API CREDENTIALS
    # ─────────────────────────────────────────────────────────────────────
    if not Bootstrap.API_ID or Bootstrap.API_ID == 0:
        errors.append("API_ID missing — my.telegram.org se lo")
    
    if not Bootstrap.API_HASH:
        errors.append("API_HASH missing — my.telegram.org se lo")
    elif len(Bootstrap.API_HASH) != 32:
        warnings.append(f"API_HASH 32 characters ka hona chahiye, aapke paas {len(Bootstrap.API_HASH)} hai")
    
    # ─────────────────────────────────────────────────────────────────────
    # 👑 OWNER ID
    # ─────────────────────────────────────────────────────────────────────
    if not Bootstrap.OWNER_ID or Bootstrap.OWNER_ID == 0:
        errors.append("OWNER_ID missing — apna Telegram ID daalo")
    elif Bootstrap.OWNER_ID < 100000:
        warnings.append("OWNER_ID bahut chhota hai — sahi ID daalo")
    
    # ─────────────────────────────────────────────────────────────────────
    # 🗄️ DATABASE
    # ─────────────────────────────────────────────────────────────────────
    if not Bootstrap.DB_HOST:
        errors.append("DB_HOST missing")
    if not Bootstrap.DB_NAME:
        errors.append("DB_NAME missing")
    if not Bootstrap.DB_USER:
        errors.append("DB_USER missing")
    if not Bootstrap.DB_PASSWORD:
        errors.append("DB_PASSWORD missing")
    elif len(Bootstrap.DB_PASSWORD) < 4:
        warnings.append("DB_PASSWORD bahut chhota hai")
    
    # ─────────────────────────────────────────────────────────────────────
    # 🔐 ENCRYPTION KEY
    # ─────────────────────────────────────────────────────────────────────
    if not Bootstrap.ENCRYPTION_KEY:
        errors.append("ENCRYPTION_KEY missing — generate karo")
    elif len(Bootstrap.ENCRYPTION_KEY) < 40:
        errors.append("ENCRYPTION_KEY galat hai — Fernet key 44 chars ki hoti hai")
    else:
        try:
            from cryptography.fernet import Fernet
            Fernet(Bootstrap.ENCRYPTION_KEY.encode())
        except Exception as e:
            errors.append(f"ENCRYPTION_KEY invalid: {e}")
    
    # ─────────────────────────────────────────────────────────────────────
    # 📝 LOGGING
    # ─────────────────────────────────────────────────────────────────────
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if Bootstrap.LOG_LEVEL not in valid_levels:
        warnings.append(f"LOG_LEVEL '{Bootstrap.LOG_LEVEL}' invalid — defaulting to INFO")
    
    # ─────────────────────────────────────────────────────────────────────
    # 📊 OUTPUT
    # ─────────────────────────────────────────────────────────────────────
    if errors:
        log.error("=" * 70)
        log.error(Colors.error("❌ CONFIGURATION ERRORS FOUND:"))
        log.error("=" * 70)
        for err in errors:
            log.error(f"  {Colors.error('•')} {err}")
        log.error("=" * 70)
    
    if warnings:
        log.warning("=" * 70)
        log.warning(Colors.warning("⚠️  WARNINGS:"))
        log.warning("=" * 70)
        for warn in warnings:
            log.warning(f"  {Colors.warning('•')} {warn}")
        log.warning("=" * 70)
    
    return len(errors) == 0


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 RUNTIME SETTINGS MANAGER
# ═══════════════════════════════════════════════════════════════════════════

class SettingsCache:
    """
    Runtime settings ko memory mein cache karta hai.
    
    Flow:
    1. Bot start hote waqt DEFAULT_SETTINGS se initialize hota hai
    2. Database se load hota hai (agar values hain toh)
    3. Admin panel se update hota hai (memory mein instantly, DB mein save)
    4. Get karte waqt memory se fast access
    """
    
    def __init__(self):
        self._cache: Dict[str, Any] = dict(DEFAULT_SETTINGS)
        self._loaded: bool = False
        self._last_update: float = 0.0
        self._version: int = 0
    
    def load_from_db(self, settings_dict: Dict[str, Any]) -> None:
        """
        Database se settings load karta hai.
        DEFAULT_SETTINGS ke upar DB values override karti hain.
        """
        self._cache = {**DEFAULT_SETTINGS, **settings_dict}
        self._loaded = True
        self._last_update = time.time()
        self._version += 1
        
        log.info(
            f"{Colors.success('✅')} Settings loaded from DB "
            f"({len(self._cache)} items, version {self._version})"
        )
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Setting value nikalta hai.
        
        Priority:
        1. Runtime cache (DB se loaded)
        2. DEFAULT_SETTINGS
        3. Given default
        """
        if key in self._cache:
            return self._cache[key]
        if key in DEFAULT_SETTINGS:
            return DEFAULT_SETTINGS[key]
        return default
    
    def set(self, key: str, value: Any, persist: bool = False) -> None:
        """
        Setting value update karta hai (memory mein).
        
        Args:
            key     : Setting name
            value   : New value
            persist : True hone pe database mein bhi save karega
        """
        old_value = self._cache.get(key)
        self._cache[key] = value
        self._last_update = time.time()
        
        if old_value != value:
            log.debug(f"Setting updated: {key} = {value}")
    
    def update_many(self, updates: Dict[str, Any]) -> None:
        """Ek saath multiple settings update karta hai"""
        for key, value in updates.items():
            self.set(key, value)
    
    def all(self) -> Dict[str, Any]:
        """Saari settings return karta hai (copy)"""
        return dict(self._cache)
    
    def reload(self, settings_dict: Dict[str, Any]) -> None:
        """Cache ko dobara load karta hai"""
        self.load_from_db(settings_dict)
    
    def is_loaded(self) -> bool:
        """Check karta hai ki DB se load hua hai ya nahi"""
        return self._loaded
    
    def get_version(self) -> int:
        """Settings version return karta hai"""
        return self._version
    
    def get_last_update(self) -> float:
        """Last update time return karta hai"""
        return self._last_update
    
    def reset(self) -> None:
        """Cache ko DEFAULT_SETTINGS pe reset karta hai"""
        self._cache = dict(DEFAULT_SETTINGS)
        self._loaded = False
        log.warning("Settings cache reset to defaults")
    
    # ─────────────────────────────────────────────────────────────────────
    # TYPE-SAFE GETTERS
    # ─────────────────────────────────────────────────────────────────────
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Integer value nikalta hai"""
        try:
            return int(self.get(key, default))
        except (ValueError, TypeError):
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Float value nikalta hai"""
        try:
            return float(self.get(key, default))
        except (ValueError, TypeError):
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Boolean value nikalta hai"""
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on", "haan")
        return bool(value)
    
    def get_str(self, key: str, default: str = "") -> str:
        """String value nikalta hai"""
        value = self.get(key, default)
        return str(value) if value is not None else default
    
    def get_list(self, key: str, default: Optional[List] = None) -> List:
        """List value nikalta hai"""
        value = self.get(key, default or [])
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return default or []
    
    def get_dict(self, key: str, default: Optional[Dict] = None) -> Dict:
        """Dict value nikalta hai"""
        value = self.get(key, default or {})
        return value if isinstance(value, dict) else (default or {})


# Global settings instance — saari files isko use karengi
settings = SettingsCache()


# ═══════════════════════════════════════════════════════════════════════════
# 🚀 STARTUP BANNER
# ═══════════════════════════════════════════════════════════════════════════

def print_banner() -> None:
    """Startup pe ek acha sa banner print karta hai"""
    
    # Server info nikalo
    info = Bootstrap.get_server_info()
    uptime = Bootstrap.get_uptime()
    
    banner = f"""
{Colors.BRIGHT_CYAN}╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   {Colors.BRIGHT_MAGENTA}🚀  I S U K O B I T   —   F I L E   S T O R E   B O T{Colors.BRIGHT_CYAN}          ║
║                                                                      ║
║   {Colors.BRIGHT_WHITE}Version  : {Bootstrap.BOT_VERSION}{Colors.BRIGHT_CYAN}                                              ║
║   {Colors.BRIGHT_WHITE}Owner    : {Bootstrap.OWNER_ID}{Colors.BRIGHT_CYAN}                                           ║
║   {Colors.BRIGHT_WHITE}Database : {Bootstrap.DB_NAME}@{Bootstrap.DB_HOST}:{Bootstrap.DB_PORT}{Colors.BRIGHT_CYAN}                            ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║   {Colors.BRIGHT_YELLOW}📊 SERVER INFO{Colors.BRIGHT_CYAN}                                                   ║
║                                                                      ║
║   {Colors.WHITE}OS       : {info.get('platform', 'Unknown')} {info.get('platform_release', '')}{Colors.BRIGHT_CYAN}                      ║
║   {Colors.WHITE}Python   : {info.get('python_version', 'Unknown')}{Colors.BRIGHT_CYAN}                                        ║
║   {Colors.WHITE}CPU      : {info.get('cpu_count', '?')} cores{Colors.BRIGHT_CYAN}                                          ║
║   {Colors.WHITE}RAM      : {info.get('ram_total_gb', '?')} GB ({info.get('ram_available_gb', '?')} GB free){Colors.BRIGHT_CYAN}         ║
║   {Colors.WHITE}Disk     : {info.get('disk_total_gb', '?')} GB ({info.get('disk_free_gb', '?')} GB free){Colors.BRIGHT_CYAN}         ║
║   {Colors.WHITE}Uptime   : {uptime}{Colors.BRIGHT_CYAN}                                                ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║   {Colors.BRIGHT_GREEN}✅ Bot ready to start{Colors.BRIGHT_CYAN}                                             ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)


def print_config_summary() -> None:
    """Config summary print karta hai"""
    print(f"\n{Colors.BRIGHT_YELLOW}{'━' * 70}{Colors.RESET}")
    print(f"{Colors.BRIGHT_YELLOW}📋 CONFIGURATION SUMMARY{Colors.RESET}")
    print(f"{Colors.BRIGHT_YELLOW}{'━' * 70}{Colors.RESET}\n")
    
    checks = [
        ("Bot Token", "✅ Set" if Bootstrap.BOT_TOKEN else "❌ Missing"),
        ("API ID", str(Bootstrap.API_ID) if Bootstrap.API_ID else "❌ Missing"),
        ("API Hash", "✅ Set" if Bootstrap.API_HASH else "❌ Missing"),
        ("Owner ID", str(Bootstrap.OWNER_ID) if Bootstrap.OWNER_ID else "❌ Missing"),
        ("DB Host", f"{Bootstrap.DB_HOST}:{Bootstrap.DB_PORT}"),
        ("DB Name", Bootstrap.DB_NAME),
        ("DB User", Bootstrap.DB_USER),
        ("DB Password", "✅ Set" if Bootstrap.DB_PASSWORD else "❌ Missing"),
        ("Encryption Key", "✅ Set" if Bootstrap.ENCRYPTION_KEY else "❌ Missing"),
        ("Log Level", Bootstrap.LOG_LEVEL),
        ("Log File", Bootstrap.LOG_FILE),
    ]
    
    for label, value in checks:
        print(f"  {Colors.CYAN}{label:<18}{Colors.RESET} : {value}")
    
    print(f"\n{Colors.BRIGHT_YELLOW}{'━' * 70}{Colors.RESET}\n")


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    # Classes
    "Bootstrap",
    "Constants",
    "Colors",
    "ColorFormatter",
    "SettingsCache",
    
    # Objects
    "settings",
    "log",
    "DEFAULT_SETTINGS",
    
    # Functions
    "get_env",
    "get_int",
    "get_float",
    "get_bool",
    "get_list",
    "get_int_list",
    "get_json",
    "validate_config",
    "print_banner",
    "print_config_summary",
    "setup_logging",
    
    # Paths
    "BASE_DIR",
    "ENV_FILE",
    "LOGS_DIR",
    "BACKUP_TEMP_DIR",
    "DOWNLOADS_TEMP_DIR",
    "CACHE_DIR",
    "DATA_DIR",
    "SESSIONS_DIR",
    "TEMP_DIR",
]


# ═══════════════════════════════════════════════════════════════════════════
# 🧪 SELF-TEST
# ═══════════════════════════════════════════════════════════════════════════

def _self_test() -> None:
    """Config file ka self-test — python config.py se chalayein"""
    print_banner()
    print_config_summary()
    
    print(f"{Colors.BRIGHT_YELLOW}🔍 Validation Check:{Colors.RESET}\n")
    
    if validate_config():
        print(f"{Colors.success('✅ All good! Bot ready to start.')}\n")
    else:
        print(f"{Colors.error('❌ Fix errors above before starting bot.')}\n")
        sys.exit(1)
    
    print(f"{Colors.BRIGHT_CYAN}📊 Default Settings : {len(DEFAULT_SETTINGS)} items{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}🌍 Languages        : {', '.join(Constants.LANGUAGES)}{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}📁 Base Directory   : {BASE_DIR}{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}📝 Log File         : {Bootstrap.LOG_FILE}{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}🗄️  Backup Dir       : {BACKUP_TEMP_DIR}{Colors.RESET}\n")
    
    # Settings test
    print(f"{Colors.BRIGHT_YELLOW}🧪 Settings Test:{Colors.RESET}\n")
    print(f"  max_file_size      : {settings.get('max_file_size')} bytes")
    print(f"  default_language   : {settings.get('default_language')}")
    print(f"  backup_interval    : {settings.get('backup_interval_hours')} hours")
    print(f"  rate_limit         : {settings.get('rate_limit_per_minute')} req/min")
    print(f"  user_locked_links  : {settings.get('user_locked_links')}")
    print()
    
    print(f"{Colors.success('✅ Config self-test complete!')}\n")


if __name__ == "__main__":
    _self_test()


# ═══════════════════════════════════════════════════════════════════════════
# 📖 END OF FILE
# ═══════════════════════════════════════════════════════════════════════════
# 
# Total lines : ~1100+
# 
# Agar koi problem aaye toh check karo:
# 1. .env file hai ya nahi
# 2. Saari required values bhari hain ya nahi
# 3. Encryption key generate ki hai ya nahi
# 4. Database credentials sahi hain ya nahi
# 
# ═══════════════════════════════════════════════════════════════════════════
