import os
import tkinter as tk
from datetime import date, timedelta, datetime
from tkinter import Scrollbar
import requests
import re
import json

index = 0
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
programs = []

window = tk.Tk()
window.geometry("550x600")
window.title("Televideo")
window.resizable(True, True)
#window.attributes('-fullscreen', True)
window.configure(background = "white")
factor = 50
offset = 50

def update_canvas_region():
    global canvas
    canvas.update_idletasks()
    canvas.config(scrollregion = canvas.bbox("all"))


def show_error_message(text):
    global index, factor, offset, canvas
    warning = tk.Label(canvas, text = text, fg = "red", bg = "white", font = ("Helvetica", 24))
    canvas.create_window(0 + offset, index * factor + offset, window = warning, anchor = "center")
    #warning.grid(row = index, column = 0, sticky = "WE")
    index += 1
    update_canvas_region()

def get_web_page(url):
    getUrl = requests.get(url)
    if (getUrl.status_code != 200):
        show_error_message("Impossibile connettersi a " + url)
        return ""
    return json.dumps(getUrl.text)

def find_channels():
    global channels
    sURL = "https://guidatv.quotidiano.net/"
    siteContent = get_web_page(sURL)
    #siteContent = "data-srcset="https://immagini.quotidiano.net/?url=https%3A%2F%2Fs3.eu-west-1.amazonaws.com%2Fstatic.guidatv.quotidiano.net%2Fimg%2Floghi_tv%2Fsky_cinema_action.png&w=100&h=100&fmt=webp&mode=fill&bg=ffffff" type="image/webp" />\n        <source data-srcset="https://immagini.quotidiano.net/?url=https%3A%2F%2Fs3.eu-west-1.amazonaws.com%2Fstatic.guidatv.quotidiano.net%2Fimg%2Floghi_tv%2Fsky_cinema_action.png&w=100&h=100&mode=fill&bg=ffffff" />\n        <img src="data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==" data-src="https://immagini.quotidiano.net/?url=https%3A%2F%2Fs3.eu-west-1.amazonaws.com%2Fstatic.guidatv.quotidiano.net%2Fimg%2Floghi_tv%2Fsky_cinema_action.png&w=100&h=100&mode=fill&bg=ffffff" class="lazyload"  title="Sky Cinema Action" alt="Sky Cinema Action" width="100" height="100" />\n    </picture>\n    \n      \n      <span class="channel-name">Sky Cinema Action</span>\n      \n    </a>\n  </header>\n  \n</section>\n\n    \n\n    \n<section class="channel channel-thumbnail">\n  <header class="channel-header">\n    <a href="/sky_cinema_collection/"\n       title="Programmi Sky Cinema Collection">\n      \n        \n    <picture>\n        <source data-srcset="https://immagini.quotidiano.net/?url=https%3A%2F%2Fs3.eu-west-1.amazonaws.com%2Fstatic.guidatv.quotidiano.net%2Fimg%2Floghi_tv%2Fsky_cinema_collection.png&w=100&h=100&fmt=webp&mode=fill&bg=ffffff" type="image/webp" />\n        <source data-srcset="https://immagini.quotidiano.net/?url=https%3A%2F%2Fs3.eu-west-1.amazonaws.com%2Fstatic.guidatv.quotidiano.net%2Fimg%2Floghi_tv%2Fsky_cinema_collection.png&w=100&h=100&mode=fill&bg=ffffff" />\n        <img src="data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==" data-src="https://immagini.quotidiano.net/?url=https%3A%2F%2Fs3.eu-west-1.amazonaws.com%2Fstatic.guidatv.quotidiano.net%2Fimg%2Floghi_tv%2Fsky_cinema_collection.png&w=100&h=100&mode=fill&bg=ffffff" class="lazyload""
    #print(siteContent)
    pattern = r'(?<=channel channel-thumbnail)(.*?)(?=title)'
    matches = re.findall(pattern, siteContent, flags = re.IGNORECASE)
    pattern2 = r'(?<=\"channel-name\\">)(.*?)(?=</span>)'
    matches2 = re.findall(pattern2, siteContent, flags = re.IGNORECASE)
    for i, s in enumerate(matches):
        pattern = r'(?<=a href=\\"/)(.*?)(?=\\")'
        match = re.findall(pattern, s, flags = re.IGNORECASE)
        canale = {"url": sURL + match[0], "name": matches2[i]}
        channels.append(canale)

def add_text_block(text, tag):
    global index, factor, offset, canvas
    title = tk.Label(canvas, text = text, fg = "black", bg = "white", font = ("Helvetica", 20))
    title.tag = tag
    canvas.create_window(0 + offset + (canvas.winfo_width()), index * factor + offset, window = title, anchor = "center")
    #title.grid(row = index, column = 0, sticky = "EW")
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
        if hasattr(widget, "tag") and getattr(widget, "tag") == tag:
            widget.destroy()
    add_program_in_panel("", index)
    index += 1
    add_search_button(index)
    index += 1

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
    for widget in canvas.winfo_children():
        if hasattr(widget, "tag"):
            widget.destroy()
    insert_programs_to_search()
    
