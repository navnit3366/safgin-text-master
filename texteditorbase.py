from PIL import Image
from PIL import ImageTk
from tkinter import colorchooser, filedialog, messagebox, font
import tkinter as tk
from os.path import exists, split, splitext
import platform
if platform.system() == 'Linux':
    try:
        import cups
    except:
        pass
elif platform.system() == 'Windows':
    try:
        from win32print import GetDefaultPrinter
        from win32api import ShellExecute
    except:
        pass
from pickle import dump, load
from time import sleep
import webbrowser
from threading import Thread
from idlelib.colorizer import ColorDelegator, make_pat
from idlelib.percolator import Percolator
import re

app_name = "SafGin Text"
class SafGinText:
    def start(self):
        window = tk.Tk()
        base = TextEditorBase(window)
        base.texteditorbase()
        window.mainloop()

    # def _nw(self):
    #     win = Tk()
    #     base = TextEditorBase(win)
    #     base.texteditorbase(False)
    #     win.mainloop()

# Base Class
class TextEditorBase(SafGinText):
    def __init__(self,window):
        self.window = window
        self.__syntaxhighlight = False

    def texteditorbase(self):
        img = Image.open('media_file/sgtexteditor_iconphoto.png')
        img = img.resize((18, 18), Image.ANTIALIAS)
        self.img = ImageTk.PhotoImage(img)
        self.__startup_loader()
        self.__window_geometry()
        self.window.iconphoto(True,self.img)
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # string vars
        self.font_style = tk.StringVar()
        self.font_style.set(self.style)
        self.font_size = tk.StringVar()
        self.font_size.set(self.size)
        self.tripemp = tk.StringVar()  # triple emphasis
        self.tripemp.set("None")
        self.statusL_text = tk.StringVar()
        self.statusL_text.set(f"{self.path}")

        # Text Frame
        self.bodyframe = tk.Frame(self.window)
        self.text = tk.Text(self.bodyframe, font=(self.style, self.size))
        self.__startupopen()
        self.scrollbary = tk.Scrollbar(self.bodyframe, command=self.text.yview)
        # self.scrollbarx = tk.Scrollbar(self.bodyframe, command=self.text.xview, orient="horizontal")
        #self.scrollbarx.pack(side="bottom", fill="x")
        self.scrollbary.pack(side="right", fill="y")
        self.text.pack(expand=True, fill="both")
        self.text.config(yscrollcommand=self.scrollbary.set, undo=True,wrap="word",tabs=40) # xscrollcommand=self.scrollbarx.set
        self.bodyframe.grid(row=0,column=0,sticky="n"+"w"+"e"+"s")
        # bottom frame
        self.bottomframe = tk.Frame(self.window)
        self.status_label = tk.Label(self.bottomframe, textvariable=self.statusL_text)


        # creating main menu bar and menus
        self.menubar = tk.Menu(self.window, background="blue",fg="white")
        self.window.config(menu=self.menubar)
        self.window.config(menu=self.menubar)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.editmenu = tk.Menu(self.menubar, tearoff=0)
        self.thememenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu = tk.Menu(self.menubar, tearoff=0)

        # configs
        self.bottomframe.grid(row=1,column=0,sticky="n"+"w"+"e"+"s")
        self.status_label.pack(anchor="w",side="left")


        # File Menu
        self.menubar.add_cascade(label='File', menu=self.filemenu)
        self.filemenu.add_command(label="New", command=self.__new, accelerator="Ctrl+N")
        # self.filemenu.add_command(label="New Window", command=self._nw)
        self.filemenu.add_command(label='Open...', command=self.__fopen, accelerator="Ctrl+O")
        self.filemenu.add_command(label='Save', command=self.__fsave, accelerator="Ctrl+S")
        self.filemenu.add_command(label='Save As...', command=self.__fsave_as, accelerator="Ctrl+Shift+S")
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Editor Settings", command=self.__es_window)
        self.filemenu.add_separator()
        self.filemenu.add_command(label='Print 🖶', command=self.__print_file, accelerator="Ctrl+P")
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.__on_closing, accelerator="Ctrl+Q")

        # Edit Menu
        self.menubar.add_cascade(label="Edit", menu=self.editmenu)
        self.editmenu.add_command(label="↶ Undo", command=self.__undo, accelerator="Ctrl+Z")
        self.editmenu.add_command(label="↷ Redo", command=self.__redo, accelerator="Ctrl+Y")
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Cut", command=self.__cut, accelerator="Ctrl+X")
        self.editmenu.add_command(label="Copy", command=self.__copy, accelerator="Ctrl+C")
        self.editmenu.add_command(label="Paste", command=self.__paste, accelerator="Ctrl+V")
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Select All", command=self.__selectall, accelerator="Ctrl+A")
        self.editmenu.add_command(label="Delete All", command=self.__delete_all, accelerator="Shift+Del")

        # Theme Menu
        self.menubar.add_cascade(label="Themes", menu=self.thememenu)
        self.thememenu.add_command(label="Light", command=lambda: self.__set_theme(0))
        self.thememenu.add_command(label="Dark", command=lambda: self.__set_theme(1))
        self.thememenu.add_command(label="Terminal", command=lambda: self.__set_theme(2))

        # Help Menu
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        self.helpmenu.add_command(label=f"About {app_name}", command=lambda: self.__about())
        self.helpmenu.add_command(label="Version Info",
                                  command=self.__version_info)
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label="Repository",
                                  command=lambda: webbrowser.open("https://github.com/SatzGOD/safgin-text"))
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label="Report a problem ⚠",
                                  command=lambda: webbrowser.open("https://github.com/SatzGOD/safgin-text/issues/new"))

        self.__window_keybinds()

        # To update the state of text in text box(if it saved or not)
        Thread(target=self.__textfileactivity, daemon=True).start()

        # to set theme on startup
        self.__themeSwitcher()
        self.window.update()  # to update idle tasks if any...

        # custom quit protocol
        self.window.protocol("WM_DELETE_WINDOW", self.__on_closing)

    # Helper Functions ................................................................................................
    def __startup_loader(self):
        self.window_cords = {'w': None, 'h': None, 'x': None, 'y': None}
        try:
            with open('data', 'rb') as f:
                loadeddata = load(f)
                self.path = loadeddata['path']
                self.theme = loadeddata['theme']
                self.style = loadeddata['fontstyle']
                self.size = loadeddata['fontsize']
                self.window_cords['w'] = loadeddata['w']
                self.window_cords['h'] = loadeddata['h']
                self.window_cords['x'] = loadeddata['x']
                self.window_cords['y'] = loadeddata['y']
        except:
            # File Path
            self.path = ""
            # for themes
            self.theme = 0
            self.size = "15"
            self.style = "Consolas"

    def __dumpjson_and_destroy(self):
        data = {'x': self.window.winfo_x(), 'y': self.window.winfo_y(), 'w': self.window.winfo_width(),
                'h': self.window.winfo_height(),
                'path': self.path, 'theme': self.theme, 'fontstyle': self.font_style.get(),
                'fontsize': self.font_size.get()}
        with open('data', 'wb') as f:
            dump(data, f)

        self.window.destroy()


    def __syntax_highlighter(self):
        if self.path == "" or splitext(self.path)[-1] == '.txt':
            try:
                self.prec.close()
                self.__syntaxhighlight = False
            except:
                pass
        else:
            if not self.__syntaxhighlight:
                self.cdg = ColorDelegator()
                self.cdg.prog = re.compile(r'\b(?P<MYGROUP>tkinter)\b|' + make_pat(), re.S)
                self.cdg.idprog = re.compile(r'\s+(\w+)', re.S)
                self.cdg.tagdefs['MYGROUP'] = {'foreground': ''}
                self.cdg.tagdefs['COMMENT'] = {'foreground': 'grey'}
                self.cdg.tagdefs['KEYWORD'] = {'foreground': '#FD9622'}
                self.cdg.tagdefs['BUILTIN'] = {'foreground': '#A47EEA'}
                self.cdg.tagdefs['STRING'] = {'foreground': '#8DD12A'}
                self.cdg.tagdefs['DEFINITION'] = {'foreground': '#51CBEE'}
                self.prec = Percolator(self.text)
                self.prec.insertfilter(self.cdg)
                self.__syntaxhighlight = True
            else:
                pass

    def __on_closing(self):
        if exists(self.path):
            with open(self.path, 'r') as f:
                if f.read() != self.text.get(1.0, "end"):
                    ask = messagebox.askyesnocancel(title="Quit",
                                                    message=f"Do you want to save changes to this \n{self.path} File?")
                    if ask == True:
                        self.__fsave()
                        self.__dumpjson_and_destroy()
                    elif ask == False:
                        self.__dumpjson_and_destroy()
                    else:
                        pass
                else:
                    self.__dumpjson_and_destroy()
        elif self.text.get(1.0, "end") > " ":
            ask = messagebox.askyesnocancel(title="Quit",
                                            message=f"Do you want to save changes to this Untitled File?")
            if ask == True:
                self.__fsave()
                try:
                    with open(self.path, 'r') as f:
                        if f.read() == self.text.get(1.0, "end")[:-1]:
                            self.__dumpjson_and_destroy()
                except:
                    pass
            elif ask == False:
                self.__dumpjson_and_destroy()
            else:
                pass
        else:
            self.__dumpjson_and_destroy()

    # text file activity detector
    def __textfileactivity(self):
        while True:
            if exists(self.path):
                with open(self.path, 'rt') as f:
                    if f.read() == self.text.get(1.0, "end"):
                        self.window.title(f"{(split(self.path)[1])} - {app_name}")
                    else:
                        self.window.title(f"*{(split(self.path)[1])} - {app_name}")
                        self.statusL_text.set(f"{self.path}")
            else:
                if self.text.get(1.0, "end") > "   ":
                    self.window.title(f"*Untitled - {app_name}")
                else:
                    self.window.title(f"Untitled - {app_name}")
            sleep(0.1)  # for smooth experience


    # window geometry setter
    def __window_geometry(self):
        window_width = self.window_cords['w'] if self.window_cords['w'] != None else 720
        window_height = self.window_cords['h'] if self.window_cords['h'] != None else 480
        x = self.window_cords['x'] if self.window_cords['w'] != None else int(
            (self.window.winfo_screenwidth() / 2) - (window_width / 2))
        y = self.window_cords['y'] if self.window_cords['w'] != None else int(
            (self.window.winfo_screenheight() / 2) - (window_height / 2))
        self.window.geometry("{}x{}+{}+{}".format(window_width, window_height, x, y))

    def __window_keybinds(self):
        # key binds
        # To Zoom in and Zoom out the text
        self.window.bind("<Control-plus>",
                         lambda _: self.__font_changer(self.font_size.set(str(int(self.font_size.get()) + 5))) if (
                                 int(self.font_size.get()) < 120) else self.font_size.set(120))  # ctr + plus
        self.window.bind("<Control-minus>",
                         lambda _: self.__font_changer(self.font_size.set(str(int(self.font_size.get()) - 5))) if (
                                 int(self.font_size.get()) > 5) else self.font_size.set(5))  # ctr + minus

        self.window.bind("<Control-KP_Add>",
                         lambda _: self.__font_changer(self.font_size.set(str(int(self.font_size.get()) + 5))) if (
                                 int(self.font_size.get()) < 120) else self.font_size.set(120))  # ctr + plus
        self.window.bind("<Control-KP_Subtract>",
                         lambda _: self.__font_changer(self.font_size.set(str(int(self.font_size.get()) - 5))) if (
                                 int(self.font_size.get()) > 5) else self.font_size.set(5))  # ctr + minus
        # To Save
        self.window.bind("<Control-S>", lambda _: self.__fsave())  # ctr + S
        self.window.bind("<Control-s>", lambda _: self.__fsave())  # ctr + s
        # To Save as
        self.window.bind("<Control-Shift-S>", lambda _: self.__fsave_as())  # ctr + shift + S
        self.window.bind("<Control-Shift-s>", lambda _: self.__fsave_as())  # ctr + shift + s
        # To Open
        self.window.bind("<Control-O>", lambda _: self.__fopen())  # ctr + O
        self.window.bind("<Control-o>", lambda _: self.__fopen())  # ctr + o
        # To New
        self.window.bind("<Control-N>", lambda _: self.__new())  # ctr + N
        self.window.bind("<Control-n>", lambda _: self.__new())  # ctr + n
        # To Delete All
        self.window.bind("<Shift-Delete>", lambda _: self.__delete_all())  # shift + del
        # To Print
        self.window.bind("<Control-P>", lambda _: self.__print_file())  # ctr + P
        self.window.bind("<Control-p>", lambda _: self.__print_file())  # ctr + p

        # to quit
        self.window.bind("<Control-Q>", lambda _: self.__on_closing())
        self.window.bind("<Control-q>", lambda _: self.__on_closing())

        self.bottomframe.bind("<ButtonPress-1>",lambda _: self.window.attributes("-alpha", 0.4))
        self.bottomframe.bind("<ButtonRelease-1>", lambda _: self.window.attributes("-alpha", 1.0))

        self.__fullscreen = False
        def fullscreen(_):
            if not self.__fullscreen:
                self.window.attributes('-fullscreen', True)
                self.__fullscreen = True
            else:
                self.window.attributes('-fullscreen', False)
                self.__fullscreen = False
        self.window.bind("<F11>", fullscreen)

    def __new(self):
        self.text.config(undo=False)
        self.window.title(f"Untitled - {app_name}")
        self.__delete_all()
        self.path = ""
        self.text.config(undo=True)
        self.statusL_text.set("")
        self.__syntax_highlighter()

    def __fopen(self):
        self.text.config(undo=False)
        opath = filedialog.askopenfilename(title='Open File', filetypes=(
            ("text file", "*.txt"), ("all files", "*.*"), ("Python File", "*.py"), ("HTML File", "*.html")))

        if exists(opath):
            with open(opath, 'r', encoding="utf8",errors="ignore") as f:
                self.__delete_all()
                self.text.insert(1.0, f.read()[:-1])
            self.window.title(f"{(split(opath)[1])} - {app_name}")
            self.path = opath
            self.statusL_text.set(opath)
            self.text.config(undo=True)
            self.__syntax_highlighter()
        else:
            pass

    def __startupopen(self):
        if exists(self.path):
            with open(self.path, 'rt', encoding="utf8") as f:
                self.__delete_all()
                self.text.insert(1.0, f.read()[:-1])
            self.window.title(f"{(split(self.path)[1])} - {app_name}")
            self.__syntax_highlighter()
        else:
            self.window.title("Untitled - TextEditor")
            self.__syntax_highlighter()

        # to save as a new file or save within an existing file

    def __fsave_as(self):
        spath = filedialog.asksaveasfile(title="Save as File",defaultextension=".txt",
                                         filetypes=(
                                             ("text File", "*.txt"), ("HTML File", "*.html"),
                                             ("Python File", "*.py"),
                                             ("all File", "*.*")))

        if spath != None and exists(spath.name):
            filetext = self.text.get(1.0, "end")
            spath.write(filetext)
            spath.close()
            self.window.title(f"{(split(spath.name)[1])} - {app_name}")
            self.path = spath.name
            self.statusL_text.set(f"{self.path} (Saved)")
            self.__syntax_highlighter()
        else:
            pass

    def __fsave(self):
        if exists(self.path):
            with open(self.path, 'w') as f:
                filetext = self.text.get(1.0, "end")
                f.write(filetext)
                self.window.title(f"{(split(self.path)[1])} - {app_name}")
                self.statusL_text.set(f"{self.path} (Saved)")
        else:
            self.__fsave_as()

    def __print_file(self):
        if platform.system() == 'Windows':
            printer = GetDefaultPrinter()
            if printer:
                self.statusL_text.set(printer)
                ask = messagebox.askokcancel(title="Print", message=f"Click ok to print this file \n{self.path} ")
                if ask and exists(self.path):
                    ShellExecute(0, "print", self.path, None, ".", 0)
            else:
                self.statusL_text.set("No Printer Available")
                messagebox.showwarning(title=f"{app_name}", message="Cannot Detect a printer:"
                                                                    "\nBe sure that your printer is connected properly and use "
                                                                    "Control Panel to verify that the printer is configured properly.")
            self.statusL_text.set(f"{self.path}")

        elif platform.system() == 'Linux':
            try:
                conn = cups.Connection()
                printer = conn.getPrinters()
                printer = printer.keys()[0]
                if printer:
                    self.statusL_text.set(printer)
                    ask = messagebox.askokcancel(title="Print", message=f"Click ok to print this file \n{self.path} ")
                    if ask and exists(self.path):
                            conn.printFile(printer, self.path, "print", options={'media': '216x280mm'})
            except:
                messagebox.showerror(title="Print Error",message="failed to connect to server, Please make sure your device is connected to the printer!")


    def __cut(self):
        self.text.event_generate("<<Cut>>")

        # copy the selected text

    def __copy(self):
        self.text.event_generate("<<Copy>>")

        # paste the text from the clipboard

    def __paste(self):
        self.text.event_generate("<<Paste>>")

        # select all the text from the text box

    def __selectall(self):
        self.text.tag_add('sel', 1.0, "end")

        # delete all text from the text box

    def __delete_all(self):
        self.text.delete(1.0, "end")

    def __undo(self):
        try:
            self.text.edit_undo()
        except:
            pass

    def __redo(self):
        try:
            self.text.edit_redo()
        except:
            pass

    def __color_fchanger(self):
        fcolor = colorchooser.askcolor(title="Choose a color for font")[1]
        self.fcolorbutton.config(bg=fcolor)
        self.text.config(fg=fcolor)

    def __color_bchanger(self):
        bcolor = colorchooser.askcolor(title="Choose a color for paper")[1]
        self.bcolorbutton.config(bg=bcolor)
        self.text.config(bg=bcolor)

    def __font_changer(self, *args):
        self.text.config(font=(self.font_style.get(), self.font_size.get()))

    def __tripemp_func(self, *args):

        def __helper(style):
            if style in current_tag:
                self.text.tag_remove(style, "sel.first", "sel.last")
                self.tripemp.set("None")
            else:
                self.text.tag_add(style, "sel.first", "sel.last")

        try:
            if self.tripemp.get() == self.tripemp_list[0]:
                self.__selectall()
                bold_font = font.Font(self.text, self.text.cget("font"))
                bold_font.configure(weight="bold")
                self.text.tag_configure("bold", font=bold_font)
                current_tag = self.text.tag_names("sel.first")
                __helper("bold")
            elif self.tripemp.get() == self.tripemp_list[1]:
                self.__selectall()
                italic_font = font.Font(self.text, self.text.cget("font"))
                italic_font.configure(slant="italic")
                self.text.tag_configure("italic", font=italic_font)
                current_tag = self.text.tag_names("sel.first")
                __helper("italic")
            elif self.tripemp.get() == self.tripemp_list[2]:
                self.__selectall()
                underline_font = font.Font(self.text, self.text.cget("font"))
                underline_font.configure(underline=True)
                self.text.tag_configure("underline", font=underline_font)
                current_tag = self.text.tag_names("sel.first")
                __helper("underline")

            else:
                self.tripemp.set("None")
        except:
            self.tripemp.set("None")

    def __about(self):
        messagebox.showinfo(f"About {app_name}",
                            "A python text editor application by Satz!\nSource Code at SatzGOD github or Click `Repository` in the Help Menu.\n"
                            "\ninstagram: @satz_._")
    def __version_info(self):
        messagebox.showinfo(title="Version Info", message=f"\nAbout This Version:-"
                                                     f"\n{app_name} v2.3.6 "
                                                     f"\nWhat's New?\n"
                                                     f"Click StatusBar to Transparent background and Added new F11 to full screen feature."
                                                     f"\nMinor Changes:\n"
                                                     f"Upgraded Editor Settings Window and Fixed Some bugs and glitches."
                            )

    def __es_window(self):
        self.tripemp_list = ["Bold", "Italics", "Underline"]
        self.filemenu.entryconfig(5, state="disabled")
        self.fw = tk.Toplevel()
        self.fw.overrideredirect(1)
        self.fw.attributes("-alpha", 0.75)
        self.fw.grid_rowconfigure(0,weight=1)
        self.fw.grid_columnconfigure(0, weight=1)
        self.eswtitle = Titlebar(self.fw,self.img,maximize=False,minimze=False,onhold=False,closef=self.__fwonclosing)
        self.eswtitle.grid(row=0,column=0,sticky="we")
        self.eswtitle.set_title("Editor Settings")
        self.fw.attributes('-topmost', True)
        self.fw.resizable(False, False)
        self.fw.title("Editor Settings")
        width, height = 300, 160
        x = int((self.window.winfo_screenwidth() / 2) - (width / 2))
        y = int((self.window.winfo_screenheight() / 2) - (height / 2))
        self.fw.geometry(f"{width}x{height}-{x}+{y}")
        self.frame = tk.Frame(self.fw)
        self.l1 = tk.Label(self.frame, text="Font Family:")
        self.l1.grid(row=0, column=0, sticky="w", pady=3)
        self.stylebox = tk.OptionMenu(self.frame, self.font_style, *font.families(), command=self.__font_changer)
        self.stylebox.grid(row=0, column=1, sticky="e", pady=3)
        self.l2 = tk.Label(self.frame, text="Font Style:")
        self.l2.grid(row=1, column=0, sticky="w", pady=3)
        self.tripempbox = tk.OptionMenu(self.frame, self.tripemp, *self.tripemp_list, command=self.__tripemp_func)
        self.tripempbox.grid(row=1, column=1, sticky="w", pady=3)
        self.l3 = tk.Label(self.frame, text="Font Size:")
        self.l3.grid(row=2, column=0, sticky="w", pady=3)
        self.sizebox = tk.Spinbox(self.frame, from_=1, to_=120, textvariable=self.font_size, width=4,
                               command=self.__font_changer)
        self.sizebox.grid(row=2, column=1, sticky="w", pady=3)
        self.fcolorbutton = tk.Button(self.frame, text="Font color", command=self.__color_fchanger)
        self.fcolorbutton.grid(row=3, column=0, sticky="w", pady=3, padx=2)
        self.bcolorbutton = tk.Button(self.frame, text="Paper color", command=self.__color_bchanger)
        self.bcolorbutton.grid(row=3, column=1, sticky="w", pady=3)
        self.frame.grid(row=1, column=0)

        self.__ts_esw()
        self.fw.mainloop()

    def __fwonclosing(self):
        self.filemenu.entryconfig(5, state="normal")
        self.fw.destroy()

    def __set_theme(self, newstate):
        self.theme = newstate
        self.__themeSwitcher()
        try:
            self.__ts_esw()
        except:
            pass

    def __themeSwitcher(self):
        if self.theme == 0:
            white = "#FCFDFD"
            defsyswhite = "#C7CCD1"
            black = "#000001"
            relief = "flat"
            highlightgrey = "#D9DDE0"
            font, size = "Consolas", "10"
            self.window.config(bg=defsyswhite)
            self.bottomframe.config(bg=defsyswhite)
            self.text.config(fg=black, bg=white, insertbackground=black)

            self.status_label.config(fg=black, bg=defsyswhite)
            self.menubar.config(bg=defsyswhite, fg=black, relief=relief, activebackground=highlightgrey,
                                selectcolor=highlightgrey, font=(font, size),
                                   activeforeground=black)
            self.filemenu.config(bg=defsyswhite, fg=black, relief=relief, activebackground=highlightgrey,
                                 selectcolor=highlightgrey, font=(font, size),
                                   activeforeground=black)
            self.editmenu.config(bg=defsyswhite, fg=black, relief=relief, activebackground=highlightgrey,
                                 selectcolor=highlightgrey, font=(font, size),
                                   activeforeground=black)
            self.thememenu.config(bg=defsyswhite, fg=black, relief=relief, activebackground=highlightgrey,
                                  selectcolor=highlightgrey, font=(font, size),
                                   activeforeground=black)
            self.helpmenu.config(bg=defsyswhite, fg=black, relief=relief, activebackground=highlightgrey,
                                 selectcolor=highlightgrey, font=(font, size),
                                   activeforeground=black)


        elif self.theme == 1:
            white = "white"
            textwhite = '#ebebeb'
            sysdark = "#2E3238"
            darkgrey = "#2B2B2B"
            textbg = "#282923"
            lightgrey = "#414141"
            relief = "flat"
            font, size = "Consolas", "10"
            self.window.config(bg=sysdark)
            self.bottomframe.config(bg=sysdark)
            self.text.config(fg=textwhite, bg=textbg, insertbackground=white)
            self.status_label.config(bg=sysdark, fg=white)
            self.menubar.config(bg=darkgrey, fg=white, relief=relief, activebackground=lightgrey,activeforeground=white,
                                selectcolor=lightgrey, font=(font, size))
            self.filemenu.config(bg=darkgrey, fg=white, relief=relief, activebackground=lightgrey,activeforeground=white,
                                 selectcolor=lightgrey, font=(font, size))
            self.editmenu.config(bg=darkgrey, fg=white, relief=relief, activebackground=lightgrey,activeforeground=white,
                                 selectcolor=lightgrey, font=(font, size))
            self.thememenu.config(bg=darkgrey, fg=white, relief=relief, activebackground=lightgrey,activeforeground=white,
                                  selectcolor=lightgrey, font=(font, size))
            self.helpmenu.config(bg=darkgrey, fg=white, relief=relief, activebackground=lightgrey,activeforeground=white,
                                 selectcolor=lightgrey, font=(font, size))
        elif self.theme == 2:
            white = "#FFFFFF"
            yelow = "#BDBE00"
            black = "#000000"
            green = "#00BF00"
            relief = "flat"
            font, size = "Consolas", "10"
            self.window.config(bg=black)
            self.bottomframe.config(bg=black)
            self.text.config(fg=white, bg=black, insertbackground=white)
            self.status_label.config(bg=black, fg=yelow)
            self.menubar.config(bg=black, fg=white, relief=relief, activebackground=green,activeforeground=white,
                                selectcolor=green, font=(font, size))
            self.filemenu.config(bg=black, fg=white, relief=relief, activebackground=green,activeforeground=white,
                                 selectcolor=green, font=(font, size))
            self.editmenu.config(bg=black, fg=white, relief=relief, activebackground=green,activeforeground=white,
                                 selectcolor=green, font=(font, size))
            self.thememenu.config(bg=black, fg=white, relief=relief, activebackground=green,activeforeground=white,
                                  selectcolor=green, font=(font, size))
            self.helpmenu.config(bg=black, fg=white, relief=relief, activebackground=green,activeforeground=white,
                                 selectcolor=green, font=(font, size))

    def __ts_esw(self):
        if self.theme == 0:
            defsyswhite = "#C7CCD1"
            black = "#000001"
            relief = "groove"
            highlightgrey = "#D9DDE0"
            self.stylebox.config(fg=black, bg=defsyswhite, activebackground=highlightgrey, activeforeground=black,
                                 relief=relief, highlightthickness=False)
            self.sizebox.config(fg=black, bg=defsyswhite, relief=relief, highlightthickness=3,
                                highlightbackground=defsyswhite)
            self.fcolorbutton.config(fg=black, bg=defsyswhite, activebackground=highlightgrey, activeforeground=black,
                                     relief=relief)
            self.bcolorbutton.config(fg=black, bg=defsyswhite, activebackground=highlightgrey, activeforeground=black,
                                     relief=relief)
            self.tripempbox.config(fg=black, bg=defsyswhite, activebackground=highlightgrey, activeforeground=black,
                                   relief=relief, highlightthickness=False)
            self.fw.config(bg=defsyswhite)
            self.frame.config(bg=defsyswhite)
            self.l1.config(bg=defsyswhite, fg=black)
            self.l2.config(bg=defsyswhite, fg=black)
            self.l3.config(bg=defsyswhite, fg=black)
            self.eswtitle.config(bg=defsyswhite,fg=black,abg=highlightgrey,afg=black)
        elif self.theme == 1:
            white = "white"
            darkgrey = "#2B2B2B"
            lightdarkgrey = "#2E3238"
            lightgrey = "#414141"
            relief = "groove"
            self.stylebox.config(bg=lightdarkgrey, fg=white, activebackground=lightgrey, activeforeground=white,
                                 relief=relief, highlightthickness=False)
            self.sizebox.config(bg=lightdarkgrey, fg=white, relief=relief, highlightthickness=3,
                                highlightbackground=lightdarkgrey)
            self.fcolorbutton.config(bg=lightdarkgrey, fg=white, activebackground=lightgrey, activeforeground=white,
                                     relief=relief)
            self.bcolorbutton.config(bg=lightdarkgrey, fg=white, activebackground=lightgrey, activeforeground=white,
                                     relief=relief)
            self.tripempbox.config(bg=lightdarkgrey, fg=white, activebackground=lightgrey, activeforeground=white,
                                   relief=relief, highlightthickness=False)
            self.fw.config(bg=darkgrey)
            self.frame.config(bg=darkgrey)
            self.l1.config(bg=darkgrey, fg=white)
            self.l2.config(bg=darkgrey, fg=white)
            self.l3.config(bg=darkgrey, fg=white)
            self.eswtitle.config(bg=darkgrey, fg=white, abg=lightgrey, afg=white)

        elif self.theme == 2:
            white = "#FFFFFF"
            black = "#000000"
            green = "#00BF00"
            relief = "groove"
            self.stylebox.config(bg=black, fg=white, activebackground=green, activeforeground=white,
                                 relief=relief, highlightthickness=False)
            self.sizebox.config(bg=black, fg=white, relief=relief, highlightthickness=3,
                                highlightbackground=black)
            self.fcolorbutton.config(bg=black, fg=white, activebackground=green, activeforeground=white,
                                     relief=relief)
            self.bcolorbutton.config(bg=black, fg=white, activebackground=green, activeforeground=white,
                                     relief=relief)
            self.tripempbox.config(bg=black, fg=white, activebackground=green, activeforeground=white,
                                   relief=relief, highlightthickness=False)
            self.fw.config(bg=black)
            self.frame.config(bg=black)
            self.l1.config(bg=black, fg=white)
            self.l2.config(bg=black, fg=white)
            self.l3.config(bg=black, fg=white)
            self.eswtitle.config(bg=black, fg=white, abg=green, afg=white)


