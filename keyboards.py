# ═══════════════════════════════════════════════════════════════════════════
# 🚀 ISUKOBIT — TELEGRAM FILE STORE BOT
# ═══════════════════════════════════════════════════════════════════════════
# File      : keyboards.py
# Purpose   : Saare inline aur reply keyboards
# Author    : Isukobit Team
# Version   : 1.0.0
# Python    : 3.10+
# Library   : aiogram 3.x
# ═══════════════════════════════════════════════════════════════════════════
#
# YEH FILE KYA KARTI HAI:
# ─────────────────────────────────────────────────────────────────────────
# 1. Main menu keyboards banati hai
# 2. Upload / My Files / Search ke keyboards
# 3. File preview keyboards (download, share, delete)
# 4. Admin panel ke saare keyboards
# 5. Settings, language, backup, broadcast ke keyboards
# 6. Confirmation dialogs (yes/no)
# 7. Pagination keyboards
# 8. Language-specific button labels
# 9. Reply keyboards (persistent bottom buttons)
#
# KAISE USE KARO:
# ─────────────────────────────────────────────────────────────────────────
# from keyboards import get_main_menu_keyboard
#
# kb = get_main_menu_keyboard(lang="hinglish", is_admin=True)
# await message.answer("Menu:", reply_markup=kb)
#
# ═══════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════
# 📦 IMPORTS
# ═══════════════════════════════════════════════════════════════════════════

from typing import List, Optional, Dict, Any

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)

from config import Constants, settings
from strings import get_string, get_language_flag, get_language_name


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 BUTTON LABELS — Language wise
# ═══════════════════════════════════════════════════════════════════════════

# Hinglish
BTN_LABELS = {
    "hinglish": {
        "upload": "📤 File Upload",
        "batch": "📦 Batch Upload",
        "my_files": "📁 Meri Files",
        "search": "🔍 Search",
        "stats": "📊 Statistics",
        "settings": "⚙️ Settings",
        "help": "❓ Madad",
        "about": "ℹ️ About",
        "admin": "👑 Admin Panel",
        "back": "⬅️ Wapas",
        "home": "🏠 Home",
        "close": "❌ Band Karo",
        "refresh": "🔄 Refresh",
        "next": "➡️ Aage",
        "prev": "⬅️ Peeche",
        "cancel": "❌ Cancel",
        "confirm": "✅ Haan",
        "verify": "✅ Verify",
        "join": "📢 Join Karo",
        "download": "📥 Download",
        "share": "🔗 Share",
        "delete": "🗑️ Delete",
        "rename": "✏️ Rename",
        "info": "ℹ️ Info",
        "qr": "📱 QR Code",
        "copy": "📋 Copy Link",
        "folder": "📂 Folder",
        "new_folder": "➕ Naya Folder",
        "move": "📦 Move",
        "premium": "💎 Premium",
        "language": "🌍 Language",
        "profile": "👤 Profile",
        "broadcast": "📣 Broadcast",
        "backup": "💾 Backup",
        "users": "👥 Users",
        "files": "📁 Files",
        "channels": "📢 Channels",
        "security": "🔐 Security",
        "maintenance": "🛠️ Maintenance",
        "logs": "📝 Logs",
        "health": "💚 Health Check",
        "restart": "🔄 Restart",
        "add_admin": "➕ Admin Add",
        "remove_admin": "➖ Admin Remove",
        "ban": "🚫 Ban",
        "unban": "✅ Unban",
        "search_user": "🔍 User Search",
        "search_file": "🔍 File Search",
        "export": "📤 Export",
        "import": "📥 Import",
        "danger": "⚠️ Danger Zone",
        "yes": "✅ Haan",
        "no": "❌ Nahi",
        "skip": "⏭️ Skip",
        "done": "✅ Done",
        "edit": "✏️ Edit",
        "add": "➕ Add",
        "remove": "➖ Remove",
        "list": "📋 List",
        "test": "🧪 Test",
        "enable": "🟢 Enable",
        "disable": "🔴 Disable",
        "on": "✅ ON",
        "off": "❌ OFF",
    },
    "english": {
        "upload": "📤 Upload File",
        "batch": "📦 Batch Upload",
        "my_files": "📁 My Files",
        "search": "🔍 Search",
        "stats": "📊 Statistics",
        "settings": "⚙️ Settings",
        "help": "❓ Help",
        "about": "ℹ️ About",
        "admin": "👑 Admin Panel",
        "back": "⬅️ Back",
        "home": "🏠 Home",
        "close": "❌ Close",
        "refresh": "🔄 Refresh",
        "next": "➡️ Next",
        "prev": "⬅️ Previous",
        "cancel": "❌ Cancel",
        "confirm": "✅ Yes",
        "verify": "✅ Verify",
        "join": "📢 Join",
        "download": "📥 Download",
        "share": "🔗 Share",
        "delete": "🗑️ Delete",
        "rename": "✏️ Rename",
        "info": "ℹ️ Info",
        "qr": "📱 QR Code",
        "copy": "📋 Copy Link",
        "folder": "📂 Folder",
        "new_folder": "➕ New Folder",
        "move": "📦 Move",
        "premium": "💎 Premium",
        "language": "🌍 Language",
        "profile": "👤 Profile",
        "broadcast": "📣 Broadcast",
        "backup": "💾 Backup",
        "users": "👥 Users",
        "files": "📁 Files",
        "channels": "📢 Channels",
        "security": "🔐 Security",
        "maintenance": "🛠️ Maintenance",
        "logs": "📝 Logs",
        "health": "💚 Health Check",
        "restart": "🔄 Restart",
        "add_admin": "➕ Add Admin",
        "remove_admin": "➖ Remove Admin",
        "ban": "🚫 Ban",
        "unban": "✅ Unban",
        "search_user": "🔍 Search User",
        "search_file": "🔍 Search File",
        "export": "📤 Export",
        "import": "📥 Import",
        "danger": "⚠️ Danger Zone",
        "yes": "✅ Yes",
        "no": "❌ No",
        "skip": "⏭️ Skip",
        "done": "✅ Done",
        "edit": "✏️ Edit",
        "add": "➕ Add",
        "remove": "➖ Remove",
        "list": "📋 List",
        "test": "🧪 Test",
        "enable": "🟢 Enable",
        "disable": "🔴 Disable",
        "on": "✅ ON",
        "off": "❌ OFF",
    },
    "nepali": {
        "upload": "📤 फाइल अपलोड",
        "batch": "📦 ब्याच अपलोड",
        "my_files": "📁 मेरा फाइलहरू",
        "search": "🔍 खोज",
        "stats": "📊 तथ्याङ्क",
        "settings": "⚙️ सेटिङ",
        "help": "❓ सहयोग",
        "about": "ℹ️ जानकारी",
        "admin": "👑 Admin Panel",
        "back": "⬅️ फर्कनुहोस्",
        "home": "🏠 गृह",
        "close": "❌ बन्द",
        "refresh": "🔄 रिफ्रेस",
        "next": "➡️ अर्को",
        "prev": "⬅️ अघिल्लो",
        "cancel": "❌ रद्द",
        "confirm": "✅ हो",
        "verify": "✅ Verify",
        "join": "📢 जोडिनुहोस्",
        "download": "📥 डाउनलोड",
        "share": "🔗 साझा",
        "delete": "🗑️ मेट्नुहोस्",
        "rename": "✏️ नाम परिवर्तन",
        "info": "ℹ️ जानकारी",
        "qr": "📱 QR कोड",
        "copy": "📋 लिङ्क कपी",
        "folder": "📂 फोल्डर",
        "new_folder": "➕ नयाँ फोल्डर",
        "move": "📦 सार्नुहोस्",
        "premium": "💎 प्रिमियम",
        "language": "🌍 भाषा",
        "profile": "👤 प्रोफाइल",
        "broadcast": "📣 प्रसारण",
        "backup": "💾 ब्याकअप",
        "users": "👥 प्रयोगकर्ता",
        "files": "📁 फाइलहरू",
        "channels": "📢 च्यानल",
        "security": "🔐 सुरक्षा",
        "maintenance": "🛠️ मर्मत",
        "logs": "📝 लगहरू",
        "health": "💚 Health Check",
        "restart": "🔄 रिस्टार्ट",
        "add_admin": "➕ Admin थप्नुहोस्",
        "remove_admin": "➖ Admin हटाउनुहोस्",
        "ban": "🚫 प्रतिबन्ध",
        "unban": "✅ प्रतिबन्ध हटाउनुहोस्",
        "search_user": "🔍 प्रयोगकर्ता खोज",
        "search_file": "🔍 फाइल खोज",
        "export": "📤 निर्यात",
        "import": "📥 आयात",
        "danger": "⚠️ खतरा",
        "yes": "✅ हो",
        "no": "❌ होइन",
        "skip": "⏭️ छोड्नुहोस्",
        "done": "✅ भयो",
        "edit": "✏️ सम्पादन",
        "add": "➕ थप्नुहोस्",
        "remove": "➖ हटाउनुहोस्",
        "list": "📋 सूची",
        "test": "🧪 परीक्षण",
        "enable": "🟢 सक्रिय",
        "disable": "🔴 निष्क्रिय",
        "on": "✅ ON",
        "off": "❌ OFF",
    },
    "latin": {
        "upload": "📤 Immittere",
        "batch": "📦 Gregatim",
        "my_files": "📁 Mei Fasciculi",
        "search": "🔍 Quaerere",
        "stats": "📊 Statistica",
        "settings": "⚙️ Optiones",
        "help": "❓ Auxilium",
        "about": "ℹ️ De Bot",
        "admin": "👑 Admin",
        "back": "⬅️ Retro",
        "home": "🏠 Domus",
        "close": "❌ Claude",
        "refresh": "🔄 Renovare",
        "next": "➡️ Proximo",
        "prev": "⬅️ Priori",
        "cancel": "❌ Cancellare",
        "confirm": "✅ Ita",
        "verify": "✅ Verify",
        "join": "📢 Iunge",
        "download": "📥 Deponere",
        "share": "🔗 Communica",
        "delete": "🗑️ Delere",
        "rename": "✏️ Renomina",
        "info": "ℹ️ Info",
        "qr": "📱 Codex QR",
        "copy": "📋 Copiare",
        "folder": "📂 Scrinium",
        "new_folder": "➕ Novum Scrinium",
        "move": "📦 Movere",
        "premium": "💎 Premium",
        "language": "🌍 Lingua",
        "profile": "👤 Profilum",
        "broadcast": "📣 Disseminare",
        "backup": "💾 Backup",
        "users": "👥 Usatores",
        "files": "📁 Fasciculi",
        "channels": "📢 Canales",
        "security": "🔐 Securitas",
        "maintenance": "🛠️ Sustentatio",
        "logs": "📝 Acta",
        "health": "💚 Salus",
        "restart": "🔄 Restart",
        "add_admin": "➕ Addere Admin",
        "remove_admin": "➖ Removere Admin",
        "ban": "🚫 Interdicere",
        "unban": "✅ Purgare",
        "search_user": "🔍 Quaerere Usatorem",
        "search_file": "🔍 Quaerere Fasciculum",
        "export": "📤 Exportare",
        "import": "📥 Importare",
        "danger": "⚠️ Periculum",
        "yes": "✅ Ita",
        "no": "❌ Non",
        "skip": "⏭️ Transilire",
        "done": "✅ Factum",
        "edit": "✏️ Emendare",
        "add": "➕ Addere",
        "remove": "➖ Removere",
        "list": "📋 Index",
        "test": "🧪 Probare",
        "enable": "🟢 Activare",
        "disable": "🔴 Deactivare",
        "on": "✅ ON",
        "off": "❌ OFF",
    },
}


