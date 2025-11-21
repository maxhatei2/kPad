import customtkinter as ctk
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter import Menu
from tkinter.messagebox import showinfo, askyesno, askyesnocancel, showerror
from tkinter import simpledialog
import time, threading, shutil
import os, json, platform, tempfile, subprocess
import venv, sys, urllib.parse, urllib.request
from io import BytesIO
from zipfile import ZipFile
from tkinter import Listbox

VERSION = '1.4.0'
ONL_VER_URL = 'https://raw.githubusercontent.com/maxhatei2/kPad/refs/heads/main/.kv'
DOWNLOAD_URLS = {
    ('Darwin', 'arm64'): 'https://github.com/maxhatei2/kPad/releases/latest/kPad-mac_arm64.zip',
    ('Darwin', 'x86_64'): 'https://github.com/maxhatei2/kPad/releases/latest/kPad-mac_x86_64.zip',
    (('Windows', 'arm64'), ('Windows', 'x86_64')): 'https://github.com/maxhatei2/kPad/releases/latest/kPad-Windows_x86_64.exe.zip'
}



# ██╗░░██╗██████╗░░█████╗░██████╗░
# ██║░██╔╝██╔══██╗██╔══██╗██╔══██╗
# █████═╝░██████╔╝███████║██║░░██║
# ██╔═██╗░██╔═══╝░██╔══██║██║░░██║
# ██║░╚██╗██║░░░░░██║░░██║██████╔╝
# ╚═╝░░╚═╝╚═╝░░░░░╚═╝░░╚═╝╚═════╝░
# Version 1.4.0      [SOURCE CODE]


if platform.system() == 'Darwin':
    config_dir = os.path.expanduser('~/Library/Application Support/kPad')
    plugin_dir = os.path.expanduser(f'{config_dir}/plugins')
    plugin_env_path = os.path.expanduser("~/Library/Application Support/kPad/plugin-env")
elif platform.system() == 'Windows':
    config_dir = os.path.join(os.getenv('APPDATA'), 'kPad')
    plugin_dir = os.path.join(os.getenv('APPDATA'), 'kPad', 'Plugins')
    plugin_env_path = os.path.join(os.getenv('APPDATA', 'kPad', 'Plugins', 'plugin_env'))
else:
    config_dir = os.path.expanduser('~/.config/kpad')
    plugin_dir = os.path.expanduser(f'{config_dir}/plugins')
    plugin_env_path = os.path.expanduser("~/Library/Application Support/kPad/plugin-env")
os.makedirs(config_dir, exist_ok=True)
os.makedirs(plugin_dir, exist_ok=True)
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
        'recent_files': {'enabled': True, 'keep_recent_files_count': 5, 'recent_file_paths': []},
}
    
if not os.path.exists(plugin_env_path):
    venv.create(plugin_env_path, with_pip=True)
os.environ["KPAD_PLUGIN_ENV"] = plugin_env_path

_fonts = ['Menlo', 'Monaco', 'Helvetica', 'Arial', 'Times New Roman', 'Georgia', 'Avenir', 'Baskerville', 'Futura', 'Verdana', 'Gill Sans', 'Courier', 'Optima', 'American Typewriter']

try:
    PROTOCOL_URL = sys.argv[1]
    parsed = urllib.parse.urlparse(PROTOCOL_URL)
    if parsed.netloc == 'InstallPlugin':
        url = parsed.query.split('=')[1]
        try:
            response = urllib.request.urlopen(url)
            data = response.read()
            with ZipFile(BytesIO(data)) as z:
                z.extract(plugin_dir)
            showinfo('Plugin installed', 'Plugin was installed from the link. If everything is correct, you\'ll find it to run in the \'Plugins\' tab to run.')
        except Exception as e: showerror('Error while installing plugin', f'Error while installing the plugin: -> {e} <- Check your Internet connection or the URL in the link.')
except: pass

