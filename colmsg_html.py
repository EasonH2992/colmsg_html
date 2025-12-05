# This script creates HTML message log files from 'colmsg' backup data.

import os
import sys
import html
from pathlib import Path 

try:
    import winreg
except ImportError:
    winreg = None

# Nickname used to substitute '%%%' in text messages.
NICK_NAME="<b>%%%</b>" 
OUTPUT_PATH=""

MEMBER_LIST=[]
MONTH_LIST=[]
MAIN_LIST=[]

# --- HTML/CSS Templates ---

HTML_HEADER=" \
<html> \
<head> \
<meta charset='UTF-8'> \
<title>Colmsg Message View</title> \
<style> \
/* General Styles */ \
body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f7f7f7; margin: 0; padding: 0;} \
.chat-container { max-width: 600px; margin: 0 auto; background-color: #fff; padding: 10px; } \
\
/* Top Header Style */ \
.top-header { \
    position: sticky; \
    top: 0; \
    max-width: 600px; \
    height: 50px; \
    margin: 0 auto; \
    background-color: white; \
    color: #333; \
    display: flex; \
    align-items: center; \
    justify-content: center; \
    font-size: 18px; \
    font-weight: bold; \
    z-index: 10; \
    padding: 0 10px; \
    border-bottom: 1px solid #eee; \
    box-shadow: 0 1px 2px rgba(0,0,0,0.05); \
} \
\
/* Message Row Style */ \
.message-row { display: flex; margin-bottom: 15px; align-items: flex-start; } \
\
/* Avatar Placeholder */ \
.avatar-placeholder { width: 40px; height: 40px; border-radius: 50%; margin-right: 10px; background-color: #ddd; display: flex; align-items: center; justify-content: center; color: #555; font-weight: bold; font-size: 14px; } \
\
/* Content Block */ \
.message-content { display: flex; flex-direction: column; max-width: 75%; } \
\
/* Sender Info & Timestamp */ \
.message-info { font-size: 12px; color: #999; margin-bottom: 2px; } \
.message-sender { font-weight: bold; color: #333; margin-right: 8px; font-size: 14px; } \
\
/* Text/Video/Image Bubble (Standard) */ \
.message-bubble { \
    background-color: #e6e6e6; \
    padding: 10px 12px; \
    border-radius: 10px; /* Reduced corner radius */ \
    position: relative; \
    word-wrap: break-word; \
    font-size: 14px; \
    line-height: 1.5; \
} \
\
\
/* Image and Video elements inside the bubble */ \
.message-bubble img, .message-bubble video { \
    max-width: 100%; \
    height: auto; \
    border-radius: 8px; \
    margin-top: 0; \
} \
\
/* Audio player element style */ \
.audio-message-bubble audio { \
    height: 50px; \
    display: block; \
} \
\
/* Date Separator */ \
.date-divider { text-align: center; font-size: 11px; color: #888; margin: 20px 0; } \
</style> \
</head> \
<body> \
\
\
<div class='top-header' id='page-header'>成員姓名</div> \
<div class='chat-container'> \
"

HTML_FOOTER=" \
</div> \
</body> \
</html> \
"

def getCleanMemberName(item_path):
    """
    Extracts the clean member folder name from the path for display (e.g., 'Member Name').
    """
    normalized_path = os.path.normpath(item_path)
    path_parts = normalized_path.split(os.path.sep)
    # The last part is typically the member's name
    member_name = path_parts[-1] if len(path_parts) > 0 else None
    return member_name

def get_windows_download_path():
    """
    Retrieves the actual Windows Downloads folder path using the Registry, 
    overcoming drive letter and localization issues.
    """
    if winreg is None:
        return None 
        
    try:
        # Registry key for User Shell Folders
        key_path = r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            # GUID for the Downloads folder
            download_path, _ = winreg.QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')
            return download_path
    except Exception:
        return None

def readTxtFile(file_path):
    f=open(file_path, 'r', encoding='utf-8')
    content=f.read()
    return content

def addUniqueMember(member):
    if member not in MEMBER_LIST:
        MEMBER_LIST.append(member)

def addUniqueMonth(month):
    if month not in MONTH_LIST:
        MONTH_LIST.append(month)
        
def getTimeString(file_name):
    parts=file_name.split('_')
    if len(parts) > 2:
        # Extracts YYYY-MM-DD HH:MM from the timestamp part of the filename
        ts = parts[2]
        return f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]} {ts[8:10]}:{ts[10:12]}"
    return ""

def getYearMonth(file_name):
    parts=file_name.split('_')
    if len(parts) > 2:
        year_month = parts[2][0:6]  # Get YYYYMM
        return year_month
    return None