def add_program_in_panel(line, tag):
    global index, factor, offset, canvas
    tb = tk.Entry(canvas, textvariable = tk.StringVar(value = line), fg = "black", bg = "white", font = ("Helvetica", 20), width = 30)
    tb.bind("<FocusOut>", lambda event: textBox_LostFocus(tb.get(), tag))
    tb.tag = tag
    canvas.create_window(0 + 5 * offset, index * factor + offset, window = tb, anchor = "e")
    #tb.grid(row = index, column = 0, sticky = "WE")
    b = tk.Button(canvas, text = "Rimuovi", command = lambda e = None, tag = tag: removeButton_Click(e, tag))
    b.tag = tag
    canvas.create_window(0 + 5 * offset, index * factor + offset, window = b, anchor = "w")
    #b.grid(row = index, column = 1, sticky = "WE")
    index += 1

def load_programs_to_search():
    global programs
    programs = []
    with open(os.path.join(__location__, 'programs.txt'), 'r', encoding = "utf-8") as file:
        for riga in file:
            programs.append(riga.rstrip('\n'))
    return programs

def find_programs():
    global index, offset, factor, canvas
    global programs
    today = date.today()
    for j, canale_x in enumerate(channels):
        for d in range(7):
            day = today + timedelta(days = d)
            day_string = day.strftime("%d-%m-%Y")
            site_content = get_web_page(channels[j]["url"] + day_string)
            if(site_content == ""):
                return
            start_index = site_content.find('<section id=\\"faqs\\">')
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
                        #found.grid(row = index, column = 0, sticky = "W")
                        index += 1
                        time_string = (matches[ctr])[0:5]
                        time = datetime.strptime(time_string + ":00", "%H:%M:%S")
                        if ((time >= datetime.strptime("00:00:00", "%H:%M:%S")) and (time < datetime.strptime("06:00:00", "%H:%M:%S"))):
                            text2 = (datetime.strptime(day_string, "%d-%m-%Y") + timedelta(days = 1)).strftime("%d-%m-%Y") + " " + channels[j]["name"] + " " + matches[ctr]
                        else:
                            text2 = day_string + " " + channels[j]["name"] + " " + matches[ctr]
                        found2 = tk.Label(canvas, text = text2, fg = "black", bg = "white", font = ("Helvetica", 20))
                        canvas.create_window(0 + offset, index * factor + offset, window = found2, anchor = "center")
                        #found2.grid(row = index, column = 0, sticky = "NSWE")
                        index += 1
    end = tk.Label(canvas, text = "Ricerca completata", fg = "green", bg = "white", font = ("Helvetica", 24))
    canvas.create_window(0 + offset, index * factor + offset, window = end, anchor = "center")
    #end.grid(row = index, column = 0, sticky = "WE")
    index += 1

def searchButton_Click(event, tag):
    global canvas
    load_programs_to_search()
    if not programs:
        return
    for widget in canvas.winfo_children():
        if hasattr(widget, "tag") and getattr(widget, "tag") > tag:
            widget.destroy()
    find_programs()
    update_canvas_region()
    window.geometry(str(canvas.winfo_width()) + "x800")

def add_search_button(tag):
    global index, offset, factor, canvas
    addButton = tk.Button(canvas, text = "Aggiungi programma", command = lambda e = None, tag= tag: addButton_Click(tag))
    addButton.tag = tag
    canvas.create_window(0 + offset, index * factor + offset, window = addButton, anchor = "e")
    #addButton.grid(row = index, column = 0, sticky = "W")
    searchButton = tk.Button(canvas, text = "Cerca programmi", command = lambda e = None, tag = tag: searchButton_Click(e, tag))
    searchButton.tag = tag
    canvas.create_window(0 + offset, index * factor + offset, window = searchButton, anchor = "w")
    #searchButton.grid(row = index, column = 0, sticky = "E")
    index += 1
    canvas.update_idletasks()
    canvas.config(scrollregion = canvas.bbox("all"))

def add_rows():
    global index, offset, factor, canvas
    for i in range(15):
        label_vuoto = tk.Label(canvas, text="", bg = "white")
        canvas.create_window(0 + offset, (index + i) * factor + offset, window = label_vuoto, anchor = "center")
        #label_vuoto.grid(row = index + i, column = 0, sticky = "WE")

def insert_programs_to_search():
    global canvas
    i = 0
    add_text_block("Programmi da cercare", i)
    i += 1
    with open(os.path.join(__location__, 'programs.txt'), 'r', encoding = "utf-8") as file:
        for line in file:
            add_program_in_panel(line.rstrip('\n'), i)
            i += 1
    add_search_button(i)
    add_rows()
    update_canvas_region()

window.grid_rowconfigure(0, weight = 1)
window.grid_columnconfigure(0, weight = 1)
#w, h = window.winfo_screenwidth(), window.winfo_screenheight()
canvas = tk.Canvas(window, bg = "white")#, scrollregion = (0, 0, 1000, 1000)) # f"0 0 {w * 2} {h * 2}")
#canvas.update_idletasks()
#canvas.config(scrollregion = canvas.bbox("all"))
canvas.grid(row = 0, column = 0, sticky = 'nswe')
wh = Scrollbar(window, orient = 'horizontal', command = canvas.xview)
wh.grid(row = 6, column = 0, sticky = 'ew')
wv = Scrollbar(window, orient = 'vertical', command = canvas.yview)
wv.grid(row = 0, column = 6, sticky = 'ns')
canvas.config(yscrollcommand = wv.set, xscrollcommand = wh.set)
canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
canvas.bind_all("<Shift-MouseWheel>", lambda event: canvas.xview_scroll(int(-1 * (event.delta / 120)), "units"))

channels = []

find_channels()
insert_programs_to_search()

if __name__ == "__main__":
    window.mainloop()