def AutoUpdate(gimme_your_self):
    try:
        online_ver = urllib.request.urlopen(ONL_VER_URL).read().decode().strip()
        if online_ver != VERSION:
            to_update = askyesno('Update available!', f'A new update to kPad {online_ver}, is available to install! Do it now?')
            if to_update:
                DownloadUpdateWindow(gimme_your_self)
            else:
                gimme_your_self.stats_line_col.configure(text='User rejected update | Ln: 1 Col: 1 Ch: 0')
        else:
            gimme_your_self.stats_line_col.configure(text='Up to date | Ln: 1 Col: 1 Ch: 0')
    except Exception as e: 
            gimme_your_self.stats_line_col.configure(text=f'⚠️ Warning! Could not check for updates: {e} | Ln: 1 Col: 1 Ch: 0')

class PluginAPI:
    def __init__(self, textbox, appinstance):
        self.textbox = textbox
        self._appinstance = appinstance
        
    def get_text_from_box(self):
        return self.textbox.get('1.0', 'end-1c')
    def get_specific_text_from_box(self, start, end):
        return self.textbox.get(start, end)
    def clear_text_from_box(self):
        self.textbox.delete('1.0', 'end')
    def insert_text_to_start_of_box(self, text):
        self.textbox.insert('1.0', text)
    def insert_text_to_end_of_box(self, text):
        self.textbox.insert('end', text)
    def bind(self, sequence, callback):
        def wrapper(event):
            try:
                callback(event)
            except TypeError:
                callback()
        self.textbox.bind(sequence, wrapper)
    def get_plugin_path(self, plugin_name):
        return os.path.join(plugin_dir, plugin_name)
    def get_current_file_path(self):
        return self._appinstance.path
    def get_current_theme_mode(self):
        return ctk.get_appearance_mode()
    def set_current_theme_mode(self, mode):
        if mode == 'light':
            ctk.set_appearance_mode('light')
        else:
            ctk.set_appearance_mode('dark')
    def set_theme_file(self, json_path):
            if os.path.exists(json_path):
                ctk.set_default_color_theme(json_path)
    def show_info(self, text):
        showinfo('Info', text)
    def show_error(self, text):
        showinfo('Error', text)
    def log(self, text):
        print(f'[PLUGIN LOG] {text}')
    def run_async(self, cmd, withdaemon=bool):
        thread = threading.Thread(target=cmd, daemon=withdaemon)
        return thread
    def Widget_Frame(self, parent, **kwargs):
        fr = ctk.CTkFrame(parent, **kwargs)
        return fr
    def Widget_Label(self, parent, text, font=('', 13), **kwargs):
        lbl = ctk.CTkLabel(parent, text=text, font=font, **kwargs)
        return lbl
    def Widget_Button(self, parent, text, cmd, font=('', 13), **kwargs):
        btn = ctk.CTkButton(parent, text=text, command=cmd, font=font, **kwargs)
        return btn
    def Widget_Other(self, parent, widget, **kwargs):
        widg = widget(parent, **kwargs)
        return widg
    def prepare_for_external_libs(self):
        'Use this when external libs are required for a plugin at the top of the action() function.'
        ver = f"{sys.version_info.major}.{sys.version_info.minor}"
        env = os.getenv("KPAD_PLUGIN_ENV")
        sys.path.append(os.path.join(env, "lib", f"python{ver}", "site-packages"))
    def get_selected_text(self):
        try:
            return self.textbox.get('sel.first', 'sel.last')
        except:
            return ''
    def get_selected_text_indexes(self):
        try:
            return (self.textbox.index('sel.first'), self.textbox.index('sel.last'))
        except:
            return None
    def add_text_tag(self, tag_name, **options):
        """Create or update a text tag (foreground, background, font, etc.)"""
        self.textbox.tag_config(tag_name, **options)

    def tag_text(self, tag_name, start, end):
        """Apply a tag to a range of text."""
        self.textbox.tag_add(tag_name, start, end)

    def remove_tag(self, tag_name, start="1.0", end="end"):
        """Remove a tag from a range."""
        self.textbox.tag_remove(tag_name, start, end)

    def clear_all_tags(self):
        """Remove all tags from the textbox."""
        for tag in self.textbox.tag_names():
            self.textbox.tag_remove(tag, "1.0", "end")
    
    def add_command_entry(self, entry_name, command):
        self._appinstance.appcmds['[PLUGIN ]' +entry_name] = command