def btn(key: str, lang: str = "hinglish") -> str:
    """Button label nikalta hai language ke hisaab se"""
    labels = BTN_LABELS.get(lang, BTN_LABELS["hinglish"])
    return labels.get(key, BTN_LABELS["hinglish"].get(key, key))


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 CALLBACK DATA PREFIXES
# ═══════════════════════════════════════════════════════════════════════════

class CB:
    """Callback data constants"""
    
    # Main
    MENU = "menu"
    HOME = "home"
    BACK = "back"
    CLOSE = "close"
    CANCEL = "cancel"
    REFRESH = "refresh"
    
    # Navigation
    PAGE = "page"
    NEXT = "next"
    PREV = "prev"
    NOOP = "noop"
    
    # Actions
    UPLOAD = "upload"
    MY_FILES = "myfiles"
    SEARCH = "search"
    STATS = "stats"
    HELP = "help"
    ABOUT = "about"
    PROFILE = "profile"
    SETTINGS = "settings"
    
    # File
    FILE = "file"
    FILE_INFO = "finfo"
    FILE_DL = "fdl"
    FILE_SHARE = "fshare"
    FILE_QR = "fqr"
    FILE_DEL = "fdel"
    FILE_RENAME = "fren"
    FILE_MOVE = "fmov"
    FILE_COPY = "fcopy"

    # Bulk delete
    FILE_BULK = "fbulk"
    DSEL = "dsel"
    DSEL_PAGE = "dselp"
    DSEL_ALL = "dsela"
    DSEL_DEL = "dseld"
    DSEL_CONF = "dself"
    DSEL_CANCEL = "dselx"
    DEL_ALL = "fdela"
    DEL_ALL_CONF = "fdelc"
    
    # Folder
    FOLDER = "folder"
    FOLDER_NEW = "fnew"
    FOLDER_DEL = "fdel"
    FOLDER_REN = "fren"
    FOLDER_OPEN = "fopen"
    
    # Confirm
    CONFIRM = "confirm"
    REJECT = "reject"
    
    # Language
    LANG = "lang"
    LANG_SET = "langset"
    
    # Admin
    ADMIN = "admin"
    ADMIN_STATS = "astats"
    ADMIN_USERS = "ausers"
    ADMIN_FILES = "afiles"
    ADMIN_BROADCAST = "abc"
    ADMIN_BACKUP = "abk"
    ADMIN_SETTINGS = "aset"
    ADMIN_CHANNELS = "ach"
    ADMIN_SECURITY = "asec"
    ADMIN_MAINTENANCE = "amaint"
    ADMIN_LOGS = "alogs"
    ADMIN_HEALTH = "ahealth"
    ADMIN_RESTART = "arestart"
    ADMIN_ADD = "aadd"
    ADMIN_REMOVE = "arem"
    ADMIN_BAN = "aban"
    ADMIN_UNBAN = "aunban"
    ADMIN_SEARCH_USER = "asu"
    ADMIN_SEARCH_FILE = "asf"
    ADMIN_DELETE_FILE = "adelf"
    ADMIN_EXPORT = "aexp"
    ADMIN_IMPORT = "aimp"
    ADMIN_DANGER = "adanger"
    
    # Force Join
    FORCE_JOIN = "fjoin"
    VERIFY = "verify"
    
    # Broadcast
    BC_CONFIRM = "bcc"
    BC_CANCEL = "bcx"

    # Batch
    BATCH = "batch"
    BATCH_DONE = "bdone"
    BATCH_CANCEL = "bcancel"
    BATCH_DL_ALL = "bdlall"
    
    # Settings keys
    SET = "set"