def getMemberName(item_path):
    normalized_path = os.path.normpath(item_path)
    path_parts = normalized_path.split(os.path.sep)
    last_folder = path_parts[-1] if len(path_parts) > 0 else None
    return last_folder
    
    
def getGroupName(item_path):
    normalized_path = os.path.normpath(item_path)
    path_parts = normalized_path.split(os.path.sep)
    second_last_folder = path_parts[-2] if len(path_parts) > 1 else None
    return second_last_folder
    
def getFileNamesFromColMsg(parent_directory):
    file_names = []
    
    # Recursively walk through directories to find message files
    for root, dirs, files in os.walk(parent_directory):
        
        normalized_root = os.path.normpath(root)
        path_parts = normalized_root.split(os.path.sep)

        # Check for the Group/Member folder depth
        if len(path_parts) >= 2 and path_parts[-2] != "": 
            group = getGroupName(root)
            member_name = getMemberName(root)
            member = group + "-" + member_name

            for file_name in files:
                
                if file_name.startswith('.'):
                    continue
                    
                month=getYearMonth(file_name)
                
                if month: 
                    addUniqueMember(member)
                    addUniqueMonth(month)
                    content=""
                    
                    file_path = os.path.join(root, file_name)
                    
                    # Read content only for text files
                    if file_name.lower().endswith(".txt"):
                      content=html.escape(readTxtFile(file_path)).replace('\n', '<br>')
                    # For media files, content remains empty
                    elif file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4')):
                      pass

                    file_names.append((member, month, getTimeString(file_name), file_name, normalized_root, content))
        
    return file_names
    
def genMonthlyPackContent(member, month):
    # Filters MAIN_LIST for messages belonging to a specific member and month
    selected=(member, month)
    matching=[record for record in MAIN_LIST if record[:2] == selected]
    return matching

def getMessageFileName(member, month):
    global OUTPUT_PATH
    # Creates member-specific output subdirectory
    directory= os.path.join(OUTPUT_PATH, member) 
    if not os.path.exists(directory):
      os.makedirs(directory)
    return os.path.join(directory, member + month +".html") 

def getTxtContent(record):
    global NICK_NAME
    
    sender_name = getCleanMemberName(record[4]) 
    
    html_output = ""
    html_output += "<div class='message-row'>"
    # Simple avatar placeholder
    initials = sender_name[0] if sender_name else 'M'
    html_output += f"<div class='avatar-placeholder'>{initials}</div>"
    
    html_output += "<div class='message-content'>"
    
    # Sender name and timestamp
    html_output += f"<div class='message-info'><span class='message-sender'>{sender_name}</span>{record[2]}</div>"
    
    # Text message bubble
    message_text = record[5].replace("%%%", NICK_NAME)
    html_output += f"<div class='message-bubble'>{message_text}</div>"
    
    html_output += "</div>" # message-content
    html_output += "</div>" # message-row
    
    return html_output

def getJpgContent(record):
    # record[4] is the file directory, record[3] is filename, record[2] is timestamp
    sender_name = getCleanMemberName(record[4]) 
    initials = sender_name[0] if sender_name else 'M'
    
    file_url = os.path.join(record[4], record[3]).replace(os.path.sep, '/')
    
    html_output = ""
    html_output += "<div class='message-row'>"
    html_output += f"<div class='avatar-placeholder'>{initials}</div>"
    
    html_output += "<div class='message-content'>"
    html_output += f"<div class='message-info'><span class='message-sender'>{sender_name}</span>{record[2]}</div>"
    
    # Image container using standard message bubble style
    html_output += f"<div class='message-bubble'>" 
    html_output += f"<img src='{file_url}' alt='Image Message' />"
    html_output += "</div>" 
    
    html_output += "</div>"
    html_output += "</div>"
    
    return html_output

def getMp4Content(record):
    # record[4] is the file directory, record[3] is filename, record[2] is timestamp
    sender_name = getCleanMemberName(record[4]) 
    initials = sender_name[0] if sender_name else 'M'
    
    file_url = os.path.join(record[4], record[3]).replace(os.path.sep, '/')
    
    # Determine if it's video (type '2') or audio (type '3') based on filename
    parts = record[3].split('_')
    media_type = parts[1] if len(parts) > 1 else '2' 
    is_audio = (media_type == '3')
    
    # Set CSS class and HTML tag accordingly
    bubble_class = 'audio-message-bubble' if is_audio else 'message-bubble'
    html_tag = 'audio' if is_audio else 'video'
    
    html_output = ""
    html_output += "<div class='message-row'>"
    html_output += f"<div class='avatar-placeholder'>{initials}</div>"
    
    html_output += "<div class='message-content'>"
    html_output += f"<div class='message-info'><span class='message-sender'>{sender_name}</span>{record[2]}</div>"
    
    # Media container (applies specific bubble style)
    html_output += f"<div class='{bubble_class}'>"
    
    # Embed audio or video player
    html_output += f"<{html_tag} controls><source src='{file_url}' type='{html_tag}/mp4'></{html_tag}>"
    
    html_output += "</div>" # bubble
    
    html_output += "</div>" # message-content
    html_output += "</div>" # message-row
    
    return html_output