class App(ctk.CTk):
    def __init__(self, title, geometry):
        super().__init__()

        self._Textboxes = []
        self._TabPaths = []
        self.tab_names = ['Untitled']

        model_textbox = ctk.CTkTextbox(self, undo=CONFIGURATION['undo']['enabled'],
                               autoseparators=CONFIGURATION['undo']['separate_edits_from_undos'],
                               maxundo=CONFIGURATION['undo']['max_undo'])
        
        self.textbox = model_textbox

        self._Textboxes.append(model_textbox)
        self._TabPaths.append(None)

        self.tabs = ctk.CTkSegmentedButton(self, values=['Untitled'])
        self.tabs.pack(fill='x', side=ctk.TOP)

        self.after(1, lambda: threading.Thread(target=AutoUpdate, args=(self,), daemon=True).start())

        import importlib.util

        def __load_plugins():
            plugins = []
            if not os.path.exists(plugin_dir):
                os.makedirs(plugin_dir)
            for folder in os.listdir(plugin_dir):
                folder_path = os.path.join(plugin_dir, folder)
                if not os.path.isdir(folder_path):
                    continue
                logic_path = os.path.join(folder_path, 'logic.py')
                if os.path.exists(logic_path):
                    name = folder
                    try:
                        spec = importlib.util.spec_from_file_location(name, logic_path)
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
                        meta_path = os.path.join(folder_path, 'metadata.json')
                        metadata = None
                        if os.path.exists(meta_path):
                            with open(meta_path, 'r') as f:
                                metadata = json.load(f)
                        if hasattr(mod, 'action'):
                            plugins.append({'module': mod, 'meta': metadata})
                    except Exception as e:
                        print(f'[PLUGIN ERROR] Failed to load \'{name}\': {e}')

            return plugins
        
        global PLUGINS_LIST
        PLUGINS_LIST = __load_plugins()
        editor_api = PluginAPI(self.textbox, self)
        self.plugins_list = PLUGINS_LIST

        self._TabPaths = [None]
        self.font_size = 14
        self.modified = False
        index = self.tabs.index(self.tab_names[0])

        def write_to_recent_files():
            if CONFIGURATION['recent_files']['enabled']:
                if len(CONFIGURATION['recent_files']['recent_file_paths']) >= CONFIGURATION['recent_files']['keep_recent_files_count']:
                    del CONFIGURATION['recent_files']['recent_file_paths'][0]
                    CONFIGURATION['recent_files']['recent_file_paths'].append(self._TabPaths[index])
                else:
                    CONFIGURATION['recent_files']['recent_file_paths'].append(self._TabPaths[index])

        def newtab(event=None, file_path=None):
            new_textbox = ctk.CTkTextbox(
                self, 
                undo=CONFIGURATION['undo']['enabled'],
                autoseparators=CONFIGURATION['undo']['separate_edits_from_undos'],
                maxundo=CONFIGURATION['undo']['max_undo']
            )
            for tb in self._Textboxes:
                tb.pack_forget()
            self._Textboxes.append(new_textbox)
            self._TabPaths.append(file_path or None)
            if file_path and os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    new_textbox.insert('1.0', f.read())
            tab_name = file_path or f'Untitled {len(self._Textboxes)}'
            self.tab_names.append(tab_name)
            self.tabs.configure(values=self.tab_names)
            self.tabs.set(tab_name)
            new_textbox.pack(fill='both', expand=True)
            self.textbox = new_textbox

        def on_tab_selected(value):
            nonlocal index
            for tb in self._Textboxes:
                tb.pack_forget()
            index = self.tab_names.index(value)
            self._Textboxes[index].pack(fill='both', expand=True)
            self._TabPaths[index] = self._TabPaths[index]
            self.textbox = self._Textboxes[index]

        def delete_tab(index):
            tb = self._Textboxes.pop(index)
            tb.pack_forget()
            self._TabPaths.pop(index)
            self.tab_names.pop(index)
            new_index = max(0, index - 1)
            if not self._Textboxes:
                new_textbox = ctk.CTkTextbox(self,
                                            undo=CONFIGURATION['undo']['enabled'],
                                            autoseparators=CONFIGURATION['undo']['separate_edits_from_undos'],
                                            maxundo=CONFIGURATION['undo']['max_undo'])
                self._Textboxes.append(new_textbox)
                self._TabPaths.append(None)
                self.tab_names.append("Untitled")
                new_textbox.pack(fill='both', expand=True)
                self.tabs.configure(values=self.tab_names)
                self.tabs.set("Untitled")
                self.textbox = new_textbox
                self.textbox.focus()
                return
            self.tabs.set(self.tab_names[new_index])
            on_tab_selected(self.tab_names[new_index])
            self.tabs.configure(values=self.tab_names)

        def __get_values_and_delete(event=None):
            value = self.tabs.get()
            index = self.tab_names.index(value)
            delete_tab(index)


        self.tabs.configure(command=on_tab_selected)


        def newfile(event=None):
            if not '*' in self.title()[7]:
                self.title('kPad - Untitled')
                self._TabPaths[index] = None
                self.textbox.delete('1.0', 'end')
            else:
                ask = askyesno('File unsaved!', 'Do you want to save your file before making a new one?')
                if ask:
                    save_file()
                else:
                    self.title('kPad - Untitled')
                    self._TabPaths[index] = None
                    self.textbox.delete('1.0', 'end')
                    

        def save_as(event=None):
            self._TabPaths[index] = asksaveasfilename(filetypes=[('Text files', '.txt'), ('Other', '.*.*')], defaultextension='.txt')
            if not self._TabPaths[index]:
                return
            try:
                with open(self._TabPaths[index], 'w', encoding='utf-8') as file:
                    file.write(self.textbox.get('1.0', 'end-1c'))
                self.title(f'kPad - {self._TabPaths[index]}')
                self.modified = False
                if self.title().endswith('*'):
                    self.title(self.title()[:-1])
            except Exception:
                return
        
        def open_plugin_folder():
            x = platform.system()
            if x == 'Darwin':
                subprocess.call(["open", plugin_dir])
            elif x == 'Windows':
                subprocess.call(['explorer', plugin_dir])
            else:
                subprocess.call(['xdg-open', plugin_dir])

        def save_file(event=None):
            if not self._TabPaths[index]:
                save_as()
                return
            with open(self._TabPaths[index], 'w', encoding='utf-8') as f:
                f.write(self.textbox.get('1.0', 'end-1c'))
            self.modified = False
            if self.title().endswith('*'):
                self.title(self.title()[:-1])

        
        def open_from_file(event=None, path=None):
            if not path:
                self._TabPaths[index] = askopenfilename(filetypes=[('Text files', '.txt'), ('All files', '*.*')], defaultextension='.txt')
            if self._TabPaths[index]:
                self.textbox.delete('1.0', 'end')
                with open(self._TabPaths[index], 'r') as file:
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
                    current_tab_name = self.tabs.get()
                    try:
                        current_index = self.tab_names.index(current_tab_name)
                    except ValueError:
                        time.sleep(CONFIGURATION['auto_save']['time_until_next_save'])
                        continue
                    if self._TabPaths[current_index] and 'Untitled' not in self.title():
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
                
        def add_second_char(char, event=None):
            def insert_char():
                cursor = self.textbox.index('insert')
                if char == '{':
                    self.textbox.insert(cursor, '}')
                elif char == '[':
                    self.textbox.insert(cursor, ']')
                elif char == '(':
                    self.textbox.insert(cursor, ')')
            self.after(1, insert_char)

        def handle_brackets(event):
            if event.char in '{[(':
                add_second_char(event.char)

        menu = Menu(self)
        file_menu = Menu(menu, tearoff=0)
        file_menu.add_command(label='Open', command=open_from_file)
        file_menu.add_command(label='Save As...', command=save_as)
        file_menu.add_command(label='Save...', command=save_file)
        file_menu.add_separator()
        for index, path in enumerate(CONFIGURATION['recent_files']['recent_file_paths']):
            file_menu.add_command(label=f'Open {path} ({index+1})...', command=lambda p=path: open_from_file(p))
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
        plugins_menu = Menu(menu, tearoff=0)
        menu.add_cascade(label='Plugins', menu=plugins_menu)
        plugins_menu.add_separator()
        plugins_menu.add_command(label='Show Plugin Information...', command=lambda: PluginsInfo(self.plugins_list))

        self.configure(menu=menu)

        self.font = ctk.CTkFont(family=CONFIGURATION['font'], size=CONFIGURATION['font_size'])
        self.font_size = CONFIGURATION['font_size']

        def update_cursor_info(event=None):
            pos = self.textbox.index('insert')
            line, col = map(int, pos.split('.'))
            chars = len(self.textbox.get('1.0', 'end-1c'))
            self.stats_line_col.configure(text=f'Ln: {line}  Col: {col + 1}  Ch: {chars}')

        self.title(title)
        self.geometry(f'{geometry[0]}x{geometry[1]}')

        self.textbox.configure(font=self.font)
        if word_wrap_var.get():
            self.textbox.configure(wrap='word')
        else:
            self.textbox.configure(wrap='none')

        self.textbox.bind('<KeyRelease>', update_cursor_info)
        self.textbox.bind('<ButtonRelease>', update_cursor_info)

        system = platform.system()
        if system == 'Darwin':
            mod = 'Command'
        else:
            mod = 'Control'

        self.bind(f'<{mod}-l>', go_to_line)
        self.bind(f'<{mod}-s>', save_file)
        self.bind(f'<{mod}-o>', open_from_file)
        self.bind(f'<{mod}-t>', toggle_theme)
        self.bind(f'<{mod}-n>', lambda event=None: newtab())
        self.bind(f'<{mod}-equal>', increment_font_size)
        self.bind(f'<{mod}-minus>', decrement_font_size)
        self.bind(f'<{mod}-k>', lambda event=None: FastCommand(self))
        self.bind(f'<{mod}-e>', __get_values_and_delete)

        self.textbox.bind('<Key>', handle_brackets)

        self.stats_text_frame = ctk.CTkFrame(self)
        self.stats_text_frame.pack(fill='x', side=ctk.BOTTOM)

        self.stats_line_col = ctk.CTkLabel(self.stats_text_frame, text='Ln: 1 Col: 1 Ch: 0')
        self.stats_line_col.pack(side=ctk.RIGHT)

        def on_text_change(event=None):
            if not self.modified:
                self.modified = True
                if not self.title().endswith('*'):
                    self.title(self.title() + '*')

        self.textbox.bind('<Key>', on_text_change, add='+')
        self.textbox.bind('<<Paste>>', on_text_change, add='+')
        self.textbox.bind('<<Cut>>', on_text_change, add='+')
        self.textbox.bind('<Delete>', on_text_change, add='+')

        def _on_quit_():
            if self.modified:
                result = askyesnocancel('Quit', 'Save changes before quitting?')
                if result is True:
                    if self._TabPaths[index]:
                        save_file()
                    else:
                        save_as()
                elif result is None:
                    return
            save_config()
            self.destroy()

        self.textbox.pack(fill='both', expand=True)
        self.protocol('WM_DELETE_WINDOW', _on_quit_)

        # Define appcmds BEFORE plugin auto-start so plugins can use it
        self.appcmds = {
            'Save': save_file,
            'Open from file': open_from_file,
            'Save as': save_as,
            'New file': newfile,
            'Open Plugin Folder': open_plugin_folder,
            'Go To Line': go_to_line,
            'Toggle Theme': toggle_theme,
            'Open Plugin Finder': lambda: PluginsInfo(self.plugins_list),
            'Increment font size': increment_font_size,
            'Decrement font size': decrement_font_size,
            'Toggle word wrap': toggle_word_wrap,
            'Save configuration': save_config,
            'Go to start': go_to_start,
            'Go to end': go_to_end
        }

        for plugin in self.plugins_list:
            name = plugin.get('meta', {}).get('name', plugin['module'].__name__)
            if name in CONFIGURATION.get('auto_start_plugins', []):
                try:
                    plugin['module'].action(editor_api)
                except Exception as e:
                    print(f"[PLUGIN ERROR] Auto-start failed for {name}: {e}")

        self.save_file = save_file
        self.open_from_file = open_from_file
        self.save_as = save_as
        self.newfile = newfile
        self.open_plugin_folder = open_plugin_folder
        self.toggle_theme = toggle_theme
        self.go_to_line = go_to_line
        self.incsize = increment_font_size
        self.decsize = decrement_font_size
        self.wordwrap = toggle_word_wrap
        self.saveconf = save_config
        self.gostart = go_to_start
        self.goend = go_to_end


        for plugin in self.plugins_list:
            meta = plugin['meta']
            name = meta.get('name') if meta else plugin['module'].__name__
            plugins_menu.add_command(label=name, command=lambda p=plugin: p['module'].action(editor_api))