# ═══════════════════════════════════════════════════════════════════════════
# 🏠 MAIN MENU KEYBOARD
# ═══════════════════════════════════════════════════════════════════════════

def get_main_menu_keyboard(
    lang: str = "hinglish",
    is_admin: bool = False,
    is_owner: bool = False,
) -> InlineKeyboardMarkup:
    """
    Main menu ka inline keyboard banata hai.
    
    Layout:
    ┌──────────────────┬──────────────────┐
    │  📤 Upload       │  📁 My Files     │
    ├──────────────────┼──────────────────┤
    │  🔍 Search       │  👤 Profile      │
    ├──────────────────┼──────────────────┤
    │  📊 Stats        │  ⚙️ Settings     │
    ├──────────────────┼──────────────────┤
    │  ❓ Help         │  ℹ️ About        │
    ├──────────────────┴──────────────────┤
    │         👑 Admin Panel              │
    └─────────────────────────────────────┘
    """
    buttons = [
        # Row 1
        [
            InlineKeyboardButton(
                text=btn("upload", lang),
                callback_data=CB.UPLOAD
            ),
            InlineKeyboardButton(
                text=btn("my_files", lang),
                callback_data=CB.MY_FILES
            ),
        ],
        # Row 2
        [
            InlineKeyboardButton(
                text=btn("search", lang),
                callback_data=CB.SEARCH
            ),
            InlineKeyboardButton(
                text=btn("profile", lang),
                callback_data=CB.PROFILE
            ),
        ],
        # Row 3
        [
            InlineKeyboardButton(
                text=btn("stats", lang),
                callback_data=CB.STATS
            ),
            InlineKeyboardButton(
                text=btn("settings", lang),
                callback_data=CB.SETTINGS
            ),
        ],
        # Row 4
        [
            InlineKeyboardButton(
                text=btn("help", lang),
                callback_data=CB.HELP
            ),
            InlineKeyboardButton(
                text=btn("about", lang),
                callback_data=CB.ABOUT
            ),
        ],
    ]
    
    # Admin row (only for admins)
    if is_admin or is_owner:
        admin_text = btn("admin", lang)
        if is_owner:
            admin_text = "👑 Owner Panel"
        buttons.append([
            InlineKeyboardButton(
                text=admin_text,
                callback_data=CB.ADMIN
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_main_menu_reply_keyboard(
    lang: str = "hinglish",
    is_admin: bool = False,
) -> ReplyKeyboardMarkup:
    """
    Main menu ka reply keyboard (persistent bottom buttons).
    """
    keyboard = [
        [
            KeyboardButton(text=btn("upload", lang)),
            KeyboardButton(text=btn("my_files", lang)),
        ],
        [
            KeyboardButton(text=btn("search", lang)),
            KeyboardButton(text=btn("profile", lang)),
        ],
        [
            KeyboardButton(text=btn("stats", lang)),
            KeyboardButton(text=btn("help", lang)),
        ],
    ]
    
    if is_admin:
        keyboard.append([
            KeyboardButton(text=btn("admin", lang))
        ])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Choose an option..."
    )


def get_back_button(
    lang: str = "hinglish",
    callback: str = CB.HOME,
    extra_row: Optional[List[InlineKeyboardButton]] = None
) -> InlineKeyboardMarkup:
    """Simple back button keyboard"""
    buttons = []
    
    if extra_row:
        buttons.append(extra_row)
    
    buttons.append([
        InlineKeyboardButton(
            text=btn("back", lang),
            callback_data=callback
        ),
        InlineKeyboardButton(
            text=btn("home", lang),
            callback_data=CB.HOME
        ),
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_close_keyboard(lang: str = "hinglish") -> InlineKeyboardMarkup:
    """Close button"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=btn("close", lang),
            callback_data=CB.CLOSE
        )]
    ])


# ═══════════════════════════════════════════════════════════════════════════
# 📤 UPLOAD KEYBOARDS
# ═══════════════════════════════════════════════════════════════════════════

def get_upload_keyboard(lang: str = "hinglish") -> InlineKeyboardMarkup:
    """Upload menu keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=btn("batch", lang),
                callback_data=CB.BATCH
            ),
        ],
        [
            InlineKeyboardButton(
                text=btn("my_files", lang),
                callback_data=CB.MY_FILES
            ),
        ],
        [
            InlineKeyboardButton(
                text=btn("cancel", lang),
                callback_data=CB.CANCEL
            ),
        ],
    ])


def get_batch_prompt_keyboard(lang: str = "hinglish") -> InlineKeyboardMarkup:
    """Batch mode — Done/Cancel buttons"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Done (Link Banao)",
                callback_data=CB.BATCH_DONE
            ),
            InlineKeyboardButton(
                text=btn("cancel", lang),
                callback_data=CB.BATCH_CANCEL
            ),
        ],
    ])


def get_batch_success_keyboard(batch_code: str, lang: str = "hinglish") -> InlineKeyboardMarkup:
    """Batch banne ke baad"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=btn("my_files", lang),
                callback_data=CB.MY_FILES
            ),
            InlineKeyboardButton(
                text=btn("upload", lang),
                callback_data=CB.UPLOAD
            ),
        ],
        [
            InlineKeyboardButton(
                text=btn("home", lang),
                callback_data=CB.HOME
            ),
        ],
    ])


