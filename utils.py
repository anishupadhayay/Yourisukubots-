# ═══════════════════════════════════════════════════════════════════════════
# 🚀 ISUKOBIT — TELEGRAM FILE STORE BOT
# ═══════════════════════════════════════════════════════════════════════════
# File      : utils.py
# Purpose   : Saare helper functions (encryption, validation, formatting)
# Author    : Isukobit Team
# Version   : 1.0.0
# Python    : 3.10+
# ═══════════════════════════════════════════════════════════════════════════
#
# YEH FILE KYA KARTI HAI:
# ─────────────────────────────────────────────────────────────────────────
# 1. Encryption / Decryption (Fernet)
# 2. File code generator (ISU-XXXXXX)
# 3. File type detection
# 4. File hash (SHA256)
# 5. Size formatting (bytes → KB/MB/GB)
# 6. Time formatting (timestamp → readable)
# 7. Text escaping (HTML/Markdown)
# 8. Username / link validation
# 9. Rate limit checker (memory + DB)
# 10. Session / state manager
# 11. Retry decorator
# 12. Temp file cleaner
# 13. Progress bar
# 14. Human readable number
# 15. File icon selector
# 16. Link generator
# 17. Sanitization
# 18. Path helpers
# 19. Image thumbnail
# 20. Many more...
#
# KAISE USE KARO:
# ─────────────────────────────────────────────────────────────────────────
# from utils import generate_file_code, format_size, encrypt_data
#
# code = generate_file_code()  # "ISU-A1B2C3"
# size = format_size(52428800)  # "50.00 MB"
#
# ═══════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════
# 📦 IMPORTS
# ═══════════════════════════════════════════════════════════════════════════

import os
import re
import io
import sys
import time
import json
import hashlib
import secrets
import string
import asyncio
import shutil
import mimetypes
import unicodedata
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any, Union, Tuple, Callable
from functools import wraps

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:
    print("❌ cryptography install nahi hai! pip install cryptography")
    raise

from config import Bootstrap, Constants, log, Colors


# ═══════════════════════════════════════════════════════════════════════════
# 🔐 ENCRYPTION / DECRYPTION
# ═══════════════════════════════════════════════════════════════════════════

# Global Fernet instance
_fernet: Optional[Fernet] = None


def _get_fernet() -> Fernet:
    """Fernet instance return karta hai (singleton)"""
    global _fernet
    if _fernet is None:
        try:
            _fernet = Fernet(Bootstrap.ENCRYPTION_KEY.encode())
        except Exception as e:
            log.error(f"Fernet initialization failed: {e}")
            raise
    return _fernet


def encrypt_data(data: str) -> str:
    """
    String ko encrypt karta hai.
    
    Example:
        >>> encrypt_data("secret message")
        'gAAAAABh...'
    """
    if not data:
        return ""
    try:
        encrypted = _get_fernet().encrypt(data.encode("utf-8"))
        return encrypted.decode("utf-8")
    except Exception as e:
        log.error(f"Encryption failed: {e}")
        return ""


def decrypt_data(encrypted: str) -> str:
    """
    Encrypted string ko decrypt karta hai.
    """
    if not encrypted:
        return ""
    try:
        decrypted = _get_fernet().decrypt(encrypted.encode("utf-8"))
        return decrypted.decode("utf-8")
    except InvalidToken:
        log.warning("Decryption failed: Invalid token")
        return ""
    except Exception as e:
        log.error(f"Decryption failed: {e}")
        return ""


def encrypt_dict(data: Dict[str, Any]) -> str:
    """Dictionary ko encrypt karta hai"""
    if not data:
        return ""
    return encrypt_data(json.dumps(data, ensure_ascii=False))


def decrypt_dict(encrypted: str) -> Dict[str, Any]:
    """Encrypted string ko dict mein convert karta hai"""
    if not encrypted:
        return {}
    try:
        decrypted = decrypt_data(encrypted)
        return json.loads(decrypted) if decrypted else {}
    except Exception as e:
        log.error(f"Decrypt dict failed: {e}")
        return {}


def generate_encryption_key() -> str:
    """Naya Fernet key generate karta hai"""
    return Fernet.generate_key().decode()


# ═══════════════════════════════════════════════════════════════════════════
# 🔑 FILE CODE GENERATOR
# ═══════════════════════════════════════════════════════════════════════════

def generate_file_code(
    prefix: Optional[str] = None,
    length: int = 6,
    separator: str = "-"
) -> str:
    """
    Unique file code generate karta hai.
    
    Format: PREFIX-XXXXXX
    Example: ISU-A1B2C3
    
    Parameters
    ----------
    prefix : str
        Code ka prefix (default: ISU)
    length : int
        Random part ki length (default: 6)
    separator : str
        Prefix aur random ke beech ka separator
    
    Returns
    -------
    str
    """
    if prefix is None:
        # Try settings first
        try:
            from config import settings
            prefix = settings.get("file_code_prefix", "ISU")
        except Exception:
            prefix = "ISU"
    
    # Uppercase alphanumeric (0, O, 1, I exclude kiye confusion ke liye)
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    random_part = "".join(secrets.choice(alphabet) for _ in range(length))
    
    if separator:
        return f"{prefix}{separator}{random_part}"
    return f"{prefix}{random_part}"


