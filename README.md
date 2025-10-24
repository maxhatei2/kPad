# kPad
kPad is a Notepad app made in Python and CustomTkinter.

**If you want to compile for your platform or just run the file, you will need customtkinter installed.**

### kPad 1.2.1 (RC3.1) Extensia

## Description
kPad is a lightweight and user-friendly text editor designed for quick note-taking and editing. Built using Python and the CustomTkinter library, it offers a modern interface with essential features for everyday text editing tasks.

## Installation
To use kPad, you need to have Python installed on your system. Additionally, the CustomTkinter library is required.

You can install CustomTkinter using pip:

```bash
 python3 -m pip install customtkinter
```

Make sure you have Python 3.9+.

## Features
- Clean and intuitive UI built with CustomTkinter.
- Basic text editing functionalities (open, save, edit).
- Keyboard shortcuts for common actions:

  **Control-L** -> go to line

  **Cmd-S** -> save (auto save as)

  **Command-O** -> Save as

  **Cmd-T** -> Switch to light/dark mode

  **Cmd-N** -> New file

   Config files in their respective folder.
- Responsive window resizing.

## Running the App
Once you have installed the dependencies, you can run kPad by executing the main Python script:

```bash
python main.py
```

Replace `main.py` with the actual filename if different.

## Binaries

Binaries are available in the **Releases** tab by default, artifacts compiled by GitHub Actions.

---

Requests features with a new **issue**.

---

Feel free to contribute or report issues on the **project repository**.

## TODO
- [ ] Add syntax highlighting for Python
- [x] Implement recent files menu
- [ ] Add find/search dialog
- [ ] Improve autosave with dirty flag
- [x] Implement extensions