def get_batch_view_keyboard(
    files: List[Dict[str, Any]],
    batch_code: str,
    lang: str = "hinglish"
) -> InlineKeyboardMarkup:
    """Batch ki files list — har file ka download button"""
    buttons = []

    for f in files[:15]:
        file_name = f.get("file_name", "file")
        if len(file_name) > 25:
            file_name = file_name[:22] + "..."
        size_str = format_file_size(f.get("file_size", 0))
        buttons.append([
            InlineKeyboardButton(
                text=f"📄 {file_name} ({size_str})",
                callback_data=f"{CB.FILE_DL}:{f.get('file_code')}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="📥 Sab Download Karo (1-1 karke)",
            callback_data=f"{CB.BATCH_DL_ALL}:{batch_code}"
        )
    ])

    buttons.append([
        InlineKeyboardButton(
            text=btn("home", lang),
            callback_data=CB.HOME
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_upload_success_keyboard(
    file_code: str,
    lang: str = "hinglish"
) -> InlineKeyboardMarkup:
    """Upload success ke baad keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=btn("info", lang),
                callback_data=f"{CB.FILE_INFO}:{file_code}"
            ),
            InlineKeyboardButton(
                text=btn("share", lang),
                callback_data=f"{CB.FILE_SHARE}:{file_code}"
            ),
        ],
        [
            InlineKeyboardButton(
                text=btn("upload", lang),
                callback_data=CB.UPLOAD
            ),
            InlineKeyboardButton(
                text=btn("my_files", lang),
                callback_data=CB.MY_FILES
            ),
        ],
        [
            InlineKeyboardButton(
                text=btn("home", lang),
                callback_data=CB.HOME
            ),
        ],
    ])


# ═══════════════════════════════════════════════════════════════════════════
# 📁 MY FILES KEYBOARDS
# ═══════════════════════════════════════════════════════════════════════════

def get_my_files_keyboard(
    files: List[Dict[str, Any]],
    page: int,
    total_pages: int,
    lang: str = "hinglish",
    has_folder_support: bool = True,
) -> InlineKeyboardMarkup:
    """
    Files list ka keyboard — har file ke liye ek button.
    """
    buttons = []
    
    # File buttons (max 10 per page)
    for f in files:
        file_name = f.get("file_name", "Unknown")
        if len(file_name) > 30:
            file_name = file_name[:27] + "..."
        
        file_size = f.get("file_size", 0)
        size_str = format_file_size(file_size)
        
        buttons.append([
            InlineKeyboardButton(
                text=f"📄 {file_name} ({size_str})",
                callback_data=f"{CB.FILE}:{f.get('id')}"
            )
        ])
    
    # Pagination
    if total_pages > 1:
        buttons.append(build_pagination_row(page, total_pages, "myfiles"))
    
    # Actions row
    action_row = []
    if has_folder_support:
        action_row.append(InlineKeyboardButton(
            text=btn("new_folder", lang),
            callback_data=CB.FOLDER_NEW
        ))
    action_row.append(InlineKeyboardButton(
        text=btn("upload", lang),
        callback_data=CB.UPLOAD
    ))
    buttons.append(action_row)
    
    # Bulk delete row
    buttons.append([
        InlineKeyboardButton(
            text="🗑️ Select & Delete",
            callback_data=CB.FILE_BULK
        ),
    ])

    # Navigation row
    buttons.append([
        InlineKeyboardButton(
            text=btn("refresh", lang),
            callback_data=f"myfiles:refresh"
        ),
        InlineKeyboardButton(
            text=btn("home", lang),
            callback_data=CB.HOME
        ),
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_empty_files_keyboard(lang: str = "hinglish") -> InlineKeyboardMarkup:
    """Jab user ki koi file nahi ho"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=btn("upload", lang),
                callback_data=CB.UPLOAD
            ),
        ],
        [
            InlineKeyboardButton(
                text=btn("home", lang),
                callback_data=CB.HOME
            ),
        ],
    ])


def get_file_actions_keyboard(
    file_code: str,
    is_owner: bool = True,
    lang: str = "hinglish"
) -> InlineKeyboardMarkup:
    """
    Ek file ke actions — Download, Share, Info, Delete, Rename.
    """
    buttons = []
    
    # Row 1: Download + Share
    buttons.append([
        InlineKeyboardButton(
            text=btn("download", lang),
            callback_data=f"{CB.FILE_DL}:{file_code}"
        ),
        InlineKeyboardButton(
            text=btn("share", lang),
            callback_data=f"{CB.FILE_SHARE}:{file_code}"
        ),
    ])
    
    # Row 2: Info + QR
    buttons.append([
        InlineKeyboardButton(
            text=btn("info", lang),
            callback_data=f"{CB.FILE_INFO}:{file_code}"
        ),
        InlineKeyboardButton(
            text=btn("qr", lang),
            callback_data=f"{CB.FILE_QR}:{file_code}"
        ),
    ])
    
    # Row 3: Rename + Move (only for owner)
    if is_owner:
        buttons.append([
            InlineKeyboardButton(
                text=btn("rename", lang),
                callback_data=f"{CB.FILE_RENAME}:{file_code}"
            ),
            InlineKeyboardButton(
                text=btn("move", lang),
                callback_data=f"{CB.FILE_MOVE}:{file_code}"
            ),
        ])
        
        # Row 4: Delete
        buttons.append([
            InlineKeyboardButton(
                text=btn("delete", lang),
                callback_data=f"{CB.FILE_DEL}:{file_code}"
            ),
        ])
    
    # Row 5: Back
    buttons.append([
        InlineKeyboardButton(
            text=btn("back", lang),
            callback_data=CB.MY_FILES
        ),
        InlineKeyboardButton(
            text=btn("home", lang),
            callback_data=CB.HOME
        ),
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_file_confirm_delete_keyboard(
    file_code: str,
    lang: str = "hinglish"
) -> InlineKeyboardMarkup:
    """Delete confirmation ke liye"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=btn("yes", lang),
                callback_data=f"{CB.CONFIRM}:del:{file_code}"
            ),
            InlineKeyboardButton(
                text=btn("no", lang),
                callback_data=f"{CB.FILE}:{file_code}"
            ),
        ],
    ])


def get_file_info_keyboard(
    file_code: str,
    lang: str = "hinglish"
) -> InlineKeyboardMarkup:
    """File info ke baad keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=btn("download", lang),
                callback_data=f"{CB.FILE_DL}:{file_code}"
            ),
            InlineKeyboardButton(
                text=btn("share", lang),
                callback_data=f"{CB.FILE_SHARE}:{file_code}"
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


# ═══════════════════════════════════════════════════════════════════════════
# 🔍 SEARCH KEYBOARDS
# ═══════════════════════════════════════════════════════════════════════════

def get_search_keyboard(lang: str = "hinglish") -> InlineKeyboardMarkup:
    """Search prompt ka keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=btn("cancel", lang),
                callback_data=CB.CANCEL
            ),
            InlineKeyboardButton(
                text=btn("home", lang),
                callback_data=CB.HOME
            ),
        ],
    ])


def get_search_results_keyboard(
    files: List[Dict[str, Any]],
    query: str,
    page: int,
    total_pages: int,
    lang: str = "hinglish"
) -> InlineKeyboardMarkup:
    """Search results keyboard"""
    buttons = []
    
    # File buttons
    for f in files:
        file_name = f.get("file_name", "Unknown")
        if len(file_name) > 28:
            file_name = file_name[:25] + "..."
        
        size_str = format_file_size(f.get("file_size", 0))
        
        buttons.append([
            InlineKeyboardButton(
                text=f"📄 {file_name} ({size_str})",
                callback_data=f"{CB.FILE}:{f.get('id')}"
            )
        ])
    
    # Pagination
    if total_pages > 1:
        # Truncate query for callback data (64 char limit)
        q_short = query[:20]
        buttons.append(build_pagination_row(page, total_pages, f"srch:{q_short}"))
    
    # Actions
    buttons.append([
        InlineKeyboardButton(
            text=btn("search", lang),
            callback_data=CB.SEARCH
        ),
        InlineKeyboardButton(
            text=btn("home", lang),
            callback_data=CB.HOME
        ),
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_no_results_keyboard(lang: str = "hinglish") -> InlineKeyboardMarkup:
    """No search results keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=btn("search", lang),
                callback_data=CB.SEARCH
            ),
            InlineKeyboardButton(
                text=btn("home", lang),
                callback_data=CB.HOME
            ),
        ],
    ])


