# ═══════════════════════════════════════════════════════════════════════════
# 🚀 ISUKOBIT — TELEGRAM FILE STORE BOT
# ═══════════════════════════════════════════════════════════════════════════
# File      : strings.py
# Purpose   : Saare bot messages 4 languages mein
# Author    : Isukobit Team
# Version   : 1.0.0
# Python    : 3.10+
# ═══════════════════════════════════════════════════════════════════════════
#
# YEH FILE KYA KARTI HAI:
# ─────────────────────────────────────────────────────────────────────────
# 1. 4 languages ke saare bot messages store karti hai
# 2. get_string() function se language ke hisaab se message deti hai
# 3. format_string() se dynamic values (name, count, etc.) inject karti hai
# 4. Missing key ho toh English fallback deti hai
# 5. Self-test bhi hai — python strings.py se check kar sakte ho
#
# LANGUAGE SUPPORT:
# ─────────────────────────────────────────────────────────────────────────
# • Hinglish  — Hindi + English mix (default)
# • English   — Pure English
# • Nepali    — नेपाली
# • Latin     — Romanized classic style
#
# KAISE USE KARO:
# ─────────────────────────────────────────────────────────────────────────
# from strings import get_string
#
# msg = get_string("welcome", lang="hinglish", name="Raj")
# print(msg)
#
# ═══════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════
# 📦 IMPORTS
# ═══════════════════════════════════════════════════════════════════════════

from typing import Dict, Optional, Any


# ═══════════════════════════════════════════════════════════════════════════
# 🌍 SUPPORTED LANGUAGES
# ═══════════════════════════════════════════════════════════════════════════

SUPPORTED_LANGUAGES = ["hinglish", "english", "nepali", "latin"]
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

LANGUAGE_NAMES_NATIVE = {
    "hinglish": "Hinglish (हिंग्लिश)",
    "english": "English",
    "nepali": "नेपाली (Nepali)",
    "latin": "Latina (Latin)",
}


# ═══════════════════════════════════════════════════════════════════════════
# 🇮🇳 HINGLISH STRINGS — Hindi + English mix (default)
# ═══════════════════════════════════════════════════════════════════════════