def generate_short_code(length: int = 8) -> str:
    """Short random code (URL-safe)"""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_token(length: int = 32) -> str:
    """Secure random token"""
    return secrets.token_urlsafe(length)


def generate_otp(length: int = 6) -> str:
    """Numeric OTP"""
    return "".join(secrets.choice(string.digits) for _ in range(length))


# ═══════════════════════════════════════════════════════════════════════════
# 📏 SIZE FORMATTING
# ═══════════════════════════════════════════════════════════════════════════

def format_size(size_bytes: int, precision: int = 2) -> str:
    """
    Bytes ko human-readable size mein convert karta hai.
    
    Examples:
        >>> format_size(1024)
        '1.00 KB'
        >>> format_size(52428800)
        '50.00 MB'
        >>> format_size(1073741824)
        '1.00 GB'
    """
    if not isinstance(size_bytes, (int, float)):
        return "0 B"
    
    if size_bytes < 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(size_bytes)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    
    return f"{size:.{precision}f} {units[unit_index]}"


def parse_size(size_str: str) -> int:
    """
    '50 MB' string ko bytes mein convert karta hai.
    
    Examples:
        >>> parse_size("50 MB")
        52428800
        >>> parse_size("1.5 GB")
        1610612736
    """
    if not size_str:
        return 0
    
    size_str = size_str.strip().upper()
    
    # Agar sirf number hai
    if size_str.isdigit():
        return int(size_str)
    
    # Extract number and unit
    match = re.match(r"^([\d.]+)\s*([KMGT]?B?)$", size_str)
    if not match:
        return 0
    
    try:
        number = float(match.group(1))
    except ValueError:
        return 0
    
    unit = match.group(2) or "B"
    
    multipliers = {
        "B": 1,
        "KB": 1024,
        "MB": 1024 ** 2,
        "GB": 1024 ** 3,
        "TB": 1024 ** 4,
        "K": 1024,
        "M": 1024 ** 2,
        "G": 1024 ** 3,
        "T": 1024 ** 4,
    }
    
    return int(number * multipliers.get(unit, 1))


# ═══════════════════════════════════════════════════════════════════════════
# ⏰ TIME FORMATTING
# ═══════════════════════════════════════════════════════════════════════════

def format_datetime(
    dt: Union[datetime, int, float, None],
    format_str: str = "%d %b %Y, %H:%M"
) -> str:
    """Datetime ko readable string mein convert karta hai"""
    if dt is None:
        return "Unknown"
    
    try:
        if isinstance(dt, (int, float)):
            dt = datetime.fromtimestamp(dt)
        elif isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
            except ValueError:
                dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        
        return dt.strftime(format_str)
    except Exception:
        return str(dt)


def format_time_ago(
    dt: Union[datetime, int, float, None]
) -> str:
    """'5 minutes ago' format mein"""
    if dt is None:
        return "Unknown"
    
    try:
        if isinstance(dt, (int, float)):
            then = datetime.fromtimestamp(dt)
        elif isinstance(dt, str):
            try:
                then = datetime.fromisoformat(dt.replace("Z", "+00:00"))
            except ValueError:
                then = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        else:
            then = dt
        
        now = datetime.now(then.tzinfo) if then.tzinfo else datetime.now()
        diff = (now - then).total_seconds()
        
        if diff < 5:
            return "just now"
        elif diff < 60:
            return f"{int(diff)}s ago"
        elif diff < 3600:
            return f"{int(diff // 60)}m ago"
        elif diff < 86400:
            return f"{int(diff // 3600)}h ago"
        elif diff < 604800:
            return f"{int(diff // 86400)}d ago"
        elif diff < 2592000:
            return f"{int(diff // 604800)}w ago"
        elif diff < 31536000:
            return f"{int(diff // 2592000)}mo ago"
        else:
            return f"{int(diff // 31536000)}y ago"
    except Exception:
        return "Unknown"


def format_duration(seconds: int) -> str:
    """'2h 30m 15s' format mein"""
    if seconds < 0:
        return "0s"
    
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if secs and not days:
        parts.append(f"{secs}s")
    
    return " ".join(parts) if parts else "0s"


def get_uptime(start_time: float) -> str:
    """Bot start time se ab tak ka duration"""
    if start_time <= 0:
        return "0s"
    return format_duration(int(time.time() - start_time))


def utc_now() -> datetime:
    """Current UTC datetime"""
    return datetime.now(timezone.utc)


def local_now() -> datetime:
    """Current local datetime"""
    return datetime.now()