# ═══════════════════════════════════════════════════════════════════════════
# 📊 STATS KEYBOARDS
# ═══════════════════════════════════════════════════════════════════════════

def get_stats_keyboard(lang: str = "hinglish") -> InlineKeyboardMarkup:
    """Stats page keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=btn("refresh", lang),
                callback_data=CB.STATS
            ),
        ],
        [
            InlineKeyboardButton(
                text=btn("home", lang),
                callback_data=CB.HOME
            ),
        ],
    ])


def get_profile_keyboard(lang: str = "hinglish") -> InlineKeyboardMarkup:
    """Profile keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=btn("my_files", lang),
                callback_data=CB.MY_FILES
            ),
        ],
        [
            InlineKeyboardButton(
                text=btn("settings", lang),
                callback_data=CB.SETTINGS
            ),
            InlineKeyboardButton(
                text=btn("home", lang),
                callback_data=CB.HOME
            ),
        ],
    ])


# ═══════════════════════════════════════════════════════════════════════════
# ⚙️ SETTINGS KEYBOARDS
# ═══════════════════════════════════════════════════════════════════════════

def get_settings_keyboard(
    user_lang: str,
    lang: str = "hinglish"
) -> InlineKeyboardMarkup:
    """User settings keyboard"""
    current_flag = get_language_flag(user_lang)
    current_name = get_language_name(user_lang)
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{btn('language', lang)} ({current_flag} {current_name})",
                callback_data=CB.LANG
            ),
        ],
        [
            InlineKeyboardButton(
                text=btn("profile", lang),
                callback_data=CB.PROFILE
            ),
            InlineKeyboardButton(
                text=btn("home", lang),
                callback_data=CB.HOME
            ),
        ],
    ])


