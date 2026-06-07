import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, font as tkfont, ttk, colorchooser
from markdowncompiler import compila_markdown
import Logicafunz
import Scorciatoie
import os
import platform
import tempfile
import webbrowser


# Tag booleani "semplici" (non toccano il font)
SIMPLE_TAGS = ("underline", "strike", "highlight")
ALIGN_TAGS = ("align_left", "align_center", "align_right")
SCRIPT_TAGS = ("superscript", "subscript")   # apice / pedice

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
        "«", "»", "‹", "›", "„", """, """, "'", "'", "…", "–", "—",
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
    "sep_color":      "#555555",
    "paned_bg":       "#3c3c3c",
    "menu_bg":        "#2d2d2d",
    "menu_fg":        "#d4d4d4",
}


class MorNoteGUI:
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

        # massimizza
        try:
            if platform.system() == "Windows":
                self.root.state("zoomed")
            else:
                self.root.attributes("-zoomed", True)
        except tk.TclError:
            self.root.geometry("1200x700")
        self.root.minsize(800, 500)

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
        menu_formato.add_command(label="Rimuovi formattazione", command=self.clear_formatting)
        menubar.add_cascade(label="Formato", menu=menu_formato)

        menu_visualizza = tk.Menu(menubar, tearoff=0)
        self._dark_mode_var = tk.BooleanVar(value=False)
        menu_visualizza.add_checkbutton(label="Tema scuro", variable=self._dark_mode_var,
                                        command=self.toggle_tema)
        menubar.add_cascade(label="Visualizza", menu=menu_visualizza)

        self.root.config(menu=menubar)

        # ===== TOOLBAR =====
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        toolbar.pack(fill=tk.X)
        self._theme_widgets.append((toolbar, "toolbar_bg"))

        # font family
        self.font_family_var = tk.StringVar(value=DEFAULT_FAMILY)
        family_cb = ttk.Combobox(toolbar, textvariable=self.font_family_var,
                                 values=FONT_FAMILIES, width=18, state="readonly")
        family_cb.pack(side=tk.LEFT, padx=4, pady=3)
        family_cb.bind("<ButtonPress-1>", lambda e: self._save_selection())
        family_cb.bind("<<ComboboxSelected>>", lambda e: self.apply_font_family())

        # font size
        self.font_size_var = tk.IntVar(value=DEFAULT_SIZE)
        size_cb = ttk.Combobox(toolbar, textvariable=self.font_size_var,
                               values=FONT_SIZES, width=4, state="readonly")
        size_cb.pack(side=tk.LEFT, padx=4, pady=3)
        size_cb.bind("<ButtonPress-1>", lambda e: self._save_selection())
        size_cb.bind("<<ComboboxSelected>>", lambda e: self.apply_font_size())
        size_cb.bind("Button-1", lambda e: "break")
        size_cb.bind("<ButtonRelease-1>", lambda e: self.apply_font_size())

        def sep():
            tk.Frame(toolbar, width=2, bg="#bbb").pack(side=tk.LEFT, fill=tk.Y, padx=4, pady=4)

        sep()
        btn_b = tk.Button(toolbar, text="B", width=2, font=("TkDefaultFont", 10, "bold"),   command=self.bold_text)
        btn_i = tk.Button(toolbar, text="I", width=2, font=("TkDefaultFont", 10, "italic"),  command=self.italic_text)
        btn_u = tk.Button(toolbar, text="U", width=2, font=("TkDefaultFont", 10, "underline"), command=self.underline_text)
        btn_s = tk.Button(toolbar, text="S", width=2, font=("TkDefaultFont", 10, "overstrike"), command=self.strike_text)
        for b in (btn_b, btn_i, btn_u, btn_s):
            b.pack(side=tk.LEFT, padx=1)
            self._theme_widgets.append((b, "button"))

        sep()
        # Evidenziatore con palette
        self._build_color_menu(toolbar, "🖍", HIGHLIGHT_PALETTE,
                               self.apply_highlight, self.remove_highlight, "Evidenzia")
        # Colore testo con palette
        self._build_color_menu(toolbar, "A▾", TEXT_COLOR_PALETTE,
                               self.apply_text_color, self.remove_text_color, "Colore testo")

        sep()
        btn_al = tk.Button(toolbar, text="⟸", width=2, command=lambda: self.set_align("align_left"))
        btn_ac = tk.Button(toolbar, text="≡",  width=2, command=lambda: self.set_align("align_center"))
        btn_ar = tk.Button(toolbar, text="⟹", width=2, command=lambda: self.set_align("align_right"))
        for b in (btn_al, btn_ac, btn_ar):
            b.pack(side=tk.LEFT, padx=1)
            self._theme_widgets.append((b, "button"))

        sep()
        btn_pulisci = tk.Button(toolbar, text="Pulisci stile", command=self.clear_formatting)
        btn_pulisci.pack(side=tk.LEFT, padx=4)
        self._theme_widgets.append((btn_pulisci, "button"))

        sep()
        btn_sup = tk.Button(toolbar, text="x²", width=3, command=self.superscript_text)
        btn_sub = tk.Button(toolbar, text="x₂", width=3, command=self.subscript_text)
        for b in (btn_sup, btn_sub):
            b.pack(side=tk.LEFT, padx=1)
            self._theme_widgets.append((b, "button"))

        sep()
        btn_special = tk.Button(toolbar, text="Ω", width=3, command=self.apri_caratteri_speciali)
        btn_special.pack(side=tk.LEFT, padx=4)
        self._theme_widgets.append((btn_special, "button"))

        # selezione file + azioni
        top_frame = tk.Frame(root)
        top_frame.pack(fill=tk.X, pady=4)
        self._theme_widgets.append((top_frame, "top_frame_bg"))
        btn_apri      = tk.Button(top_frame, text="Apri", command=self.scegli_file)
        btn_nuovo     = tk.Button(top_frame, text="Nuovo", command=self.nuovo_file)
        btn_salva     = tk.Button(top_frame, text="Salva", command=self.scrivi_nota)
        btn_salva_cn  = tk.Button(top_frame, text="Salva con nome", command=self.salva_con_nome)
        btn_anteprima = tk.Button(top_frame, text="Apri anteprima (browser)", command=self.compila_output)
        for b in (btn_apri, btn_nuovo, btn_salva, btn_salva_cn, btn_anteprima):
            b.pack(side=tk.LEFT, padx=4)
            self._theme_widgets.append((b, "button"))
        self.label_file = tk.Label(top_frame, text="Nessun file selezionato")
        self.label_file.pack(side=tk.LEFT, padx=10)
        self._theme_widgets.append((self.label_file, "label_left_bg"))

        # ===== EDITOR DOPPIO =====
        self.paned = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        self.paned.pack(fill=tk.BOTH, expand=True)
        self._theme_widgets.append((self.paned, "paned_bg"))

        left_frame = tk.Frame(self.paned)
        self._label_left = tk.Label(left_frame, text="Storia (sinistra)", anchor="w", bg="#e8e8f0")
        self._label_left.pack(fill=tk.X)
        self._theme_widgets.append((left_frame,        "toolbar_bg"))
        self._theme_widgets.append((self._label_left,  "label_left"))
        self.editor_left = scrolledtext.ScrolledText(
            left_frame, undo=True, wrap="word",
            font=(DEFAULT_FAMILY, DEFAULT_SIZE)
        )
        self.editor_left.pack(fill=tk.BOTH, expand=True)
        self.paned.add(left_frame, minsize=200)

        right_frame = tk.Frame(self.paned)
        self._label_right = tk.Label(right_frame, text="Appunti partita (destra)", anchor="w", bg="#f0e8e8")
        self._label_right.pack(fill=tk.X)
        self._theme_widgets.append((right_frame,        "toolbar_bg"))
        self._theme_widgets.append((self._label_right,  "label_right"))
        self.editor_right = scrolledtext.ScrolledText(
            right_frame, undo=True, wrap="word",
            font=(DEFAULT_FAMILY, DEFAULT_SIZE)
        )
        self.editor_right.pack(fill=tk.BOTH, expand=True)
        self.paned.add(right_frame, minsize=200)

        # cache dei Font objects per i tag compositi
        self._font_cache = {}

        # selezione salvata prima che il Combobox rubi il focus
        self._saved_sel = None   # (start, end) | None
        self._saved_ed  = None   # editor a cui appartiene la selezione

        self._last_focus = self.editor_left
        for ed in (self.editor_left, self.editor_right):
            ed.bind("<FocusIn>", self._on_focus_in)
            ed.bind("<KeyRelease>", self._on_key_release)
            ed.bind("<ButtonRelease>", self.update_status)
            self._setup_tags(ed)

        # status bar
        self.status = tk.Label(self.root, text="Pronto", anchor="w", relief=tk.SUNKEN)
        self.status.pack(fill=tk.X, side=tk.BOTTOM)
        self._theme_widgets.append((self.status, "status"))

        Scorciatoie.bind_shortcuts(self.root, self.editor_left, self.editor_right, self)
        self.update_status()

    # ============================================================
    # Toolbar: menu colori
    # ============================================================
    def _build_color_menu(self, parent, label, palette, on_pick, on_clear, title):
        mb = tk.Menubutton(parent, text=label, relief=tk.RAISED, padx=4)
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

    def _on_key_release(self, event=None):
        self.modified = True
        self.update_status(event)

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
                                     activeforeground=t["button_fg"])
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
        # Prima prova la selezione live
        try:
            return ed.index("sel.first"), ed.index("sel.last")
        except tk.TclError:
            pass
        # Fallback: selezione salvata (può succedere quando il Combobox ha il focus)
        if self._saved_sel and self._saved_ed is ed:
            return self._saved_sel
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
        if not sel: return
        start, end = sel
        new_val = not self._attr_active_in_selection(ed, start, end, 2)
        self._apply_attrs_to_range(ed, start, end, bold=new_val)

    def italic_text(self):
        ed = self.focused_editor()
        sel = self._selection_range(ed)
        if not sel: return
        start, end = sel
        new_val = not self._attr_active_in_selection(ed, start, end, 3)
        self._apply_attrs_to_range(ed, start, end, italic=new_val)

    def apply_font_family(self):
        ed = self._saved_ed or self.focused_editor()
        sel = self._selection_range(ed)
        if not sel:
            return
        self._apply_attrs_to_range(ed, sel[0], sel[1], family=self.font_family_var.get())
        self._saved_sel = None

    def apply_font_size(self):
        ed = self._saved_ed or self.focused_editor()
        sel = self._selection_range(ed)
        if not sel:
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
        if not sel: return
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

        all_super = all(
            "superscript" in ed.tag_names(ed.index(f"{start}+{i}c"))
            for i in range(int(float(ed.index(end))) - int(float(ed.index(start))) + 1)
            if ed.compare(f"{start}+{i}c", "<", end)
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
    
        all_sub = all(
            "subscript" in ed.tag_names(ed.index(f"{start}+{i}c"))
            for i in range(int(float(ed.index(end))) - int(float(ed.index(start))) + 1)
            if ed.compare(f"{start}+{i}c", "<", end)
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

    # ----- highlight color personalizzato -----
    def apply_highlight(self, color):
        ed = self.focused_editor()
        sel = self._selection_range(ed)
        if not sel: return
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
        if not sel: return
        start, end = sel
        for t in ed.tag_names():
            if t.startswith("hl_") or t == "highlight":
                ed.tag_remove(t, start, end)
        self.modified = True

    # ----- text color -----
    def apply_text_color(self, color):
        ed = self.focused_editor()
        sel = self._selection_range(ed)
        if not sel: return
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
        if not sel: return
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
        ed = self.focused_editor()
        sel = self._selection_range(ed)
        if not sel: return
        start, end = sel
        for t in ed.tag_names():
            if t == "sel": continue
            ed.tag_remove(t, start, end)
        self.modified = True

    # ============================================================
    # Nuovo / Apri / Salva
    # ============================================================
    def nuovo_file(self):
        self.root.after(100, self._nuovo_file_dialog)

    def _nuovo_file_dialog(self):
        path = filedialog.asksaveasfilename(
            parent=self.root,
            title="Crea nuovo file", defaultextension=".mnote",
            filetypes=[("MorNote", "*.mnote"), ("Markdown", "*.md"),
                       ("HTML", "*.html"), ("Testo", "*.txt"), ("Tutti i file", "*.*")],
        )
        if not path: return
        self.path = path
        self.file_ext = os.path.splitext(path)[1].lower()

        if self.file_ext == ".md":
            contenuto = Logicafunz.template_markdown()
        elif self.file_ext == ".html":
            contenuto = Logicafunz.template_html()
        elif self.file_ext == ".mnote":
            contenuto = Logicafunz.template_mnote()
        else:
            contenuto = ""

        with open(self.path, "w", encoding="utf-8") as f:
            f.write(contenuto)

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
        path = filedialog.askopenfilename(
            parent=self.root,
            title="Seleziona file",
            filetypes=[("MorNote", "*.mnote"), ("Markdown", "*.md"),
                       ("HTML", "*.html"), ("Testo", "*.txt"), ("Tutti i file", "*.*")],
        )
        if not path: return
        self.path = path
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
            data = Logicafunz.serializza_mnote(left, right)
            with open(self.path, "w", encoding="utf-8") as f:
                f.write(data)
            self.modified = False
            self._flash_status("File .mnote salvato.")
            return

        contenuto = self.editor_left.get("1.0", tk.END).rstrip("\n")
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(contenuto)
        self.modified = False
        self._flash_status("File salvato.")

    def salva_con_nome(self):
        self.root.after(100, self._salva_con_nome_dialog)

    def _salva_con_nome_dialog(self):
        path = filedialog.asksaveasfilename(
            parent=self.root,
            title="Salva con nome",
            defaultextension=self.file_ext if self.file_ext else ".mnote",
            filetypes=[("MorNote", "*.mnote"), ("Markdown", "*.md"),
                       ("HTML", "*.html"), ("Testo", "*.txt"), ("Tutti i file", "*.*")],
        )
        if not path: return
        self.path = path
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
        with open(self.path, "r", encoding="utf-8") as f:
            data = f.read()
        self._carica_mnote_da_stringa(data)

    def _carica_mnote_da_stringa(self, data):
        left, right = Logicafunz.parse_mnote(data)
        self._clear_both_editors()
        self._applica_ranges(self.editor_left, left)
        self._applica_ranges(self.editor_right, right)

    def _clear_both_editors(self):
        self.editor_left.delete("1.0", tk.END)
        self.editor_right.delete("1.0", tk.END)

    # ============================================================
    # COMPILAZIONE → apre nel browser come una pagina web vera
    # ============================================================
    def compila_output(self):
        if not self.path or self.file_ext not in (".md", ".html"):
            messagebox.showinfo("Anteprima",
                "L'anteprima nel browser è disponibile solo per file .md o .html.")
            return

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
            webbrowser.open(f"file://{os.path.abspath(tmp_html.name)}")
            self._flash_status("Anteprima aperta nel browser.")

        elif self.file_ext == ".html":
            # salva su disco e apri il file vero
            contenuto = self.editor_left.get("1.0", tk.END)
            with open(self.path, "w", encoding="utf-8") as f:
                f.write(contenuto)
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


if __name__ == "__main__":
    root = tk.Tk()
    root.iconphoto(True, tk.PhotoImage(file = "logo.png"))
    app = MorNoteGUI(root)
    root.mainloop()