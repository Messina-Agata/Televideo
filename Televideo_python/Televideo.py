import os
import tkinter as tk
from datetime import date, timedelta, datetime
from tkinter import Scrollbar
import re
import aiohttp
import asyncio
import inspect

index = 0
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
programs = []

window = tk.Tk()
window.geometry("550x600")
window.title("Televideo")
window.resizable(True, True)
window.configure(background = "white")
factor = 50
offset = 50
metadati = []

def update_canvas_region():
    global canvas
    canvas.update_idletasks()
    canvas.config(scrollregion = canvas.bbox("all"))


def show_error_message(text):
    global index, factor, offset, canvas
    warning = tk.Label(canvas, text = text, fg = "red", bg = "white", font = ("Helvetica", 24))
    canvas.create_window(0 + offset, index * factor + offset, window = warning, anchor = "center")
    index += 1
    update_canvas_region()

# def get_web_page(url):
#     getUrl = requests.get(url)
#     if (getUrl.status_code != 200):
#         show_error_message("Impossibile connettersi a " + url)
#         return ""
#     return json.dumps(getUrl.text)

async def get_web_page(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return ""
            return await resp.text()

async def find_channels():
    global channels
    sURL = "https://guidatv.quotidiano.net/"
    siteContent = await get_web_page(sURL)
    pattern = r'<section class="channel channel-thumbnail">(.*?)</section>'
    matches = re.findall(pattern, siteContent, flags = re.IGNORECASE | re.DOTALL)
    pattern2 = r'(?<=class="channel-name">)(.*?)(?=</span>)'
    matches2 = re.findall(pattern2, siteContent, flags = re.IGNORECASE)
    for i, s in enumerate(matches):
        pattern = r'(?<=a href="/)(.*?)(?=")'
        match = re.findall(pattern, s, flags = re.IGNORECASE)
        canale = {"url": sURL + match[0], "name": matches2[i]}
        channels.append(canale)

def add_text_block(text, tag):
    global index, factor, offset, canvas
    title = tk.Label(canvas, text = text, fg = "black", bg = "white", font = ("Helvetica", 20))
    title.tag = tag
    canvas.create_window(0 + 2 * offset, index * factor + offset, window = title, anchor = "center")
    index += 1

def textBox_LostFocus(text, tag):
    newLines = []
    righe = []
    with open(os.path.join(__location__, 'programs.txt'), 'r', encoding = "utf-8") as file:
        righeR = file.readlines()
        for r in righeR:
            righe.append(r.rstrip('\n'))
        numero_righe = len(righe)
        if (tag > numero_righe):
            newLines = righe.copy()
            newLines.append(text)
        else:
            righe[tag - 1] = text
            newLines = righe.copy()
    with open(os.path.join(__location__, 'programs.txt'), 'w', encoding = "utf-8") as file:
        file.writelines([line + '\n' for line in newLines])

def addButton_Click(tag):
    global index, canvas
    for widget in canvas.winfo_children():
        if hasattr(widget, "tag") and getattr(widget, "tag") >= tag:
            widget.destroy()
            if widget.widgetName == 'label':
                index -= 1
    index -= 1
    add_program_in_panel("", index)
    add_search_button(index)

def removeButton_Click(event, tag):
    global index, canvas
    newLines = []
    righe = []
    with open(os.path.join(__location__, 'programs.txt'), 'r', encoding = "utf-8") as file:
        righeR = file.readlines()
        for rig in righeR:
            righe.append(rig.rstrip('\n'))
        numero_righe = len(righe)
        if (tag <= numero_righe):
            del righe[tag - 1]
            newLines = righe.copy()
    with open(os.path.join(__location__, 'programs.txt'), 'w', encoding = "utf-8") as file:
        file.writelines([line + '\n' for line in newLines])
    insert_programs_to_search()
    
def add_program_in_panel(line, tag):
    global index, factor, offset, canvas
    tb = tk.Entry(canvas, textvariable = tk.StringVar(value = line), fg = "black", bg = "white", font = ("Helvetica", 20), width = 30)
    tb.bind("<FocusOut>", lambda event: textBox_LostFocus(tb.get(), tag))
    tb.tag = tag
    canvas.create_window(0 + 5 * offset, index * factor + offset, window = tb, anchor = "e")
    b = tk.Button(canvas, text = "Rimuovi", command = lambda e = None, tag = tag: removeButton_Click(e, tag))
    b.tag = tag
    canvas.create_window(0 + 5 * offset, index * factor + offset, window = b, anchor = "w")
    index += 1
    if inspect.stack()[1].function == "addButton_Click":
        with open(os.path.join(__location__, 'programs.txt'), "a", encoding="utf-8") as f:
            f.writelines("\n")


def load_programs_to_search():
    global programs
    programs = []
    with open(os.path.join(__location__, 'programs.txt'), 'r', encoding = "utf-8") as file:
        for riga in file:
            programs.append(riga.rstrip('\n'))
    return programs

async def fetch_all_pages(channels):
    global metadati
    today = date.today()
    tasks = []

    for j, canale_x in enumerate(channels):
        for d in range(7):
            day = today + timedelta(days=d)
            day_string = day.strftime("%d-%m-%Y")
            url = channels[j]["url"] + day_string
            tasks.append(get_web_page(url))
            metadati.append((j, day_string))

    return await asyncio.gather(*tasks)

def find_programs():
    global index, offset, factor, canvas, metadati
    global programs
    metadati.clear()
    i = 0
    results = asyncio.run(fetch_all_pages(channels))
    for j, canale_x in enumerate(channels):
        for d in range(7):
            site_content = results[i]
            day_string = metadati[i][1]
            j = metadati[i][0]
            i += 1
            if(site_content == ""):
                return
            start_index = site_content.find('<section id=\"faqs\">')
            if (start_index < 0):
                continue
            site_content = site_content[start_index:]
            end_index = site_content.find("</li></ul>")
            site_content = site_content[0:end_index + 5]
            rx = r'(?<=<li>)(.*?)(?=</li>)'
            matches = re.findall(rx, site_content, flags = re.IGNORECASE)
            last_time_string = (matches[len(matches) - 1])[0:5]
            last_time = datetime.strptime(last_time_string + ":00", "%H:%M:%S")
            first_time = datetime.strptime("06:00:00", "%H:%M:%S")
            elements_count = len(matches)
            if (first_time == last_time):
                elements_count -= 1
            for ctr in range(elements_count):
                for k in range(len(programs)):
                    stringa1 = matches[ctr].lower()
                    stringa2 = programs[k].lower()
                    if (stringa1.find(stringa2) >= 0):
                        found = tk.Label(canvas, text = programs[k], fg = "black", bg = "cyan", font = ("Helvetica", 20))
                        canvas.create_window(0 + offset, index * factor + offset, window = found, anchor = "center")
                        found.tag = index
                        index += 1
                        time_string = (matches[ctr])[0:5]
                        time = datetime.strptime(time_string + ":00", "%H:%M:%S")
                        if ((time >= datetime.strptime("00:00:00", "%H:%M:%S")) and (time < datetime.strptime("06:00:00", "%H:%M:%S"))):
                            text2 = (datetime.strptime(day_string, "%d-%m-%Y") + timedelta(days = 1)).strftime("%d-%m-%Y") + " " + channels[j]["name"] + " " + matches[ctr]
                        else:
                            text2 = day_string + " " + channels[j]["name"] + " " + matches[ctr]
                        found2 = tk.Label(canvas, text = text2, fg = "black", bg = "white", font = ("Helvetica", 20))
                        canvas.create_window(0 + offset, index * factor + offset, window = found2, anchor = "center")
                        found2.tag = index
                        index += 1
    end = tk.Label(canvas, text = "Ricerca completata", fg = "green", bg = "white", font = ("Helvetica", 24))
    canvas.create_window(0 + offset, index * factor + offset, window = end, anchor = "center")
    end.tag = index
    index += 1

def searchButton_Click(event, tag):
    global canvas, index
    load_programs_to_search()
    if not programs:
        return
    for widget in canvas.winfo_children():
        if hasattr(widget, "tag") and getattr(widget, "tag") > tag:
            widget.destroy()
            index -= 1
    find_programs()
    update_canvas_region()
    window.geometry(str(canvas.winfo_width()) + "x800")

def add_search_button(tag):
    global index, offset, factor, canvas
    addButton = tk.Button(canvas, text = "Aggiungi programma", command = lambda e = None, tag= tag: addButton_Click(tag))
    addButton.tag = tag
    canvas.create_window(0 + offset, index * factor + offset, window = addButton, anchor = "e")
    searchButton = tk.Button(canvas, text = "Cerca programmi", command = lambda e = None, tag = tag: searchButton_Click(e, tag))
    searchButton.tag = tag
    canvas.create_window(0 + offset, index * factor + offset, window = searchButton, anchor = "w")
    index += 1
    canvas.update_idletasks()
    canvas.config(scrollregion = canvas.bbox("all"))

def add_rows():
    global index, offset, factor, canvas
    for i in range(15):
        label_vuoto = tk.Label(canvas, text="", bg = "white")
        canvas.create_window(0 + offset, (index + i) * factor + offset, window = label_vuoto, anchor = "center")

def insert_programs_to_search():
    global canvas, index
    for widget in canvas.winfo_children():
        widget.destroy()
    i = 0
    index = 0
    add_text_block("Programmi da cercare", i)
    i += 1
    with open(os.path.join(__location__, 'programs.txt'), 'r', encoding = "utf-8") as file:
        for line in file:
            add_program_in_panel(line.rstrip('\n'), i)
            i += 1
    index = i
    add_search_button(i)
    add_rows()
    update_canvas_region()

window.grid_rowconfigure(0, weight = 1)
window.grid_columnconfigure(0, weight = 1)
canvas = tk.Canvas(window, bg = "white")
canvas.grid(row = 0, column = 0, sticky = 'nswe')
wh = Scrollbar(window, orient = 'horizontal', command = canvas.xview)
wh.grid(row = 6, column = 0, sticky = 'ew')
wv = Scrollbar(window, orient = 'vertical', command = canvas.yview)
wv.grid(row = 0, column = 6, sticky = 'ns')
canvas.config(yscrollcommand = wv.set, xscrollcommand = wh.set)
canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
canvas.bind_all("<Shift-MouseWheel>", lambda event: canvas.xview_scroll(int(-1 * (event.delta / 120)), "units"))

channels = []

asyncio.run(find_channels())
insert_programs_to_search()

if __name__ == "__main__":
    window.mainloop()