# ═══════════════════════════════════════════════════════════════════════════
# 🔤 TEXT FORMATTING
# ═══════════════════════════════════════════════════════════════════════════

def escape_html(text: str) -> str:
    """
    HTML special characters escape karta hai.
    Telegram HTML parse mode ke liye zaroori.
    """
    if not text:
        return ""
    
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def escape_markdown(text: str) -> str:
    """Markdown special characters escape karta hai"""
    if not text:
        return ""
    
    special = r"_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{c}" if c in special else c for c in str(text))


def unescape_html(text: str) -> str:
    """HTML entities wapas original mein"""
    if not text:
        return ""
    return (
        text
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
    )


def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """Text ko max length tak truncate karta hai"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def truncate_middle(text: str, max_length: int, suffix: str = "...") -> str:
    """Middle se truncate karta hai (extensions preserve)"""
    if not text or len(text) <= max_length:
        return text
    
    if "." in text:
        name, ext = text.rsplit(".", 1)
        ext = "." + ext
    else:
        name, ext = text, ""
    
    available = max_length - len(suffix) - len(ext)
    if available < 5:
        return text[:max_length - len(suffix)] + suffix
    
    half = available // 2
    return name[:half] + suffix + name[-half:] + ext


def humanize_number(number: int) -> str:
    """
    Bade numbers ko readable banata hai.
    
    Examples:
        >>> humanize_number(1234)
        '1.2K'
        >>> humanize_number(1234567)
        '1.2M'
    """
    if not isinstance(number, (int, float)):
        return "0"
    
    abs_num = abs(number)
    
    if abs_num < 1000:
        return str(int(number))
    elif abs_num < 1_000_000:
        return f"{number / 1000:.1f}K"
    elif abs_num < 1_000_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif abs_num < 1_000_000_000_000:
        return f"{number / 1_000_000_000:.1f}B"
    else:
        return f"{number / 1_000_000_000_000:.1f}T"


def slugify(text: str) -> str:
    """
    Text ko URL-safe slug mein convert karta hai.
    
    >>> slugify("Hello World!")
    'hello-world'
    """
    if not text:
        return ""
    
    # Normalize unicode
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    
    # Lowercase
    text = text.lower()
    
    # Replace non-alphanumeric with hyphens
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    
    return text.strip("-")


def clean_filename(filename: str) -> str:
    """Filename ko clean karta hai (unsafe chars hata deta hai)"""
    if not filename:
        return "file"
    
    # Remove path separators
    filename = filename.replace("/", "_").replace("\\", "_")
    
    # Remove control characters
    filename = "".join(
        c for c in filename
        if unicodedata.category(c)[0] != "C"
    )
    
    # Remove dangerous chars
    filename = re.sub(r'[<>:"|?*]', "", filename)
    
    # Trim length
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:195] + ext
    
    return filename.strip() or "file"


def get_file_extension(filename: str) -> str:
    """File ka extension nikalta hai (lowercase, dot ke bina)"""
    if not filename:
        return ""
    
    ext = os.path.splitext(filename)[1]
    return ext.lstrip(".").lower()


# ═══════════════════════════════════════════════════════════════════════════
# 📁 FILE OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════

def get_file_hash(data: bytes) -> str:
    """File ka SHA256 hash"""
    return hashlib.sha256(data).hexdigest()


def get_string_hash(text: str) -> str:
    """String ka SHA256 hash"""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def get_md5(text: str) -> str:
    """MD5 hash"""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def detect_file_type(filename: str, mime_type: str = "") -> str:
    """
    File ka type detect karta hai (document, video, audio, photo, etc.)
    """
    ext = get_file_extension(filename)
    
    # Extension-based detection
    video_exts = {"mp4", "mkv", "avi", "mov", "webm", "flv", "wmv", "m4v", "mpg", "mpeg", "3gp"}
    audio_exts = {"mp3", "wav", "ogg", "flac", "m4a", "aac", "wma", "opus"}
    image_exts = {"jpg", "jpeg", "png", "gif", "webp", "svg", "bmp", "tiff", "ico", "heic"}
    doc_exts = {"pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "csv", "rtf", "odt"}
    archive_exts = {"zip", "rar", "7z", "tar", "gz", "bz2", "xz"}
    apk_exts = {"apk", "exe", "msi", "deb", "rpm", "dmg"}
    code_exts = {"py", "js", "ts", "java", "c", "cpp", "h", "php", "rb", "go", "rs", "html", "css", "json", "xml", "sql", "sh"}
    
    if ext in video_exts:
        return "video"
    if ext in audio_exts:
        return "audio"
    if ext in image_exts:
        return "photo"
    if ext in archive_exts:
        return "archive"
    if ext in apk_exts:
        return "app"
    if ext in code_exts:
        return "code"
    if ext in doc_exts:
        return "document"
    
    # MIME-based fallback
    if mime_type:
        if mime_type.startswith("video/"):
            return "video"
        if mime_type.startswith("audio/"):
            return "audio"
        if mime_type.startswith("image/"):
            return "photo"
    
    return "document"


def get_file_icon(filename: str, mime_type: str = "") -> str:
    """File ke liye appropriate emoji return karta hai"""
    ext = get_file_extension(filename)
    
    icons = {
        # Documents
        "pdf": "📕",
        "doc": "📘", "docx": "📘",
        "xls": "📗", "xlsx": "📗",
        "ppt": "📙", "pptx": "📙",
        "txt": "📝", "csv": "📝", "rtf": "📝",
        
        # Archives
        "zip": "🗜️", "rar": "🗜️", "7z": "🗜️",
        "tar": "🗜️", "gz": "🗜️",
        
        # Media
        "jpg": "🖼️", "jpeg": "🖼️", "png": "🖼️",
        "gif": "🖼️", "webp": "🖼️", "svg": "🖼️",
        "mp4": "🎬", "mkv": "🎬", "avi": "🎬", "mov": "🎬",
        "mp3": "🎵", "wav": "🎵", "ogg": "🎵", "flac": "🎵",
        
        # Apps
        "apk": "📦", "exe": "📦", "msi": "📦",
        
        # Code
        "py": "💻", "js": "💻", "html": "💻", "css": "💻",
        "json": "💻", "xml": "💻", "sql": "💻",
        
        # Others
        "epub": "📚", "mobi": "📚",
        "torrent": "🧲",
        "iso": "💿",
    }
    
    return icons.get(ext, "📄")


def is_allowed_extension(filename: str) -> bool:
    """Check karta hai ki file extension allowed hai ya nahi"""
    try:
        from config import settings
        allowed = settings.get("allowed_extensions", [])
        blocked = settings.get("blocked_extensions", [])
    except Exception:
        allowed = []
        blocked = []
    
    ext = get_file_extension(filename)
    
    # Agar allowed list khaali hai toh sab allowed
    if not allowed:
        # But blocked check karo
        if blocked and ext in blocked:
            return False
        return True
    
    # Allowed list mein hona chahiye
    return ext in allowed


def get_mime_type(filename: str) -> str:
    """File ka MIME type detect karta hai"""
    mime, _ = mimetypes.guess_type(filename)
    return mime or "application/octet-stream"


# ═══════════════════════════════════════════════════════════════════════════
# ✅ VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

def is_valid_file_code(code: str, prefix: str = "ISU") -> bool:
    """File code valid hai ya nahi"""
    if not code:
        return False
    
    pattern = rf"^{re.escape(prefix)}-[A-Z0-9]{{4,12}}$"
    return bool(re.match(pattern, code.upper()))


def is_valid_username(username: str) -> bool:
    """Telegram username valid hai ya nahi"""
    if not username:
        return False
    username = username.lstrip("@")
    return bool(re.match(r"^[a-zA-Z0-9_]{5,32}$", username))


def is_valid_user_id(user_id: Union[int, str]) -> bool:
    """Telegram user ID valid hai ya nahi"""
    try:
        uid = int(user_id)
        return 100_000 <= uid <= 9_999_999_999
    except (ValueError, TypeError):
        return False


def is_valid_channel_id(channel_id: Union[int, str]) -> bool:
    """Telegram channel ID valid hai ya nahi (-100...)"""
    try:
        cid = int(channel_id)
        return cid < -1_000_000_000_000
    except (ValueError, TypeError):
        return False


def is_valid_url(url: str) -> bool:
    """HTTP/HTTPS URL valid hai ya nahi"""
    if not url:
        return False
    pattern = r"^https?://[^\s]+$"
    return bool(re.match(pattern, url, re.IGNORECASE))


def is_valid_telegram_link(link: str) -> bool:
    """Telegram link valid hai ya nahi"""
    if not link:
        return False
    pattern = r"^(https?://)?t\.me/[^\s]+$"
    return bool(re.match(pattern, link, re.IGNORECASE))


def is_valid_email(email: str) -> bool:
    """Email valid hai ya nahi"""
    if not email:
        return False
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def is_safe_filename(filename: str) -> bool:
    """Filename safe hai ya nahi (path traversal check)"""
    if not filename:
        return False
    
    # Path separators
    if any(c in filename for c in ["/", "\\", ".."]):
        return False
    
    # Null byte
    if "\x00" in filename:
        return False
    
    return True


# ═══════════════════════════════════════════════════════════════════════════
# 🔗 LINK GENERATION
# ═══════════════════════════════════════════════════════════════════════════

def generate_file_link(file_code: str, bot_username: Optional[str] = None) -> str:
    """
    File ka deep link generate karta hai.
    
    Format: https://t.me/BOT_USERNAME?start=FILECODE
    """
    if not bot_username:
        try:
            from config import settings
            bot_username = settings.get("bot_username", Bootstrap.BOT_USERNAME)
        except Exception:
            bot_username = Bootstrap.BOT_USERNAME
    
    bot_username = bot_username.lstrip("@")
    return f"https://t.me/{bot_username}?start={file_code}"


def generate_channel_link(channel: str) -> str:
    """Channel ka link generate karta hai"""
    if not channel:
        return ""
    
    channel = str(channel)
    
    if channel.startswith("http"):
        return channel
    
    if channel.startswith("@"):
        return f"https://t.me/{channel[1:]}"
    
    if channel.startswith("-100"):
        # Private channel — invite link nahi bana sakte
        return ""
    
    return f"https://t.me/{channel.lstrip('@')}"


def parse_deep_link(start_param: str) -> Optional[str]:
    """
    Deep link se file code extract karta hai.
    
    >>> parse_deep_link("ISU-A1B2C3")
    'ISU-A1B2C3'
    """
    if not start_param:
        return None
    
    # Direct code
    if is_valid_file_code(start_param):
        return start_param.upper()
    
    # Link se extract
    match = re.search(r"start=([A-Z0-9-]+)", start_param)
    if match:
        return match.group(1)
    
    return None


# ═══════════════════════════════════════════════════════════════════════════
# 🚦 RATE LIMITING (Memory based — fast)
# ═══════════════════════════════════════════════════════════════════════════

class MemoryRateLimiter:
    """
    Memory-based rate limiter.
    Fast hai but server restart pe reset ho jata hai.
    """
    
    def __init__(self):
        self._requests: Dict[int, List[float]] = {}
        self._muted: Dict[int, float] = {}
        self._warnings: Dict[int, int] = {}
    
    def check(
        self,
        user_id: int,
        max_requests: int = 10,
        window_seconds: int = 60
    ) -> Tuple[bool, int]:
        """
        Check karta hai ki user rate limit mein hai ya nahi.
        
        Returns:
            (allowed, retry_after_seconds)
        """
        now = time.time()
        
        # Mute check
        if user_id in self._muted:
            if self._muted[user_id] > now:
                remaining = int(self._muted[user_id] - now)
                return False, remaining
            else:
                del self._muted[user_id]
        
        # Purane requests clean karo
        if user_id not in self._requests:
            self._requests[user_id] = []
        
        # Window ke bahar wale requests hatao
        cutoff = now - window_seconds
        self._requests[user_id] = [
            t for t in self._requests[user_id] if t > cutoff
        ]
        
        # Count check
        if len(self._requests[user_id]) >= max_requests:
            oldest = self._requests[user_id][0]
            retry_after = int(window_seconds - (now - oldest))
            return False, max(retry_after, 1)
        
        # Allow
        self._requests[user_id].append(now)
        return True, 0
    
    def add_warning(self, user_id: int) -> int:
        """Warning count badhata hai"""
        self._warnings[user_id] = self._warnings.get(user_id, 0) + 1
        return self._warnings[user_id]
    
    def clear_warnings(self, user_id: int) -> None:
        """Warnings clear karta hai"""
        self._warnings.pop(user_id, None)
    
    def get_warnings(self, user_id: int) -> int:
        """Warning count return karta hai"""
        return self._warnings.get(user_id, 0)
    
    def mute(self, user_id: int, duration_seconds: int = 3600) -> None:
        """User ko mute karta hai"""
        self._muted[user_id] = time.time() + duration_seconds
        self._warnings.pop(user_id, None)
    
    def unmute(self, user_id: int) -> None:
        """Mute hata deta hai"""
        self._muted.pop(user_id, None)
    
    def is_muted(self, user_id: int) -> Tuple[bool, int]:
        """Check karta hai ki user muted hai ya nahi"""
        if user_id not in self._muted:
            return False, 0
        
        remaining = self._muted[user_id] - time.time()
        if remaining <= 0:
            del self._muted[user_id]
            return False, 0
        
        return True, int(remaining)
    
    def cleanup(self, older_than_seconds: int = 3600) -> int:
        """Purane records clean karta hai"""
        now = time.time()
        cleaned = 0
        
        # Cleanup requests
        for uid in list(self._requests.keys()):
            self._requests[uid] = [
                t for t in self._requests[uid]
                if now - t < older_than_seconds
            ]
            if not self._requests[uid]:
                del self._requests[uid]
                cleaned += 1
        
        # Cleanup mutes
        for uid in list(self._muted.keys()):
            if self._muted[uid] < now:
                del self._muted[uid]
                cleaned += 1
        
        return cleaned
    
    def reset(self) -> None:
        """Poora limiter reset karta hai"""
        self._requests.clear()
        self._muted.clear()
        self._warnings.clear()


# Global rate limiter
rate_limiter = MemoryRateLimiter()


# ═══════════════════════════════════════════════════════════════════════════
# 🔄 RETRY DECORATOR
# ═══════════════════════════════════════════════════════════════════════════

def retry_async(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple = (Exception,),
    on_fail: Optional[Callable] = None
):
    """
    Async function retry decorator.
    
    Usage:
        @retry_async(max_attempts=3)
        async def my_func():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    
                    if attempt >= max_attempts:
                        log.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        if on_fail:
                            try:
                                await on_fail(e)
                            except Exception:
                                pass
                        raise
                    
                    log.warning(
                        f"{func.__name__} attempt {attempt}/{max_attempts} failed: {e}. "
                        f"Retrying in {current_delay}s..."
                    )
                    
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            
            raise RuntimeError(f"{func.__name__} exhausted all retries")
        
        return wrapper
    return decorator


