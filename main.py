import customtkinter as ctk
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter import Menu
from tkinter.messagebox import showinfo, askyesno
from tkinter import simpledialog
import time, threading
import os, json, platform


# ██╗░░██╗██████╗░░█████╗░██████╗░
# ██║░██╔╝██╔══██╗██╔══██╗██╔══██╗
# █████═╝░██████╔╝███████║██║░░██║
# ██╔═██╗░██╔═══╝░██╔══██║██║░░██║
# ██║░╚██╗██║░░░░░██║░░██║██████╔╝
# ╚═╝░░╚═╝╚═╝░░░░░╚═╝░░╚═╝╚═════╝░
# Version 1.1.0      [SOURCE CODE]

if platform.system() == 'Darwin':
    config_dir = os.path.expanduser('~/Library/Application Support/kPad')
elif platform.system() == 'Windows':
    config_dir = os.path.join(os.getenv('APPDATA'), 'kPad')
else:
    config_dir = os.path.expanduser('~/.config/kpad')
os.makedirs(config_dir, exist_ok=True)
CONFIG_PATH = os.path.join(config_dir, 'config.json')
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r') as f:
        CONFIGURATION = json.load(f)
else:
    CONFIGURATION = {
        'auto_save': {'enabled': True, 'time_until_next_save': 5},
        'undo': {'enabled': True, 'max_undo': 20, 'separate_edits_from_undos': True},
        'word_wrap': True,
        'font': 'Menlo',
        'font_size': 14,
        'window_geometry': [500, 400],
        'recent_files': {'enabled': True, 'keep_recent_files_count': 5, 'recent_file_paths': []}
}

_fonts = ['Menlo', 'Monaco', 'Helvetica', 'Arial', 'Times New Roman', 'Georgia', 'Avenir', 'Baskerville', 'Futura', 'Verdana', 'Gill Sans', 'Courier', 'Optima', 'American Typewriter']

