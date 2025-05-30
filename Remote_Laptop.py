from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import screen_brightness_control as sbc
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import os
import subprocess
import time
import keyboard as kb  # Renamed to avoid conflict with variable names
import psutil
import pyautogui
import cv2
import webbrowser
import pyperclip
import random
from comtypes import CLSCTX_ALL

# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "Enter your bot token here")
ALLOWED_USER_ID = 123456789  # Replace with your Telegram user ID 
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB max file size for transfers

# Initialize the Application with your bot token
app = Application.builder().token(BOT_TOKEN).build()

response_dict = {
    "hello": "Hello! How are you, sir?",
    "hi": "Hi! How can I assist you today?",
    "how are you": "I'm just a bot, but I'm functioning perfectly!",
    "what is your name": "I am your friendly chatbot. You can call me Bot!",
    "bye": "Goodbye! Have a great day!"
}

shortcuts = {
    'copy': 'ctrl+c',
    'cut': 'ctrl+x',
    'paste': 'ctrl+v',
    'undo': 'ctrl+z',
    'redo': 'ctrl+y',
    'save': 'ctrl+s',
    'open': 'ctrl+o',
    'print': 'ctrl+p',
    'select all': 'ctrl+a',
    'find': 'ctrl+f',
    'new': 'ctrl+n',
    'close': 'ctrl+w',
    'new folder': 'ctrl+shift+n',
    'reopen closed tab': 'ctrl+shift+t',
    'next tab': 'ctrl+tab',
    'previous tab': 'ctrl+shift+tab',
    'new tab': 'ctrl+t',
    'underline': 'ctrl+u',
    'bold': 'ctrl+b',
    'italic': 'ctrl+i',
    'open start menu': 'ctrl+esc',
    'close window': 'alt+f4',
    'switch apps': 'alt+tab',
    'window menu': 'alt+space',
    'show desktop': 'windows+d',
    'file explorer': 'windows+e',
    'run': 'windows+r',
    'lock computer': 'windows +l',
    'task view': 'windows+tab',
    'help': 'f1',
    'rename': 'f2',
    'search': 'f3',
    'address bar': 'f4',
    'refresh': 'f5',
    'cycle through elements': 'f6',
    'spell check': 'f7',
    'extend selection': 'f8',
    'update fields': 'f9',
    'activate menu': 'f10',
    'toggle fullscreen': 'f11',
    'save as': 'f12',
    'cancel': 'esc',
    'hold for uppercase': 'shift',
    'right-click': 'shift+f10',
    'change case': 'shift+f3',
    'shrink selection': 'shift+f8',
    'task manager': 'ctrl+shift+esc',
    'zoom in': 'ctrl+plus',
    'zoom out': 'ctrl+-',
    'reset zoom': 'ctrl+0',
    'clear browsing data': 'ctrl+shift+delete',
    'new incognito window': 'ctrl+shift+n',
    'private browsing': 'ctrl+shift+p',
    'navigate tabs backward': 'ctrl+shift+tab',
    'switch to next window': 'ctrl+alt+tab',
    'switch to previous window': 'ctrl+alt+shift+tab',
    'open new tab': 'ctrl+alt+t',
    'open new private window': 'ctrl+alt+p',
    'open developer tools': 'ctrl+alt+i',
    'open console': 'ctrl+alt+c',
    'view page source': 'ctrl+alt+u',
    'find in page': 'ctrl+alt+f',
    'lock screen orientation': 'ctrl+alt+l',
    'reload': 'ctrl+alt+r',
    'save page as': 'ctrl+alt+s',
    'close current tab': 'ctrl+alt+w',
    'quit browser': 'ctrl+alt+q',
    'backslash': '|',
}

# ==================== UTILITY FUNCTIONS ====================
async def is_authorized(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == ALLOWED_USER_ID:
        return True
    else:
        await update.message.reply_text("❌ Access Denied: You are not authorized to use this bot.")
        return False

async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE, error: Exception):
    """Centralized error handling"""
    try:
        message = update.message or (update.callback_query.message if update.callback_query else None)
        if message:
            await message.reply_text(f"❌ Error: {str(error)}")
        print(f"Error: {error}", flush=True)
    except Exception as e:
        print(f"Critical error handler failure: {e}", flush=True)

# ==================== START COMMAND (ADDED) ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context):
        return
        
    await update.message.reply_text(
        "👋 *Welcome to Remote Control Bot!*\n\n"
        "I can help you control your computer remotely. Use /menu to see available options "
        "or type /help for a list of commands.",
        parse_mode="Markdown",
        reply_markup=main_menu_markup
    )