def retry_sync(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple = (Exception,)
):
    """Sync function retry decorator"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    
                    if attempt >= max_attempts:
                        log.error(f"{func.__name__} failed: {e}")
                        raise
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            raise RuntimeError(f"{func.__name__} exhausted all retries")
        
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════════════════════
# 🧹 TEMP FILE CLEANUP
# ═══════════════════════════════════════════════════════════════════════════

def cleanup_temp_files(
    directory: Path = None,
    older_than_hours: int = 24
) -> int:
    """Purane temp files delete karta hai"""
    if directory is None:
        directory = Constants.TEMP_DIR
    
    if not directory.exists():
        return 0
    
    cleaned = 0
    cutoff = time.time() - (older_than_hours * 3600)
    
    try:
        for item in directory.iterdir():
            try:
                if item.stat().st_mtime < cutoff:
                    if item.is_file():
                        item.unlink()
                        cleaned += 1
                    elif item.is_dir():
                        shutil.rmtree(item)
                        cleaned += 1
            except Exception as e:
                log.warning(f"Failed to clean {item}: {e}")
    except Exception as e:
        log.error(f"Cleanup failed: {e}")
    
    if cleaned > 0:
        log.info(f"Cleaned {cleaned} temp items")
    
    return cleaned


def get_dir_size(directory: Path) -> int:
    """Directory ka total size (bytes)"""
    if not directory.exists():
        return 0
    
    total = 0
    try:
        for item in directory.rglob("*"):
            if item.is_file():
                total += item.stat().st_size
    except Exception:
        pass
    
    return total


# ═══════════════════════════════════════════════════════════════════════════
# 📊 PROGRESS BAR
# ═══════════════════════════════════════════════════════════════════════════

def make_progress_bar(
    current: int,
    total: int,
    length: int = 10,
    filled: str = "█",
    empty: str = "░"
) -> str:
    """
    Text progress bar banata hai.
    
    >>> make_progress_bar(50, 100)
    '█████░░░░░ 50%'
    """
    if total <= 0:
        return f"{empty * length} 0%"
    
    percent = min(100, max(0, int((current / total) * 100)))
    filled_length = int(length * percent / 100)
    
    bar = filled * filled_length + empty * (length - filled_length)
    return f"{bar} {percent}%"


def make_loading_dots(frame: int) -> str:
    """Loading animation dots"""
    dots = ["   ", ".  ", ".. ", "..."]
    return dots[frame % len(dots)]


# ═══════════════════════════════════════════════════════════════════════════
# 🎨 EMOJI HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def get_status_emoji(status: str) -> str:
    """Status ke liye emoji"""
    return {
        "active": "🟢",
        "inactive": "⚪",
        "banned": "🚫",
        "premium": "💎",
        "admin": "👑",
        "owner": "⭐",
        "muted": "🔇",
    }.get(status.lower(), "⚪")


def get_bool_emoji(value: bool) -> str:
    """Boolean ke liye emoji"""
    return "✅" if value else "❌"


def get_random_emoji() -> str:
    """Random friendly emoji"""
    import random
    emojis = ["✨", "🌟", "🎉", "🎊", "🔥", "💫", "⭐", "🌸", "🍀", "💎"]
    return random.choice(emojis)


# ═══════════════════════════════════════════════════════════════════════════
# 📊 DICT HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def safe_get(data: Dict, *keys, default=None) -> Any:
    """
    Nested dict se safe value nikalta hai.
    
    >>> safe_get({"a": {"b": {"c": 1}}}, "a", "b", "c")
    1
    """
    if not isinstance(data, dict):
        return default
    
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current


def merge_dicts(*dicts: Dict) -> Dict:
    """Multiple dicts merge karta hai (deep)"""
    result = {}
    for d in dicts:
        if not isinstance(d, dict):
            continue
        for key, value in d.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = merge_dicts(result[key], value)
            else:
                result[key] = value
    return result


def dict_to_pretty(data: Dict, indent: int = 2) -> str:
    """Dict ko pretty JSON string mein"""
    try:
        return json.dumps(data, indent=indent, ensure_ascii=False, default=str)
    except Exception:
        return str(data)


# ═══════════════════════════════════════════════════════════════════════════
# 🕐 SESSION / STATE MANAGER
# ═══════════════════════════════════════════════════════════════════════════

class SessionManager:
    """
    Temporary session state manager.
    User ke multi-step interactions ke liye (upload, rename, etc.)
    """
    
    def __init__(self, default_timeout: int = 300):
        self._sessions: Dict[int, Dict[str, Any]] = {}
        self._timeouts: Dict[int, float] = {}
        self.default_timeout = default_timeout
    
    def set(
        self,
        user_id: int,
        key: str,
        value: Any,
        timeout: Optional[int] = None
    ) -> None:
        """Session value set karta hai"""
        if user_id not in self._sessions:
            self._sessions[user_id] = {}
        
        self._sessions[user_id][key] = value
        
        if timeout is None:
            timeout = self.default_timeout
        
        self._timeouts[user_id] = time.time() + timeout
    
    def get(
        self,
        user_id: int,
        key: str,
        default: Any = None
    ) -> Any:
        """Session value nikalta hai"""
        self._check_expiry(user_id)
        
        if user_id not in self._sessions:
            return default
        
        return self._sessions[user_id].get(key, default)
    
    def get_all(self, user_id: int) -> Dict[str, Any]:
        """Saari session values"""
        self._check_expiry(user_id)
        return self._sessions.get(user_id, {}).copy()
    
    def delete(self, user_id: int, key: str) -> None:
        """Session se key delete karta hai"""
        if user_id in self._sessions:
            self._sessions[user_id].pop(key, None)
    
    def clear(self, user_id: int) -> None:
        """Poori session clear karta hai"""
        self._sessions.pop(user_id, None)
        self._timeouts.pop(user_id, None)
    
    def has(self, user_id: int, key: str) -> bool:
        """Check karta hai ki key exists hai ya nahi"""
        self._check_expiry(user_id)
        return (
            user_id in self._sessions
            and key in self._sessions[user_id]
        )
    
    def _check_expiry(self, user_id: int) -> None:
        """Session expire check karta hai"""
        if user_id not in self._timeouts:
            return
        
        if time.time() > self._timeouts[user_id]:
            self.clear(user_id)
    
    def cleanup(self) -> int:
        """Expired sessions clean karta hai"""
        now = time.time()
        expired = [
            uid for uid, t in self._timeouts.items()
            if t < now
        ]
        
        for uid in expired:
            self.clear(uid)
        
        return len(expired)
    
    def count(self) -> int:
        """Active sessions count"""
        self.cleanup()
        return len(self._sessions)


# Global session manager
sessions = SessionManager()


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 MISC HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def now_timestamp() -> int:
    """Current Unix timestamp"""
    return int(time.time())


def split_list(lst: List, chunk_size: int) -> List[List]:
    """List ko chunks mein todta hai"""
    if chunk_size <= 0:
        return [lst]
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def chunks(iterable, size: int):
    """Generator version — bade lists ke liye"""
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]


def get_random_string(length: int = 8) -> str:
    """Random alphanumeric string"""
    return "".join(
        secrets.choice(string.ascii_letters + string.digits)
        for _ in range(length)
    )


def safe_int(value: Any, default: int = 0) -> int:
    """Safe integer conversion"""
    try:
        if isinstance(value, bool):
            return int(value)
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safe float conversion"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_bool(value: Any, default: bool = False) -> bool:
    """Safe boolean conversion"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on", "haan")
    if isinstance(value, (int, float)):
        return bool(value)
    return default