def get_language_selection_keyboard(
    current_lang: str = "hinglish"
) -> InlineKeyboardMarkup:
    """Language selection keyboard"""
    from strings import SUPPORTED_LANGUAGES, LANGUAGE_NAMES_NATIVE, LANGUAGE_FLAGS
    
    buttons = []
    
    for lang_code in SUPPORTED_LANGUAGES:
        flag = LANGUAGE_FLAGS.get(lang_code, "🌍")
        name = LANGUAGE_NAMES_NATIVE.get(lang_code, lang_code)
        
        # Current language pe checkmark
        prefix = "✅ " if lang_code == current_lang else ""
        
        buttons.append([
            InlineKeyboardButton(
                text=f"{prefix}{flag} {name}",
                callback_data=f"{CB.LANG_SET}:{lang_code}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(
            text=btn("back", current_lang),
            callback_data=CB.SETTINGS
        ),
        InlineKeyboardButton(
            text=btn("home", current_lang),
            callback_data=CB.HOME
        ),
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ═══════════════════════════════════════════════════════════════════════════
# ❓ HELP & ABOUT KEYBOARDS
# ═══════════════════════════════════════════════════════════════════════════

def get_help_keyboard(
    lang: str = "hinglish",
    support_username: str = ""
) -> InlineKeyboardMarkup:
    """Help page keyboard"""
    buttons = []
    
    if support_username:
        buttons.append([
            InlineKeyboardButton(
                text="📞 Contact Support",
                url=f"https://t.me/{support_username.lstrip('@')}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(
            text=btn("about", lang),
            callback_data=CB.ABOUT
        ),
        InlineKeyboardButton(
            text=btn("home", lang),
            callback_data=CB.HOME
        ),
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_about_keyboard(
    lang: str = "hinglish",
    update_channel: str = ""
) -> InlineKeyboardMarkup:
    """About page keyboard"""
    buttons = []
    
    if update_channel:
        buttons.append([
            InlineKeyboardButton(
                text="📢 Updates Channel",
                url=f"https://t.me/{update_channel.lstrip('@')}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(
            text=btn("help", lang),
            callback_data=CB.HELP
        ),
        InlineKeyboardButton(
            text=btn("home", lang),
            callback_data=CB.HOME
        ),
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ═══════════════════════════════════════════════════════════════════════════
# 📢 FORCE JOIN KEYBOARD
# ═══════════════════════════════════════════════════════════════════════════

def get_force_join_keyboard(
    channels: List[Dict[str, str]],
    lang: str = "hinglish"
) -> InlineKeyboardMarkup:
    """
    Force join keyboard with channel links + verify button.
    
    channels: [{"name": "...", "url": "..."}, ...]
    """
    buttons = []
    
    for ch in channels:
        if ch.get("url"):
            buttons.append([
                InlineKeyboardButton(
                    text=f"📢 {ch.get('name', 'Join')}",
                    url=ch["url"]
                )
            ])
    
    # Verify button
    buttons.append([
        InlineKeyboardButton(
            text=btn("verify", lang),
            callback_data=CB.VERIFY
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ═══════════════════════════════════════════════════════════════════════════
# 👑 ADMIN PANEL KEYBOARD
# ═══════════════════════════════════════════════════════════════════════════

def get_admin_panel_keyboard(
    lang: str = "hinglish",
    is_owner: bool = False,
) -> InlineKeyboardMarkup:
    """
    Admin panel main menu.
    """
    buttons = [
        # Row 1: Stats + Users
        [
            InlineKeyboardButton(
                text=btn("stats", lang),
                callback_data=CB.ADMIN_STATS
            ),
            InlineKeyboardButton(
                text=btn("users", lang),
                callback_data=CB.ADMIN_USERS
            ),
        ],
        # Row 2: Files + Broadcast
        [
            InlineKeyboardButton(
                text=btn("files", lang),
                callback_data=CB.ADMIN_FILES
            ),
            InlineKeyboardButton(
                text=btn("broadcast", lang),
                callback_data=CB.ADMIN_BROADCAST
            ),
        ],
        # Row 3: Backup + Settings
        [
            InlineKeyboardButton(
                text=btn("backup", lang),
                callback_data=CB.ADMIN_BACKUP
            ),
            InlineKeyboardButton(
                text=btn("settings", lang),
                callback_data=CB.ADMIN_SETTINGS
            ),
        ],
        # Row 4: Channels + Security
        [
            InlineKeyboardButton(
                text=btn("channels", lang),
                callback_data=CB.ADMIN_CHANNELS
            ),
            InlineKeyboardButton(
                text=btn("security", lang),
                callback_data=CB.ADMIN_SECURITY
            ),
        ],
        # Row 5: Maintenance + Logs
        [
            InlineKeyboardButton(
                text=btn("maintenance", lang),
                callback_data=CB.ADMIN_MAINTENANCE
            ),
            InlineKeyboardButton(
                text=btn("logs", lang),
                callback_data=CB.ADMIN_LOGS
            ),
        ],
        # Row 6: Health + Restart
        [
            InlineKeyboardButton(
                text=btn("health", lang),
                callback_data=CB.ADMIN_HEALTH
            ),
            InlineKeyboardButton(
                text=btn("restart", lang),
                callback_data=CB.ADMIN_RESTART
            ),
        ],
    ]
    
    # Owner only row
    if is_owner:
        buttons.append([
            InlineKeyboardButton(
                text=btn("add_admin", lang),
                callback_data=CB.ADMIN_ADD
            ),
            InlineKeyboardButton(
                text=btn("remove_admin", lang),
                callback_data=CB.ADMIN_REMOVE
            ),
        ])
        
        buttons.append([
            InlineKeyboardButton(
                text=btn("danger", lang),
                callback_data=CB.ADMIN_DANGER
            ),
        ])
    
    # Back to home
    buttons.append([
        InlineKeyboardButton(
            text=btn("home", lang),
            callback_data=CB.HOME
        ),
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_stats_keyboard(lang: str = "hinglish") -> InlineKeyboardMarkup:
    """Admin stats keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=btn("refresh", lang),
                callback_data=CB.ADMIN_STATS
            ),
        ],
        [
            InlineKeyboardButton(
                text=btn("back", lang),
                callback_data=CB.ADMIN
            ),
            InlineKeyboardButton(
                text=btn("home", lang),
                callback_data=CB.HOME
            ),
        ],
    ])


# ═══════════════════════════════════════════════════════════════════════════
# 👥 ADMIN — USER MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

def get_admin_users_keyboard(
    lang: str = "hinglish"
) -> InlineKeyboardMarkup:
    """Admin users menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=btn("search_user", lang),
                callback_data=CB.ADMIN_SEARCH_USER
            ),
        ],
        [
            InlineKeyboardButton(
                text=btn("ban", lang),
                callback_data=CB.ADMIN_BAN
            ),
            InlineKeyboardButton(
                text=btn("unban", lang),
                callback_data=CB.ADMIN_UNBAN
            ),
        ],
        [
            InlineKeyboardButton(
                text=btn("list", lang),
                callback_data=f"{CB.ADMIN_USERS}:list"
            ),
        ],
        [
            InlineKeyboardButton(
                text=btn("back", lang),
                callback_data=CB.ADMIN
            ),
            InlineKeyboardButton(
                text=btn("home", lang),
                callback_data=CB.HOME
            ),
        ],
    ])


def get_admin_user_list_keyboard(
    users: List[Dict[str, Any]],
    page: int,
    total_pages: int,
    lang: str = "hinglish"
) -> InlineKeyboardMarkup:
    """User list keyboard"""
    buttons = []
    
    for u in users:
        name = u.get("first_name", "Unknown")
        if len(name) > 20:
            name = name[:17] + "..."
        
        uid = u.get("user_id", 0)
        is_banned = u.get("is_banned", False)
        is_admin = u.get("is_admin", False)
        
        prefix = "🚫 " if is_banned else ("👑 " if is_admin else "👤 ")
        
        buttons.append([
            InlineKeyboardButton(
                text=f"{prefix}{name} [{uid}]",
                callback_data=f"{CB.ADMIN_USERS}:view:{uid}"
            )
        ])
    
    # Pagination
    if total_pages > 1:
        buttons.append(build_pagination_row(page, total_pages, "ausers:list"))
    
    buttons.append([
        InlineKeyboardButton(
            text=btn("back", lang),
            callback_data=CB.ADMIN_USERS
        ),
        InlineKeyboardButton(
            text=btn("home", lang),
            callback_data=CB.HOME
        ),
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_user_actions_keyboard(
    user_id: int,
    is_banned: bool = False,
    is_admin: bool = False,
    lang: str = "hinglish"
) -> InlineKeyboardMarkup:
    """Ek user ke actions"""
    buttons = []
    
    # Ban / Unban
    if is_banned:
        buttons.append([
            InlineKeyboardButton(
                text=btn("unban", lang),
                callback_data=f"{CB.ADMIN_UNBAN}:{user_id}"
            ),
        ])
    else:
        buttons.append([
            InlineKeyboardButton(
                text=btn("ban", lang),
                callback_data=f"{CB.ADMIN_BAN}:{user_id}"
            ),
        ])
    
    # Admin toggle
    if is_admin:
        buttons.append([
            InlineKeyboardButton(
                text=btn("remove_admin", lang),
                callback_data=f"{CB.ADMIN_REMOVE}:{user_id}"
            ),
        ])
    else:
        buttons.append([
            InlineKeyboardButton(
                text=btn("add_admin", lang),
                callback_data=f"{CB.ADMIN_ADD}:{user_id}"
            ),
        ])
    
    buttons.append([
        InlineKeyboardButton(
            text=btn("back", lang),
            callback_data=f"{CB.ADMIN_USERS}:list"
        ),
        InlineKeyboardButton(
            text=btn("home", lang),
            callback_data=CB.HOME
        ),
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ═══════════════════════════════════════════════════════════════════════════
# 📁 ADMIN — FILE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

def get_admin_files_keyboard(lang: str = "hinglish") -> InlineKeyboardMarkup:
    """Admin files menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=btn("search_file", lang),
                callback_data=CB.ADMIN_SEARCH_FILE
            ),
        ],
        [
            InlineKeyboardButton(
                text=btn("delete", lang),
                callback_data=CB.ADMIN_DELETE_FILE
            ),
        ],
        [
            InlineKeyboardButton(
                text=btn("export", lang),
                callback_data=CB.ADMIN_EXPORT
            ),
            InlineKeyboardButton(
                text=btn("import", lang),
                callback_data=CB.ADMIN_IMPORT
            ),
        ],
        [
            InlineKeyboardButton(
                text=btn("back", lang),
                callback_data=CB.ADMIN
            ),
            InlineKeyboardButton(
                text=btn("home", lang),
                callback_data=CB.HOME
            ),
        ],
    ])


# ═══════════════════════════════════════════════════════════════════════════
# 📣 ADMIN — BROADCAST
# ═══════════════════════════════════════════════════════════════════════════

def get_admin_broadcast_keyboard(lang: str = "hinglish") -> InlineKeyboardMarkup:
    """Broadcast menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=btn("cancel", lang),
                callback_data=CB.CANCEL
            ),
        ],
    ])


def get_broadcast_confirm_keyboard(
    lang: str = "hinglish"
) -> InlineKeyboardMarkup:
    """Broadcast confirm"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=btn("yes", lang),
                callback_data=CB.BC_CONFIRM
            ),
            InlineKeyboardButton(
                text=btn("no", lang),
                callback_data=CB.BC_CANCEL
            ),
        ],
    ])


# ═══════════════════════════════════════════════════════════════════════════
# 💾 ADMIN — BACKUP
# ═══════════════════════════════════════════════════════════════════════════

def get_admin_backup_keyboard(lang: str = "hinglish") -> InlineKeyboardMarkup:
    """Backup menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💾 Create Backup Now",
                callback_data=f"{CB.ADMIN_BACKUP}:create"
            ),
        ],
        [
            InlineKeyboardButton(
                text="📋 List Backups",
                callback_data=f"{CB.ADMIN_BACKUP}:list"
            ),
            InlineKeyboardButton(
                text="🧹 Cleanup Old",
                callback_data=f"{CB.ADMIN_BACKUP}:cleanup"
            ),
        ],
        [
            InlineKeyboardButton(
                text=btn("back", lang),
                callback_data=CB.ADMIN
            ),
            InlineKeyboardButton(
                text=btn("home", lang),
                callback_data=CB.HOME
            ),
        ],
    ])


# ═══════════════════════════════════════════════════════════════════════════
# 📢 ADMIN — CHANNELS
# ═══════════════════════════════════════════════════════════════════════════

def get_admin_channels_keyboard(lang: str = "hinglish") -> InlineKeyboardMarkup:
    """Channels management"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📥 Storage Channel",
                callback_data=f"{CB.ADMIN_CHANNELS}:storage"
            ),
        ],
        [
            InlineKeyboardButton(
                text="💾 Backup Channel",
                callback_data=f"{CB.ADMIN_CHANNELS}:backup"
            ),
        ],
        [
            InlineKeyboardButton(
                text="📝 Log Channel",
                callback_data=f"{CB.ADMIN_CHANNELS}:log"
            ),
        ],
        [
            InlineKeyboardButton(
                text="📢 Force Join",
                callback_data=f"{CB.ADMIN_CHANNELS}:force_join"
            ),
        ],
        [
            InlineKeyboardButton(
                text=btn("back", lang),
                callback_data=CB.ADMIN
            ),
            InlineKeyboardButton(
                text=btn("home", lang),
                callback_data=CB.HOME
            ),
        ],
    ])


# ═══════════════════════════════════════════════════════════════════════════
# 🔐 ADMIN — SECURITY
# ═══════════════════════════════════════════════════════════════════════════

def get_admin_security_keyboard(
    anti_spam: bool = True,
    maintenance: bool = False,
    lang: str = "hinglish"
) -> InlineKeyboardMarkup:
    """Security settings keyboard"""
    spam_text = f"Anti-Spam: {btn('on', lang) if anti_spam else btn('off', lang)}"
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=spam_text,
                callback_data=f"{CB.ADMIN_SECURITY}:toggle_spam"
            ),
        ],
        [
            InlineKeyboardButton(
                text="⏱️ Rate Limit",
                callback_data=f"{CB.ADMIN_SECURITY}:rate_limit"
            ),
            InlineKeyboardButton(
                text="🔒 User Lock",
                callback_data=f"{CB.ADMIN_SECURITY}:user_lock"
            ),
        ],
        [
            InlineKeyboardButton(
                text=btn("back", lang),
                callback_data=CB.ADMIN
            ),
            InlineKeyboardButton(
                text=btn("home", lang),
                callback_data=CB.HOME
            ),
        ],
    ])


# ═══════════════════════════════════════════════════════════════════════════
# 🛠️ ADMIN — MAINTENANCE
# ═══════════════════════════════════════════════════════════════════════════

def get_admin_maintenance_keyboard(
    is_on: bool = False,
    lang: str = "hinglish"
) -> InlineKeyboardMarkup:
    """Maintenance keyboard"""
    toggle_text = "✅ Turn OFF" if is_on else "🛠️ Turn ON"
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=toggle_text,
                callback_data=f"{CB.ADMIN_MAINTENANCE}:toggle"
            ),
        ],
        [
            InlineKeyboardButton(
                text="✏️ Edit Message",
                callback_data=f"{CB.ADMIN_MAINTENANCE}:edit"
            ),
        ],
        [
            InlineKeyboardButton(
                text=btn("back", lang),
                callback_data=CB.ADMIN
            ),
            InlineKeyboardButton(
                text=btn("home", lang),
                callback_data=CB.HOME
            ),
        ],
    ])


# ═══════════════════════════════════════════════════════════════════════════
# 📝 ADMIN — LOGS
# ═══════════════════════════════════════════════════════════════════════════

def get_admin_logs_keyboard(lang: str = "hinglish") -> InlineKeyboardMarkup:
    """Logs filter keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📥 Downloads",
                callback_data=f"{CB.ADMIN_LOGS}:downloads"
            ),
            InlineKeyboardButton(
                text="📤 Uploads",
                callback_data=f"{CB.ADMIN_LOGS}:uploads"
            ),
        ],
        [
            InlineKeyboardButton(
                text="👥 Users",
                callback_data=f"{CB.ADMIN_LOGS}:users"
            ),
            InlineKeyboardButton(
                text="🚨 Errors",
                callback_data=f"{CB.ADMIN_LOGS}:errors"
            ),
        ],
        [
            InlineKeyboardButton(
                text="📋 All Logs",
                callback_data=f"{CB.ADMIN_LOGS}:all"
            ),
        ],
        [
            InlineKeyboardButton(
                text=btn("back", lang),
                callback_data=CB.ADMIN
            ),
            InlineKeyboardButton(
                text=btn("home", lang),
                callback_data=CB.HOME
            ),
        ],
    ])