class PluginsInfo(ctk.CTkToplevel):
    def __init__(self, plugins_list):
        super().__init__()

        def make_separator():
            ctk.CTkFrame(self.main, height=3).pack(fill='x', pady=5, padx=10)

        self.title('Plugin Info')
        self.geometry(f'500x600')
        
        self.main = ctk.CTkScrollableFrame(self)

        for plugin in plugins_list:
            meta = plugin.get('meta', {})
            name = meta.get('name', plugin['module'].__name__)
            author = meta.get('author', 'Unknown')
            version = meta.get('version', '1.0')
            desc = meta.get('desc', 'No description available.')

            ctk.CTkLabel(self.main, text=f'Name: {name}', font=ctk.CTkFont(weight='bold')).pack(anchor='w')
            ctk.CTkLabel(self.main, text=f'Author: {author}').pack(anchor='w')
            ctk.CTkLabel(self.main, text=f'Version: {version}').pack(anchor='w')
            ctk.CTkLabel(self.main, text=f'Description: {desc}', wraplength=360, justify='left').pack(anchor='w', pady=(0,5))
            ctk.CTkButton(self.main, text=f'Mark {name} as Autostarter...', command=lambda n=name: CONFIGURATION['auto_start_plugins'].append(n)).pack(pady=5, anchor='w')
            make_separator()
        self.main.pack(fill='both', expand='True')

class DownloadUpdateWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        syst = platform.system()
        arch = platform.machine().lower()
        if arch in ("x86_64", "amd64"):
            arch = "x86_64"
        elif arch in ("arm64", "aarch64"):
            arch = "arm64"

        
        def create_start_menu_shortcut(exe_path, name="kPad"):
            start_menu = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs")
            shortcut_path = os.path.join(start_menu, f"{name}.lnk")
            ps_cmd = f'''
            $WshShell = New-Object -ComObject WScript.Shell;
            $Shortcut = $WshShell.CreateShortcut("{shortcut_path}");
            $Shortcut.TargetPath = "{exe_path}";
            $Shortcut.WorkingDirectory = "{os.path.dirname(exe_path)}";
            $Shortcut.Save();
        '''
            os.system(f'powershell -Command "{ps_cmd}"')

        def Download():
            syst = platform.system()
            arch = platform.machine().lower()
            if arch in ("x86_64", "amd64"):
                arch = "x86_64"
            elif arch in ("arm64", "aarch64"):
                arch = "arm64"
            requiredUrl = DOWNLOAD_URLS.get((syst, arch))
            if not requiredUrl:
                showerror("Error", f"No download available for {syst} {arch}")
                return
            if syst == 'Darwin':
                try:
                    data = urllib.request.urlopen(requiredUrl).read()
                    with tempfile.TemporaryDirectory() as tmp_outer:
                        outer_zip_path = os.path.join(tmp_outer, os.path.basename(requiredUrl))
                        with open(outer_zip_path, "wb") as f:
                            f.write(data)
                        with ZipFile(outer_zip_path) as outer_zip:
                            outer_zip.extractall(tmp_outer)
                        inner_zip_path = None
                        for root, _, files in os.walk(tmp_outer):
                            for file in files:
                                if file.endswith(".zip"):
                                    inner_zip_path = os.path.join(root, file)
                                    break
                            if inner_zip_path:
                                break
                        if not inner_zip_path:
                            showerror("Error", "Could not find inner zip containing the .app")
                            self.destroy()
                            return
                        with tempfile.TemporaryDirectory() as tmp_inner:
                            with ZipFile(inner_zip_path) as inner_zip:
                                inner_zip.extractall(tmp_inner)
                            app_folder = None
                            for item in os.listdir(tmp_inner):
                                if item.endswith(".app"):
                                    app_folder = os.path.join(tmp_inner, item)
                                    break
                            if not app_folder:
                                showerror("Error", "Could not find .app inside the inner zip")
                                self.destroy()
                                return
                            dest = "/Applications/kPad.app"
                            if os.path.exists(dest):
                                shutil.rmtree(dest)
                            shutil.move(app_folder, dest)
                            showinfo("Update Installed", f"kPad installed to {dest}")
                except Exception as e:
                    showerror("Error", f"[Errno EXCEPTION]: Failed to install update: {e}")
                    self.destroy()
                    return
            elif syst == 'Windows':
                dest_folder = os.path.join(os.getenv("LOCALAPPDATA"), "kPad")
                os.makedirs(dest_folder, exist_ok=True)
                dest_file = os.path.join(dest_folder, "kPad.exe")
                try:
                    data = urllib.request.urlopen(requiredUrl).read()
                    with tempfile.TemporaryDirectory() as tmp:
                        with ZipFile(BytesIO(data)) as zip:
                            zip.extract(tmp)
                            shutil.move(f'{tmp}/kPad-Windows_x86_64/kPad-Windows_x86_64.exe', dest_file)
                            create_start_menu_shortcut(dest_file, f'kPad')
                except Exception as e:
                    showerror('Failed!', f'[Errno EXCEPTION]: {e}')
                    self.destroy()
                    return
        
        downloading_new_version = ctk.CTkLabel(self, text='Downloading update...')
        downloading_new_version.pack()
        this_might_etc = ctk.CTkLabel(self, text='This might take a bit, depending on your Internet connection. When done, the app will close.')
        this_might_etc.pack()
        load_pbar = ctk.CTkProgressBar(self, mode='indeterminate')
        load_pbar.pack()
        load_pbar.start()

        self.after(1, Download)