def genMessageFile(member, month, content):
    html_output="";
    
    # Generate the header with the correct member name
    if content:
        clean_member_name = getCleanMemberName(content[0][4]) 
        
        # Replace the placeholder in HTML_HEADER
        header_with_title = HTML_HEADER.replace("<div class='top-header' id='page-header'>成員姓名</div>", 
                                                f"<div class='top-header' id='page-header'>{clean_member_name}</div>")
    else:
        header_with_title = HTML_HEADER
    
    html_output+=header_with_title
    
    # Populate content
    for record in content:
      if record[3].lower().endswith(".txt"):
        html_output+=getTxtContent(record)
      elif record[3].lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        html_output+=getJpgContent(record)
      elif record[3].lower().endswith(".mp4"):
        html_output+=getMp4Content(record)
        
    html_output+=HTML_FOOTER

    with open(getMessageFileName(member, month), 'w', encoding='utf-8') as file:
      file.write(html_output)

def loopList():
    # Iterates through all unique members and months to generate monthly files
    for member in MEMBER_LIST:
        for month in MONTH_LIST:
            content=genMonthlyPackContent(member, month)
            if content:
                genMessageFile(member, month, content)


# --- Main Execution Logic ---

if __name__ == "__main__":
    
    # --- 1. Determine Base Directory ---
    
    # Attempt to get the accurate Windows Downloads path first
    windows_path = get_windows_download_path()
    
    if windows_path:
        base_dir = windows_path
        default_source = "Windows Registry"
    else:
        # Fallback to cross-platform default (Home/Downloads)
        try:
            base_dir = str(Path.home() / 'Downloads')
            default_source = "Path.home() / 'Downloads'"
        except:
            # Final fallback to script directory
            base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            default_source = "Script Folder"
            
        
    # --- 2. Process Arguments and Set Paths ---
    
    if len(sys.argv) >= 2:
        # Override default base_dir with first argument
        base_dir = os.path.abspath(sys.argv[1])
        default_source = "Argument 1"

    # Default Input Path: base_dir + 'colmsg'
    parent_dir = os.path.join(base_dir, "colmsg")
    
    # Default Output Path: base_dir + 'colmsg-html'
    OUTPUT_PATH = os.path.join(base_dir, "colmsg-html")
    
    
    # Override Output Path with second argument
    if len(sys.argv) >= 3:
        OUTPUT_PATH = os.path.abspath(sys.argv[2])
        
    # --- 3. Check and Create Output Directory ---
    
    if not os.path.exists(OUTPUT_PATH):
        try:
            os.makedirs(OUTPUT_PATH)
            print(f"Created output directory: {OUTPUT_PATH}")
        except OSError as e:
            print(f"Error creating output directory {OUTPUT_PATH}: {e}")
            sys.exit(1)

    # --- 4. Interactive Nick Name Prompt ---
    
    default_nickname_display = NICK_NAME.strip('<b>').strip('</b>')
    
    print("\n--- Configuration Summary ---")
    print(f"Input Directory: {parent_dir}")
    print(f"Output Directory: {OUTPUT_PATH}\n")
    
    try:
        nickname_input = input(f"Please enter your Nick Name (default: {default_nickname_display}): ")
    except EOFError:
        nickname_input = "" 
        print("Non-interactive session detected, using default nickname.")
        
    if nickname_input:
        NICK_NAME = f"<b>{nickname_input}</b>"
    
    # --- 5. Execute Main Logic ---
    
    if not os.path.exists(parent_dir):
        print(f"Error: Input directory not found: {parent_dir}")
        print("Please ensure the 'colmsg' folder exists inside your Base Directory.")
        sys.exit(1)
        
    print(f"Start generating HTML...")
    
    MAIN_LIST=getFileNamesFromColMsg(parent_dir)
    
    if not MAIN_LIST:
        print("Warning: No valid files found in the input directory structure. Exiting.")
        sys.exit(0)
        
    MEMBER_LIST.sort()
    MONTH_LIST.sort()
    loopList()
    
    print(f"\nGeneration complete. HTML files saved to: {OUTPUT_PATH}")