# ═══════════════════════════════════════════════════════════════════════════
# 🎛️ ADMIN — SETTINGS
# ═══════════════════════════════════════════════════════════════════════════

def get_admin_settings_keyboard(lang: str = "hinglish") -> InlineKeyboardMarkup:
    """Admin settings categories"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📁 File Settings",
                callback_data=f"{CB.ADMIN_SETTINGS}:file"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🎨 UI Settings",
                callback_data=f"{CB.ADMIN_SETTINGS}:ui"
            ),
        ],
        [
            InlineKeyboardButton(
                text="💎 Premium",
                callback_data=f"{CB.ADMIN_SETTINGS}:premium"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🌍 Languages",
                callback_data=f"{CB.ADMIN_SETTINGS}:lang"
            ),
        ],
        [
            InlineKeyboardButton(
                text="📜 Terms & Privacy",
                callback_data=f"{CB.ADMIN_SETTINGS}:terms"
            ),
        ],
        [
            InlineKeyboardButton(
                text=btn("back", lang),
                callback_data=CB.ADMIN
            ),
            InlineKeyboardButton(
                text=btn("home", lang),
                callback_data=CB.HOME
            ),
        ],
    ])


# ═══════════════════════════════════════════════════════════════════════════
# ⚠️ ADMIN — DANGER ZONE
# ═══════════════════════════════════════════════════════════════════════════

def get_admin_danger_keyboard(lang: str = "hinglish") -> InlineKeyboardMarkup:
    """Danger zone keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🗑️ Clear Old Logs",
                callback_data=f"{CB.ADMIN_DANGER}:clear_logs"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🧹 Cleanup Expired Files",
                callback_data=f"{CB.ADMIN_DANGER}:cleanup_files"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔄 Reset Settings",
                callback_data=f"{CB.ADMIN_DANGER}:reset_settings"
            ),
        ],
        [
            InlineKeyboardButton(
                text="💣 Full Reset (DANGEROUS)",
                callback_data=f"{CB.ADMIN_DANGER}:full_reset"
            ),
        ],
        [
            InlineKeyboardButton(
                text=btn("back", lang),
                callback_data=CB.ADMIN
            ),
            InlineKeyboardButton(
                text=btn("home", lang),
                callback_data=CB.HOME
            ),
        ],
    ])


# ═══════════════════════════════════════════════════════════════════════════
# 🗑️ BULK DELETE — Select & Delete keyboards
# ═══════════════════════════════════════════════════════════════════════════