class FastCommand(ctk.CTkToplevel): 
    def __init__(self, parent):
        super().__init__()


        self.overrideredirect(True)
        self.after(10, lambda: self.attributes('-topmost', True))
        self.title(' ')
        self.geometry('300x200')

        

        results_box = Listbox(self, bg='#1D1D1D',
                                    fg='white',
                                    selectbackground='#FF8000',
                                    selectforeground='white',
                                    font=('JetBrains Mono', 12),
                                    activestyle='none',
                                    highlightthickness=0,
                                    bd=0
                                    )
        results_box.pack(fill='both', side=ctk.BOTTOM)

        COMMANDS = parent.appcmds

        def exit_window(event=None):
            parent.textbox.focus()
            self.destroy()
         
        def run_command(event=None):
            selection = results_box.curselection()
            if not selection:
                return
            sel = results_box.get(selection[0])
            COMMANDS[sel]()
            exit_window()
        
        def filter_(event=None):
            query = command_entry.get().lower()
            results_box.delete(0, "end")
            COMMANDS = parent.appcmds
            if query.strip() != "":
                for name in COMMANDS:
                    if query in name.lower():
                        results_box.insert("end", name)
            else:
                for name in COMMANDS:
                    results_box.insert("end", name)
            if results_box.size() > 0:
                results_box.selection_set(0)
        
        def run_filtering(event=None):
            threading.Thread(target=filter_, daemon=True).start()


        command_entry = ctk.CTkEntry(self, placeholder_text='Type a command or press Esc to exit...')
        command_entry.pack(fill='x', side=ctk.TOP)
        command_entry.focus()


        for command in COMMANDS:
            results_box.insert('end', command)

        self.bind('<Escape>', exit_window)
        results_box.bind('<Return>', run_command)
        command_entry.bind('<KeyRelease>', run_filtering)
        command_entry.bind('<Return>', run_command)



app = App('kPad - Untitled', CONFIGURATION['window_geometry'])
app.mainloop()
