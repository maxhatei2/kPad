import customtkinter as ctk
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter import Menu
from tkinter.messagebox import showinfo, askyesno, askyesnocancel, showerror
from tkinter import simpledialog
import time, threading, shutil
import os, json, platform, tempfile
import venv, sys, urllib.parse, urllib.request
from io import BytesIO
from zipfile import ZipFile

VERSION = '1.3.67'
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
# Version 1.3.0      [SOURCE CODE]


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
        'auto_start_plugins': []
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


class App(ctk.CTk):
    def __init__(self, title, geometry):
        super().__init__()

        self.after(1, lambda: threading.Thread(AutoUpdate(gimme_your_self=self)))

        import importlib.util

        self.textbox = ctk.CTkTextbox(self, undo=CONFIGURATION['undo']['enabled'], autoseparators=CONFIGURATION['undo']['separate_edits_from_undos'], maxundo=CONFIGURATION['undo']['max_undo'])

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

        self.path = None
        self.font_size = 14
        self.modified = False

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
            if not self.path:
                return
            try:
                with open(self.path, 'w', encoding='utf-8') as file:
                    file.write(self.textbox.get('1.0', 'end-1c'))
                self.title(f'kPad - {self.path}')
                self.modified = False
                if self.title().endswith('*'):
                    self.title(self.title()[:-1])
            except Exception:
                return

        def save_file(event=None):
            if not self.path:
                save_as()
                return
            with open(self.path, 'w', encoding='utf-8') as f:
                f.write(self.textbox.get('1.0', 'end-1c'))
            self.modified = False
            if self.title().endswith('*'):
                self.title(self.title()[:-1])

        
        def open_from_file(event=None, path=None):
            if not path:
                self.path = askopenfilename(filetypes=[('Text files', '.txt'), ('All files', '*.*')], defaultextension='.txt')
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
        
        def auto_indent(event):
            tb = event.widget
            cursor_index = tb.index('insert')
            line_number = int(cursor_index.split('.')[0])
            indent = 0
            prev_line_num = line_number - 1
            while prev_line_num > 0:
                prev_line_text = tb.get(f'{prev_line_num}.0', f'{prev_line_num}.end')
                if prev_line_text.strip() != '':
                    indent = len(prev_line_text) - len(prev_line_text.lstrip(' '))
                    if prev_line_text.rstrip().endswith((':', '{')):
                        indent += 4
                    break
                prev_line_num -= 1
            current_line_text = tb.get(f'{line_number}.0', f'{line_number}.end')
            if current_line_text.strip() == '':
                tb.insert('insert', ' ' * indent)
            tb.insert('insert', '\n' + ' ' * indent)
            return 'break'
                
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
        for plugin in self.plugins_list:
            meta = plugin['meta']
            name = meta.get('name') if meta else plugin['module'].__name__
            plugins_menu.add_command(label=name, command=lambda p=plugin: p['module'].action(editor_api))
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
        self.textbox.bind('<Return>', auto_indent)

        system = platform.system()
        if system == 'Darwin':
            mod = 'Command'
        else:
            mod = 'Control'

        self.bind(f'<{mod}-l>', go_to_line)
        self.bind(f'<{mod}-s>', save_file)
        self.bind(f'<{mod}-o>', open_from_file)
        self.bind(f'<{mod}-t>', toggle_theme)
        self.bind(f'<{mod}-n>', newfile)
        self.bind(f'<{mod}-equal>', increment_font_size)
        self.bind(f'<{mod}-minus>', decrement_font_size)

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
                    if self.path:
                        save_file()
                    else:
                        save_as()
                elif result is None:
                    return
            save_config()
            self.destroy()

        for plugin in self.plugins_list:
            name = plugin.get('meta', {}).get('name', plugin['module'].__name__)
            if name in CONFIGURATION.get('auto_start_plugins', []):
                try:
                    plugin['module'].action(editor_api)
                except Exception as e:
                    print(f"[PLUGIN ERROR] Auto-start failed for {name}: {e}")

        self.textbox.pack(fill='both', expand=True)
        self.protocol('WM_DELETE_WINDOW', _on_quit_)

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


app = App('kPad - Untitled', CONFIGURATION['window_geometry'])
app.mainloop()
