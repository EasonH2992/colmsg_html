# ColMsg HTML Viewer
Note: This project is a modified version of [ktsh2024/colmsg_html](https://github.com/ktsh2024/colmsg_html).



##  Improvements

1.  **System Downloads as Default Path:** 
    * **Input Directory:** `.\Downloads\colmsg`  (Same as Colmsg output folder)
    * **Output Directory:** `.\Downloads\colmsg-html` (Generated HTML files are saved here).

2.  **App-like UI Optimization:** Optimized the HTML output format to closely resemble the look and feel of the original application, including proper media (audio/video) classification.
![Generated chat view example](https://raw.githubusercontent.com/A872356/colmsg_html/refs/heads/main/.github/images/example.png)
---

## 🚀 How to Use

You must have Python 3 installed on your system.

Run the script and enter your nickname when prompted (optional).

```bash
python colmsg_html.py
```
**Example:**
```bash
$ python colmsg_html.py

Input Directory: C:\download\colmsg
Output Directory: C:\download\colmsg-html

Please enter your Nick Name (default: %%%): 日向太郎
Start generating HTML...

Generation complete. HTML files saved to: C:\download\colmsg-html
```

### Option: Using the Batch Script

Use the provided `run_demo.cmd` to automatically input your nickname:

1.  Modify `run_demo.cmd`.
    
2.  Change `<Your Nickname>` to your desired.
```
@echo off
set NICKNAME_INPUT=<Your Nickname>
echo %NICKNAME_INPUT% | python colmsg_html.py
pause
```