class App(ctk.CTk):
    def __init__(self, title, geometry):
        super().__init__()

        self.path = None
        self.font_size = 14

        def write_to_recent_files():
            if CONFIGURATION['recent_files']['enabled']:
                if len(CONFIGURATION['recent_files']['recent_file_paths']) >= CONFIGURATION['recent_files']['keep_recent_files_count']:
                    del CONFIGURATION['recent_files']['recent_file_paths'][0]
                    CONFIGURATION['recent_files']['recent_file_paths'].append(self.path)
                else:
                    CONFIGURATION['recent_files']['recent_file_paths'].append(self.path)


        def newfile(event=None):
            if not '*' in self.title()[7]:
                self.title('kPad - Untitled')
                self.path = None
                self.textbox.delete('1.0', 'end')
            else:
                ask = askyesno('File unsaved!', 'Do you want to save your file before making a new one?')
                if ask:
                    save_file()
                else:
                    self.title('kPad - Untitled')
                    self.path = None
                    self.textbox.delete('1.0', 'end')
                    

        def save_as(event=None):
            self.path = asksaveasfilename(filetypes=[('Text files', '.txt'), ('Other', '.*.*')], defaultextension='.txt')
            with open(self.path, 'w') as file:
                file.write(self.textbox.get('1.0'))
            self.title(f'kPad - {self.path}')

        def save_file(event=None):
            if not self.path:
                save_as()
            with open(self.path, 'w', encoding='utf-8') as f:
                f.write(self.textbox.get('1.0', 'end-1c'))
            self.title(f'kPad - {self.path}')

        
        def open_from_file(event=None, path=None):
            if not path:
                self.path = askopenfilename(filetypes=[('Text files', '.txt'), ('kPad notefile', '.kpad')], defaultextension='.txt')
            if self.path:
                self.textbox.delete('1.0', 'end')
                with open(self.path, 'r') as file:
                    self.textbox.insert('1.0', file.read())
                write_to_recent_files()
                print(CONFIGURATION['recent_files']['recent_file_paths'])
            else:
                pass

        def set_font(font):
            self.font.configure(family=font)
            self.textbox.configure(font=self.font)

        def autosave():
            while True:
                if CONFIGURATION['auto_save']['enabled']:
                    if self.path and 'Untitled' not in self.title():
                        save_file()
                time.sleep(CONFIGURATION['auto_save']['time_until_next_save'])
            
        threading.Thread(target=autosave, daemon=True).start()

        def toggle_theme(event=None):
            mode = ctk.get_appearance_mode()
            ctk.set_appearance_mode('Light' if mode == 'Dark' else 'Dark')

        def go_to_start(event=None):
            self.textbox.yview_moveto(0)

        def go_to_end(event=None):
            self.textbox.yview_moveto(1)

        def increment_font_size(event=None):
            self.font_size += 2
            self.font = ctk.CTkFont(family=self.font._family, size=self.font_size)
            self.textbox.configure(font=self.font)
            return 'break'

        def decrement_font_size(event=None):
            self.font_size = max(2, self.font_size - 2)
            self.font = ctk.CTkFont(family=self.font._family, size=self.font_size)
            self.textbox.configure(font=self.font)
            return 'break'

        def go_to_line(event=None):
            line = simpledialog.askinteger('Go To Line', 'Enter line number:')
            if line is None:
                return
            total_lines = int(self.textbox.index('end-1c').split('.')[0])
            line = max(1, min(line, total_lines))
            line_text = self.textbox.get(f'{line}.0', f'{line}.end')
            max_col = len(line_text)
            self.textbox.mark_set('insert', f'{line}.0')
            self.textbox.see('insert')
            self.textbox.focus()
        
        word_wrap_var = ctk.BooleanVar(value=CONFIGURATION['word_wrap'])

        def toggle_word_wrap():
            if word_wrap_var.get():
                self.textbox.configure(wrap='word')
                CONFIGURATION['word_wrap'] = True
            else:
                self.textbox.configure(wrap='none')
                CONFIGURATION['word_wrap'] = False
        
        def save_config():
            CONFIGURATION['font'] = self.font._family
            CONFIGURATION['font_size'] = self.font_size
            CONFIGURATION['word_wrap'] = word_wrap_var.get()
            CONFIGURATION['window_geometry'] = [self.winfo_width(), self.winfo_height()]
            with open(CONFIG_PATH, 'w') as f:
                json.dump(CONFIGURATION, f, indent=4)

        menu = Menu(self)
        file_menu = Menu(menu, tearoff=0)
        file_menu.add_command(label='Open', command=open_from_file)
        file_menu.add_command(label='Save As...', command=save_as)
        file_menu.add_command(label='Save...', command=save_file)
        file_menu.add_separator()
        for index, path in CONFIGURATION['recent_files']['recent_files_paths']:
            file_menu.add_command(label=f'Open {path} ({index+1})...')
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.destroy)
        menu.add_cascade(label='File', menu=file_menu)
        font_menu = Menu(menu, tearoff=0)
        for _font in _fonts:
            font_menu.add_command(label=_font, command=lambda f=_font: set_font(f))
        menu.add_cascade(label='Change Font', menu=font_menu)
        view_menu = Menu(menu, tearoff=0)
        view_menu.add_command(label='Go to Start...', command=go_to_start)
        view_menu.add_command(label='Go to End...', command=go_to_end)
        view_menu.add_separator()
        view_menu.add_command(label='Go to Line...', command=go_to_line)
        view_menu.add_separator()
        view_menu.add_checkbutton(label='Word Wrap...', onvalue=True, variable=word_wrap_var, command=toggle_word_wrap)
        menu.add_cascade(label='View', menu=view_menu)

        self.configure(menu=menu)

        self.font = ctk.CTkFont(family=CONFIGURATION['font'], size=CONFIGURATION['font_size'])
        self.font_size = CONFIGURATION['font_size']

        def update_cursor_info(event=None):
            pos = self.textbox.index('insert')
            line, col = map(int, pos.split('.'))
            chars = len(self.textbox.get('1.0', 'end-1c'))
            self.stats_line_col.configure(text=f'Ln: {line}  Col: {col + 1}  Ch: {chars}')
            if self.path != None:
                self.title(f'kPad - *{self.path}')
            else:
                self.title('kPad - *Untitled')

        self.title(title)
        self.geometry(f'{geometry[0]}x{geometry[1]}')

        self.textbox = ctk.CTkTextbox(self, undo=CONFIGURATION['undo']['enabled'], autoseparators=CONFIGURATION['undo']['separate_edits_from_undos'], maxundo=CONFIGURATION['undo']['max_undo'])
        self.textbox.configure(font=self.font)
        if word_wrap_var.get():
            self.textbox.configure(wrap='word')
        else:
            self.textbox.configure(wrap='none')

        self.textbox.bind('<KeyRelease>', update_cursor_info)
        self.textbox.bind('<ButtonRelease>', update_cursor_info)

        # Cross-platform key bindings
        system = platform.system()
        if system == "Darwin":
            mod = "Command"
        else:
            mod = "Control"

        self.bind(f'<{mod}-l>', go_to_line)
        self.bind(f'<{mod}-s>', save_file)
        self.bind(f'<{mod}-o>', open_from_file)
        self.bind(f'<{mod}-t>', toggle_theme)
        self.bind(f'<{mod}-n>', newfile)
        self.bind(f'<{mod}-equal>', increment_font_size)
        self.bind(f'<{mod}-minus>', decrement_font_size)


        self.stats_text_frame = ctk.CTkFrame(self)
        self.stats_text_frame.pack(fill='x', side=ctk.BOTTOM)

        self.stats_line_col = ctk.CTkLabel(self.stats_text_frame, text='Ln: 1 Col: 1 Ch: 0')
        self.stats_line_col.pack(side=ctk.RIGHT)

        self.textbox.pack(fill='both', expand=True)
        self.protocol('WM_DELETE_WINDOW', lambda: [save_file(), save_config(), self.destroy()])


App('kPad - Untitled', CONFIGURATION['window_geometry']).mainloop()