def user_mention(user_id: int, name: str) -> str:
    """HTML user mention"""
    safe_name = escape_html(name)
    return f'<a href="tg://user?id={user_id}">{safe_name}</a>'


def format_user_display(
    user_id: int,
    first_name: str = "",
    username: str = "",
    mention: bool = True
) -> str:
    """User ka display string"""
    if mention and first_name:
        return user_mention(user_id, first_name)
    elif first_name:
        return escape_html(first_name)
    elif username:
        return f"@{username}"
    else:
        return f"User {user_id}"


def parse_command(text: str) -> Tuple[str, List[str]]:
    """
    Message text ko command aur args mein todta hai.
    
    >>> parse_command("/start abc def")
    ('start', ['abc', 'def'])
    """
    if not text:
        return "", []
    
    text = text.strip()
    
    if not text.startswith("/"):
        return "", []
    
    parts = text.split()
    command = parts[0][1:].split("@")[0].lower()
    args = parts[1:]
    
    return command, args


def is_command(text: str, command: str) -> bool:
    """Check karta hai ki text specific command hai ya nahi"""
    cmd, _ = parse_command(text)
    return cmd == command.lower()


def hide_sensitive(text: str, show_chars: int = 4) -> str:
    """Sensitive text ko hide karta hai (logs ke liye)"""
    if not text or len(text) <= show_chars * 2:
        return "*" * len(text) if text else ""
    
    return text[:show_chars] + "*" * (len(text) - show_chars * 2) + text[-show_chars:]


