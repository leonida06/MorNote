import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, font as tkfont, ttk, colorchooser
from markdowncompiler import compila_markdown
import Logicafunz
import Scorciatoie
import SceltaFile
import os
import platform
import re
import tempfile
import webbrowser


# Tag booleani (non toccano il font)
SIMPLE_TAGS = ("underline", "strike", "highlight")
ALIGN_TAGS = ("align_left", "align_center", "align_right")
SCRIPT_TAGS = ("superscript", "subscript")   # apice / pedice

# Pattern per il riconoscimento delle righe negli elenchi
BULLET_RE = re.compile(r"^(\s*)-\s+")
NUMBERED_RE = re.compile(r"^(\s*)\d+\.\s+")

# Catalogo caratteri speciali  { "Categoria": ["char", ...] }
SPECIAL_CHARS = {
    "Matematica": [
        "±", "×", "÷", "≠", "≈", "≤", "≥", "∞", "√", "∑", "∏", "∂",
        "∫", "∆", "∇", "∈", "∉", "∩", "∪", "⊂", "⊃", "⊄", "⊆", "⊇",
        "∀", "∃", "¬", "∧", "∨", "⊕", "⊗", "°", "‰", "π", "μ",
    ],
    "Frecce": [
        "←", "→", "↑", "↓", "↔", "↕", "⇐", "⇒", "⇑", "⇓", "⇔",
        "↖", "↗", "↘", "↙", "↺", "↻", "➔", "➡", "⬅", "⬆", "⬇",
    ],
    "Valuta": [
        "€", "£", "¥", "¢", "₹", "₽", "₩", "₿", "₺", "₴", "₦", "₫",
    ],
    "Punteggiatura": [
        "«", "»", "‹", "›", "„", "\u201c", "\u201d", "'", "'", "…", "–", "—",
        "•", "·", "†", "‡", "§", "¶", "©", "®", "™", "℃", "℉",
    ],
    "Lettere": [
        "À", "Á", "Â", "Ã", "Ä", "Å", "Æ", "Ç", "È", "É", "Ê", "Ë",
        "Ì", "Í", "Î", "Ï", "Ñ", "Ò", "Ó", "Ô", "Õ", "Ö", "Ø", "Ù",
        "Ú", "Û", "Ü", "Ý", "ß", "à", "á", "â", "ã", "ä", "å", "æ",
        "ç", "è", "é", "ê", "ë", "ì", "í", "î", "ï", "ñ", "ò", "ó",
        "ô", "õ", "ö", "ø", "ù", "ú", "û", "ü", "ý", "ÿ",
    ],
    "Geometria": [
        "■", "□", "▪", "▫", "▲", "△", "▼", "▽", "◆", "◇", "●", "○",
        "◉", "★", "☆", "♠", "♣", "♥", "♦", "⬛", "⬜", "🔷", "🔶",
    ],
}

DEFAULT_FAMILY = "Arial"
DEFAULT_SIZE = 12

# struttura per il tasto pulisci stile.
DEFAULT_STYLE = {
    "family":    DEFAULT_FAMILY,
    "size":      DEFAULT_SIZE,
    "bold":      False,
    "italic":    False,
    "underline": False,
    "strike":    False,
    "highlight": None,
    "color":     None,
    "align":     "align_left",
}

FONT_FAMILIES = ["Arial", "Calibri", "Times New Roman", "Courier New",
                 "Georgia", "Verdana", "Consolas", "DejaVu Sans", "DejaVu Serif"]
FONT_SIZES = [8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 32, 40, 48]

# Palette colori
HIGHLIGHT_PALETTE = [
    ("Giallo",   "#fff59d"),
    ("Verde",    "#c5e1a5"),
    ("Ciano",    "#b3e5fc"),
    ("Rosa",     "#f8bbd0"),
    ("Arancio",  "#ffcc80"),
    ("Rosso",    "#ef9a9a"),
    ("Viola",    "#ce93d8"),
    ("Grigio",   "#cfd8dc"),
]
TEXT_COLOR_PALETTE = [
    ("Nero",     "#000000"),
    ("Rosso",    "#c62828"),
    ("Blu",      "#1565c0"),
    ("Verde",    "#2e7d32"),
    ("Arancio",  "#ef6c00"),
    ("Viola",    "#6a1b9a"),
    ("Marrone",  "#5d4037"),
    ("Grigio",   "#616161"),
]

# Temi chiaro / scuro
THEME_LIGHT = {
    "root_bg":        "#f0f0f0",
    "toolbar_bg":     "#f0f0f0",
    "top_frame_bg":   "#f0f0f0",
    "editor_bg":      "#ffffff",
    "editor_fg":      "#000000",
    "editor_insert":  "#000000",
    "editor_sel_bg":  "#3399ff",
    "label_left_bg":  "#e8e8f0",
    "label_right_bg": "#f0e8e8",
    "label_fg":       "#000000",
    "status_bg":      "#f0f0f0",
    "status_fg":      "#000000",
    "button_bg":      "#e0e0e0",
    "button_fg":      "#000000",
    "button_active":  "#d0d0d0",
    "button_border":  "#000000",
    "sep_color":      "#bbbbbb",
    "paned_bg":       "#c8c8c8",
    "menu_bg":        "#f0f0f0",
    "menu_fg":        "#000000",
}
THEME_DARK = {
    "root_bg":        "#1e1e1e",
    "toolbar_bg":     "#2d2d2d",
    "top_frame_bg":   "#2d2d2d",
    "editor_bg":      "#252526",
    "editor_fg":      "#d4d4d4",
    "editor_insert":  "#ffffff",
    "editor_sel_bg":  "#264f78",
    "label_left_bg":  "#2a2a3a",
    "label_right_bg": "#3a2a2a",
    "label_fg":       "#cccccc",
    "status_bg":      "#007acc",
    "status_fg":      "#ffffff",
    "button_bg":      "#3c3c3c",
    "button_fg":      "#d4d4d4",
    "button_active":  "#505050",
    "button_border":  "#d4d4d4",
    "sep_color":      "#555555",
    "paned_bg":       "#3c3c3c",
    "menu_bg":        "#2d2d2d",
    "menu_fg":        "#d4d4d4",
}