# Custom Title Bar
class Titlebar:
    def __init__(self,master,icon,*,maximize=True,minimze=True,onhold=True,closef=None):
        self.master = master
        self.max = maximize
        self.mini = minimze
        self.onhold = onhold
        self.closef = closef
        self.__ovri = False
        self.title_bar = tk.Frame(master,bd=0,relief="flat")
        # self.title_bar.grid(row=0, column=0, sticky="nsew")
        self.title_bar.bind("<ButtonPress-1>", self.__start_move)
        self.title_bar.bind("<ButtonRelease-1>", self.__stop_move)
        self.title_bar.bind("<B1-Motion>",self.__move_window)
        self.title_bar.bind("<Map>",self.__screen_appear)
        self.master.bind("<Button-2>",self.__show_overrides)

        self.appicon = tk.Label(self.title_bar,image=icon)
        self.appicon.pack(side="left",anchor="w")

        self.close = tk.Button(self.title_bar, text="✕", relief="flat", height=1, width=4, font="consolas", bd=1,
                               command=self.closef if self.closef != None else self.master.destroy)
        self.close.pack(anchor="e", side="right")

        if self.max:
            self.maxd = tk.Button(self.title_bar, text="🗖", relief="flat", height=1, width=4, font="consolas", bd=1,
                                  command=self.__maxd, activebackground="grey")
            self.maxd.pack(anchor="e", side="right")
            self.__maxdstate = None

        if self.mini:
            self.min = tk.Button(self.title_bar, text="―", relief="flat", height=1, width=4, font="consolas",
                                 comman=self.__min, bd=1, activebackground="grey")
            self.min.pack(anchor="e", side="right")

        self.title_label = tk.Label(self.title_bar,text=app_name)
        self.title_label.pack(side="left",anchor="w")


    def set_title(self,text):
        self.title_label.config(text=text)

    def grid(self,*args,**kwargs):
        self.title_bar.grid(*args,**kwargs)

    def pack(self,*args,**kwargs):
        self.title_bar.pack(*args,**kwargs)

    def place(self, *args, **kwargs):
        self.title_bar.place(*args,**kwargs)

    def __start_move(self, event):
        self.x = event.x
        self.y = event.y
        if self.onhold:
            self.master.attributes("-alpha", 0.75)

    def __stop_move(self, event):
        self.x = None
        self.y = None
        if self.onhold:
            self.master.attributes("-alpha", 1.0)

    def __show_overrides(self,_):
        if not self.__ovri:
            self.master.overrideredirect(0)
            self.master.deiconify()
            self.title_bar.grid_forget()
            self.__ovri = True
        else:
            self.master.overrideredirect(1)
            self.title_bar.grid(row=0,column=0,sticky="nsew")
            self.__ovri = False


    def __move_window(self,event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.master.winfo_x() + deltax
        y = self.master.winfo_y() + deltay
        self.master.geometry(f"+{x}+{y}")


    def __maxd(self):
        if self.__maxdstate == None or not self.__maxdstate:
            self.px, self.py = self.master.winfo_x(), self.master.winfo_y()
            self.pw, self.ph = self.master.winfo_width(),self.master.winfo_height()
            w, h = self.master.winfo_screenwidth(), self.master.winfo_screenheight()
            self.master.geometry("%dx%d+0+0" % (w,h))
            self.maxd.config(text="🗗")
            self.__maxdstate = True
        else:
            self.master.geometry(f"{self.pw}x{self.ph}+{self.px}+{self.py}")
            self.maxd.config(text="🗖")
            self.__maxdstate = False

    def __min(self):
        self.master.overrideredirect(0)
        self.master.iconify()

    def __screen_appear(self,_):
        # self.master.overrideredirect(1)
        pass

    def config(self,bg,fg,abg,afg):
        self.title_bar.config(bg=bg)
        self.appicon.config(bg=bg, fg=fg, activebackground=abg, activeforeground=afg)
        self.close.config(bg=bg, fg=fg, activebackground="red", activeforeground="white")
        self.title_label.config(bg=bg, fg=fg, activebackground=abg, activeforeground=afg)
        self.close.bind("<Enter>", lambda _: self.close.config(bg="red", fg="white"))
        self.close.bind("<Leave>", lambda _: self.close.config(bg=bg, fg=fg))
        if self.max:
            self.maxd.config(bg=bg, fg=fg, activebackground=abg, activeforeground=afg)
            self.min.config(bg=bg, fg=fg, activebackground=abg, activeforeground=afg)
            self.maxd.bind("<Enter>", lambda _: self.maxd.config(bg="grey"))
            self.maxd.bind("<Leave>", lambda _: self.maxd.config(bg=bg))
        if self.mini:
            self.min.bind("<Enter>", lambda _: self.min.config(bg="grey"))
            self.min.bind("<Leave>", lambda _: self.min.config(bg=bg))