HINGLISH: Dict[str, str] = {
    
    # ─────────────────────────────────────────────────────────────────────
    # 🎁 WELCOME & START
    # ─────────────────────────────────────────────────────────────────────
    "welcome": (
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
    "welcome_back": (
        "🎉 <b>Wapas swagat, {name}!</b>\n\n"
        "Aap kya karna chahte hain?\n"
        "Neeche ke buttons se select karein 👇"
    ),
    "hello": "Namaste, {name}! 🙏",
    "good_morning": "Suprabhat, {name}! ☀️",
    "good_evening": "Shubh sandhya, {name}! 🌆",
    "good_night": "Shubh ratri, {name}! 🌙",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📋 MAIN MENU
    # ─────────────────────────────────────────────────────────────────────
    "main_menu": (
        "📋 <b>Main Menu</b>\n\n"
        "Kya karna chahte hain? Neeche ke buttons se select karein 👇"
    ),
    "menu_upload": "📤 File Upload",
    "menu_my_files": "📁 Meri Files",
    "menu_search": "🔍 Search",
    "menu_stats": "📊 Statistics",
    "menu_settings": "⚙️ Settings",
    "menu_help": "❓ Madad",
    "menu_about": "ℹ️ About",
    "menu_back": "⬅️ Wapas",
    "menu_home": "🏠 Home",
    "menu_close": "❌ Band Karo",
    "menu_refresh": "🔄 Refresh",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📤 UPLOAD
    # ─────────────────────────────────────────────────────────────────────
    "upload_prompt": (
        "📤 <b>File Upload</b>\n\n"
        "Apni file bhejo (document, video, audio, photo, etc.)\n\n"
        "📌 <b>Limits:</b>\n"
        "• Max size: {max_size}\n"
        "• Allowed: {allowed_types}\n\n"
        "File bhejte hi main save kar dunga."
    ),
    "upload_processing": "⏳ File process ho rahi hai, ruko...",
    "upload_success": (
        "✅ <b>File upload ho gayi!</b>\n\n"
        "📄 <b>Name:</b> <code>{filename}</code>\n"
        "📦 <b>Size:</b> {size}\n"
        "🔑 <b>Code:</b> <code>{code}</code>\n"
        "🔗 <b>Link:</b> {link}\n\n"
        "📌 File save karne ke liye yeh code/link sambhal ke rakho."
    ),
    "upload_failed": "❌ File upload nahi ho payi. Dobara try karo.",
    "upload_too_large": (
        "❌ <b>File bahut badi hai!</b>\n\n"
        "📦 Aapki file: {size}\n"
        "📏 Max allowed: {max_size}\n\n"
        "Chhoti file bhejo ya admin se baat karo."
    ),
    "upload_type_not_allowed": (
        "❌ <b>Yeh file type allowed nahi hai!</b>\n\n"
        "📄 Aapki file: <code>{extension}</code>\n"
        "✅ Allowed: {allowed}\n\n"
        "Allowed file bhejo."
    ),
    "upload_cancelled": "❌ Upload cancel ho gaya.",
    "upload_limit_reached": (
        "⚠️ <b>Aapki upload limit khatam ho gayi!</b>\n\n"
        "Aapne {limit} files upload kar li hain.\n"
        "Kal dobara try karo ya admin se baat karo."
    ),
    "upload_wait": "⏳ Ruko, pehle wala file process ho raha hai...",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📁 MY FILES
    # ─────────────────────────────────────────────────────────────────────
    "my_files_header": (
        "📁 <b>Aapki Files</b>\n\n"
        "Total: <b>{count}</b> files\n"
        "Page: <b>{page}/{total_pages}</b>"
    ),
    "my_files_empty": (
        "📂 <b>Abhi tak koi file upload nahi ki!</b>\n\n"
        "Neeche 'Upload File' button dabakar apni pehli file bhejo."
    ),
    "my_files_error": "❌ Files load nahi ho payi. Dobara try karo.",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🔍 SEARCH
    # ─────────────────────────────────────────────────────────────────────
    "search_prompt": (
        "🔍 <b>File Search</b>\n\n"
        "File ka naam, code, ya keyword bhejo.\n"
        "Example: <code>pdf</code>, <code>ISU-A1B2C3</code>, <code>notes</code>"
    ),
    "search_no_results": (
        "🔍 <b>Koi file nahi mili!</b>\n\n"
        "Query: <code>{query}</code>\n\n"
        "Alag keyword try karo."
    ),
    "search_results": (
        "🔍 <b>Search Results</b>\n\n"
        "Query: <code>{query}</code>\n"
        "Found: <b>{count}</b> files\n"
        "Page: <b>{page}/{total_pages}</b>"
    ),
    "search_too_short": (
        "⚠️ Query bahut chhoti hai!\n\n"
        "Kam se kam <b>{min_length}</b> characters bhejo."
    ),
    "search_processing": "🔍 Search ho rahi hai...",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📄 FILE INFO
    # ─────────────────────────────────────────────────────────────────────
    "file_info": (
        "📄 <b>File Details</b>\n\n"
        "📝 <b>Name:</b> <code>{filename}</code>\n"
        "🔑 <b>Code:</b> <code>{code}</code>\n"
        "📦 <b>Size:</b> {size}\n"
        "📅 <b>Uploaded:</b> {date}\n"
        "👤 <b>Uploader:</b> {uploader}\n"
        "📥 <b>Downloads:</b> {downloads}\n"
        "📂 <b>Type:</b> {file_type}"
    ),
    "file_not_found": "❌ File nahi mili! Code sahi hai?",
    "file_deleted": "✅ File delete ho gayi!",
    "file_delete_confirm": (
        "⚠️ <b>Pakka delete karna hai?</b>\n\n"
        "📄 File: <code>{filename}</code>\n"
        "🔑 Code: <code>{code}</code>\n\n"
        "Yeh action undo nahi ho sakta!"
    ),
    "file_delete_success": "🗑️ File successfully delete ho gayi!",
    "file_delete_cancelled": "❌ Delete cancel kar diya.",
    "file_access_denied": (
        "🔒 <b>Yeh file aapki nahi hai!</b>\n\n"
        "Yeh file {owner} ne upload ki hai.\n"
        "Aap sirf apni files access kar sakte hain."
    ),
    "file_expired": (
        "⏰ <b>Yeh file expire ho gayi hai!</b>\n\n"
        "Expiry date: {expiry}\n"
        "Admin se contact karo dobara upload karne ke liye."
    ),
    "file_download_started": "📥 Download shuru ho gaya...",
    "file_sending": "📤 File bheji ja rahi hai...",
    "file_sent": "✅ File bhej di gayi!",
    "file_send_failed": "❌ File bhejne mein problem aayi.",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🔗 SHARE & LINK
    # ─────────────────────────────────────────────────────────────────────
    "share_link": (
        "🔗 <b>File Link</b>\n\n"
        "📄 <b>File:</b> <code>{filename}</code>\n"
        "🔗 <b>Link:</b>\n{link}\n\n"
        "📌 Yeh link aap hi use kar sakte hain (user-locked)."
    ),
    "share_copied": "✅ Link copy ho gaya!",
    "share_qr": "📱 <b>QR Code</b>\n\nScan karke file access karo.",
    "link_invalid": "❌ Link invalid ya expire ho gaya!",
    
    # ─────────────────────────────────────────────────────────────────────
    # 👤 USER PROFILE
    # ─────────────────────────────────────────────────────────────────────
    "my_profile": (
        "👤 <b>Aapki Profile</b>\n\n"
        "📝 <b>Name:</b> {name}\n"
        "🆔 <b>User ID:</b> <code>{user_id}</code>\n"
        "📛 <b>Username:</b> @{username}\n"
        "📅 <b>Joined:</b> {join_date}\n"
        "📁 <b>Files:</b> {total_files}\n"
        "📥 <b>Downloads:</b> {total_downloads}\n"
        "⭐ <b>Status:</b> {status}\n"
        "💎 <b>Premium:</b> {premium}"
    ),
    "profile_updated": "✅ Profile update ho gayi!",
    "user_banned_msg": (
        "🚫 <b>Aap banned hain!</b>\n\n"
        "Reason: {reason}\n"
        "Contact: {contact}\n\n"
        "Ban hatane ke liye admin se baat karo."
    ),
    "user_not_registered": "❌ Aap registered nahi hain. /start bhejo pehle.",
    
    # ─────────────────────────────────────────────────────────────────────
    # ⚙️ SETTINGS
    # ─────────────────────────────────────────────────────────────────────
    "settings_menu": (
        "⚙️ <b>Settings</b>\n\n"
        "Apni preferences set karo 👇"
    ),
    "settings_language": "🌍 Language badlo",
    "settings_notifications": "🔔 Notifications",
    "settings_theme": "🎨 Theme",
    "settings_buttons": "🎛️ Buttons Style",
    "settings_saved": "✅ Settings save ho gayi!",
    "settings_buttons_inline": "📱 Inline Buttons",
    "settings_buttons_reply": "⌨️ Reply Buttons",
    "settings_buttons_both": "📱⌨️ Dono",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📊 STATISTICS
    # ─────────────────────────────────────────────────────────────────────
    "stats_header": (
        "📊 <b>Bot Statistics</b>\n\n"
        "👥 <b>Total Users:</b> {total_users}\n"
        "📁 <b>Total Files:</b> {total_files}\n"
        "📥 <b>Total Downloads:</b> {total_downloads}\n"
        "📤 <b>Total Uploads:</b> {total_uploads}\n"
        "💾 <b>Total Size:</b> {total_size}\n\n"
        "📅 <b>Today:</b>\n"
        "• New users: {today_users}\n"
        "• Uploads: {today_uploads}\n"
        "• Downloads: {today_downloads}\n\n"
        "⏰ <b>Uptime:</b> {uptime}"
    ),
    "stats_user": (
        "📊 <b>Aapke Stats</b>\n\n"
        "📁 Files: <b>{files}</b>\n"
        "📥 Downloads: <b>{downloads}</b>\n"
        "💾 Total size: <b>{size}</b>\n"
        "📅 Joined: <b>{joined}</b>"
    ),
    "stats_admin": (
        "📊 <b>Admin Statistics</b>\n\n"
        "👥 Users: <b>{users}</b>\n"
        "📁 Files: <b>{files}</b>\n"
        "💾 Database: <b>{db_size}</b>\n"
        "🖥️ RAM: <b>{ram_used}/{ram_total}</b>\n"
        "💿 Disk: <b>{disk_used}/{disk_total}</b>"
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # ❓ HELP
    # ─────────────────────────────────────────────────────────────────────
    "help": (
        "❓ <b>Madad / Help</b>\n\n"
        "📌 <b>Available Commands:</b>\n\n"
        "/start — Main menu\n"
        "/help — Yeh message\n"
        "/upload — File upload karo\n"
        "/myfiles — Apni files dekho\n"
        "/search — File dhundho\n"
        "/profile — Apni profile\n"
        "/settings — Settings\n"
        "/about — Bot ke baare mein\n\n"
        "📌 <b>Kaise use karein:</b>\n"
        "1. 'Upload File' button dabao\n"
        "2. File bhejo\n"
        "3. Aapko file code + link milega\n"
        "4. Woh code/link sambhal ke rakho\n"
        "5. Search/My Files se wapas paao\n\n"
        "Koi problem? Admin se contact karo: {support}"
    ),
    "help_short": "❓ Madad chahiye? /help bhejo",
    
    # ─────────────────────────────────────────────────────────────────────
    # ℹ️ ABOUT
    # ─────────────────────────────────────────────────────────────────────
    "about": (
        "ℹ️ <b>Bot ke Baare Mein</b>\n\n"
        "🤖 <b>Name:</b> {bot_name}\n"
        "📦 <b>Version:</b> {version}\n"
        "👑 <b>Owner:</b> {owner}\n"
        "🌍 <b>Languages:</b> {languages}\n"
        "🖥️ <b>Server:</b> {server}\n\n"
        "📌 <b>Features:</b>\n"
        "• File upload & storage\n"
        "• Fast search\n"
        "• Multi-language support\n"
        "• Secure user-locked links\n"
        "• Auto backup system\n\n"
        "📞 <b>Support:</b> {support}\n"
        "📢 <b>Updates:</b> {updates}"
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # 📢 FORCE JOIN
    # ─────────────────────────────────────────────────────────────────────
    "force_join": (
        "🔒 <b>Access Denied!</b>\n\n"
        "Bot use karne ke liye pehle neeche diye gaye channels "
        "ko join karein, phir <b>✅ Verify</b> button dabayein."
    ),
    "force_join_verified": "✅ Verified! Ab aap bot use kar sakte hain.",
    "force_join_not_verified": (
        "❌ <b>Verify nahi hua!</b>\n\n"
        "Pehle saare channels join karo, phir verify dabao."
    ),
    "force_join_channels": "📢 <b>Join these channels:</b>",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🚨 ERRORS
    # ─────────────────────────────────────────────────────────────────────
    "error_generic": (
        "❌ <b>Kuch gadbad ho gayi!</b>\n\n"
        "Error: <code>{error}</code>\n\n"
        "Admin ko bata do, woh fix kar denge."
    ),
    "error_unknown": "❌ Unknown error aaya. Dobara try karo.",
    "error_timeout": "⏰ Time out ho gaya! Dobara try karo.",
    "error_rate_limit": (
        "⚠️ <b>Ruko thoda!</b>\n\n"
        "Aap bahut tez request bhej rahe ho.\n"
        "{seconds} seconds baad try karo."
    ),
    "error_maintenance": (
        "🛠️ <b>Bot maintenance mein hai</b>\n\n"
        "Thodi der baad try karein. Shukriya! 🙏"
    ),
    "error_banned": "🚫 Aap banned hain. Admin se contact karo.",
    "error_not_admin": "❌ Yeh command sirf admin ke liye hai.",
    "error_not_owner": "❌ Yeh sirf owner ke liye hai.",
    "error_invalid_input": "❌ Input invalid hai. Sahi format mein bhejo.",
    "error_network": "🌐 Network problem hai. Thodi der baad try karo.",
    "error_database": "🗄️ Database problem hai. Admin ko bata do.",
    "error_telegram": "📡 Telegram se connect nahi ho raha.",
    "error_file_corrupt": "❌ File corrupt hai ya padhi nahi ja sakti.",
    "error_session_expired": "⏰ Session expire ho gaya. /start bhejo dobara.",
    
    # ─────────────────────────────────────────────────────────────────────
    # ⚠️ WARNINGS
    # ─────────────────────────────────────────────────────────────────────
    "warning_delete": "⚠️ Yeh action undo nahi ho sakta!",
    "warning_spam": (
        "⚠️ <b>Spam warning {count}/{max}!</b>\n\n"
        "Agar aur spam kiya toh mute ho jaoge."
    ),
    "warning_muted": (
        "🔇 <b>Aap mute ho gaye!</b>\n\n"
        "Duration: {duration}\n"
        "Reason: Spam\n\n"
        "Waqt khatam hone pe wapas try karo."
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # 👑 ADMIN PANEL
    # ─────────────────────────────────────────────────────────────────────
    "admin_panel": (
        "👑 <b>Admin Panel</b>\n\n"
        "Welcome, {name}!\n"
        "Kya karna chahte ho? 👇"
    ),
    "admin_stats": "📊 Statistics",
    "admin_users": "👥 Users",
    "admin_files": "📁 Files",
    "admin_broadcast": "📣 Broadcast",
    "admin_backup": "💾 Backup",
    "admin_settings": "⚙️ Settings",
    "admin_channels": "📢 Channels",
    "admin_security": "🔐 Security",
    "admin_maintenance": "🛠️ Maintenance",
    "admin_logs": "📝 Logs",
    "admin_health": "💚 Health Check",
    "admin_restart": "🔄 Restart",
    "admin_add_admin": "➕ Add Admin",
    "admin_remove_admin": "➖ Remove Admin",
    "admin_ban_user": "🚫 Ban User",
    "admin_unban_user": "✅ Unban User",
    "admin_search_user": "🔍 Search User",
    "admin_search_file": "🔍 Search File",
    "admin_delete_file": "🗑️ Delete File",
    "admin_export_data": "📤 Export Data",
    "admin_import_data": "📥 Import Data",
    "admin_danger_zone": "⚠️ Danger Zone",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📣 BROADCAST
    # ─────────────────────────────────────────────────────────────────────
    "broadcast_prompt": (
        "📣 <b>Broadcast</b>\n\n"
        "Message bhejo jo sab users ko jayega.\n\n"
        "Options:\n"
        "• Text\n"
        "• Photo + caption\n"
        "• Video + caption\n"
        "• Document + caption\n\n"
        "Cancel karne ke liye /cancel bhejo."
    ),
    "broadcast_confirm": (
        "⚠️ <b>Broadcast confirm karo?</b>\n\n"
        "Yeh message <b>{count}</b> users ko jayega.\n\n"
        "Confirm karne ke liye ✅ dabao."
    ),
    "broadcast_started": "🚀 Broadcast shuru ho gaya!",
    "broadcast_progress": (
        "📣 <b>Broadcasting...</b>\n\n"
        "✅ Sent: {sent}\n"
        "❌ Failed: {failed}\n"
        "📊 Progress: {progress}%"
    ),
    "broadcast_complete": (
        "✅ <b>Broadcast complete!</b>\n\n"
        "✅ Sent: {sent}\n"
        "❌ Failed: {failed}\n"
        "⏱️ Time: {time}"
    ),
    "broadcast_cancelled": "❌ Broadcast cancel ho gaya.",
    
    # ─────────────────────────────────────────────────────────────────────
    # 💾 BACKUP
    # ─────────────────────────────────────────────────────────────────────
    "backup_started": "💾 Backup shuru ho raha hai...",
    "backup_in_progress": "⏳ Backup chal raha hai, ruko...",
    "backup_complete": (
        "✅ <b>Backup complete!</b>\n\n"
        "📦 Size: {size}\n"
        "⏱️ Time: {time}\n"
        "📁 Location: {location}"
    ),
    "backup_failed": "❌ Backup fail ho gaya: {error}",
    "backup_creating": "📦 Database dump ban raha hai...",
    "backup_uploading": "📤 Backup upload ho raha hai...",
    "backup_verifying": "🔍 Backup verify ho raha hai...",
    "backup_restored": "✅ Backup restore ho gaya!",
    "backup_list": (
        "💾 <b>Recent Backups</b>\n\n"
        "{backups}\n\n"
        "Total: <b>{count}</b> backups"
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # 👥 USER MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────
    "user_list": (
        "👥 <b>User List</b>\n\n"
        "Page {page}/{total}\n"
        "Total: <b>{count}</b> users"
    ),
    "user_info": (
        "👤 <b>User Info</b>\n\n"
        "🆔 ID: <code>{user_id}</code>\n"
        "📝 Name: {name}\n"
        "📛 Username: @{username}\n"
        "📅 Joined: {joined}\n"
        "📁 Files: {files}\n"
        "📥 Downloads: {downloads}\n"
        "⭐ Status: {status}"
    ),
    "user_banned": "🚫 User ban ho gaya!",
    "user_unbanned": "✅ User unban ho gaya!",
    "user_not_found": "❌ User nahi mila!",
    "user_ban_reason": "📝 Ban reason bhejo:",
    "user_banned_confirm": (
        "🚫 <b>Ban confirm?</b>\n\n"
        "User: {name}\n"
        "Reason: {reason}\n\n"
        "Confirm karne ke liye ✅ dabao."
    ),
    "user_already_banned": "⚠️ User pehle se banned hai.",
    "user_already_admin": "⚠️ User pehle se admin hai.",
    "user_added_admin": "✅ User admin ban gaya!",
    "user_removed_admin": "✅ User admin se hata diya!",
    
    # ─────────────────────────────────────────────────────────────────────
    # ⚙️ SETTINGS MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────
    "settings_updated": "✅ Setting update ho gayi: <code>{key}</code>",
    "settings_invalid": "❌ Invalid value di gayi.",
    "settings_confirm": "⚠️ Setting <code>{key}</code> ko <code>{value}</code> pe change karna hai?",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🛠️ MAINTENANCE
    # ─────────────────────────────────────────────────────────────────────
    "maintenance_enabled": "🛠️ Maintenance mode ON ho gaya!",
    "maintenance_disabled": "✅ Maintenance mode OFF ho gaya!",
    "maintenance_already_on": "⚠️ Maintenance pehle se ON hai.",
    "maintenance_already_off": "⚠️ Maintenance pehle se OFF hai.",
    "maintenance_message_set": "✅ Maintenance message update ho gaya!",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🎉 CONFIRMATIONS
    # ─────────────────────────────────────────────────────────────────────
    "confirm_yes": "✅ Haan",
    "confirm_no": "❌ Nahi",
    "confirm_cancel": "❌ Cancel",
    "confirm_ok": "✅ OK",
    "confirm_done": "✅ Ho gaya!",
    "confirm_saved": "💾 Save ho gaya!",
    "confirm_deleted": "🗑️ Delete ho gaya!",
    "confirm_updated": "✅ Update ho gaya!",
    "confirm_created": "✅ Create ho gaya!",
    "confirm_copied": "📋 Copy ho gaya!",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🎊 LOADING & WAITING
    # ─────────────────────────────────────────────────────────────────────
    "loading": "⏳ Load ho raha hai...",
    "processing": "⚙️ Process ho raha hai...",
    "please_wait": "⏳ Ruko...",
    "searching": "🔍 Search ho rahi hai...",
    "saving": "💾 Save ho raha hai...",
    "deleting": "🗑️ Delete ho raha hai...",
    "uploading": "📤 Upload ho raha hai...",
    "downloading": "📥 Download ho raha hai...",
    "connecting": "🔗 Connect ho raha hai...",
    "verifying": "🔍 Verify ho raha hai...",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📅 DATE & TIME FORMATS
    # ─────────────────────────────────────────────────────────────────────
    "time_just_now": "abhi",
    "time_minutes_ago": "{count} minute pehle",
    "time_hours_ago": "{count} ghante pehle",
    "time_days_ago": "{count} din pehle",
    "time_weeks_ago": "{count} hafte pehle",
    "time_months_ago": "{count} mahine pehle",
    "time_years_ago": "{count} saal pehle",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📏 FILE SIZE UNITS
    # ─────────────────────────────────────────────────────────────────────
    "size_bytes": "{count} B",
    "size_kb": "{count} KB",
    "size_mb": "{count} MB",
    "size_gb": "{count} GB",
    "size_tb": "{count} TB",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🎁 MISC
    # ─────────────────────────────────────────────────────────────────────
    "thank_you": "🙏 Shukriya!",
    "your_welcome": "🙏 Aapka swagat hai!",
    "congratulations": "🎉 Badhai ho!",
    "good_luck": "🍀 Best of luck!",
    "no_permission": "🚫 Aapko permission nahi hai!",
    "coming_soon": "🚧 Yeh feature jaldi aa raha hai!",
    "not_available": "❌ Yeh abhi available nahi hai.",
    "try_again": "🔄 Dobara try karo.",
    "contact_support": "📞 Support se contact karo.",
    "thanks_for_using": "🙏 Isukobit use karne ke liye shukriya!",
}


# ═══════════════════════════════════════════════════════════════════════════
# 🇬🇧 ENGLISH STRINGS
# ═══════════════════════════════════════════════════════════════════════════

ENGLISH: Dict[str, str] = {
    
    # ─────────────────────────────────────────────────────────────────────
    # 🎁 WELCOME & START
    # ─────────────────────────────────────────────────────────────────────
    "welcome": (
        "🎉 <b>Welcome to Isukobit!</b>\n\n"
        "I am a File Store Bot. You can upload, search, and "
        "download files through me.\n\n"
        "📌 <b>Quick Commands:</b>\n"
        "• /start — Main menu\n"
        "• /help — Help\n"
        "• /upload — Upload file\n"
        "• /myfiles — View your files\n"
        "• /search — Search files\n\n"
        "Get started with the buttons below 👇"
    ),
    "welcome_back": (
        "🎉 <b>Welcome back, {name}!</b>\n\n"
        "What would you like to do?\n"
        "Select from the buttons below 👇"
    ),
    "hello": "Hello, {name}! 🙏",
    "good_morning": "Good morning, {name}! ☀️",
    "good_evening": "Good evening, {name}! 🌆",
    "good_night": "Good night, {name}! 🌙",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📋 MAIN MENU
    # ─────────────────────────────────────────────────────────────────────
    "main_menu": (
        "📋 <b>Main Menu</b>\n\n"
        "What would you like to do? Select from the buttons below 👇"
    ),
    "menu_upload": "📤 Upload File",
    "menu_my_files": "📁 My Files",
    "menu_search": "🔍 Search",
    "menu_stats": "📊 Statistics",
    "menu_settings": "⚙️ Settings",
    "menu_help": "❓ Help",
    "menu_about": "ℹ️ About",
    "menu_back": "⬅️ Back",
    "menu_home": "🏠 Home",
    "menu_close": "❌ Close",
    "menu_refresh": "🔄 Refresh",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📤 UPLOAD
    # ─────────────────────────────────────────────────────────────────────
    "upload_prompt": (
        "📤 <b>File Upload</b>\n\n"
        "Send your file (document, video, audio, photo, etc.)\n\n"
        "📌 <b>Limits:</b>\n"
        "• Max size: {max_size}\n"
        "• Allowed: {allowed_types}\n\n"
        "I will save it as soon as you send it."
    ),
    "upload_processing": "⏳ Processing file, please wait...",
    "upload_success": (
        "✅ <b>File uploaded!</b>\n\n"
        "📄 <b>Name:</b> <code>{filename}</code>\n"
        "📦 <b>Size:</b> {size}\n"
        "🔑 <b>Code:</b> <code>{code}</code>\n"
        "🔗 <b>Link:</b> {link}\n\n"
        "📌 Save this code/link to access your file later."
    ),
    "upload_failed": "❌ Upload failed. Please try again.",
    "upload_too_large": (
        "❌ <b>File too large!</b>\n\n"
        "📦 Your file: {size}\n"
        "📏 Max allowed: {max_size}\n\n"
        "Please send a smaller file."
    ),
    "upload_type_not_allowed": (
        "❌ <b>File type not allowed!</b>\n\n"
        "📄 Your file: <code>{extension}</code>\n"
        "✅ Allowed: {allowed}\n\n"
        "Please send an allowed file."
    ),
    "upload_cancelled": "❌ Upload cancelled.",
    "upload_limit_reached": (
        "⚠️ <b>Upload limit reached!</b>\n\n"
        "You have uploaded {limit} files.\n"
        "Try again tomorrow or contact admin."
    ),
    "upload_wait": "⏳ Please wait, previous file is processing...",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📁 MY FILES
    # ─────────────────────────────────────────────────────────────────────
    "my_files_header": (
        "📁 <b>Your Files</b>\n\n"
        "Total: <b>{count}</b> files\n"
        "Page: <b>{page}/{total_pages}</b>"
    ),
    "my_files_empty": (
        "📂 <b>No files uploaded yet!</b>\n\n"
        "Tap 'Upload File' below to send your first file."
    ),
    "my_files_error": "❌ Could not load files. Try again.",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🔍 SEARCH
    # ─────────────────────────────────────────────────────────────────────
    "search_prompt": (
        "🔍 <b>File Search</b>\n\n"
        "Send file name, code, or keyword.\n"
        "Example: <code>pdf</code>, <code>ISU-A1B2C3</code>, <code>notes</code>"
    ),
    "search_no_results": (
        "🔍 <b>No files found!</b>\n\n"
        "Query: <code>{query}</code>\n\n"
        "Try a different keyword."
    ),
    "search_results": (
        "🔍 <b>Search Results</b>\n\n"
        "Query: <code>{query}</code>\n"
        "Found: <b>{count}</b> files\n"
        "Page: <b>{page}/{total_pages}</b>"
    ),
    "search_too_short": (
        "⚠️ Query too short!\n\n"
        "Send at least <b>{min_length}</b> characters."
    ),
    "search_processing": "🔍 Searching...",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📄 FILE INFO
    # ─────────────────────────────────────────────────────────────────────
    "file_info": (
        "📄 <b>File Details</b>\n\n"
        "📝 <b>Name:</b> <code>{filename}</code>\n"
        "🔑 <b>Code:</b> <code>{code}</code>\n"
        "📦 <b>Size:</b> {size}\n"
        "📅 <b>Uploaded:</b> {date}\n"
        "👤 <b>Uploader:</b> {uploader}\n"
        "📥 <b>Downloads:</b> {downloads}\n"
        "📂 <b>Type:</b> {file_type}"
    ),
    "file_not_found": "❌ File not found! Check the code.",
    "file_deleted": "✅ File deleted!",
    "file_delete_confirm": (
        "⚠️ <b>Really delete?</b>\n\n"
        "📄 File: <code>{filename}</code>\n"
        "🔑 Code: <code>{code}</code>\n\n"
        "This action cannot be undone!"
    ),
    "file_delete_success": "🗑️ File deleted successfully!",
    "file_delete_cancelled": "❌ Delete cancelled.",
    "file_access_denied": (
        "🔒 <b>This file is not yours!</b>\n\n"
        "This file was uploaded by {owner}.\n"
        "You can only access your own files."
    ),
    "file_expired": (
        "⏰ <b>This file has expired!</b>\n\n"
        "Expiry date: {expiry}\n"
        "Contact admin to re-upload."
    ),
    "file_download_started": "📥 Download started...",
    "file_sending": "📤 Sending file...",
    "file_sent": "✅ File sent!",
    "file_send_failed": "❌ Failed to send file.",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🔗 SHARE & LINK
    # ─────────────────────────────────────────────────────────────────────
    "share_link": (
        "🔗 <b>File Link</b>\n\n"
        "📄 <b>File:</b> <code>{filename}</code>\n"
        "🔗 <b>Link:</b>\n{link}\n\n"
        "📌 Only you can use this link (user-locked)."
    ),
    "share_copied": "✅ Link copied!",
    "share_qr": "📱 <b>QR Code</b>\n\nScan to access the file.",
    "link_invalid": "❌ Link invalid or expired!",
    
    # ─────────────────────────────────────────────────────────────────────
    # 👤 USER PROFILE
    # ─────────────────────────────────────────────────────────────────────
    "my_profile": (
        "👤 <b>Your Profile</b>\n\n"
        "📝 <b>Name:</b> {name}\n"
        "🆔 <b>User ID:</b> <code>{user_id}</code>\n"
        "📛 <b>Username:</b> @{username}\n"
        "📅 <b>Joined:</b> {join_date}\n"
        "📁 <b>Files:</b> {total_files}\n"
        "📥 <b>Downloads:</b> {total_downloads}\n"
        "⭐ <b>Status:</b> {status}\n"
        "💎 <b>Premium:</b> {premium}"
    ),
    "profile_updated": "✅ Profile updated!",
    "user_banned_msg": (
        "🚫 <b>You are banned!</b>\n\n"
        "Reason: {reason}\n"
        "Contact: {contact}\n\n"
        "Contact admin to lift the ban."
    ),
    "user_not_registered": "❌ You are not registered. Send /start first.",
    
    # ─────────────────────────────────────────────────────────────────────
    # ⚙️ SETTINGS
    # ─────────────────────────────────────────────────────────────────────
    "settings_menu": (
        "⚙️️ <b>Settings</b>\n\n"
        "Set your preferences below 👇"
    ),
    "settings_language": "🌍 Change Language",
    "settings_notifications": "🔔 Notifications",
    "settings_theme": "🎨 Theme",
    "settings_buttons": "🎛️ Buttons Style",
    "settings_saved": "✅ Settings saved!",
    "settings_buttons_inline": "📱 Inline Buttons",
    "settings_buttons_reply": "⌨️ Reply Buttons",
    "settings_buttons_both": "📱⌨️ Both",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📊 STATISTICS
    # ─────────────────────────────────────────────────────────────────────
    "stats_header": (
        "📊 <b>Bot Statistics</b>\n\n"
        "👥 <b>Total Users:</b> {total_users}\n"
        "📁 <b>Total Files:</b> {total_files}\n"
        "📥 <b>Total Downloads:</b> {total_downloads}\n"
        "📤 <b>Total Uploads:</b> {total_uploads}\n"
        "💾 <b>Total Size:</b> {total_size}\n\n"
        "📅 <b>Today:</b>\n"
        "• New users: {today_users}\n"
        "• Uploads: {today_uploads}\n"
        "• Downloads: {today_downloads}\n\n"
        "⏰ <b>Uptime:</b> {uptime}"
    ),
    "stats_user": (
        "📊 <b>Your Stats</b>\n\n"
        "📁 Files: <b>{files}</b>\n"
        "📥 Downloads: <b>{downloads}</b>\n"
        "💾 Total size: <b>{size}</b>\n"
        "📅 Joined: <b>{joined}</b>"
    ),
    "stats_admin": (
        "📊 <b>Admin Statistics</b>\n\n"
        "👥 Users: <b>{users}</b>\n"
        "📁 Files: <b>{files}</b>\n"
        "💾 Database: <b>{db_size}</b>\n"
        "🖥️ RAM: <b>{ram_used}/{ram_total}</b>\n"
        "💿 Disk: <b>{disk_used}/{disk_total}</b>"
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # ❓ HELP
    # ─────────────────────────────────────────────────────────────────────
    "help": (
        "❓ <b>Help</b>\n\n"
        "📌 <b>Available Commands:</b>\n\n"
        "/start — Main menu\n"
        "/help — This message\n"
        "/upload — Upload file\n"
        "/myfiles — View your files\n"
        "/search — Search files\n"
        "/profile — Your profile\n"
        "/settings — Settings\n"
        "/about — About bot\n\n"
        "📌 <b>How to use:</b>\n"
        "1. Tap 'Upload File'\n"
        "2. Send your file\n"
        "3. Get file code + link\n"
        "4. Save that code/link\n"
        "5. Access via Search/My Files\n\n"
        "Problem? Contact admin: {support}"
    ),
    "help_short": "❓ Need help? Send /help",
    
    # ─────────────────────────────────────────────────────────────────────
    # ℹ️ ABOUT
    # ─────────────────────────────────────────────────────────────────────
    "about": (
        "ℹ️ <b>About Bot</b>\n\n"
        "🤖 <b>Name:</b> {bot_name}\n"
        "📦 <b>Version:</b> {version}\n"
        "👑 <b>Owner:</b> {owner}\n"
        "🌍 <b>Languages:</b> {languages}\n"
        "🖥️ <b>Server:</b> {server}\n\n"
        "📌 <b>Features:</b>\n"
        "• File upload & storage\n"
        "• Fast search\n"
        "• Multi-language support\n"
        "• Secure user-locked links\n"
        "• Auto backup system\n\n"
        "📞 <b>Support:</b> {support}\n"
        "📢 <b>Updates:</b> {updates}"
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # 📢 FORCE JOIN
    # ─────────────────────────────────────────────────────────────────────
    "force_join": (
        "🔒 <b>Access Denied!</b>\n\n"
        "To use the bot, first join the channels below, "
        "then tap <b>✅ Verify</b>."
    ),
    "force_join_verified": "✅ Verified! You can now use the bot.",
    "force_join_not_verified": (
        "❌ <b>Not verified!</b>\n\n"
        "Join all channels first, then tap verify."
    ),
    "force_join_channels": "📢 <b>Join these channels:</b>",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🚨 ERRORS
    # ─────────────────────────────────────────────────────────────────────
    "error_generic": (
        "❌ <b>Something went wrong!</b>\n\n"
        "Error: <code>{error}</code>\n\n"
        "Report this to the admin."
    ),
    "error_unknown": "❌ Unknown error occurred. Try again.",
    "error_timeout": "⏰ Timed out! Try again.",
    "error_rate_limit": (
        "⚠️ <b>Slow down!</b>\n\n"
        "You're sending requests too fast.\n"
        "Try again in {seconds} seconds."
    ),
    "error_maintenance": (
        "🛠️ <b>Bot is under maintenance</b>\n\n"
        "Please try again later. Thank you! 🙏"
    ),
    "error_banned": "🚫 You are banned. Contact admin.",
    "error_not_admin": "❌ This command is admin-only.",
    "error_not_owner": "❌ This is owner-only.",
    "error_invalid_input": "❌ Invalid input. Send correct format.",
    "error_network": "🌐 Network problem. Try again later.",
    "error_database": "🗄️ Database problem. Contact admin.",
    "error_telegram": "📡 Cannot connect to Telegram.",
    "error_file_corrupt": "❌ File is corrupt or unreadable.",
    "error_session_expired": "⏰ Session expired. Send /start again.",
    
    # ─────────────────────────────────────────────────────────────────────
    # ⚠️ WARNINGS
    # ─────────────────────────────────────────────────────────────────────
    "warning_delete": "⚠️ This action cannot be undone!",
    "warning_spam": (
        "⚠️ <b>Spam warning {count}/{max}!</b>\n\n"
        "Further spam will mute you."
    ),
    "warning_muted": (
        "🔇 <b>You have been muted!</b>\n\n"
        "Duration: {duration}\n"
        "Reason: Spam\n\n"
        "Try again after the duration."
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # 👑 ADMIN PANEL
    # ─────────────────────────────────────────────────────────────────────
    "admin_panel": (
        "👑 <b>Admin Panel</b>\n\n"
        "Welcome, {name}!\n"
        "What would you like to do? 👇"
    ),
    "admin_stats": "📊 Statistics",
    "admin_users": "👥 Users",
    "admin_files": "📁 Files",
    "admin_broadcast": "📣 Broadcast",
    "admin_backup": "💾 Backup",
    "admin_settings": "⚙️ Settings",
    "admin_channels": "📢 Channels",
    "admin_security": "🔐 Security",
    "admin_maintenance": "🛠️ Maintenance",
    "admin_logs": "📝 Logs",
    "admin_health": "💚 Health Check",
    "admin_restart": "🔄 Restart",
    "admin_add_admin": "➕ Add Admin",
    "admin_remove_admin": "➖ Remove Admin",
    "admin_ban_user": "🚫 Ban User",
    "admin_unban_user": "✅ Unban User",
    "admin_search_user": "🔍 Search User",
    "admin_search_file": "🔍 Search File",
    "admin_delete_file": "🗑️ Delete File",
    "admin_export_data": "📤 Export Data",
    "admin_import_data": "📥 Import Data",
    "admin_danger_zone": "⚠️ Danger Zone",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📣 BROADCAST
    # ─────────────────────────────────────────────────────────────────────
    "broadcast_prompt": (
        "📣 <b>Broadcast</b>\n\n"
        "Send a message to broadcast to all users.\n\n"
        "Options:\n"
        "• Text\n"
        "• Photo + caption\n"
        "• Video + caption\n"
        "• Document + caption\n\n"
        "Send /cancel to cancel."
    ),
    "broadcast_confirm": (
        "⚠️ <b>Confirm broadcast?</b>\n\n"
        "This message will go to <b>{count}</b> users.\n\n"
        "Tap ✅ to confirm."
    ),
    "broadcast_started": "🚀 Broadcast started!",
    "broadcast_progress": (
        "📣 <b>Broadcasting...</b>\n\n"
        "✅ Sent: {sent}\n"
        "❌ Failed: {failed}\n"
        "📊 Progress: {progress}%"
    ),
    "broadcast_complete": (
        "✅ <b>Broadcast complete!</b>\n\n"
        "✅ Sent: {sent}\n"
        "❌ Failed: {failed}\n"
        "⏱️ Time: {time}"
    ),
    "broadcast_cancelled": "❌ Broadcast cancelled.",
    
    # ─────────────────────────────────────────────────────────────────────
    # 💾 BACKUP
    # ─────────────────────────────────────────────────────────────────────
    "backup_started": "💾 Backup started...",
    "backup_in_progress": "⏳ Backup in progress...",
    "backup_complete": (
        "✅ <b>Backup complete!</b>\n\n"
        "📦 Size: {size}\n"
        "⏱️ Time: {time}\n"
        "📁 Location: {location}"
    ),
    "backup_failed": "❌ Backup failed: {error}",
    "backup_creating": "📦 Creating database dump...",
    "backup_uploading": "📤 Uploading backup...",
    "backup_verifying": "🔍 Verifying backup...",
    "backup_restored": "✅ Backup restored!",
    "backup_list": (
        "💾 <b>Recent Backups</b>\n\n"
        "{backups}\n\n"
        "Total: <b>{count}</b> backups"
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # 👥 USER MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────
    "user_list": (
        "👥 <b>User List</b>\n\n"
        "Page {page}/{total}\n"
        "Total: <b>{count}</b> users"
    ),
    "user_info": (
        "👤 <b>User Info</b>\n\n"
        "🆔 ID: <code>{user_id}</code>\n"
        "📝 Name: {name}\n"
        "📛 Username: @{username}\n"
        "📅 Joined: {joined}\n"
        "📁 Files: {files}\n"
        "📥 Downloads: {downloads}\n"
        "⭐ Status: {status}"
    ),
    "user_banned": "🚫 User banned!",
    "user_unbanned": "✅ User unbanned!",
    "user_not_found": "❌ User not found!",
    "user_ban_reason": "📝 Send ban reason:",
    "user_banned_confirm": (
        "🚫 <b>Confirm ban?</b>\n\n"
        "User: {name}\n"
        "Reason: {reason}\n\n"
        "Tap ✅ to confirm."
    ),
    "user_already_banned": "⚠️ User is already banned.",
    "user_already_admin": "⚠️ User is already admin.",
    "user_added_admin": "✅ User is now admin!",
    "user_removed_admin": "✅ User removed from admin!",
    
    # ─────────────────────────────────────────────────────────────────────
    # ⚙️ SETTINGS MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────
    "settings_updated": "✅ Setting updated: <code>{key}</code>",
    "settings_invalid": "❌ Invalid value provided.",
    "settings_confirm": "⚠️ Change <code>{key}</code> to <code>{value}</code>?",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🛠️ MAINTENANCE
    # ─────────────────────────────────────────────────────────────────────
    "maintenance_enabled": "🛠️ Maintenance mode ON!",
    "maintenance_disabled": "✅ Maintenance mode OFF!",
    "maintenance_already_on": "⚠️ Maintenance is already ON.",
    "maintenance_already_off": "⚠️️ Maintenance is already OFF.",
    "maintenance_message_set": "✅ Maintenance message updated!",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🎉 CONFIRMATIONS
    # ─────────────────────────────────────────────────────────────────────
    "confirm_yes": "✅ Yes",
    "confirm_no": "❌ No",
    "confirm_cancel": "❌ Cancel",
    "confirm_ok": "✅ OK",
    "confirm_done": "✅ Done!",
    "confirm_saved": "💾 Saved!",
    "confirm_deleted": "🗑️ Deleted!",
    "confirm_updated": "✅ Updated!",
    "confirm_created": "✅ Created!",
    "confirm_copied": "📋 Copied!",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🎊 LOADING & WAITING
    # ─────────────────────────────────────────────────────────────────────
    "loading": "⏳ Loading...",
    "processing": "⚙️ Processing...",
    "please_wait": "⏳ Please wait...",
    "searching": "🔍 Searching...",
    "saving": "💾 Saving...",
    "deleting": "🗑️ Deleting...",
    "uploading": "📤 Uploading...",
    "downloading": "📥 Downloading...",
    "connecting": "🔗 Connecting...",
    "verifying": "🔍 Verifying...",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📅 DATE & TIME FORMATS
    # ─────────────────────────────────────────────────────────────────────
    "time_just_now": "just now",
    "time_minutes_ago": "{count} minutes ago",
    "time_hours_ago": "{count} hours ago",
    "time_days_ago": "{count} days ago",
    "time_weeks_ago": "{count} weeks ago",
    "time_months_ago": "{count} months ago",
    "time_years_ago": "{count} years ago",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📏 FILE SIZE UNITS
    # ─────────────────────────────────────────────────────────────────────
    "size_bytes": "{count} B",
    "size_kb": "{count} KB",
    "size_mb": "{count} MB",
    "size_gb": "{count} GB",
    "size_tb": "{count} TB",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🎁 MISC
    # ─────────────────────────────────────────────────────────────────────
    "thank_you": "🙏 Thank you!",
    "your_welcome": "🙏 You're welcome!",
    "congratulations": "🎉 Congratulations!",
    "good_luck": "🍀 Best of luck!",
    "no_permission": "🚫 You don't have permission!",
    "coming_soon": "🚧 This feature is coming soon!",
    "not_available": "❌ Not available right now.",
    "try_again": "🔄 Try again.",
    "contact_support": "📞 Contact support.",
    "thanks_for_using": "🙏 Thanks for using Isukobit!",
}


# ═══════════════════════════════════════════════════════════════════════════
# 🇳🇵 NEPALI STRINGS — नेपाली
# ═══════════════════════════════════════════════════════════════════════════

NEPALI: Dict[str, str] = {
    
    # ─────────────────────────────────────────────────────────────────────
    # 🎁 WELCOME & START
    # ─────────────────────────────────────────────────────────────────────
    "welcome": (
        "🎉 <b>Isukobit मा स्वागत छ!</b>\n\n"
        "म एउटा File Store Bot हुँ। तपाईं मेरो माध्यमबाट फाइलहरू "
        "अपलोड, खोज र डाउनलोड गर्न सक्नुहुन्छ।\n\n"
        "📌 <b>Quick Commands:</b>\n"
        "• /start — मुख्य मेनु\n"
        "• /help — सहयोग\n"
        "• /upload — फाइल अपलोड\n"
        "• /myfiles — आफ्ना फाइलहरू\n"
        "• /search — फाइल खोज\n\n"
        "तलका बटनहरूबाट सुरु गर्नुहोस् 👇"
    ),
    "welcome_back": (
        "🎉 <b>पुनः स्वागत, {name}!</b>\n\n"
        "तपाईं के गर्न चाहनुहुन्छ?\n"
        "तलका बटनहरूबाट चयन गर्नुहोस् 👇"
    ),
    "hello": "नमस्ते, {name}! 🙏",
    "good_morning": "शुभ प्रभात, {name}! ☀️",
    "good_evening": "शुभ सन्ध्या, {name}! 🌆",
    "good_night": "शुभ रात्री, {name}! 🌙",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📋 MAIN MENU
    # ─────────────────────────────────────────────────────────────────────
    "main_menu": (
        "📋 <b>मुख्य मेनु</b>\n\n"
        "तपाईं के गर्न चाहनुहुन्छ? तलका बटनहरूबाट चयन गर्नुहोस् 👇"
    ),
    "menu_upload": "📤 फाइल अपलोड",
    "menu_my_files": "📁 मेरा फाइलहरू",
    "menu_search": "🔍 खोज",
    "menu_stats": "📊 तथ्याङ्क",
    "menu_settings": "⚙️ सेटिङ",
    "menu_help": "❓ सहयोग",
    "menu_about": "ℹ️ जानकारी",
    "menu_back": "⬅️ फर्कनुहोस्",
    "menu_home": "🏠 गृह",
    "menu_close": "❌ बन्द",
    "menu_refresh": "🔄 रिफ्रेस",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📤 UPLOAD
    # ─────────────────────────────────────────────────────────────────────
    "upload_prompt": (
        "📤 <b>फाइल अपलोड</b>\n\n"
        "आफ्नो फाइल पठाउनुहोस् (document, video, audio, photo आदि)\n\n"
        "📌 <b>सीमाहरू:</b>\n"
        "• अधिकतम: {max_size}\n"
        "• अनुमति: {allowed_types}\n\n"
        "फाइल पठाउने बित्तिकै म सुरक्षित गर्नेछु।"
    ),
    "upload_processing": "⏳ फाइल प्रशोधन हुँदैछ, कृपया प्रतीक्षा गर्नुहोस्...",
    "upload_success": (
        "✅ <b>फाइल अपलोड भयो!</b>\n\n"
        "📄 <b>नाम:</b> <code>{filename}</code>\n"
        "📦 <b>आकार:</b> {size}\n"
        "🔑 <b>कोड:</b> <code>{code}</code>\n"
        "🔗 <b>लिङ्क:</b> {link}\n\n"
        "📌 पछि पहुँच गर्न यो कोड/लिङ्क सुरक्षित राख्नुहोस्।"
    ),
    "upload_failed": "❌ अपलोड असफल। पुनः प्रयास गर्नुहोस्।",
    "upload_too_large": (
        "❌ <b>फाइल धेरै ठूलो छ!</b>\n\n"
        "📦 तपाईंको फाइल: {size}\n"
        "📏 अधिकतम: {max_size}\n\n"
        "सानो फाइल पठाउनुहोस्।"
    ),
    "upload_type_not_allowed": (
        "❌ <b>यो फाइल प्रकार अनुमति छैन!</b>\n\n"
        "📄 तपाईंको: <code>{extension}</code>\n"
        "✅ अनुमति: {allowed}"
    ),
    "upload_cancelled": "❌ अपलोड रद्द।",
    "upload_limit_reached": (
        "⚠️ <b>अपलोड सीमा पुग्यो!</b>\n\n"
        "तपाईंले {limit} फाइलहरू अपलोड गर्नुभयो।"
    ),
    "upload_wait": "⏳ प्रतीक्षा गर्नुहोस्...",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📁 MY FILES
    # ─────────────────────────────────────────────────────────────────────
    "my_files_header": (
        "📁 <b>तपाईंका फाइलहरू</b>\n\n"
        "कुल: <b>{count}</b> फाइलहरू\n"
        "पृष्ठ: <b>{page}/{total_pages}</b>"
    ),
    "my_files_empty": (
        "📂 <b>अहिलेसम्म कुनै फाइल अपलोड गरिएको छैन!</b>\n\n"
        "तल 'फाइल अपलोड' बटन थिच्नुहोस्।"
    ),
    "my_files_error": "❌ फाइलहरू लोड हुन सकेन।",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🔍 SEARCH
    # ─────────────────────────────────────────────────────────────────────
    "search_prompt": (
        "🔍 <b>फाइल खोज</b>\n\n"
        "फाइलको नाम, कोड, वा कीवर्ड पठाउनुहोस्।"
    ),
    "search_no_results": (
        "🔍 <b>कुनै फाइल भेटिएन!</b>\n\n"
        "Query: <code>{query}</code>"
    ),
    "search_results": (
        "🔍 <b>खोज परिणाम</b>\n\n"
        "Query: <code>{query}</code>\n"
        "भेटिए: <b>{count}</b> फाइलहरू\n"
        "पृष्ठ: <b>{page}/{total_pages}</b>"
    ),
    "search_too_short": (
        "⚠️ Query धेरै छोटो छ!\n\n"
        "कम्तीमा <b>{min_length}</b> अक्षर पठाउनुहोस्।"
    ),
    "search_processing": "🔍 खोज्दै...",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📄 FILE INFO
    # ─────────────────────────────────────────────────────────────────────
    "file_info": (
        "📄 <b>फाइल विवरण</b>\n\n"
        "📝 <b>नाम:</b> <code>{filename}</code>\n"
        "🔑 <b>कोड:</b> <code>{code}</code>\n"
        "📦 <b>आकार:</b> {size}\n"
        "📅 <b>अपलोड:</b> {date}\n"
        "👤 <b>अपलोडर:</b> {uploader}\n"
        "📥 <b>डाउनलोड:</b> {downloads}"
    ),
    "file_not_found": "❌ फाइल भेटिएन!",
    "file_deleted": "✅ फाइल मेटियो!",
    "file_delete_confirm": (
        "⚠️ <b>पक्का मेट्ने?</b>\n\n"
        "📄 फाइल: <code>{filename}</code>\n\n"
        "यो कार्य फिर्ता गर्न सकिँदैन!"
    ),
    "file_delete_success": "🗑️ फाइल सफलतापूर्वक मेटियो!",
    "file_delete_cancelled": "❌ मेट्ने रद्द।",
    "file_access_denied": (
        "🔒 <b>यो फाइल तपाईंको होइन!</b>\n\n"
        "यो फाइल {owner} ले अपलोड गरेको हो।"
    ),
    "file_expired": "⏰ <b>यो फाइल म्याद सकियो!</b>",
    "file_download_started": "📥 डाउनलोड सुरु भयो...",
    "file_sending": "📤 फाइल पठाउँदै...",
    "file_sent": "✅ फाइल पठाइयो!",
    "file_send_failed": "❌ फाइल पठाउन सकिएन।",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🔗 SHARE & LINK
    # ─────────────────────────────────────────────────────────────────────
    "share_link": (
        "🔗 <b>फाइल लिङ्क</b>\n\n"
        "📄 <b>फाइल:</b> <code>{filename}</code>\n"
        "🔗 <b>लिङ्क:</b>\n{link}"
    ),
    "share_copied": "✅ लिङ्क कपी भयो!",
    "share_qr": "📱 <b>QR कोड</b>",
    "link_invalid": "❌ लिङ्क अवैध!",
    
    # ─────────────────────────────────────────────────────────────────────
    # 👤 USER PROFILE
    # ─────────────────────────────────────────────────────────────────────
    "my_profile": (
        "👤 <b>तपाईंको प्रोफाइल</b>\n\n"
        "📝 <b>नाम:</b> {name}\n"
        "🆔 <b>User ID:</b> <code>{user_id}</code>\n"
        "📅 <b>सामेल:</b> {join_date}\n"
        "📁 <b>फाइलहरू:</b> {total_files}"
    ),
    "profile_updated": "✅ प्रोफाइल अपडेट भयो!",
    "user_banned_msg": (
        "🚫 <b>तपाईं प्रतिबन्धित हुनुहुन्छ!</b>\n\n"
        "कारण: {reason}"
    ),
    "user_not_registered": "❌ तपाईं दर्ता हुनुहुन्न। /start पठाउनुहोस्।",
    
    # ─────────────────────────────────────────────────────────────────────
    # ⚙️ SETTINGS
    # ─────────────────────────────────────────────────────────────────────
    "settings_menu": "⚙️ <b>सेटिङ</b>\n\nतलका विकल्पहरूबाट चयन गर्नुहोस् 👇",
    "settings_language": "🌍 भाषा परिवर्तन",
    "settings_saved": "✅ सेटिङ सुरक्षित भयो!",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📊 STATISTICS
    # ─────────────────────────────────────────────────────────────────────
    "stats_header": (
        "📊 <b>Bot तथ्याङ्क</b>\n\n"
        "👥 <b>कुल प्रयोगकर्ता:</b> {total_users}\n"
        "📁 <b>कुल फाइलहरू:</b> {total_files}\n"
        "📥 <b>कुल डाउनलोड:</b> {total_downloads}\n"
        "💾 <b>कुल आकार:</b> {total_size}"
    ),
    "stats_user": (
        "📊 <b>तपाईंको तथ्याङ्क</b>\n\n"
        "📁 फाइलहरू: <b>{files}</b>\n"
        "📥 डाउनलोड: <b>{downloads}</b>"
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # ❓ HELP & ABOUT
    # ─────────────────────────────────────────────────────────────────────
    "help": (
        "❓ <b>सहयोग</b>\n\n"
        "📌 <b>Commands:</b>\n"
        "/start — मुख्य मेनु\n"
        "/help — यो सन्देश\n"
        "/upload — फाइल अपलोड\n"
        "/myfiles — आफ्ना फाइलहरू\n\n"
        "📞 <b>Support:</b> {support}"
    ),
    "help_short": "❓ /help पठाउनुहोस्",
    "about": (
        "ℹ️ <b>Bot को बारेमा</b>\n\n"
        "🤖 नाम: {bot_name}\n"
        "📦 संस्करण: {version}\n"
        "👑 मालिक: {owner}"
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # 📢 FORCE JOIN
    # ─────────────────────────────────────────────────────────────────────
    "force_join": (
        "🔒 <b>पहुँच अस्वीकृत!</b>\n\n"
        "Bot प्रयोग गर्न तलका च्यानलहरू जोडिनुहोस्, "
        "त्यसपछि <b>✅ Verify</b> थिच्नुहोस्।"
    ),
    "force_join_verified": "✅ Verified! अब तपाईं bot प्रयोग गर्न सक्नुहुन्छ।",
    "force_join_not_verified": "❌ Verify भएन! पहिले सबै च्यानल जोडिनुहोस्।",
    "force_join_channels": "📢 <b>यी च्यानलहरू जोडिनुहोस्:</b>",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🚨 ERRORS
    # ─────────────────────────────────────────────────────────────────────
    "error_generic": (
        "❌ <b>केही गलत भयो!</b>\n\n"
        "Error: <code>{error}</code>"
    ),
    "error_unknown": "❌ अज्ञात त्रुटि।",
    "error_timeout": "⏰ समय सकियो!",
    "error_rate_limit": "⚠️ धेरै छिटो! {seconds} सेकेन्डमा प्रयास गर्नुहोस्।",
    "error_maintenance": "🛠️ Bot मर्मतमा छ। पछि प्रयास गर्नुहोस्।",
    "error_banned": "🚫 तपाईं प्रतिबन्धित हुनुहुन्छ।",
    "error_not_admin": "❌ यो admin-only हो।",
    "error_not_owner": "❌ यो owner-only हो।",
    "error_network": "🌐 नेटवर्क समस्या।",
    "error_file_corrupt": "❌ फाइल बिग्रिएको छ।",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🎉 CONFIRMATIONS
    # ─────────────────────────────────────────────────────────────────────
    "confirm_yes": "✅ हो",
    "confirm_no": "❌ होइन",
    "confirm_cancel": "❌ रद्द",
    "confirm_ok": "✅ ठीक",
    "confirm_done": "✅ भयो!",
    "confirm_saved": "💾 सुरक्षित!",
    "confirm_deleted": "🗑️ मेटियो!",
    "confirm_updated": "✅ अपडेट!",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🎊 LOADING
    # ─────────────────────────────────────────────────────────────────────
    "loading": "⏳ लोड हुँदै...",
    "processing": "⚙️ प्रशोधन हुँदै...",
    "please_wait": "⏳ प्रतीक्षा गर्नुहोस्...",
    "searching": "🔍 खोज्दै...",
    "saving": "💾 सुरक्षित गर्दै...",
    "deleting": "🗑️ मेट्दै...",
    "uploading": "📤 अपलोड गर्दै...",
    "downloading": "📥 डाउनलोड गर्दै...",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📅 TIME
    # ─────────────────────────────────────────────────────────────────────
    "time_just_now": "अहिले",
    "time_minutes_ago": "{count} मिनेट अघि",
    "time_hours_ago": "{count} घण्टा अघि",
    "time_days_ago": "{count} दिन अघि",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📏 SIZE
    # ─────────────────────────────────────────────────────────────────────
    "size_bytes": "{count} B",
    "size_kb": "{count} KB",
    "size_mb": "{count} MB",
    "size_gb": "{count} GB",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🎁 MISC
    # ─────────────────────────────────────────────────────────────────────
    "thank_you": "🙏 धन्यवाद!",
    "your_welcome": "🙏 स्वागत छ!",
    "congratulations": "🎉 बधाई छ!",
    "good_luck": "🍀 शुभकामना!",
    "no_permission": "🚫 अनुमति छैन!",
    "coming_soon": "🚧 चाँडै आउँदैछ!",
    "try_again": "🔄 पुनः प्रयास गर्नुहोस्।",
    "thanks_for_using": "🙏 Isukobit प्रयोग गर्नुभएकोमा धन्यवाद!",
}


# ═══════════════════════════════════════════════════════════════════════════
# 🏛️ LATIN STRINGS — Latina
# ═══════════════════════════════════════════════════════════════════════════

LATIN: Dict[str, str] = {
    
    # ─────────────────────────────────────────────────────────────────────
    # 🎁 WELCOME & START
    # ─────────────────────────────────────────────────────────────────────
    "welcome": (
        "🎉 <b>Salve ad Isukobit!</b>\n\n"
        "Ego sum File Store Bot. Potes per me fasciculos "
        "immittere, quaerere et deponere.\n\n"
        "📌 <b>Mandata Celer:</b>\n"
        "• /start — Index principalis\n"
        "• /help — Auxilium\n"
        "• /upload — Immittere fasciculum\n"
        "• /myfiles — Videre fasciculos\n"
        "• /search — Quaerere\n\n"
        "Incipe cum bullis infra 👇"
    ),
    "welcome_back": (
        "🎉 <b>Salve iterum, {name}!</b>\n\n"
        "Quid facere vis?\n"
        "Elige ex bullis infra 👇"
    ),
    "hello": "Salve, {name}! 🙏",
    "good_morning": "Bonum mane, {name}! ☀️",
    "good_evening": "Bonam vesperam, {name}! 🌆",
    "good_night": "Bonam noctem, {name}! 🌙",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📋 MAIN MENU
    # ─────────────────────────────────────────────────────────────────────
    "main_menu": (
        "📋 <b>Index Principalis</b>\n\n"
        "Quid facere vis? Elige ex bullis infra 👇"
    ),
    "menu_upload": "📤 Immittere Fasciculum",
    "menu_my_files": "📁 Mei Fasciculi",
    "menu_search": "🔍 Quaerere",
    "menu_stats": "📊 Statistica",
    "menu_settings": "⚙️ Optiones",
    "menu_help": "❓ Auxilium",
    "menu_about": "ℹ️ De Bot",
    "menu_back": "⬅️ Retro",
    "menu_home": "🏠 Domus",
    "menu_close": "❌ Claude",
    "menu_refresh": "🔄 Renovare",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📤 UPLOAD
    # ─────────────────────────────────────────────────────────────────────
    "upload_prompt": (
        "📤 <b>Immittere Fasciculum</b>\n\n"
        "Mitte fasciculum tuum (documentum, video, audio, imago, etc.)\n\n"
        "📌 <b>Limites:</b>\n"
        "• Maxima magnitudo: {max_size}\n"
        "• Permissa: {allowed_types}\n\n"
        "Servabo quam primum mittis."
    ),
    "upload_processing": "⏳ Fasciculus processatur, exspecta...",
    "upload_success": (
        "✅ <b>Fasciculus immissus!</b>\n\n"
        "📄 <b>Nomen:</b> <code>{filename}</code>\n"
        "📦 <b>Magnitudo:</b> {size}\n"
        "🔑 <b>Codex:</b> <code>{code}</code>\n"
        "🔗 <b>Nexus:</b> {link}\n\n"
        "📌 Serva hunc codicem/nexum."
    ),
    "upload_failed": "❌ Immissio defecit. Tenta iterum.",
    "upload_too_large": (
        "❌ <b>Fasciculus nimis magnus!</b>\n\n"
        "📦 Tuus: {size}\n"
        "📏 Maximus: {max_size}"
    ),
    "upload_type_not_allowed": (
        "❌ <b>Hoc genus non permittitur!</b>\n\n"
        "📄 Tuus: <code>{extension}</code>\n"
        "✅ Permissa: {allowed}"
    ),
    "upload_cancelled": "❌ Immissio cancellata.",
    "upload_limit_reached": "⚠️ <b>Limes attinctus!</b>",
    "upload_wait": "⏳ Exspecta...",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📁 MY FILES
    # ─────────────────────────────────────────────────────────────────────
    "my_files_header": (
        "📁 <b>Tui Fasciculi</b>\n\n"
        "Totales: <b>{count}</b> fasciculi\n"
        "Pagina: <b>{page}/{total_pages}</b>"
    ),
    "my_files_empty": "📂 <b>Nulli fasciculi adhuc immissi!</b>",
    "my_files_error": "❌ Fasciculi non onerari possunt.",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🔍 SEARCH
    # ─────────────────────────────────────────────────────────────────────
    "search_prompt": "🔍 <b>Quaerere Fasciculum</b>\n\nMitte nomen, codicem, vel verbum.",
    "search_no_results": "🔍 <b>Nulli fasciculi inventi!</b>\n\nQuaesitum: <code>{query}</code>",
    "search_results": (
        "🔍 <b>Resultata</b>\n\n"
        "Quaesitum: <code>{query}</code>\n"
        "Inventi: <b>{count}</b>"
    ),
    "search_too_short": "⚠️ Nimis breve! Minimum <b>{min_length}</b> litterae.",
    "search_processing": "🔍 Quaerens...",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📄 FILE INFO
    # ─────────────────────────────────────────────────────────────────────
    "file_info": (
        "📄 <b>De Fasciculo</b>\n\n"
        "📝 <b>Nomen:</b> <code>{filename}</code>\n"
        "🔑 <b>Codex:</b> <code>{code}</code>\n"
        "📦 <b>Magnitudo:</b> {size}\n"
        "📅 <b>Immissus:</b> {date}\n"
        "👤 <b>Immissor:</b> {uploader}\n"
        "📥 <b>Depositiones:</b> {downloads}"
    ),
    "file_not_found": "❌ Fasciculus non inventus!",
    "file_deleted": "✅ Fasciculus deletus!",
    "file_delete_confirm": (
        "⚠️ <b>Vere delere?</b>\n\n"
        "📄 <code>{filename}</code>\n\n"
        "Hoc non potest revocari!"
    ),
    "file_delete_success": "🗑️ Fasciculus deletus!",
    "file_delete_cancelled": "❌ Deletio cancellata.",
    "file_access_denied": "🔒 <b>Hic fasciculus non est tuus!</b>",
    "file_expired": "⏰ <b>Hic fasciculus expiravit!</b>",
    "file_download_started": "📥 Depositio incepit...",
    "file_sending": "📤 Mittens fasciculum...",
    "file_sent": "✅ Fasciculus missus!",
    "file_send_failed": "❌ Mittere defecit.",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🔗 SHARE & LINK
    # ─────────────────────────────────────────────────────────────────────
    "share_link": (
        "🔗 <b>Nexus Fasciculi</b>\n\n"
        "📄 <b>Fasciculus:</b> <code>{filename}</code>\n"
        "🔗 <b>Nexus:</b>\n{link}"
    ),
    "share_copied": "✅ Nexus copiatus!",
    "share_qr": "📱 <b>Codex QR</b>",
    "link_invalid": "❌ Nexus invalidus!",
    
    # ─────────────────────────────────────────────────────────────────────
    # 👤 USER PROFILE
    # ─────────────────────────────────────────────────────────────────────
    "my_profile": (
        "👤 <b>Tuum Profilum</b>\n\n"
        "📝 <b>Nomen:</b> {name}\n"
        "🆔 <b>ID:</b> <code>{user_id}</code>\n"
        "📅 <b>Iunctus:</b> {join_date}\n"
        "📁 <b>Fasciculi:</b> {total_files}"
    ),
    "profile_updated": "✅ Profilum renovatum!",
    "user_banned_msg": "🚫 <b>Interdictus es!</b>\n\nCausa: {reason}",
    "user_not_registered": "❌ Non registratus. Mitte /start.",
    
    # ─────────────────────────────────────────────────────────────────────
    # ⚙️ SETTINGS
    # ─────────────────────────────────────────────────────────────────────
    "settings_menu": "⚙️ <b>Optiones</b>\n\nElige infra 👇",
    "settings_language": "🌍 Mutare Linguam",
    "settings_saved": "✅ Optiones servatae!",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📊 STATISTICS
    # ─────────────────────────────────────────────────────────────────────
    "stats_header": (
        "📊 <b>Statistica Bot</b>\n\n"
        "👥 <b>Usatores:</b> {total_users}\n"
        "📁 <b>Fasciculi:</b> {total_files}\n"
        "📥 <b>Depositiones:</b> {total_downloads}\n"
        "💾 <b>Magnitudo:</b> {total_size}"
    ),
    "stats_user": (
        "📊 <b>Tua Statistica</b>\n\n"
        "📁 Fasciculi: <b>{files}</b>\n"
        "📥 Depositiones: <b>{downloads}</b>"
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # ❓ HELP & ABOUT
    # ─────────────────────────────────────────────────────────────────────
    "help": (
        "❓ <b>Auxilium</b>\n\n"
        "📌 <b>Mandata:</b>\n"
        "/start — Index\n"
        "/help — Hoc\n"
        "/upload — Immittere\n"
        "/myfiles — Mei fasciculi\n\n"
        "📞 <b>Suffragium:</b> {support}"
    ),
    "help_short": "❓ Mitte /help",
    "about": (
        "ℹ️ <b>De Bot</b>\n\n"
        "🤖 Nomen: {bot_name}\n"
        "📦 Versio: {version}\n"
        "👑 Dominus: {owner}"
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # 📢 FORCE JOIN
    # ─────────────────────────────────────────────────────────────────────
    "force_join": (
        "🔒 <b>Aditus Negatus!</b>\n\n"
        "Iunge canales infra, deinde preme <b>✅ Verify</b>."
    ),
    "force_join_verified": "✅ Verificatus! Nunc uti potes.",
    "force_join_not_verified": "❌ Non verificatus! Iunge omnes canales.",
    "force_join_channels": "📢 <b>Iunge hos canales:</b>",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🚨 ERRORS
    # ─────────────────────────────────────────────────────────────────────
    "error_generic": "❌ <b>Aliquid mali factum!</b>\n\nError: <code>{error}</code>",
    "error_unknown": "❌ Error ignotus.",
    "error_timeout": "⏰ Tempus exiit!",
    "error_rate_limit": "⚠️ Nimis celer! Tenta in {seconds} secundis.",
    "error_maintenance": "🛠️ Bot in maintenance est.",
    "error_banned": "🚫 Interdictus es.",
    "error_not_admin": "❌ Hoc solum admin.",
    "error_not_owner": "❌ Hoc solum dominus.",
    "error_network": "🌐 Problema retis.",
    "error_file_corrupt": "❌ Fasciculus corruptus.",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🎉 CONFIRMATIONS
    # ─────────────────────────────────────────────────────────────────────
    "confirm_yes": "✅ Ita",
    "confirm_no": "❌ Non",
    "confirm_cancel": "❌ Cancellare",
    "confirm_ok": "✅ OK",
    "confirm_done": "✅ Factum!",
    "confirm_saved": "💾 Servatum!",
    "confirm_deleted": "🗑️ Deletum!",
    "confirm_updated": "✅ Renovatum!",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🎊 LOADING
    # ─────────────────────────────────────────────────────────────────────
    "loading": "⏳ Onerans...",
    "processing": "⚙️ Processans...",
    "please_wait": "⏳ Exspecta...",
    "searching": "🔍 Quaerens...",
    "saving": "💾 Servans...",
    "deleting": "🗑️ Delens...",
    "uploading": "📤 Immittens...",
    "downloading": "📥 Deponens...",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📅 TIME
    # ─────────────────────────────────────────────────────────────────────
    "time_just_now": "nunc",
    "time_minutes_ago": "{count} minutis ante",
    "time_hours_ago": "{count} horis ante",
    "time_days_ago": "{count} diebus ante",
    
    # ─────────────────────────────────────────────────────────────────────
    # 📏 SIZE
    # ─────────────────────────────────────────────────────────────────────
    "size_bytes": "{count} B",
    "size_kb": "{count} KB",
    "size_mb": "{count} MB",
    "size_gb": "{count} GB",
    
    # ─────────────────────────────────────────────────────────────────────
    # 🎁 MISC
    # ─────────────────────────────────────────────────────────────────────
    "thank_you": "🙏 Gratias!",
    "your_welcome": "🙏 Libenter!",
    "congratulations": "🎉 Gratulationes!",
    "good_luck": "🍀 Bona fortuna!",
    "no_permission": "🚫 Non permittitur!",
    "coming_soon": "🚧 Mox venit!",
    "try_again": "🔄 Tenta iterum.",
    "thanks_for_using": "🙏 Gratias pro Isukobit!",
}


# ═══════════════════════════════════════════════════════════════════════════
# 📚 ALL STRINGS DICTIONARY
# ═══════════════════════════════════════════════════════════════════════════

ALL_STRINGS: Dict[str, Dict[str, str]] = {
    "hinglish": HINGLISH,
    "english": ENGLISH,
    "nepali": NEPALI,
    "latin": LATIN,
}


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 MAIN FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def get_string(
    key: str,
    lang: str = DEFAULT_LANGUAGE,
    **kwargs: Any
) -> str:
    """
    Language ke hisaab se string return karta hai.
    
    Parameters
    ----------
    key : str
        String ka key (e.g. "welcome")
    lang : str
        Language code — hinglish, english, nepali, latin
    **kwargs
        Dynamic values jo string mein inject hongi (e.g. name="Raj")
    
    Returns
    -------
    str
        Formatted message
    
    Examples
    --------
    >>> get_string("hello", lang="hinglish", name="Raj")
    'Namaste, Raj! 🙏'
    
    >>> get_string("upload_success", lang="english", 
    ...            filename="doc.pdf", size="2 MB", 
    ...            code="ISU-A1B2C3", link="https://t.me/...")
    """
    
    # Language validate karo (Case-insensitive)
    lang = lang.lower() if isinstance(lang, str) else DEFAULT_LANGUAGE
    if lang not in ALL_STRINGS:
        lang = DEFAULT_LANGUAGE
    
    # Language dictionary lo
    lang_dict = ALL_STRINGS[lang]
    
    # Key dhundho — agar nahi mili toh English se lo
    text = lang_dict.get(key)
    
    if text is None:
        # Fallback to English
        text = ENGLISH.get(key)
    
    if text is None:
        # Fallback to Hinglish
        text = HINGLISH.get(key)
    
    if text is None:
        # Bilkul nahi mili — return key as-is with warning
        return f"⚠️ [Missing string: {key}]"
    
    # Format karo agar kwargs hain
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError as e:
            # Missing placeholder
            text = f"⚠️ [Format error in '{key}': missing {e}]"
        except Exception as e:
            text = f"⚠️ [Format error in '{key}': {e}]"
    
    return text


def get_string_safe(
    key: str,
    lang: str = DEFAULT_LANGUAGE,
    default: str = "",
    **kwargs: Any
) -> str:
    """
    Safe version — kabhi error nahi dega.
    Missing key hone pe default return karega.
    """
    try:
        result = get_string(key, lang, **kwargs)
        if result.startswith("⚠️ ["):
            return default or key
        return result
    except Exception:
        return default or key


def has_string(key: str, lang: str = DEFAULT_LANGUAGE) -> bool:
    """Check karta hai ki string exists karti hai ya nahi"""
    lang = lang.lower() if isinstance(lang, str) else DEFAULT_LANGUAGE
    if lang not in ALL_STRINGS:
        return False
    return key in ALL_STRINGS[lang]


def get_all_keys() -> set:
    """Saare available string keys return karta hai"""
    keys = set()
    for lang_dict in ALL_STRINGS.values():
        keys.update(lang_dict.keys())
    return keys


def get_missing_keys(lang: str) -> list:
    """Kisi language mein kaunsi keys missing hain"""
    lang = lang.lower() if isinstance(lang, str) else DEFAULT_LANGUAGE
    if lang not in ALL_STRINGS:
        return []
    
    all_keys = get_all_keys()
    lang_keys = set(ALL_STRINGS[lang].keys())
    
    return sorted(all_keys - lang_keys)


def get_language_dict(lang: str) -> Dict[str, str]:
    """Kisi language ka poora dictionary return karta hai"""
    lang = lang.lower() if isinstance(lang, str) else DEFAULT_LANGUAGE
    return ALL_STRINGS.get(lang, HINGLISH).copy()


def get_language_name(lang: str, native: bool = False) -> str:
    """Language ka display name return karta hai"""
    lang = lang.lower() if isinstance(lang, str) else DEFAULT_LANGUAGE
    if native:
        return LANGUAGE_NAMES_NATIVE.get(lang, lang)
    return LANGUAGE_NAMES.get(lang, lang)


def get_language_flag(lang: str) -> str:
    """Language ka flag emoji return karta hai"""
    lang = lang.lower() if isinstance(lang, str) else DEFAULT_LANGUAGE
    return LANGUAGE_FLAGS.get(lang, "🌍")


def is_valid_language(lang: str) -> bool:
    """Check karta hai ki language valid hai ya nahi"""
    return isinstance(lang, str) and lang.lower() in SUPPORTED_LANGUAGES


# ═══════════════════════════════════════════════════════════════════════════
# 📏 HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def format_size(size_bytes: int, lang: str = DEFAULT_LANGUAGE) -> str:
    """
    Bytes ko human-readable size mein convert karta hai.
    
    Examples
    --------
    >>> format_size(1024)
    '1.00 KB'
    >>> format_size(1048576)
    '1.00 MB'
    """
    if size_bytes <= 0:
        return get_string("size_bytes", lang, count=0)
    
    KB = 1024
    MB = KB * 1024
    GB = MB * 1024
    TB = GB * 1024
    
    if size_bytes < KB:
        return get_string("size_bytes", lang, count=size_bytes)
    elif size_bytes < MB:
        return get_string("size_kb", lang, count=round(size_bytes / KB, 2))
    elif size_bytes < GB:
        return get_string("size_mb", lang, count=round(size_bytes / MB, 2))
    elif size_bytes < TB:
        return get_string("size_gb", lang, count=round(size_bytes / GB, 2))
    else:
        return get_string("size_tb", lang, count=round(size_bytes / TB, 2))


def format_time_ago(seconds: int, lang: str = DEFAULT_LANGUAGE) -> str:
    """Seconds ko 'X minutes ago' format mein convert karta hai"""
    if seconds <= 0:
        return get_string("time_just_now", lang)
    if seconds < 60:
        return get_string("time_just_now", lang)
    elif seconds < 3600:
        return get_string("time_minutes_ago", lang, count=seconds // 60)
    elif seconds < 86400:
        return get_string("time_hours_ago", lang, count=seconds // 3600)
    elif seconds < 604800:
        return get_string("time_days_ago", lang, count=seconds // 86400)
    elif seconds < 2592000:
        return get_string("time_weeks_ago", lang, count=seconds // 604800)
    elif seconds < 31536000:
        return get_string("time_months_ago", lang, count=seconds // 2592000)
    else:
        return get_string("time_years_ago", lang, count=seconds // 31536000)


def format_duration(seconds: int) -> str:
    """Seconds ko 'Xd Yh Zm' format mein convert karta hai"""
    if seconds <= 0:
        return "0s"
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 and not days:
        parts.append(f"{secs}s")
    
    return " ".join(parts) if parts else "0s"


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    # Dictionaries
    "HINGLISH",
    "ENGLISH",
    "NEPALI",
    "LATIN",
    "ALL_STRINGS",
    
    # Constants
    "SUPPORTED_LANGUAGES",
    "DEFAULT_LANGUAGE",
    "LANGUAGE_FLAGS",
    "LANGUAGE_NAMES",
    "LANGUAGE_NAMES_NATIVE",
    
    # Functions
    "get_string",
    "get_string_safe",
    "has_string",
    "get_all_keys",
    "get_missing_keys",
    "get_language_dict",
    "get_language_name",
    "get_language_flag",
    "is_valid_language",
    
    # Formatters
    "format_size",
    "format_time_ago",
    "format_duration",
]


# ═══════════════════════════════════════════════════════════════════════════
# 🧪 SELF-TEST
# ═══════════════════════════════════════════════════════════════════════════

def _self_test() -> None:
    """String file ka self-test"""
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  🧪 ISUKOBIT — STRINGS SELF-TEST                        ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    # Languages info
    print(f"🌍 Supported Languages: {', '.join(SUPPORTED_LANGUAGES)}")
    print(f"🎯 Default Language   : {DEFAULT_LANGUAGE}")
    print(f"📚 Total String Keys  : {len(get_all_keys())}")
    print()
    
    # Per-language stats
    print("📊 Per-Language Stats:")
    for lang in SUPPORTED_LANGUAGES:
        count = len(ALL_STRINGS[lang])
        missing = len(get_missing_keys(lang))
        flag = get_language_flag(lang)
        name = get_language_name(lang, native=True)
        print(f"   {flag} {name:<28} : {count:>3} strings ({missing} missing)")
    print()
    
    # Test strings
    print("🧪 Sample Strings:")
    print()
    
    samples = [
        ("hello", "hinglish", {"name": "Raj"}),
        ("hello", "english", {"name": "Raj"}),
        ("hello", "nepali", {"name": "Raj"}),
        ("hello", "latin", {"name": "Marcus"}),
        ("upload_success", "hinglish", {
            "filename": "notes.pdf",
            "size": "2.5 MB",
            "code": "ISU-A1B2C3",
            "link": "https://t.me/IsukobitBot?start=ISU-A1B2C3"
        }),
    ]
    
    for key, lang, kwargs in samples:
        result = get_string(key, lang, **kwargs)
        # Remove HTML for console display
        clean = result.replace("<b>", "").replace("</b>", "")
        clean = clean.replace("<code>", "").replace("</code>", "")
        # Pehli line only
        first_line = clean.split("\n")[0]
        print(f"   [{lang}] {first_line}")
    print()
    
    # Format tests
    print("📏 Format Tests:")
    print(f"   format_size(1024)       = {format_size(1024)}")
    print(f"   format_size(1048576)    = {format_size(1048576)}")
    print(f"   format_size(52428800)   = {format_size(52428800)}")
    print(f"   format_time_ago(30)     = {format_time_ago(30)}")
    print(f"   format_time_ago(3600)   = {format_time_ago(3600)}")
    print(f"   format_duration(3661)   = {format_duration(3661)}")
    print()
    
    # Validation
    errors = []
    for lang in SUPPORTED_LANGUAGES:
        missing = get_missing_keys(lang)
        if missing:
            errors.append(f"{lang}: {missing[:5]}...")
    
    if errors:
        print(f"⚠️  Warnings:")
        for err in errors:
            print(f"   • {err}")
    else:
        print("✅ All languages have all keys!")
    
    print()
    print("✅ Self-test complete!")
    print()


if __name__ == "__main__":
    _self_test()


# ═══════════════════════════════════════════════════════════════════════════
# 📖 END OF FILE
# ═══════════════════════════════════════════════════════════════════════════
#
# Total lines : ~1100+
# Languages   : 4 (Hinglish, English, Nepali, Latin)
# String keys : 150+ per language
#
# USAGE:
# ─────────────────────────────────────────────────────────────────────────
# from strings import get_string, format_size
#
# # Simple
# msg = get_string("welcome", lang="hinglish")
#
# # With variables
# msg = get_string("upload_success", lang="english",
#                  filename="doc.pdf", size="2 MB",
#                  code="ISU-ABC123", link="https://t.me/...")
#
# # Format helpers
# size_str = format_size(52428800)  # "50.00 MB"
#
# ═══════════════════════════════════════════════════════════════════════════