class MorNoteGUI:
    @staticmethod
    def _get_home_dir():
        """
        Ritorna la home dell'utente corrente da usare come cartella di
        partenza nei dialog Apri/Salva, indipendentemente da chi sta
        eseguendo lo script o da come si chiama.
        """
        home = os.path.expanduser("~")
        if os.path.isdir(home):
            return home
        try:
            import getpass
            candidate = f"/home/{getpass.getuser()}"
            if os.path.isdir(candidate):
                return candidate
        except Exception:
            pass
        return os.getcwd()

    def __init__(self, root):
        self.root = root
        self.root.title("MorNote")
        self.path = None
        self.file_ext = None
        self.shortcuts_enabled = True
        self.compile_job = None
        self.modified = False
        self._dark_mode = False
        self._theme_widgets = []   # lista di (widget, ruolo) da ricolorare
        self._last_dir = self._get_home_dir()  # cartella iniziale/ultima usata nei dialog
        self._tmp_html_path = None  # ultimo file temporaneo di anteprima creato

        # Formattazione "sticky": stile scelto senza selezione, che verrà

        self._typing_format = {
            "bold": False, "italic": False, "underline": False, "strike": False,
            "highlight": None, "color": None, "family": None, "size": None,
        }
        self._sticky_anchor = None   # (editor, index) | None

        # massimizza
        try:
            if platform.system() == "Windows":
                self.root.state("zoomed")
            else:
                self.root.attributes("-zoomed", True)
        except tk.TclError:
            self.root.geometry("1200x700")
        self.root.minsize(800, 500)

        # stile ttk più morbido (pulsanti piatti, niente rilievo pesante)
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Soft.TButton", padding=6, relief="flat")
        style.configure("Soft.TCombobox", padding=3)

        # ===== MENUBAR =====
        menubar = tk.Menu(self.root)

        menu_file = tk.Menu(menubar, tearoff=0)
        menu_file.add_command(label="Nuovo            Ctrl+N", command=self.nuovo_file)
        menu_file.add_command(label="Apri             Ctrl+O", command=self.scegli_file)
        menu_file.add_command(label="Salva            Ctrl+S", command=self.scrivi_nota)
        menu_file.add_command(label="Salva con nome   Ctrl+Shift+S", command=self.salva_con_nome)
        menu_file.add_separator()
        menu_file.add_command(label="Esci", command=self.root.quit)
        menubar.add_cascade(label="File", menu=menu_file)

        menu_modifica = tk.Menu(menubar, tearoff=0)
        menu_modifica.add_command(label="Copia    Ctrl+C", command=lambda: self.focused_editor().event_generate("<<Copy>>"))
        menu_modifica.add_command(label="Incolla  Ctrl+V", command=lambda: self.focused_editor().event_generate("<<Paste>>"))
        menu_modifica.add_command(label="Taglia   Ctrl+X", command=lambda: self.focused_editor().event_generate("<<Cut>>"))
        menu_modifica.add_separator()
        menu_modifica.add_command(label="Annulla  Ctrl+Z", command=lambda: self.focused_editor().event_generate("<<Undo>>"))
        menu_modifica.add_command(label="Ripeti   Ctrl+Y", command=lambda: self.focused_editor().event_generate("<<Redo>>"))
        menu_modifica.add_separator()
        menu_modifica.add_command(label="Cerca    Ctrl+F", command=self.apri_ricerca)
        menubar.add_cascade(label="Modifica", menu=menu_modifica)

        menu_formato = tk.Menu(menubar, tearoff=0)
        menu_formato.add_command(label="Grassetto    Ctrl+B", command=self.bold_text)
        menu_formato.add_command(label="Corsivo      Ctrl+I", command=self.italic_text)
        menu_formato.add_command(label="Sottolineato Ctrl+U", command=self.underline_text)
        menu_formato.add_command(label="Barrato", command=self.strike_text)
        menu_formato.add_separator()
        menu_formato.add_command(label="Apice   (superscript)", command=self.superscript_text)
        menu_formato.add_command(label="Pedice  (subscript)",   command=self.subscript_text)
        menu_formato.add_separator()
        menu_formato.add_command(label="Allinea a sinistra", command=lambda: self.set_align("align_left"))
        menu_formato.add_command(label="Centra",            command=lambda: self.set_align("align_center"))
        menu_formato.add_command(label="Allinea a destra",  command=lambda: self.set_align("align_right"))
        menu_formato.add_separator()
        menu_formato.add_command(label="Elenco puntato", command=self.toggle_bullet_list)
        menu_formato.add_command(label="Elenco numerato", command=self.toggle_numbered_list)
        menu_formato.add_separator()
        menu_formato.add_command(label="Rimuovi formattazione", command=self.clear_formatting)
        menubar.add_cascade(label="Formato", menu=menu_formato)

        menu_visualizza = tk.Menu(menubar, tearoff=0)
        self._dark_mode_var = tk.BooleanVar(value=False)
        menu_visualizza.add_checkbutton(label="Tema scuro", variable=self._dark_mode_var,
                                        command=self.toggle_tema)
        menubar.add_cascade(label="Visualizza", menu=menu_visualizza)

        menu_aiuto = tk.Menu(menubar, tearoff=0)
        menu_aiuto.add_command(label="Scorciatoie da tastiera", command=self.mostra_scorciatoie)
        menubar.add_cascade(label="?", menu=menu_aiuto)

        self.root.config(menu=menubar)

        # ===== TOOLBAR =====
        toolbar = tk.Frame(self.root, bd=0, relief=tk.FLAT)
        toolbar.pack(fill=tk.X)
        self._theme_widgets.append((toolbar, "toolbar_bg"))

        # font family
        self.font_family_var = tk.StringVar(value=DEFAULT_FAMILY)
        family_cb = ttk.Combobox(toolbar, textvariable=self.font_family_var,
                                 values=FONT_FAMILIES, width=18, state="readonly",
                                 style="Soft.TCombobox")
        family_cb.pack(side=tk.LEFT, padx=4, pady=4)
        family_cb.bind("<ButtonPress-1>", lambda e: self._save_selection())
        family_cb.bind("<<ComboboxSelected>>", lambda e: self.apply_font_family())
        ToolTip(family_cb, "Famiglia del carattere")

        # font size
        self.font_size_var = tk.IntVar(value=DEFAULT_SIZE)
        size_cb = ttk.Combobox(toolbar, textvariable=self.font_size_var,
                               values=FONT_SIZES, width=4, state="readonly",
                               style="Soft.TCombobox")
        size_cb.pack(side=tk.LEFT, padx=4, pady=4)
        size_cb.bind("<ButtonPress-1>", lambda e: self._save_selection())
        size_cb.bind("<<ComboboxSelected>>", lambda e: self.apply_font_size())
        ToolTip(size_cb, "Dimensione del carattere")

        def sep():
            tk.Frame(toolbar, width=2, bg="#bbb").pack(side=tk.LEFT, fill=tk.Y, padx=4, pady=4)

        sep()
        self.btn_b = tk.Button(toolbar, text="B", width=2, relief=tk.FLAT, font=("TkDefaultFont", 10, "bold"),   command=self.bold_text)
        self.btn_i = tk.Button(toolbar, text="I", width=2, relief=tk.FLAT, font=("TkDefaultFont", 10, "italic"),  command=self.italic_text)
        self.btn_u = tk.Button(toolbar, text="U", width=2, relief=tk.FLAT, font=("TkDefaultFont", 10, "underline"), command=self.underline_text)
        self.btn_s = tk.Button(toolbar, text="S", width=2, relief=tk.FLAT, font=("TkDefaultFont", 10, "overstrike"), command=self.strike_text)
        for b, tip in ((self.btn_b, "Grassetto (Ctrl+B)"), (self.btn_i, "Corsivo (Ctrl+I)"),
                       (self.btn_u, "Sottolineato (Ctrl+U)"), (self.btn_s, "Barrato")):
            b.pack(side=tk.LEFT, padx=1)
            self._theme_widgets.append((b, "button"))
            ToolTip(b, tip)

        sep()
        # Evidenziatore con palette
        self._build_color_menu(toolbar, "🖍", HIGHLIGHT_PALETTE,
                               self.apply_highlight, self.remove_highlight, "Evidenzia",
                               "Evidenzia il testo selezionato")
        # Colore testo con palette
        self._build_color_menu(toolbar, "A", TEXT_COLOR_PALETTE,
                               self.apply_text_color, self.remove_text_color, "Colore testo",
                               "Cambia colore al testo selezionato")

        sep()
        btn_bullet = tk.Button(toolbar, text="•≡", width=3, relief=tk.FLAT, command=self.toggle_bullet_list)
        btn_numlist = tk.Button(toolbar, text="1≡", width=3, relief=tk.FLAT, command=self.toggle_numbered_list)
        for b, tip in ((btn_bullet, "Elenco puntato"), (btn_numlist, "Elenco numerato")):
            b.pack(side=tk.LEFT, padx=1)
            self._theme_widgets.append((b, "button"))
            ToolTip(b, tip)

        sep()
        btn_al = tk.Button(toolbar, text="⟸", width=2, relief=tk.FLAT, command=lambda: self.set_align("align_left"))
        btn_ac = tk.Button(toolbar, text="≡",  width=2, relief=tk.FLAT, command=lambda: self.set_align("align_center"))
        btn_ar = tk.Button(toolbar, text="⟹", width=2, relief=tk.FLAT, command=lambda: self.set_align("align_right"))
        for b, tip in ((btn_al, "Allinea a sinistra"), (btn_ac, "Centra"), (btn_ar, "Allinea a destra")):
            b.pack(side=tk.LEFT, padx=1)
            self._theme_widgets.append((b, "button"))
            ToolTip(b, tip)

        sep()
        btn_pulisci = tk.Button(toolbar, text="🧹", width=3, relief=tk.FLAT, command=self.clear_formatting)
        btn_pulisci.pack(side=tk.LEFT, padx=4)
        self._theme_widgets.append((btn_pulisci, "button"))
        ToolTip(btn_pulisci, "Rimuovi formattazione")

        sep()
        btn_sup = tk.Button(toolbar, text="x²", width=3, relief=tk.FLAT, command=self.superscript_text)
        btn_sub = tk.Button(toolbar, text="x₂", width=3, relief=tk.FLAT, command=self.subscript_text)
        for b, tip in ((btn_sup, "Apice"), (btn_sub, "Pedice")):
            b.pack(side=tk.LEFT, padx=1)
            self._theme_widgets.append((b, "button"))
            ToolTip(b, tip)

        sep()
        btn_special = tk.Button(toolbar, text="Ω", width=3, relief=tk.FLAT, command=self.apri_caratteri_speciali)
        btn_special.pack(side=tk.LEFT, padx=4)
        self._theme_widgets.append((btn_special, "button"))
        ToolTip(btn_special, "Caratteri speciali")

        # ----- pulsante Info/Scorciatoie, ancorato a destra della toolbar -----
        btn_info = tk.Button(toolbar, text="ℹ️", width=3, relief=tk.FLAT, command=self.mostra_scorciatoie)
        btn_info.pack(side=tk.RIGHT, padx=6)
        self._theme_widgets.append((btn_info, "button"))
        ToolTip(btn_info, "Scorciatoie da tastiera")

        # selezione file + azioni
        top_frame = tk.Frame(root)
        top_frame.pack(fill=tk.X, pady=4)
        self._theme_widgets.append((top_frame, "top_frame_bg"))
        azioni = [
            ("🆕", "Nuovo (Ctrl+N)", self.nuovo_file),
            ("📂", "Apri (Ctrl+O)", self.scegli_file),
            ("💾", "Salva (Ctrl+S)", self.scrivi_nota),
            ("💾▾", "Salva con nome (Ctrl+Shift+S)", self.salva_con_nome),
            ("🌐", "Apri anteprima nel browser", self.compila_output),
        ]
        for icona, tip, comando in azioni:
            b = tk.Button(top_frame, text=icona, relief=tk.FLAT, padx=6, command=comando)
            b.pack(side=tk.LEFT, padx=4)
            self._theme_widgets.append((b, "button"))
            ToolTip(b, tip)
        self.label_file = tk.Label(top_frame, text="Nessun file selezionato")
        self.label_file.pack(side=tk.LEFT, padx=10)
        self._theme_widgets.append((self.label_file, "label_left_bg"))

        # ===== EDITOR DOPPIO =====
        self.paned = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief=tk.FLAT, sashwidth=6)
        self.paned.pack(fill=tk.BOTH, expand=True)
        self._theme_widgets.append((self.paned, "paned_bg"))

        left_frame = tk.Frame(self.paned)
        self._label_left = tk.Label(left_frame, text="Editor SX", anchor="w", bg="#e8e8f0")
        self._label_left.pack(fill=tk.X)
        self._theme_widgets.append((left_frame,        "toolbar_bg"))
        self._theme_widgets.append((self._label_left,  "label_left"))
        self.editor_left = scrolledtext.ScrolledText(
            left_frame, undo=True, wrap="word",
            font=(DEFAULT_FAMILY, DEFAULT_SIZE), relief=tk.FLAT, borderwidth=6
        )
        self.editor_left.pack(fill=tk.BOTH, expand=True)
        self.paned.add(left_frame, minsize=200)

        right_frame = tk.Frame(self.paned)
        self._label_right = tk.Label(right_frame, text="Editor DX", anchor="w", bg="#f0e8e8")
        self._label_right.pack(fill=tk.X)
        self._theme_widgets.append((right_frame,        "toolbar_bg"))
        self._theme_widgets.append((self._label_right,  "label_right"))
        self.editor_right = scrolledtext.ScrolledText(
            right_frame, undo=True, wrap="word",
            font=(DEFAULT_FAMILY, DEFAULT_SIZE), relief=tk.FLAT, borderwidth=6
        )
        self.editor_right.pack(fill=tk.BOTH, expand=True)
        self.paned.add(right_frame, minsize=200)

        # cache dei Font objects per i tag compositi
        self._font_cache = {}

        # selezione salvata prima che il Combobox rubi il focus
        self._saved_sel = None   # (start, end) | None
        self._saved_ed  = None   # editor a cui appartiene la selezione

        # tasti di navigazione dopo i quali lo stile attivo va risincronizzato

        NAV_KEYSYMS = ("Left", "Right", "Up", "Down", "Home", "End", "Prior", "Next")

        self._last_focus = self.editor_left
        for ed in (self.editor_left, self.editor_right):
            ed.bind("<FocusIn>", self._on_focus_in)
            ed.bind("<KeyRelease>", self._on_key_release)
            ed.bind("<ButtonRelease>", self._on_button_release)
            ed.bind("<Return>", self._on_return_key)
            for keysym in NAV_KEYSYMS:
                ed.bind(f"<KeyRelease-{keysym}>", self._on_cursor_nav)
            self._setup_tags(ed)
            self._setup_typing_format_proxy(ed)

        # status bar
        self.status = tk.Label(self.root, text="Pronto", anchor="w", relief=tk.SUNKEN)
        self.status.pack(fill=tk.X, side=tk.BOTTOM)
        self._theme_widgets.append((self.status, "status"))

        Scorciatoie.bind_shortcuts(self.root, self.editor_left, self.editor_right, self)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.toggle_tema()  # applica subito i colori/bordi del tema chiaro di default
        self.update_status()

    def _on_close(self):
        """Ripulisce l'eventuale file temporaneo di anteprima rimasto in
        /tmp prima di chiudere l'app (vedi compila_output)."""
        self._rimuovi_tmp_html()
        self.root.destroy()

    def _rimuovi_tmp_html(self):
        if self._tmp_html_path:
            try:
                os.remove(self._tmp_html_path)
            except OSError:
                pass
            self._tmp_html_path = None

    # ============================================================
    # Toolbar: menu colori
    # ============================================================
    def _build_color_menu(self, parent, label, palette, on_pick, on_clear, title, tip=None):
        mb = tk.Menubutton(parent, text=label, relief=tk.FLAT, padx=4)
        menu = tk.Menu(mb, tearoff=0)
        menu.add_command(label=title, state="disabled")
        menu.add_separator()
        for name, color in palette:
            # Icona colorata accanto al nome (tramite bitmap surrogate: usiamo background)
            menu.add_command(label=f"  ■  {name}", foreground=color,
                             command=lambda c=color: on_pick(c))
        menu.add_separator()
        menu.add_command(label="Altro…",
                         command=lambda: self._pick_custom_color(on_pick, title))
        menu.add_command(label="Rimuovi", command=on_clear)
        mb.config(menu=menu)
        mb.pack(side=tk.LEFT, padx=2)
        self._theme_widgets.append((mb, "button"))
        if tip:
            ToolTip(mb, tip)
        return mb

    def _pick_custom_color(self, on_pick, title):
        c = colorchooser.askcolor(title=title)
        if c and c[1]:
            on_pick(c[1])

    # ============================================================
    # Helpers focus / editor attivo
    # ============================================================
    def focused_editor(self):
        return self._last_focus or self.editor_left

    def _on_focus_in(self, event):
        self._last_focus = event.widget

    def _on_return_key(self, event):
        """Se il cursore è su una riga di elenco (puntato o numerato),
        Invio continua l'elenco sulla riga successiva senza bisogno di
        ripremere il pulsante ogni volta. Invio su una riga di elenco
        vuota (solo il prefisso, nessun contenuto) esce dall'elenco
        rimuovendo il prefisso, invece di continuarlo all'infinito."""
        ed = event.widget
        if ed not in (self.editor_left, self.editor_right):
            return None

        try:
            insert_idx = ed.index("insert")
        except tk.TclError:
            return None

        line_no = int(insert_idx.split(".")[0])
        line_start = f"{line_no}.0"
        line_text = ed.get(line_start, f"{line_no}.end")

        m_bul = BULLET_RE.match(line_text)
        m_num = NUMBERED_RE.match(line_text)
        if not (m_bul or m_num):
            return None  # riga normale: comportamento di default di Tk

        prefix = (m_bul or m_num).group(0)
        resto = line_text[len(prefix):]

        if resto.strip() == "":
            ed.delete(line_start, f"{line_start}+{len(prefix)}c")
            self.modified = True
            self.update_status()
            return "break"

        ed.insert("insert", "\n")
        if m_bul:
            nuovo_prefix = "- "
        else:
            num_match = re.match(r"^\s*(\d+)\.", line_text)
            n = int(num_match.group(1)) + 1 if num_match else 1
            nuovo_prefix = f"{n}. "
        ed.insert("insert", nuovo_prefix)

        self.modified = True
        self.update_status()
        return "break"

    def _on_key_release(self, event=None):
        self.modified = True
        self.update_status(event)

    def _on_button_release(self, event=None):
        """Click del mouse: aggiorna status bar e stile attivo sul nuovo punto del cursore."""
        self.update_status(event)
        if event is not None:
            self._sync_typing_format_from_cursor(event.widget)

    def _on_cursor_nav(self, event=None):
        """Frecce/Home/End/PageUp/PageDown: il cursore si è spostato senza
        digitare, quindi risincronizza lo stile attivo sul nuovo punto."""
        self.update_status(event)
        if event is not None:
            self._sync_typing_format_from_cursor(event.widget)

    def _sync_typing_format_from_cursor(self, ed):
        """Aggiorna typing_format e toolbar (bottoni B/I/U/S, font, dimensione)
        in base al testo subito a sinistra del cursore, così muovendosi nel
        documento lo stile 'attivo' segue sempre il punto in cui ci si trova,
        come in Word. Non viene chiamata durante la digitazione normale, per
        non entrare in conflitto con lo sticky-format già in uso mentre si scrive.
        """
        try:
            insert_idx = ed.index("insert")
        except tk.TclError:
            return

        anchor = self._sticky_anchor
        if anchor is not None and anchor[0] is ed and anchor[1] == insert_idx:
            return
        self._sticky_anchor = None

        if ed.compare(insert_idx, ">", "1.0"):
            ref_idx = ed.index(f"{insert_idx} -1c")
        else:
            ref_idx = insert_idx

        family, size, bold, italic = self._get_char_attrs(ed, ref_idx)
        tags_at = ed.tag_names(ref_idx)

        self._typing_format["bold"] = bold
        self._typing_format["italic"] = italic
        self._typing_format["underline"] = "underline" in tags_at
        self._typing_format["strike"] = "strike" in tags_at

        highlight = None
        for t in tags_at:
            if t.startswith("hl_"):
                highlight = t[3:]
                break
            if t == "highlight":
                highlight = "#fff59d"
                break
        self._typing_format["highlight"] = highlight

        color = None
        for t in tags_at:
            if t.startswith("col_"):
                color = t[4:]
                break
        self._typing_format["color"] = color

        self._typing_format["family"] = family
        self._typing_format["size"] = size

        self._update_format_buttons()
        self.font_family_var.set(family)
        self.font_size_var.set(size)

    # ============================================================
    # TEMA SCURO / CHIARO
    # ============================================================
    def toggle_tema(self):
        self._dark_mode = self._dark_mode_var.get()
        t = THEME_DARK if self._dark_mode else THEME_LIGHT
        self.root.configure(bg=t["root_bg"])

        for widget, role in self._theme_widgets:
            try:
                if role == "toolbar_bg":
                    widget.configure(bg=t["toolbar_bg"])
                elif role == "top_frame_bg":
                    widget.configure(bg=t["top_frame_bg"])
                elif role == "button":
                    widget.configure(bg=t["button_bg"], fg=t["button_fg"],
                                     activebackground=t["button_active"],
                                     activeforeground=t["button_fg"],
                                     highlightbackground=t["button_border"],
                                     highlightcolor=t["button_border"],
                                     highlightthickness=1)
                elif role == "label_left":
                    widget.configure(bg=t["label_left_bg"], fg=t["label_fg"])
                elif role == "label_right":
                    widget.configure(bg=t["label_right_bg"], fg=t["label_fg"])
                elif role == "label_left_bg":   # label_file
                    widget.configure(bg=t["top_frame_bg"], fg=t["label_fg"])
                elif role == "status":
                    widget.configure(bg=t["status_bg"], fg=t["status_fg"])
                elif role == "paned_bg":
                    widget.configure(bg=t["paned_bg"])
            except tk.TclError:
                pass

        for ed in (self.editor_left, self.editor_right):
            ed.configure(
                bg=t["editor_bg"],
                fg=t["editor_fg"],
                insertbackground=t["editor_insert"],
                selectbackground=t["editor_sel_bg"],
            )

    # ============================================================
    # Tag setup (stili che NON toccano il font)
    # ============================================================
    def _setup_tags(self, editor):
        editor.tag_configure("underline", underline=True)
        editor.tag_configure("strike", overstrike=True)
        editor.tag_configure("highlight", background="#fff59d")
        editor.tag_configure("align_left", justify="left")
        editor.tag_configure("align_center", justify="center")
        editor.tag_configure("align_right", justify="right")
        # apice: offset positivo (va su), pedice: offset negativo (va giù)
        sup_font = tkfont.Font(family=DEFAULT_FAMILY, size=int(DEFAULT_SIZE * 0.7))
        sub_font = tkfont.Font(family=DEFAULT_FAMILY, size=int(DEFAULT_SIZE * 0.7))
        editor.tag_configure("superscript", offset=6,  font=sup_font)
        editor.tag_configure("subscript",   offset=-4, font=sub_font)

    # ============================================================
    # FORMATTAZIONE "STICKY" (senza selezione)
    # ============================================================
    def _setup_typing_format_proxy(self, ed):
        orig_name = ed._w + "_orig"
        ed.tk.call("rename", ed._w, orig_name)
        ed.tk.createcommand(
            ed._w, lambda *args, ed=ed, orig=orig_name: self._text_proxy(ed, orig, *args)
        )

    def _text_proxy(self, ed, orig_name, *args):
        is_cursor_insert = (
            args and args[0] == "insert" and len(args) >= 3 and args[1] == "insert"
        )

        try:
            result = ed.tk.call((orig_name,) + args)
        except tk.TclError as e:
            # Il widget Text invoca sé stesso internamente per moltissime operazioni di bookkeeping (es. verificare lo stato del tag
            if is_cursor_insert:
                raise
            return ""

        if is_cursor_insert:
            text = args[2]
            if text:
                try:
                    end_index = ed.index("insert")
                    start_index = ed.index(f"{end_index} - {len(text)}c")
                    self._apply_typing_format(ed, start_index, end_index)
                except tk.TclError:
                    pass

        return result

    def _apply_typing_format(self, ed, start, end):
        pf = self._typing_format
        if pf["bold"] or pf["italic"] or pf["family"] or pf["size"]:
            self._apply_attrs_to_range(
                ed, start, end,
                bold=pf["bold"],
                italic=pf["italic"],
                family=pf["family"],
                size=pf["size"],
            )
        if pf["underline"]:
            ed.tag_add("underline", start, end)
        if pf["strike"]:
            ed.tag_add("strike", start, end)
        if pf["highlight"]:
            tag = f"hl_{pf['highlight']}"
            if tag not in ed.tag_names():
                ed.tag_configure(tag, background=pf["highlight"])
            ed.tag_add(tag, start, end)
        if pf["color"]:
            tag = f"col_{pf['color']}"
            if tag not in ed.tag_names():
                ed.tag_configure(tag, foreground=pf["color"])
            ed.tag_add(tag, start, end)

    def _update_format_buttons(self):
        """Mostra visivamente quali stili sticky sono attivi (bottone premuto)."""
        mapping = {
            "bold": getattr(self, "btn_b", None),
            "italic": getattr(self, "btn_i", None),
            "underline": getattr(self, "btn_u", None),
            "strike": getattr(self, "btn_s", None),
        }
        for key, btn in mapping.items():
            if btn is None:
                continue
            try:
                btn.configure(relief=tk.SUNKEN if self._typing_format.get(key) else tk.FLAT)
            except tk.TclError:
                pass

    def _set_sticky_anchor(self, ed):
        """Ricorda dove si trova il cursore quando viene impostato uno
        sticky format da toolbar/menu senza selezione, così un click di
        rientro nello stesso punto non lo cancella (vedi _sync_typing_format_from_cursor)."""
        try:
            self._sticky_anchor = (ed, ed.index("insert"))
        except tk.TclError:
            self._sticky_anchor = None

    def _reset_typing_format(self):
        for k in self._typing_format:
            self._typing_format[k] = False if k in ("bold", "italic", "underline", "strike") else None
        self._update_format_buttons()

    # ============================================================
    # SISTEMA FONT COMPOSITO
    #   Tag nome: _cf_<family>|<size>|<bold01>|<italic01>
    # ============================================================
    def _composite_tag(self, ed, family, size, bold, italic):
        name = f"_cf_{family}|{int(size)}|{1 if bold else 0}|{1 if italic else 0}"
        if name not in ed.tag_names():
            key = (family, int(size), bool(bold), bool(italic))
            f = self._font_cache.get(key)
            if f is None:
                f = tkfont.Font(
                    family=family, size=int(size),
                    weight=("bold" if bold else "normal"),
                    slant=("italic" if italic else "roman"),
                )
                self._font_cache[key] = f
            ed.tag_configure(name, font=f)
        return name

    def _parse_cf(self, name):
        try:
            body = name[4:]
            family, size, b, i = body.split("|")
            return family, int(size), b == "1", i == "1"
        except Exception:
            return None

    def _get_char_attrs(self, ed, idx):
        family = self.font_family_var.get()
        size = self.font_size_var.get()
        bold = False
        italic = False
        for t in ed.tag_names(idx):
            if t.startswith("_cf_"):
                p = self._parse_cf(t)
                if p:
                    family, size, bold, italic = p
                    break
        return [family, size, bold, italic]

    def _apply_attrs_to_range(self, ed, start, end, *,
                              family=None, size=None, bold=None, italic=None):
        idx = start
        while ed.compare(idx, "<", end):
            nxt = ed.index(f"{idx}+1c")
            a = self._get_char_attrs(ed, idx)
            if family is not None: a[0] = family
            if size   is not None: a[1] = size
            if bold   is not None: a[2] = bold
            if italic is not None: a[3] = italic
            new_tag = self._composite_tag(ed, *a)
            # rimuovi vecchi _cf_ su questo carattere
            for t in ed.tag_names(idx):
                if t.startswith("_cf_") and t != new_tag:
                    ed.tag_remove(t, idx, nxt)
            ed.tag_add(new_tag, idx, nxt)
            idx = nxt
        self.modified = True

    def _save_selection(self):
        """Salva la selezione corrente prima che il Combobox prenda il focus."""
        ed = self._last_focus or self.editor_left
        try:
            self._saved_sel = (ed.index("sel.first"), ed.index("sel.last"))
            self._saved_ed  = ed
        except tk.TclError:
            self._saved_sel = None
            self._saved_ed  = None

    def _save_selection_from(self, ed):
        """Salva la selezione da un editor specifico (usato dalle scorciatoie)."""
        try:
            self._saved_sel = (ed.index("sel.first"), ed.index("sel.last"))
            self._saved_ed  = ed
        except tk.TclError:
            self._saved_sel = None
            self._saved_ed  = None

    def _selection_range(self, ed):
        try:
            first, last = ed.index("sel.first"), ed.index("sel.last")
            if first and last and ed.compare(first, "<", last):
                return first, last
        except tk.TclError:
            pass
        # Fallback: selezione salvata (può succedere quando il Combobox ha il focus)
        if self._saved_sel and self._saved_ed is ed:
            s, e = self._saved_sel
            try:
                if ed.compare(s, "<", e):
                    return self._saved_sel
            except tk.TclError:
                pass
        return None

    def _attr_active_in_selection(self, ed, start, end, attr_idx):
        """True se TUTTI i caratteri della selezione hanno l'attributo attivo."""
        idx = start
        while ed.compare(idx, "<", end):
            a = self._get_char_attrs(ed, idx)
            if not a[attr_idx]:
                return False
            idx = ed.index(f"{idx}+1c")
        return True

    # ----- comandi pubblici -----
    def bold_text(self):
        ed = self.focused_editor()
        sel = self._selection_range(ed)
        if not sel:
            self._typing_format["bold"] = not self._typing_format["bold"]
            self._set_sticky_anchor(ed)
            self._update_format_buttons()
            stato = "attivo" if self._typing_format["bold"] else "disattivato"
            self._flash_status(f"Grassetto {stato} per il testo che scriverai.")
            return
        start, end = sel
        new_val = not self._attr_active_in_selection(ed, start, end, 2)
        self._apply_attrs_to_range(ed, start, end, bold=new_val)

    def italic_text(self):
        ed = self.focused_editor()
        sel = self._selection_range(ed)
        if not sel:
            self._typing_format["italic"] = not self._typing_format["italic"]
            self._set_sticky_anchor(ed)
            self._update_format_buttons()
            stato = "attivo" if self._typing_format["italic"] else "disattivato"
            self._flash_status(f"Corsivo {stato} per il testo che scriverai.")
            return
        start, end = sel
        new_val = not self._attr_active_in_selection(ed, start, end, 3)
        self._apply_attrs_to_range(ed, start, end, italic=new_val)

    def apply_font_family(self):
        ed = self._saved_ed or self.focused_editor()
        sel = self._selection_range(ed)
        if not sel:
            self._typing_format["family"] = self.font_family_var.get()
            self._set_sticky_anchor(ed)
            self._flash_status(f"Font '{self.font_family_var.get()}' attivo per il testo che scriverai.")
            return
        self._apply_attrs_to_range(ed, sel[0], sel[1], family=self.font_family_var.get())
        self._saved_sel = None

    def apply_font_size(self):
        ed = self._saved_ed or self.focused_editor()
        sel = self._selection_range(ed)
        if not sel:
            self._typing_format["size"] = self.font_size_var.get()
            self._set_sticky_anchor(ed)
            self._flash_status(f"Dimensione {self.font_size_var.get()} attiva per il testo che scriverai.")
            return
        start, end = sel
        new_size = self.font_size_var.get()
        idx = start
        while ed.compare(idx, "<", end):
            nxt = ed.index(f"{idx}+1c")
            family, old_size, bold, italic = self._get_char_attrs(ed, idx)
            new_tag = self._composite_tag(ed, family, new_size, bold, italic)
            for t in ed.tag_names(idx):
                if t.startswith("_cf_") and t != new_tag:
                    ed.tag_remove(t, idx, nxt)
            ed.tag_add(new_tag, idx, nxt)
            idx = nxt
        self.modified = True
        self._saved_sel = None


    # ----- toggle semplici (underline/strike/highlight standard) -----
    def _toggle_simple(self, tag):
        ed = self.focused_editor()
        sel = self._selection_range(ed)
        if not sel:
            self._typing_format[tag] = not self._typing_format[tag]
            self._set_sticky_anchor(ed)
            self._update_format_buttons()
            nome = "Sottolineato" if tag == "underline" else "Barrato"
            stato = "attivo" if self._typing_format[tag] else "disattivato"
            self._flash_status(f"{nome} {stato} per il testo che scriverai.")
            return
        start, end = sel
        if tag in ed.tag_names(start):
            ed.tag_remove(tag, start, end)
        else:
            ed.tag_add(tag, start, end)
        self.modified = True

    def underline_text(self): self._toggle_simple("underline")
    def strike_text(self):    self._toggle_simple("strike")

    def superscript_text(self):
        ed = self.focused_editor()
        sel = self._selection_range(ed)
        if not sel: return
        start, end = sel

        # Nota: il conteggio dei caratteri va fatto con ed.count() e non
        # facendo aritmetica sugli indici "riga.colonna" convertiti a float
        # (bug precedente: "1.10" interpretato come 1.10 = 1.1 dava un
        # conteggio sbagliato). Vedi anche subscript_text.
        n_char = ed.count(start, end, "chars")[0]
        all_super = all(
            "superscript" in ed.tag_names(f"{start}+{i}c")
            for i in range(n_char)
        )

        if all_super:
            ed.tag_remove("superscript", start, end)
        else:
            ed.tag_remove("subscript", start, end)
            ed.tag_add("superscript", start, end)

        self.modified = True


    def subscript_text(self):
        ed = self.focused_editor()
        sel = self._selection_range(ed)
        if not sel: return
        start, end = sel

        n_char = ed.count(start, end, "chars")[0]
        all_sub = all(
            "subscript" in ed.tag_names(f"{start}+{i}c")
            for i in range(n_char)
        )

        if all_sub:
            ed.tag_remove("subscript", start, end)
        else:
            ed.tag_remove("superscript", start, end)
            ed.tag_add("subscript", start, end)

        self.modified = True


    # ============================================================
    # CARATTERI SPECIALI
    # ============================================================
    def apri_caratteri_speciali(self):
        win = tk.Toplevel(self.root)
        win.title("Caratteri speciali")
        win.resizable(False, False)
        win.transient(self.root)

        # Notebook con una tab per categoria
        nb = ttk.Notebook(win)
        nb.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        t = THEME_DARK if self._dark_mode else THEME_LIGHT
        ed = self.focused_editor()

        def inserisci(char):
            ed.insert(tk.INSERT, char)
            self.modified = True

        for categoria, chars in SPECIAL_CHARS.items():
            frame = tk.Frame(nb, bg=t["root_bg"])
            nb.add(frame, text=categoria)

            cols = 12
            for idx, ch in enumerate(chars):
                row, col = divmod(idx, cols)
                btn = tk.Button(
                    frame, text=ch, width=3, font=("Arial", 13),
                    relief=tk.FLAT, cursor="hand2",
                    bg=t["button_bg"], fg=t["button_fg"],
                    activebackground=t["editor_sel_bg"],
                    command=lambda c=ch: inserisci(c),
                )
                btn.grid(row=row, column=col, padx=2, pady=2)

        # Barra di ricerca in fondo
        bottom = tk.Frame(win, bg=t["root_bg"])
        bottom.pack(fill=tk.X, padx=8, pady=(0, 8))
        tk.Label(bottom, text="Cerca:", bg=t["root_bg"], fg=t["label_fg"]).pack(side=tk.LEFT)
        cerca_var = tk.StringVar()
        cerca_entry = tk.Entry(bottom, textvariable=cerca_var, width=20)
        cerca_entry.pack(side=tk.LEFT, padx=4)

        risultati_frame = tk.Frame(win, bg=t["root_bg"])
        risultati_frame.pack(fill=tk.X, padx=8, pady=(0, 8))

        def aggiorna_ricerca(*_):
            for w in risultati_frame.winfo_children():
                w.destroy()
            q = cerca_var.get().strip()
            if not q: return
            trovati = [
                ch for chars in SPECIAL_CHARS.values()
                for ch in chars
                if q.lower() in ch.lower()
            ]
            tk.Label(risultati_frame, text="Risultati:", bg=t["root_bg"],
                     fg=t["label_fg"]).pack(side=tk.LEFT)
            for ch in trovati[:30]:
                tk.Button(
                    risultati_frame, text=ch, width=3, font=("Arial", 13),
                    relief=tk.FLAT, cursor="hand2",
                    bg=t["button_bg"], fg=t["button_fg"],
                    activebackground=t["editor_sel_bg"],
                    command=lambda c=ch: inserisci(c),
                ).pack(side=tk.LEFT, padx=2)

        cerca_var.trace_add("write", aggiorna_ricerca)

    # ============================================================
    # INFO / SCORCIATOIE
    # ============================================================
    def mostra_scorciatoie(self):
        """Finestra con l'elenco di tutte le scorciatoie da tastiera
        (vedi Scorciatoie.py per i bind effettivi)."""
        win = tk.Toplevel(self.root)
        win.title("Scorciatoie da tastiera")
        win.resizable(False, False)
        win.transient(self.root)

        t = THEME_DARK if self._dark_mode else THEME_LIGHT
        win.configure(bg=t["root_bg"])

        gruppi = [
            ("File", [
                ("Ctrl+N", "Nuovo file"),
                ("Ctrl+O", "Apri file"),
                ("Ctrl+S", "Salva"),
                ("Ctrl+Shift+S", "Salva con nome"),
            ]),
            ("Modifica", [
                ("Ctrl+C", "Copia"),
                ("Ctrl+V", "Incolla"),
                ("Ctrl+X", "Taglia"),
                ("Ctrl+Z", "Annulla"),
                ("Ctrl+Y", "Ripeti"),
                ("Ctrl+F", "Cerca"),
                ("Ctrl+Shift+O", "Caratteri speciali"),
            ]),
            ("Formattazione", [
                ("Ctrl+B", "Grassetto"),
                ("Ctrl+I", "Corsivo"),
                ("Ctrl+U", "Sottolineato"),
                ("Ctrl+H", "Evidenzia"),
                ("Ctrl+Shift+P", "Rimuovi formattazione"),
                ("Ctrl+Shift+↑", "Apice (superscript)"),
                ("Ctrl+Shift+↓", "Pedice (subscript)"),
            ]),
        ]

        cont = tk.Frame(win, bg=t["root_bg"])
        cont.pack(padx=16, pady=12)

        for titolo, righe in gruppi:
            tk.Label(cont, text=titolo, bg=t["root_bg"], fg=t["label_fg"],
                     font=("TkDefaultFont", 10, "bold")).pack(anchor="w", pady=(8, 2))
            for tasto, descr in righe:
                riga = tk.Frame(cont, bg=t["root_bg"])
                riga.pack(fill=tk.X)
                tk.Label(riga, text=tasto, width=16, anchor="w", bg=t["root_bg"],
                         fg=t["label_fg"], font=("TkFixedFont", 9)).pack(side=tk.LEFT)
                tk.Label(riga, text=descr, anchor="w", bg=t["root_bg"],
                         fg=t["label_fg"]).pack(side=tk.LEFT)

        tk.Button(win, text="Chiudi", relief=tk.FLAT, command=win.destroy).pack(pady=(4, 12))

    # ----- highlight color personalizzato -----
    def apply_highlight(self, color):
        ed = self.focused_editor()
        sel = self._selection_range(ed)
        if not sel:
            self._typing_format["highlight"] = None if self._typing_format["highlight"] == color else color
            self._set_sticky_anchor(ed)
            stato = "disattivato" if self._typing_format["highlight"] is None else "attivo"
            self._flash_status(f"Evidenziatore {stato} per il testo che scriverai.")
            return
        start, end = sel
        tag = f"hl_{color}"
        if tag not in ed.tag_names():
            ed.tag_configure(tag, background=color)
        # rimuovi altri hl_ e l'highlight base
        for t in ed.tag_names():
            if t.startswith("hl_") and t != tag:
                ed.tag_remove(t, start, end)
        ed.tag_remove("highlight", start, end)
        ed.tag_add(tag, start, end)
        self.modified = True

    def remove_highlight(self):
        ed = self.focused_editor()
        sel = self._selection_range(ed)
        if not sel:
            self._typing_format["highlight"] = None
            self._set_sticky_anchor(ed)
            self._flash_status("Evidenziatore disattivato per il testo che scriverai.")
            return
        start, end = sel
        for t in ed.tag_names():
            if t.startswith("hl_") or t == "highlight":
                ed.tag_remove(t, start, end)
        self.modified = True

    # ----- text color -----
    def apply_text_color(self, color):
        ed = self.focused_editor()
        sel = self._selection_range(ed)
        if not sel:
            self._typing_format["color"] = None if self._typing_format["color"] == color else color
            self._set_sticky_anchor(ed)
            stato = "disattivato" if self._typing_format["color"] is None else "attivo"
            self._flash_status(f"Colore testo {stato} per il testo che scriverai.")
            return
        start, end = sel
        tag = f"col_{color}"
        if tag not in ed.tag_names():
            ed.tag_configure(tag, foreground=color)
        for t in ed.tag_names():
            if t.startswith("col_") and t != tag:
                ed.tag_remove(t, start, end)
        ed.tag_add(tag, start, end)
        self.modified = True

    def remove_text_color(self):
        ed = self.focused_editor()
        sel = self._selection_range(ed)
        if not sel:
            self._typing_format["color"] = None
            self._set_sticky_anchor(ed)
            self._flash_status("Colore testo disattivato per il testo che scriverai.")
            return
        start, end = sel
        for t in ed.tag_names():
            if t.startswith("col_"):
                ed.tag_remove(t, start, end)
        self.modified = True

    def set_align(self, align_tag):
        ed = self.focused_editor()
        try:
            start = ed.index("sel.first linestart")
            end = ed.index("sel.last lineend")
        except tk.TclError:
            start = ed.index("insert linestart")
            end = ed.index("insert lineend")
        for t in ALIGN_TAGS:
            ed.tag_remove(t, start, end)
        ed.tag_add(align_tag, start, end)
        self.modified = True

    def clear_formatting(self):
        """Applica la struttura DEFAULT_STYLE: riporta lo stile "sticky" ai
        valori di base (font, dimensione, grassetto, corsivo, sottolineato,
        barrato, colore, evidenziatore) SEMPRE, indipendentemente dal fatto
        che ci sia una selezione. Se in più c'è del testo selezionato, la
        stessa struttura viene applicata anche a quel testo (posizione,
        cioè allineamento e apice/pedice compresi)."""
        ed = self.focused_editor()
        sel = self._selection_range(ed)

        # 1) Stile di base: sempre azzerato ai valori di DEFAULT_STYLE, con o senza selezione.
        self._typing_format.update({
            "bold":      DEFAULT_STYLE["bold"],
            "italic":    DEFAULT_STYLE["italic"],
            "underline": DEFAULT_STYLE["underline"],
            "strike":    DEFAULT_STYLE["strike"],
            "highlight": DEFAULT_STYLE["highlight"],
            "color":     DEFAULT_STYLE["color"],
            "family":    DEFAULT_STYLE["family"],
            "size":      DEFAULT_STYLE["size"],
        })
        self.font_family_var.set(DEFAULT_STYLE["family"])
        self.font_size_var.set(DEFAULT_STYLE["size"])
        self._set_sticky_anchor(ed)
        self._update_format_buttons()

        # 2) Se c'è del testo selezionato, applica lo stesso DEFAULT_STYLE anche lì, invece di limitarsi a rimuovere tag a casaccio.
        if sel:
            start, end = sel

            self._apply_attrs_to_range(
                ed, start, end,
                family=DEFAULT_STYLE["family"], size=DEFAULT_STYLE["size"],
                bold=DEFAULT_STYLE["bold"], italic=DEFAULT_STYLE["italic"],
            )

            ed.tag_remove("underline", start, end)
            ed.tag_remove("strike", start, end)

            for t in ed.tag_names():
                if t.startswith("hl_") or t == "highlight" or t.startswith("col_"):
                    ed.tag_remove(t, start, end)

            # posizione: apice/pedice e allineamento tornano al default
            ed.tag_remove("superscript", start, end)
            ed.tag_remove("subscript", start, end)
            line_start = ed.index(f"{start} linestart")
            line_end = ed.index(f"{end} lineend")
            for t in ALIGN_TAGS:
                ed.tag_remove(t, line_start, line_end)
            ed.tag_add(DEFAULT_STYLE["align"], line_start, line_end)

            self.modified = True
            self._flash_status("Stile predefinito applicato al testo selezionato.")
        else:
            self._flash_status("Stile predefinito attivo per il testo che scriverai.")

    # ============================================================
    # ELENCHI (puntati / numerati)
    # ============================================================
    def _selected_line_numbers(self, ed):
        try:
            start_raw = ed.index("sel.first")
            end_raw = ed.index("sel.last")
            if not start_raw or not end_raw:
                raise tk.TclError("nessuna selezione")
            start_line = int(start_raw.split(".")[0])
            end_line = int(end_raw.split(".")[0])

            if end_raw.split(".")[1] == "0" and end_line > start_line:
                end_line -= 1
        except (tk.TclError, ValueError):
            start_line = end_line = int(ed.index("insert").split(".")[0])
        return list(range(start_line, end_line + 1))

    def toggle_bullet_list(self):
        ed = self.focused_editor()
        lines = self._selected_line_numbers(ed)
        if not lines: return

        first_text = ed.get(f"{lines[0]}.0", f"{lines[0]}.end")
        turn_off = bool(BULLET_RE.match(first_text))

        for n in lines:
            line_start = f"{n}.0"
            text = ed.get(line_start, f"{n}.end")
            if turn_off:
                m = BULLET_RE.match(text)
                if m:
                    ed.delete(line_start, f"{line_start}+{len(m.group(0))}c")
            else:
                m_bul = BULLET_RE.match(text)
                if m_bul:
                    continue  # già puntata
                m_num = NUMBERED_RE.match(text)
                if m_num:
                    ed.delete(line_start, f"{line_start}+{len(m_num.group(0))}c")
                ed.insert(line_start, "- ")

        self.modified = True
        self.update_status()

    def toggle_numbered_list(self):
        ed = self.focused_editor()
        lines = self._selected_line_numbers(ed)
        if not lines: return

        first_text = ed.get(f"{lines[0]}.0", f"{lines[0]}.end")
        turn_off = bool(NUMBERED_RE.match(first_text))
        counter = 1

        for n in lines:
            line_start = f"{n}.0"
            text = ed.get(line_start, f"{n}.end")
            if turn_off:
                m = NUMBERED_RE.match(text)
                if m:
                    ed.delete(line_start, f"{line_start}+{len(m.group(0))}c")
            else:
                m_bul = BULLET_RE.match(text)
                if m_bul:
                    ed.delete(line_start, f"{line_start}+{len(m_bul.group(0))}c")
                    text = ed.get(line_start, f"{n}.end")
                m_num = NUMBERED_RE.match(text)
                if m_num:
                    ed.delete(line_start, f"{line_start}+{len(m_num.group(0))}c")
                ed.insert(line_start, f"{counter}. ")
                counter += 1

        self.modified = True
        self.update_status()

    # ============================================================
    # Nuovo / Apri / Salva
    # ============================================================
    def nuovo_file(self):
        self.root.after(100, self._nuovo_file_dialog)

    def _nuovo_file_dialog(self):
        path = SceltaFile.chiedi_file_salvataggio(
            self.root, self._last_dir,
            filetypes=[("MorNote", "*.mnote"), ("Markdown", "*.md"),
                       ("HTML", "*.html"), ("Testo", "*.txt"), ("Tutti i file", "*.*")],
            defaultextension=".mnote",
            title="Crea nuovo file",
        )
        if not path: return
        self.path = path
        self._last_dir = os.path.dirname(path) or self._last_dir
        self.file_ext = os.path.splitext(path)[1].lower()

        if self.file_ext == ".md":
            contenuto = Logicafunz.template_markdown()
        elif self.file_ext == ".html":
            contenuto = Logicafunz.template_html()
        elif self.file_ext == ".mnote":
            contenuto = Logicafunz.template_mnote()
        else:
            contenuto = ""

        Logicafunz.scrivi_nota(self.path, contenuto)

        self.label_file.config(text=os.path.basename(path))
        self._clear_both_editors()
        if self.file_ext == ".mnote":
            self._carica_mnote_da_stringa(contenuto)
        else:
            self.editor_left.insert("1.0", contenuto)

        self.modified = False
        self.update_status()

    def scegli_file(self):
        self.root.after(100, self._scegli_file_dialog)

    def _scegli_file_dialog(self):
        path = SceltaFile.chiedi_file_apertura(
            self.root, self._last_dir,
            filetypes=[("MorNote", "*.mnote"), ("Markdown", "*.md"),
                       ("HTML", "*.html"), ("Testo", "*.txt"), ("Tutti i file", "*.*")],
            title="Seleziona file",
        )
        if not path: return
        self.path = path
        self._last_dir = os.path.dirname(path) or self._last_dir
        self.file_ext = os.path.splitext(path)[1].lower()
        self.label_file.config(text=os.path.basename(path))
        if self.file_ext == ".mnote":
            self.carica_mnote()
        else:
            self.leggi_nota()
        self.modified = False
        self.update_status()

    def leggi_nota(self):
        if not self.path:
            messagebox.showwarning("Errore", "Seleziona prima un file.")
            return
        if self.file_ext == ".mnote":
            self.carica_mnote(); return

        contenuto = Logicafunz.leggi_nota(self.path)
        self._clear_both_editors()
        self.editor_left.insert(tk.END, contenuto)
        self.update_status()

    def scrivi_nota(self):
        if not self.path:
            self.salva_con_nome(); return

        if self.file_ext == ".mnote":
            left = self._serializza_editor(self.editor_left)
            right = self._serializza_editor(self.editor_right)
            Logicafunz.scrivi_mnote(self.path, left, right)
            self.modified = False
            self._flash_status("File .mnote salvato.")
            return

        contenuto = self.editor_left.get("1.0", tk.END).rstrip("\n")
        Logicafunz.scrivi_nota(self.path, contenuto)
        self.modified = False
        self._flash_status("File salvato.")

    def salva_con_nome(self):
        self.root.after(100, self._salva_con_nome_dialog)

    def _salva_con_nome_dialog(self):
        path = SceltaFile.chiedi_file_salvataggio(
            self.root, self._last_dir,
            filetypes=[("MorNote", "*.mnote"), ("Markdown", "*.md"),
                       ("HTML", "*.html"), ("Testo", "*.txt"), ("Tutti i file", "*.*")],
            defaultextension=self.file_ext if self.file_ext else ".mnote",
            title="Salva con nome",
        )
        if not path: return
        self.path = path
        self._last_dir = os.path.dirname(path) or self._last_dir
        self.file_ext = os.path.splitext(path)[1].lower()
        self.label_file.config(text=os.path.basename(path))
        self.scrivi_nota()

    # ============================================================
    # .mnote – serializza / deserializza con tag
    # ============================================================
    PERSIST_SIMPLE = set(SIMPLE_TAGS) | set(ALIGN_TAGS) | set(SCRIPT_TAGS)

    def _serializza_editor(self, editor):
        text = editor.get("1.0", "end-1c")
        ranges = []
        for tag in editor.tag_names():
            if tag == "sel": continue
            keep = (tag in self.PERSIST_SIMPLE
                    or tag.startswith("_cf_")
                    or tag.startswith("hl_")
                    or tag.startswith("col_"))
            if not keep: continue
            r = editor.tag_ranges(tag)
            for i in range(0, len(r), 2):
                ranges.append({"tag": tag, "start": str(r[i]), "end": str(r[i+1])})
        return {"text": text, "ranges": ranges}

    def _ensure_dynamic_tag(self, editor, tag):
        if tag in editor.tag_names(): return
        if tag in ("superscript", "subscript"):
            self._setup_tags(editor)   # ricrea tutti i tag base inclusi apice/pedice
        elif tag.startswith("_cf_"):
            p = self._parse_cf(tag)
            if p:
                family, size, bold, italic = p
                self._composite_tag(editor, family, size, bold, italic)
        elif tag.startswith("hl_"):
            color = tag[3:]
            editor.tag_configure(tag, background=color)
        elif tag.startswith("col_"):
            color = tag[4:]
            editor.tag_configure(tag, foreground=color)

    def _applica_ranges(self, editor, data):
        editor.delete("1.0", tk.END)
        editor.insert("1.0", data.get("text", ""))
        for rng in data.get("ranges", []):
            tag = rng.get("tag")
            if not tag: continue
            self._ensure_dynamic_tag(editor, tag)
            try:
                editor.tag_add(tag, rng["start"], rng["end"])
            except tk.TclError:
                pass

    def carica_mnote(self):
        left, right = Logicafunz.leggi_mnote(self.path)
        self._clear_both_editors()
        self._applica_ranges(self.editor_left, left)
        self._applica_ranges(self.editor_right, right)

    def _carica_mnote_da_stringa(self, data):
        left, right = Logicafunz.parse_mnote(data)
        self._clear_both_editors()
        self._applica_ranges(self.editor_left, left)
        self._applica_ranges(self.editor_right, right)

    def _clear_both_editors(self):
        self.editor_left.delete("1.0", tk.END)
        self.editor_right.delete("1.0", tk.END)
        self._reset_typing_format()

    # ============================================================
    # COMPILAZIONE → apre nel browser come una pagina web vera
    # ============================================================
    def compila_output(self):
        if not self.path or self.file_ext not in (".md", ".html"):
            messagebox.showinfo("Anteprima",
                "L'anteprima nel browser è disponibile solo per file .md o .html.")
            return

        # Il vecchio file temporaneo (se presente) va ripulito PRIMA di
        # crearne uno nuovo, non alla chiusura dell'app: altrimenti ogni
        # anteprima aggiunge un .html orfano in /tmp (bug segnalato prima).
        self._rimuovi_tmp_html()

        if self.file_ext == ".md":
            testo = self.editor_left.get("1.0", tk.END)
            tmp_md = tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", suffix=".md", delete=False)
            tmp_md.write(testo); tmp_md.close()
            try:
                html_body = compila_markdown(tmp_md.name)
            finally:
                try: os.remove(tmp_md.name)
                except OSError: pass

            html_doc = self._wrap_html(html_body, os.path.basename(self.path))
            tmp_html = tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", suffix=".html", delete=False)
            tmp_html.write(html_doc); tmp_html.close()
            self._tmp_html_path = tmp_html.name
            webbrowser.open(f"file://{os.path.abspath(tmp_html.name)}")
            self._flash_status("Anteprima aperta nel browser.")

        elif self.file_ext == ".html":
            # salva su disco e apri il file vero
            contenuto = self.editor_left.get("1.0", tk.END)
            Logicafunz.scrivi_nota(self.path, contenuto)
            webbrowser.open(f"file://{os.path.abspath(self.path)}")
            self._flash_status("Pagina HTML aperta nel browser.")

    def _wrap_html(self, body, title):
        return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Roboto, sans-serif;
          max-width: 820px; margin: 2em auto; padding: 0 1em; line-height: 1.6;
          color: #222; }}
  h1, h2, h3 {{ color: #1a1a1a; }}
  code, pre {{ background: #f4f4f4; padding: 2px 6px; border-radius: 4px; }}
  pre {{ padding: 12px; overflow-x: auto; }}
  blockquote {{ border-left: 4px solid #ccc; margin: 0; padding: 0 1em; color: #555; }}
  table {{ border-collapse: collapse; }} td, th {{ border: 1px solid #ccc; padding: 4px 8px; }}
</style>
</head>
<body>
{body}
</body>
</html>"""

    # ============================================================
    # Status bar + ricerca
    # ============================================================
    def update_status(self, event=None):
        ed = self.focused_editor()
        try:
            row, col = ed.index(tk.INSERT).split(".")
        except Exception:
            row, col = "1", "0"
        nome = os.path.basename(self.path) if self.path else "nessun file"
        ext = self.file_ext if self.file_ext else ""
        mod = " ●" if self.modified else ""
        which = "SX" if ed is self.editor_left else "DX"
        self.status.config(text=f"{nome} {ext}{mod}   [{which}]   riga:{row}  col:{col}")

    def _flash_status(self, msg):
        original = self.status.cget("text")
        self.status.config(text=msg)
        self.root.after(2000, lambda: self.status.config(text=original))
        self.update_status()

    def apri_ricerca(self):
        finestra = tk.Toplevel(self.root)
        finestra.title("Cerca")
        finestra.geometry("300x110")
        finestra.transient(self.root)

        tk.Label(finestra, text="Testo da cercare:").pack(pady=4)
        entry = tk.Entry(finestra, width=35)
        entry.pack()
        entry.focus_set()

        def cerca():
            ed = self.focused_editor()
            ed.tag_remove("found", "1.0", tk.END)
            testo = entry.get()
            if not testo: return
            start = "1.0"; count = 0
            while True:
                pos = ed.search(testo, start, stopindex=tk.END, nocase=True)
                if not pos: break
                end = f"{pos}+{len(testo)}c"
                ed.tag_add("found", pos, end)
                start = end; count += 1
            ed.tag_config("found", background="#ffe082")
            self._flash_status(f"{count} risultati")

        tk.Button(finestra, text="Cerca", command=cerca).pack(pady=4)
        entry.bind("<Return>", lambda e: cerca())


class ToolTip:
    """Tooltip minimale in puro Tkinter (nessuna dipendenza esterna): mostra
    una piccola etichetta gialla vicino al puntatore dopo un breve indugio
    sul widget, per suggerire cosa fa un pulsante-icona senza dover leggere
    una scritta permanente in barra."""

    _RITARDO_MS = 500

    def __init__(self, widget, testo):
        self.widget = widget
        self.testo = testo
        self._after_id = None
        self._finestra = None
        widget.bind("<Enter>", self._pianifica, add="+")
        widget.bind("<Leave>", self._nascondi, add="+")
        widget.bind("<ButtonPress>", self._nascondi, add="+")

    def _pianifica(self, _event=None):
        self._annulla()
        self._after_id = self.widget.after(self._RITARDO_MS, self._mostra)

    def _annulla(self):
        if self._after_id is not None:
            try:
                self.widget.after_cancel(self._after_id)
            except tk.TclError:
                pass
            self._after_id = None

    def _mostra(self):
        if self._finestra is not None:
            return
        try:
            x = self.widget.winfo_rootx() + 12
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        except tk.TclError:
            return
        self._finestra = tk.Toplevel(self.widget)
        self._finestra.wm_overrideredirect(True)
        self._finestra.wm_geometry(f"+{x}+{y}")
        tk.Label(
            self._finestra, text=self.testo, justify=tk.LEFT,
            background="#ffffe0", foreground="#333333",
            relief=tk.SOLID, borderwidth=1, font=("TkDefaultFont", 9),
            padx=6, pady=2,
        ).pack()

    def _nascondi(self, _event=None):
        self._annulla()
        if self._finestra is not None:
            self._finestra.destroy()
            self._finestra = None


if __name__ == "__main__":
    root = tk.Tk()
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
    try:
        root.iconphoto(True, tk.PhotoImage(file=logo_path))
    except tk.TclError:
        pass
    app = MorNoteGUI(root)
    root.mainloop()