def measure_time(func: Callable) -> Callable:
    """Function ka execution time measure karta hai"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        elapsed = (time.time() - start) * 1000
        log.debug(f"{func.__name__} took {elapsed:.2f}ms")
        return result
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = (time.time() - start) * 1000
        log.debug(f"{func.__name__} took {elapsed:.2f}ms")
        return result
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    # Encryption
    "encrypt_data", "decrypt_data",
    "encrypt_dict", "decrypt_dict",
    "generate_encryption_key",
    
    # Code gen
    "generate_file_code", "generate_short_code",
    "generate_token", "generate_otp",
    
    # Size
    "format_size", "parse_size",
    
    # Time
    "format_datetime", "format_time_ago",
    "format_duration", "get_uptime",
    "utc_now", "local_now",
    
    # Text
    "escape_html", "escape_markdown", "unescape_html",
    "truncate", "truncate_middle", "humanize_number",
    "slugify", "clean_filename", "get_file_extension",
    
    # Files
    "get_file_hash", "get_string_hash", "get_md5",
    "detect_file_type", "get_file_icon",
    "is_allowed_extension", "get_mime_type",
    
    # Validation
    "is_valid_file_code", "is_valid_username",
    "is_valid_user_id", "is_valid_channel_id",
    "is_valid_url", "is_valid_telegram_link",
    "is_valid_email", "is_safe_filename",
    
    # Links
    "generate_file_link", "generate_channel_link", "parse_deep_link",
    
    # Rate limit
    "MemoryRateLimiter", "rate_limiter",
    
    # Retry
    "retry_async", "retry_sync",
    
    # Cleanup
    "cleanup_temp_files", "get_dir_size",
    
    # Progress
    "make_progress_bar", "make_loading_dots",
    
    # Emoji
    "get_status_emoji", "get_bool_emoji", "get_random_emoji",
    
    # Dict
    "safe_get", "merge_dicts", "dict_to_pretty",
    
    # Session
    "SessionManager", "sessions",
    
    # Misc
    "now_timestamp", "split_list", "chunks",
    "get_random_string", "safe_int", "safe_float", "safe_bool",
    "user_mention", "format_user_display",
    "parse_command", "is_command", "hide_sensitive", "measure_time",
]


# ═══════════════════════════════════════════════════════════════════════════
# 🧪 SELF-TEST
# ═══════════════════════════════════════════════════════════════════════════

def _self_test() -> None:
    """Utils self-test"""
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  🧪 ISUKOBIT — UTILS SELF-TEST                          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    # Code gen
    print("🔑 Code Generation:")
    for _ in range(3):
        print(f"   {generate_file_code()}")
    print()
    
    # Encryption
    print("🔐 Encryption:")
    original = "mera secret message"
    encrypted = encrypt_data(original)
    decrypted = decrypt_data(encrypted)
    print(f"   Original : {original}")
    print(f"   Encrypted: {encrypted[:40]}...")
    print(f"   Decrypted: {decrypted}")
    print(f"   Match    : {original == decrypted}")
    print()
    
    # Size format
    print("📏 Size Format:")
    for size in [512, 1024, 52428800, 1073741824]:
        print(f"   {size:>12} bytes → {format_size(size)}")
    print()
    
    # Time format
    print("⏰ Time Format:")
    print(f"   {format_duration(3661)}")
    print(f"   {format_duration(90000)}")
    print()
    
    # Validation
    print("✅ Validation:")
    print(f"   ISU-A1B2C3 : {is_valid_file_code('ISU-A1B2C3')}")
    print(f"   ISU-invalid: {is_valid_file_code('ISU-invalid')}")
    print(f"   @raj_123   : {is_valid_username('@raj_123')}")
    print(f"   7682705436 : {is_valid_user_id(7682705436)}")
    print()
    
    # File icon
    print("📄 File Icons:")
    for fname in ["doc.pdf", "video.mp4", "song.mp3", "app.apk", "code.py"]:
        print(f"   {fname:>12} → {get_file_icon(fname)}")
    print()
    
    # Progress
    print("📊 Progress Bar:")
    for i in [0, 25, 50, 75, 100]:
        print(f"   {make_progress_bar(i, 100)}")
    print()
    
    # Number
    print("🔢 Humanize:")
    for n in [500, 1500, 1500000, 2500000000]:
        print(f"   {n:>15} → {humanize_number(n)}")
    print()
    
    # Session
    print("📋 Session Test:")
    sessions.set(123, "action", "upload")
    print(f"   Set: action=upload")
    print(f"   Get: {sessions.get(123, 'action')}")
    print(f"   Has: {sessions.has(123, 'action')}")
    sessions.clear(123)
    print(f"   After clear: {sessions.get(123, 'action')}")
    print()
    
    print("✅ Self-test complete!")
    print()


if __name__ == "__main__":
    _self_test()


# ═══════════════════════════════════════════════════════════════════════════
# 📖 END OF FILE
# ═══════════════════════════════════════════════════════════════════════════
#
# Total lines : ~1150+
# Functions   : 70+
#
# ═══════════════════════════════════════════════════════════════════════════