def get_delete_selection_keyboard(
    files: List[Dict[str, Any]],
    selected_ids: List[int],
    page: int,
    total_pages: int,
    total_count: int,
    lang: str = "hinglish"
) -> InlineKeyboardMarkup:
    """Selection mode — har file pe tap = select/deselect"""
    buttons = []

    for f in files:
        fid = f.get("id")
        name = f.get("file_name", "file")
        if len(name) > 22:
            name = name[:19] + "..."
        mark = "☑️" if fid in selected_ids else "⬜"
        buttons.append([
            InlineKeyboardButton(
                text=f"{mark} {name}",
                callback_data=f"{CB.DSEL}:{fid}"
            )
        ])

    if total_pages > 1:
        buttons.append(build_pagination_row(page, total_pages, CB.DSEL_PAGE))

    sel_count = len(selected_ids)
    buttons.append([
        InlineKeyboardButton(
            text=f"🗑️ Delete Selected ({sel_count})",
            callback_data=CB.DSEL_DEL
        ),
    ])
    buttons.append([
        InlineKeyboardButton(
            text=f"✅ Select All ({total_count})",
            callback_data=CB.DSEL_ALL
        ),
        InlineKeyboardButton(
            text="💣 Delete ALL",
            callback_data=CB.DEL_ALL
        ),
    ])
    buttons.append([
        InlineKeyboardButton(
            text=btn("cancel", lang),
            callback_data=CB.DSEL_CANCEL
        ),
        InlineKeyboardButton(
            text=btn("home", lang),
            callback_data=CB.HOME
        ),
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_bulk_confirm_keyboard(
    confirm_cb: str,
    cancel_cb: str,
    count: int,
    lang: str = "hinglish"
) -> InlineKeyboardMarkup:
    """Bulk delete confirmation"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"✅ Haan, {count} Files Delete Karo",
                callback_data=confirm_cb
            ),
        ],
        [
            InlineKeyboardButton(
                text=btn("no", lang),
                callback_data=cancel_cb
            ),
        ],
    ])


# ═══════════════════════════════════════════════════════════════════════════
# 🔢 PAGINATION HELPER
# ═══════════════════════════════════════════════════════════════════════════

def build_pagination_row(
    page: int,
    total_pages: int,
    prefix: str = "page",
    lang: str = "hinglish"
) -> List[InlineKeyboardButton]:
    """
    Pagination row banata hai.
    
    Layout:
    [ ⬅️ Prev ] [ 1/5 ] [ Next ➡️ ]
    """
    buttons = []
    
    # Previous button
    if page > 1:
        buttons.append(InlineKeyboardButton(
            text="⬅️",
            callback_data=f"{prefix}:{page - 1}"
        ))
    
    # Page indicator (noop)
    buttons.append(InlineKeyboardButton(
        text=f"{page}/{total_pages}",
        callback_data=CB.NOOP
    ))
    
    # Next button
    if page < total_pages:
        buttons.append(InlineKeyboardButton(
            text="➡️",
            callback_data=f"{prefix}:{page + 1}"
        ))
    
    return buttons


# ═══════════════════════════════════════════════════════════════════════════
# 📏 HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def format_file_size(size_bytes: int) -> str:
    """File size ko readable format mein"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


# ═══════════════════════════════════════════════════════════════════════════
# 🗑️ KEYBOARD REMOVAL
# ═══════════════════════════════════════════════════════════════════════════

def remove_keyboard() -> ReplyKeyboardRemove:
    """Reply keyboard hata deta hai"""
    return ReplyKeyboardRemove()


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    # Constants
    "CB",
    "BTN_LABELS",
    "btn",
    
    # Main menu
    "get_main_menu_keyboard",
    "get_main_menu_reply_keyboard",
    "get_back_button",
    "get_close_keyboard",
    
    # Upload
    "get_upload_keyboard",
    "get_upload_success_keyboard",
    "get_batch_prompt_keyboard",
    "get_batch_success_keyboard",
    "get_batch_view_keyboard",
    "get_delete_selection_keyboard",
    "get_bulk_confirm_keyboard",
    
    # Files
    "get_my_files_keyboard",
    "get_empty_files_keyboard",
    "get_file_actions_keyboard",
    "get_file_confirm_delete_keyboard",
    "get_file_info_keyboard",
    
    # Search
    "get_search_keyboard",
    "get_search_results_keyboard",
    "get_no_results_keyboard",
    
    # Stats/Profile
    "get_stats_keyboard",
    "get_profile_keyboard",
    
    # Settings
    "get_settings_keyboard",
    "get_language_selection_keyboard",
    
    # Help
    "get_help_keyboard",
    "get_about_keyboard",
    
    # Force join
    "get_force_join_keyboard",
    
    # Admin
    "get_admin_panel_keyboard",
    "get_admin_stats_keyboard",
    "get_admin_users_keyboard",
    "get_admin_user_list_keyboard",
    "get_admin_user_actions_keyboard",
    "get_admin_files_keyboard",
    "get_admin_broadcast_keyboard",
    "get_broadcast_confirm_keyboard",
    "get_admin_backup_keyboard",
    "get_admin_channels_keyboard",
    "get_admin_security_keyboard",
    "get_admin_maintenance_keyboard",
    "get_admin_logs_keyboard",
    "get_admin_settings_keyboard",
    "get_admin_danger_keyboard",
    
    # Helpers
    "build_pagination_row",
    "format_file_size",
    "remove_keyboard",
]


# ═══════════════════════════════════════════════════════════════════════════
# 🧪 SELF-TEST
# ═══════════════════════════════════════════════════════════════════════════

def _self_test() -> None:
    """Keyboard file ka self-test"""
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  🧪 ISUKOBIT — KEYBOARDS SELF-TEST                      ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    # Test button labels for all languages
    print("🌍 Button Label Tests:")
    print()
    for lang in ["hinglish", "english", "nepali", "latin"]:
        upload = btn("upload", lang)
        admin = btn("admin", lang)
        print(f"   [{lang}] upload='{upload}', admin='{admin}'")
    print()
    
    # Test keyboards
    print("⌨️  Keyboard Tests:")
    print()
    
    kb_main = get_main_menu_keyboard("hinglish", is_admin=True)
    print(f"   Main menu         : {len(kb_main.inline_keyboard)} rows")
    
    kb_admin = get_admin_panel_keyboard("hinglish", is_owner=True)
    print(f"   Admin panel       : {len(kb_admin.inline_keyboard)} rows")
    
    kb_lang = get_language_selection_keyboard("hinglish")
    print(f"   Language selection: {len(kb_lang.inline_keyboard)} rows")
    
    kb_upload = get_upload_keyboard("hinglish")
    print(f"   Upload            : {len(kb_upload.inline_keyboard)} rows")
    
    kb_empty = get_empty_files_keyboard("hinglish")
    print(f"   Empty files       : {len(kb_empty.inline_keyboard)} rows")
    print()
    
    # Test pagination
    print("🔢 Pagination Test:")
    print()
    pg = build_pagination_row(2, 5, "test")
    for b in pg:
        print(f"   [{b.text}] -> {b.callback_data}")
    print()
    
    # Test size format
    print("📏 Size Format Test:")
    print(f"   1024         -> {format_file_size(1024)}")
    print(f"   52428800     -> {format_file_size(52428800)}")
    print(f"   1073741824   -> {format_file_size(1073741824)}")
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
# Keyboards   : 30+
# Languages   : 4 (Hinglish, English, Nepali, Latin)
#
# ═══════════════════════════════════════════════════════════════════════════