# ==================== FILE BROWSER (NEW FEATURES) ====================
async def browse_files(update: Update, context: ContextTypes.DEFAULT_TYPE, path="C:\\"):
    if not await is_authorized(update, context):
        return
        
    try:
        message = update.message or update.callback_query.message
        items = os.listdir(path)
        
        keyboard = []
        
        
        # Add drive buttons at root level
        if path == "C:\\":
            drives = [f"{d}:\\" for d in "CDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
            for drive in drives:
                keyboard.append([InlineKeyboardButton(f"📀 Drive {drive}", callback_data=f"browse_{drive}")])
        
        # Folders first
        for item in sorted(items):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                keyboard.append([InlineKeyboardButton(f"📁 {item}", callback_data=f"browse_{full_path}")])
        
        # Files with icons
        for item in sorted(items):
            full_path = os.path.join(path, item)
            if os.path.isfile(full_path):
                icon = "📄"
                ext = os.path.splitext(item)[1].lower()
                if ext in ['.png', '.jpg', '.jpeg', '.gif']:
                    icon = "🖼️"
                elif ext in ['.mp4', '.avi', '.mov']:
                    icon = "🎬"
                keyboard.append([InlineKeyboardButton(f"{icon} {item}", callback_data=f"file_{full_path}")])
        
        # Navigation buttons
        parent = os.path.dirname(path)
        if parent != path:
            keyboard.append([InlineKeyboardButton("⬆️ Parent Directory", callback_data=f"browse_{parent}")])
        
        # Action buttons
        keyboard.append([
            InlineKeyboardButton("🖥️ Shutdown PC", callback_data="shutdown_pc"),
            InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")
        ])
        
        await message.reply_text(
            f"📂 Browsing: {path}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        await handle_error(update, context, e)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str):
    if not await is_authorized(update, context):
        return
        
    try:
        message = update.callback_query.message
        
        # Check file size
        if os.path.getsize(file_path) > MAX_FILE_SIZE:
            await message.reply_text("⚠️ File too large (max 50MB)")
            return
            
        ext = os.path.splitext(file_path)[1].lower()
        
        # Handle different file types
        if ext in ['.png', '.jpg', '.jpeg', '.gif']:
            await message.reply_photo(photo=open(file_path, 'rb'))
        elif ext in ['.mp4', '.avi', '.mov']:
            await message.reply_video(video=open(file_path, 'rb'))
        elif ext in ['.txt', '.log', '.csv', '.py']:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(4000)
                await message.reply_text(f"📝 Content:\n```\n{content}\n```", parse_mode="Markdown")
        else:
            await message.reply_document(document=open(file_path, 'rb'))
            
    except Exception as e:
        await handle_error(update, context, e)

# ==================== SYSTEM CONTROL (NEW FEATURES) ====================
async def shutdown_pc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context):
        return
        
    try:
        message = update.message or update.callback_query.message
        
        # Confirmation keyboard
        keyboard = [
            [InlineKeyboardButton("✅ Yes, shutdown now", callback_data="confirm_shutdown")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_shutdown")]
        ]
        
        await message.reply_text(
            "⚠️ Are you sure you want to shutdown the PC immediately?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        await handle_error(update, context, e)

async def confirm_shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.callback_query.message
        await message.edit_text("🖥️ Shutting down PC NOW...")
        os.system("shutdown /s /t 1")  # Immediate shutdown
    except Exception as e:
        await handle_error(update, context, e)

# ==================== MENU SYSTEM (NEW FEATURES) ====================
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context):
        return
        
    try:
        message = update.message or update.callback_query.message
        keyboard = [
            [InlineKeyboardButton("📁 Browse Files", callback_data='browse_C:\\'),
             InlineKeyboardButton("🎹 Shortcuts", callback_data='show_shortcuts')],
            [InlineKeyboardButton("🖥️ System Info", callback_data='system_info'),
             InlineKeyboardButton("📸 Screenshot", callback_data='screenshot')],
            [InlineKeyboardButton("🖥️ Shutdown PC", callback_data='shutdown_pc')]
        ]
        await message.reply_text(
            "🏠 Main Menu - Choose an option:",
            reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        await handle_error(update, context, e)

# ==================== ORIGINAL FEATURES ====================
async def send_shortcut_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message with shortcut buttons + Hide Button."""
    if not await is_authorized(update, context):
        return
    
    message = update.message or update.callback_query.message
    keyboard_buttons = [[InlineKeyboardButton(name, callback_data=f"shortcut_{name}")] for name in shortcuts.keys()]
    
    # Adding "Hide Buttons" at the end
    keyboard_buttons.append([InlineKeyboardButton("🛑 Hide Buttons", callback_data="hide_buttons")])

    reply_markup = InlineKeyboardMarkup(keyboard_buttons)

    sent_message = await message.reply_text("🎹 *Press a button to trigger a shortcut:*", 
                                           reply_markup=reply_markup, 
                                           parse_mode="Markdown")
    
    # Store the message ID to delete it later
    context.user_data["last_message_id"] = sent_message.message_id

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulate shortcut key press and delete the message when hide is clicked."""
    query = update.callback_query
    await query.answer()

    callback_data = query.data
    
    if callback_data == "hide_buttons":
        # Delete the message containing the buttons
        if "last_message_id" in context.user_data:
            try:
                await query.message.delete()
            except Exception as e:
                print(f"Error deleting message: {e}")
        
        # Send confirmation
        await query.message.reply_text("🔴 *Shortcut buttons hidden! Use /shortcuts to show again.*", parse_mode="Markdown")
        return
    
    if callback_data.startswith("shortcut_"):
        shortcut_name = callback_data.replace("shortcut_", "")
        shortcut_keys = shortcuts.get(shortcut_name, None)

        # Simulate the key press
        if shortcut_keys:
            try:
                kb.press_and_release(shortcut_keys)
                await query.message.reply_text(f"✅ *{shortcut_name}* shortcut triggered! (`{shortcut_keys}`)", parse_mode="Markdown")
            except Exception as e:
                await query.message.reply_text(f"⚠️ Error triggering shortcut: {e}")
        else:
            await query.message.reply_text("⚠️ Shortcut not found.")
    elif callback_data == "youtube":
        await youtube_url(update, context)
    elif callback_data == "open_whatsapp":
        await open_whatsapp(update, context)
    elif callback_data == "system_info":
        await system_info(update, context)
    elif callback_data == "screenshot":
        await take_screenshot(update, context)
    elif callback_data == "click_photo":
        await click_photo(update, context)
    elif callback_data == "menu":
        await menu(update, context)
    elif callback_data.startswith('browse_'):
        await browse_files(update, context, callback_data[7:])
    elif callback_data.startswith('file_'):
        await handle_file(update, context, callback_data[5:])
    elif callback_data == 'shutdown_pc':
        await shutdown_pc(update, context)
    elif callback_data == 'confirm_shutdown':
        await confirm_shutdown(update, context)
    elif callback_data == 'cancel_shutdown':
        await query.message.edit_text("✅ Shutdown cancelled")
    elif callback_data == 'main_menu':
        await main_menu(update, context)
    elif callback_data == 'show_shortcuts':
        await send_shortcut_buttons(update, context)

# Menu definitions
main_menu_buttons = [
    [KeyboardButton("📁 Files"), KeyboardButton("🖥️ System Info")],
    [KeyboardButton("📸 Screenshot"),KeyboardButton("🔃 Swap App"), KeyboardButton("📷 Click Photo")],
    [KeyboardButton("🔁 Prev Tab"), KeyboardButton("TAB"), KeyboardButton("🔁 Next Tab")],
    [KeyboardButton("Space"), KeyboardButton("Refress")],
    [KeyboardButton("ℹ️ Help"), KeyboardButton("⚙️ More Options")] 
]
main_menu_markup = ReplyKeyboardMarkup(main_menu_buttons, resize_keyboard=True)

more_options_buttons = [
    [KeyboardButton("📸 Screenshot"), KeyboardButton("📲 Show Apps")],
    [KeyboardButton("⬆️"), KeyboardButton("⬅️"), KeyboardButton("➡️"), KeyboardButton("⬇️")],
    [KeyboardButton("Home"), KeyboardButton("End"), KeyboardButton("🔙"), KeyboardButton("↩️")],
    [KeyboardButton("🔍 Zoom IN"), KeyboardButton("Space"), KeyboardButton("🔎 Zoom OUT")],
    [KeyboardButton("⏪ Main Menu"), KeyboardButton("⏩ Next Menu")]
]
more_options_markup = ReplyKeyboardMarkup(more_options_buttons, resize_keyboard=True)

system_buttons = [
    [KeyboardButton("📸 Screenshot"), KeyboardButton("🔓 Unlock System")],
    [KeyboardButton("🔅➕"), KeyboardButton("🔅➖"), KeyboardButton("🔉"), KeyboardButton("🔊")],
    [KeyboardButton("Undu"), KeyboardButton("Redu")],
    [KeyboardButton("⏪ Previus Menu"), KeyboardButton("🏠 Menu"), KeyboardButton("⏩ Next Menu")]
]
system_markup = ReplyKeyboardMarkup(system_buttons, resize_keyboard=True)

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello sir, Welcome to the Bot. Choose an option from the buttons below:",
        reply_markup=main_menu_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_authorized(update, context):
        await update.message.reply_text("""Available Commands:
        /youtube - To get the YouTube URL
        /open_whatsapp - To Open WhatsApp
        /system_info - To get system information 
        /screenshot - Take a screenshot of your system
        /click_photo - Take a photo using the webcam
        /browse - Browse files on your computer
        /shutdown - Shutdown your computer
        /shortcuts - Show keyboard shortcuts
        You can also type messages like 'hello', 'bye', etc., and I will respond!""")

async def youtube_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message if update.message else update.callback_query.message
    await message.reply_text("YouTube Link => https://www.youtube.com/")

async def open_whatsapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message if update.message else update.callback_query.message

    kb.press_and_release('windows')
    time.sleep(0.5)
    kb.write('WhatsApp')
    time.sleep(1)
    kb.press_and_release('enter')
    await message.reply_text("WhatsApp opened successfully.")

async def openfunction(update: Update, context: ContextTypes.DEFAULT_TYPE, query: str):
    app_name = query.replace("open ", "").strip()
    kb.press_and_release('windows')
    time.sleep(0.5)
    kb.write(app_name)
    time.sleep(1)
    kb.press_and_release('enter')
    await update.message.reply_text(f"Opened {app_name} successfully.")

async def typing(update: Update, context: ContextTypes.DEFAULT_TYPE, query: str):
    text_to_type = query.replace("type ", "").replace("write ", "").strip()
    kb.write(text_to_type)
    await update.message.reply_text("Typing completed successfully.")

async def press_key(update: Update, context: ContextTypes.DEFAULT_TYPE, query: str):
    key = query.replace("key press ", "").strip()
    try:
        kb.press_and_release(key)
        await update.message.reply_text(f"Pressed key: {key} successfully.")
    except Exception as e:
        await update.message.reply_text(f"Error pressing key: {key}. Please try again.")

async def system_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message if update.message else update.callback_query.message

    try:
        battery = psutil.sensors_battery()
        if battery:
            plugged = "Plugged In" if battery.power_plugged else "Not Plugged In"
            percent = battery.percent
            await message.reply_text(f"Battery is {percent}% charged and {plugged}.")
        else:
            await message.reply_text("Unable to retrieve battery information.")
        
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        await message.reply_text(f"CPU usage: {cpu_usage}%\nMemory usage: {memory_usage}%")
    except Exception as e:
        await message.reply_text(f"Error getting system info: {e}")

async def take_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message if update.message else update.callback_query.message

    try:
        screenshot_path = "screenshot.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        
        await message.reply_text("Screenshot taken successfully. Sharing it with you...")
        await message.reply_photo(photo=open(screenshot_path, "rb"))
        os.remove(screenshot_path)  # Clean up
    except Exception as e:
        await message.reply_text(f"Error taking screenshot: {e}")

async def click_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message if update.message else update.callback_query.message

    try:
        photo_path = "photo.jpg"
        camera = cv2.VideoCapture(0)
        return_value, image = camera.read()
        
        if return_value:
            cv2.imwrite(photo_path, image)
            await message.reply_text("Photo clicked successfully. Sharing it with you...")
            await message.reply_photo(photo=open(photo_path, "rb"))
            os.remove(photo_path)  # Clean up
        else:
            await message.reply_text("Failed to capture photo. Please ensure your camera is connected.")
    except Exception as e:
        await message.reply_text(f"Error capturing photo: {e}")
    finally:
        camera.release()
        cv2.destroyAllWindows()

async def show_apps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb.press_and_release("windows+tab")
    await update.message.reply_text("Show Apps successful")
    
async def Chenge_tab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb.press_and_release("ctrl+tab")
    await update.message.reply_text("Change Tab successful")

async def Press_enter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb.press_and_release("enter")
    await update.message.reply_text("Press Enter successful")

async def Chenge_window(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb.press_and_release("alt+tab")
    await update.message.reply_text("Change Window successful")

async def up(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb.press_and_release("up")
    await update.message.reply_text("⬆️ Press successful")

async def down(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb.press_and_release("down")
    await update.message.reply_text("⬇️ Press successful")

async def left(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb.press_and_release("left")
    await update.message.reply_text("⬅️ Press successful")

async def right(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb.press_and_release("right")
    await update.message.reply_text("➡️ Press successful")
    
async def backspace(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb.press_and_release("backspace")
    await update.message.reply_text("🔙 Press successful")

async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb.press_and_release("home")
    await update.message.reply_text("Home Press successful")

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb.press_and_release("end")
    await update.message.reply_text("End Press successful")

async def zoomin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb.press_and_release("ctrl+plus")
    await update.message.reply_text("Zoom IN successful")

async def zoomout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb.press_and_release("ctrl+-")
    await update.message.reply_text("Zoom OUT successful")

async def pre_tab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb.press_and_release("ctrl+shift+tab")
    await update.message.reply_text("Previous Tab successful")

async def refress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb.press_and_release("f5")
    await update.message.reply_text("Refresh successful")

async def tab_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb.press_and_release("tab")
    await update.message.reply_text("TAB press successful")

async def space(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb.press_and_release("space")
    await update.message.reply_text("Space press successful")

async def undo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb.press_and_release("ctrl+z")
    await update.message.reply_text("Undo successful")

async def redu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb.press_and_release("ctrl+y")
    await update.message.reply_text("Redo successful")

async def increase_brightness(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        current_brightness = sbc.get_brightness()[0]
        new_brightness = min(current_brightness + 10, 100)
        sbc.set_brightness(new_brightness)
        await update.message.reply_text(f"New brightness: {new_brightness}%")
    except Exception as e:
        await update.message.reply_text(f"Error adjusting brightness: {e}")

async def decrease_brightness(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        current_brightness = sbc.get_brightness()[0]
        new_brightness = max(current_brightness - 10, 0)
        sbc.set_brightness(new_brightness)
        await update.message.reply_text(f"New brightness: {new_brightness}%")
    except Exception as e:
        await update.message.reply_text(f"Error adjusting brightness: {e}")

async def increase_volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        current_volume = volume.GetMasterVolumeLevelScalar()
        new_volume = min(current_volume + 0.10, 1.0)
        volume.SetMasterVolumeLevelScalar(new_volume, None)
        await update.message.reply_text(f"New volume: {new_volume * 100:.0f}%")
    except Exception as e:
        await update.message.reply_text(f"Error adjusting volume: {e}")

async def decrease_volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        current_volume = volume.GetMasterVolumeLevelScalar()
        new_volume = max(current_volume - 0.10, 0.0)
        volume.SetMasterVolumeLevelScalar(new_volume, None)
        await update.message.reply_text(f"New volume: {new_volume * 100:.0f}%")
    except Exception as e:
        await update.message.reply_text(f"Error adjusting volume: {e}")

async def find_shortkut(update: Update, context: ContextTypes.DEFAULT_TYPE, query: str):
    try:
        query = query.replace("press ", "").replace("and ", "end")
        for k, v in shortcuts.items():
            if v == query:
                kb.write(k)
                await update.message.reply_text(f"press {v} successful")
                break
            elif k == query:
                kb.press_and_release(v)
                await update.message.reply_text(f"press {k} successful")
                break
        else:
            await update.message.reply_text("Shortcut not found. Please try again.")
    except Exception as e:
        await update.message.reply_text(f"Error executing shortcut: {e}")

async def chatbot_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context):
        return

    query = update.message.text.lower()
    user_input = update.message.text
    
    if "name" in query:
        response = response_dict.get(query, "My name is ROZ.")
        await update.message.reply_text(response)
    elif "open" in query:
        await openfunction(update, context, query)
    elif "write" in query or "type" in query:
        await typing(update, context, query)
    elif "key press" in query:
        await press_key(update, context, query)
    elif "press" in query:
        await find_shortkut(update, context, query)
    elif 'google' in query:
        query = query.replace("google", "")
        search_query = f"https://www.google.com/search?q={query}"
        webbrowser.open(search_query)
        await update.message.reply_text(f"Searching Google for: {query}")
    elif 'youtube' in query:
        query = query.replace("youtube", "")
        search_query = f"https://www.youtube.com/search?q={query}"
        webbrowser.open(search_query)
    elif user_input == "🔃 Swap App":
        await Chenge_window(update, context)
    elif user_input == "📁 Files":
        await browse_files(update, context)
    elif user_input == "🖥️ System Info":
        await system_info(update, context)
    elif user_input == "📸 Screenshot":
        await take_screenshot(update, context)
    elif user_input == "📷 Click Photo":
        await click_photo(update, context)
    elif user_input == "🔁 Next Tab":
        await Chenge_tab(update, context)
    elif user_input == "TAB":
        await tab_key(update, context)
    elif user_input == "🔁 Prev Tab":
        await pre_tab(update, context)
    elif user_input == "Space":
        await space(update, context)
    elif user_input == "Refress":
        await refress(update, context)       
    elif user_input == "↩️ Enter":
        await Press_enter(update, context)
    elif user_input == "ℹ️ Help":
        await help_command(update, context)
    elif user_input == "⚙️ More Options":
        await update.message.reply_text(
            "More options menu. Choose an option:",
            reply_markup=more_options_markup
        )
    elif user_input == "📲 Show Apps":
        await show_apps(update, context)
    elif user_input == "⬆️":
        await up(update, context)       
    elif user_input == "⬇️":
        await down(update, context)       
    elif user_input == "➡️":
        await right(update, context)
    elif user_input == "⬅️":
        await left(update, context)
    elif user_input == "Home":
        await home(update, context)
    elif user_input == "End":
        await end(update, context)
    elif user_input == "🔙":
        await backspace(update, context)
    elif user_input == "↩️":
        await Press_enter(update, context)
    elif user_input == "🔍 Zoom IN":
        await zoomin(update, context)
    elif user_input == "🔎 Zoom OUT":
        await zoomout(update, context)
    elif user_input == "⏩ Next Menu":
        await update.message.reply_text(
            "More options menu. Choose an option:",
            reply_markup=system_markup
        )
    elif user_input == "🔅➕":
        await increase_brightness(update, context)
    elif user_input == "🔅➖":
        await decrease_brightness(update, context)
    elif user_input == "🔊":
        await increase_volume(update, context)
    elif user_input == "🔉":
        await decrease_volume(update, context)
    elif user_input == "Undu":
        await undo(update, context)
    elif user_input == "Redu":
        await redu(update, context)
    elif user_input == "⏪ Previus Menu":
        await update.message.reply_text(
            "Back to the main menu:",
            reply_markup=more_options_markup
        )
    elif user_input == "🏠 Menu":
        await update.message.reply_text(
            "Back to the main menu:",
            reply_markup=main_menu_markup
        )
    elif user_input == "⏪ Main Menu":
        await update.message.reply_text(
            "Back to the main menu:",
            reply_markup=main_menu_markup
        )
    else:
        response = response_dict.get(query, "I'm sorry, I didn't understand that. Can you rephrase?")
        await update.message.reply_text(response)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    message = query.message
    
    if data == "youtube":
        await youtube_url(update, context)
    elif data == "open_whatsapp":
        await open_whatsapp(update, context)
    elif data == "system_info":
        await system_info(update, context)
    elif data == "screenshot":
        await take_screenshot(update, context)
    elif data == "click_photo":
        await click_photo(update, context)
    elif data == "menu":
        await menu(update, context)
    elif data.startswith('browse_'):
        await browse_files(update, context, data[7:])
    elif data.startswith('file_'):
        await handle_file(update, context, data[5:])
    elif data == 'shutdown_pc':
        await shutdown_pc(update, context)
    elif data == 'confirm_shutdown':
        await confirm_shutdown(update, context)
    elif data == 'cancel_shutdown':
        await query.message.edit_text("✅ Shutdown cancelled")
    elif data == 'main_menu':
        await main_menu(update, context)
    elif data == 'show_shortcuts':
        await send_shortcut_buttons(update, context)

# Register handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("menu", menu))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("youtube", youtube_url))
app.add_handler(CommandHandler("open_whatsapp", open_whatsapp))
app.add_handler(CommandHandler("system_info", system_info))
app.add_handler(CommandHandler("screenshot", take_screenshot))
app.add_handler(CommandHandler("click_photo", click_photo))
app.add_handler(CommandHandler("browse", lambda u,c: browse_files(u,c,"C:\\")))
app.add_handler(CommandHandler("shutdown", shutdown_pc))
app.add_handler(CommandHandler("shortcuts", send_shortcut_buttons))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_response))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(CallbackQueryHandler(button))

# Start the bot
if __name__ == "__main__":
    print("✅ Bot is starting...")
    app.run_polling()