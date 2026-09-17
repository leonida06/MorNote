"""
Dialoghi Apri/Salva scritti interamente in Tkinter, per sostituire quelli
nativi del sistema. Il motivo: sui dialoghi nativi GTK la barra dei
percorsi (breadcrumb) resta aperta solo finché si tiene premuto il tasto
del mouse. Qui invece ogni cartella si apre con un singolo click e resta
aperta finché non se ne sceglie un'altra, come un normale elenco.
"""

import os
import tkinter as tk


class _FileDialog(tk.Toplevel):
    def __init__(self, parent, initialdir, filetypes, title, mode, defaultextension=""):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.geometry("560x420")
        self.minsize(420, 300)

        self.mode = mode  # "open" oppure "save"
        self.filetypes = filetypes or []
        self.defaultextension = defaultextension
        self.result = None
        self.current_dir = initialdir if initialdir and os.path.isdir(initialdir) else os.path.expanduser("~")
        self._voci_correnti = []
        # Indice dell'ultima voce scelta. Serve come rete di sicurezza: vedi
        # _voce_selezionata() e la nota su exportselection più sotto.
        self._ultima_sel = None

        # ---- barra percorso ----
        top = tk.Frame(self)
        top.pack(fill=tk.X, padx=6, pady=6)
        tk.Button(top, text="⬆ Su", command=self._sali).pack(side=tk.LEFT)
        self.path_var = tk.StringVar()
        path_entry = tk.Entry(top, textvariable=self.path_var)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
        path_entry.bind("<Return>", lambda e: self._vai_a_percorso())
        tk.Button(top, text="Vai", command=self._vai_a_percorso).pack(side=tk.LEFT)

        # ---- lista cartelle/file ----
        list_frame = tk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # exportselection=False è ESSENZIALE: con il valore predefinito (True) la
        # selezione della Listbox è legata alla selezione PRIMARY di X11, quindi
        # appena un altro widget la prende (un click nella barra del percorso, o
        # del testo selezionato negli editor della finestra principale) la riga
        # evidenziata qui viene azzerata di nascosto. Il risultato era che
        # curselection() tornava vuota, _conferma() usciva subito e il file non
        # veniva mai aperto: l'app sembrava mostrare un documento vuoto.
        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                  activestyle="none", exportselection=False)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)
        self.listbox.bind("<Double-Button-1>", self._on_double_click)
        self.listbox.bind("<Return>", self._on_double_click)

        # ---- nome file (solo per "salva con nome") ----
        self.filename_var = tk.StringVar()
        if mode == "save":
            bottom = tk.Frame(self)
            bottom.pack(fill=tk.X, padx=6, pady=(0, 6))
            tk.Label(bottom, text="Nome file:").pack(side=tk.LEFT)
            fname_entry = tk.Entry(bottom, textvariable=self.filename_var)
            fname_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
            fname_entry.bind("<Return>", lambda e: self._conferma())

        # ---- pulsanti ----
        btns = tk.Frame(self)
        btns.pack(fill=tk.X, padx=6, pady=(0, 6))
        etichetta_ok = "Salva" if mode == "save" else "Apri"
        tk.Button(btns, text=etichetta_ok, command=self._conferma).pack(side=tk.RIGHT, padx=4)
        tk.Button(btns, text="Annulla", command=self._annulla).pack(side=tk.RIGHT)

        self.protocol("WM_DELETE_WINDOW", self._annulla)
        self.bind("<Escape>", lambda e: self._annulla())

        self._aggiorna_lista()

        # Grab modale rimandato: su alcuni window manager un grab immediato
        # su una finestra non ancora "mappata" solleva TclError.
        self.after(10, self._grab_modale)

        self.wait_window(self)

    def _grab_modale(self):
        try:
            self.grab_set()
        except tk.TclError:
            pass

    # ---------------------------------------------------------------
    def _estensioni_ammesse(self):
        """Ritorna un set di estensioni tipo {'.md', '.mnote'} oppure
        None se tra i filtri è presente '*.*' (nessun filtro: mostra tutto,
        replicando il comportamento del dialogo nativo con 'Tutti i file')."""
        estensioni = set()
        for _label, pattern in self.filetypes:
            for p in pattern.split():
                if p == "*.*":
                    return None
                if p.startswith("*."):
                    estensioni.add(p[1:].lower())
        return estensioni or None

    def _aggiorna_lista(self):
        self.path_var.set(self.current_dir)
        self.listbox.delete(0, tk.END)
        try:
            voci = sorted(os.listdir(self.current_dir), key=str.lower)
        except OSError:
            voci = []

        estensioni = self._estensioni_ammesse()
        cartelle, file_validi = [], []
        for v in voci:
            if v.startswith("."):
                continue
            full = os.path.join(self.current_dir, v)
            if os.path.isdir(full):
                cartelle.append(v)
            elif estensioni is None or os.path.splitext(v)[1].lower() in estensioni:
                file_validi.append(v)

        self._ultima_sel = None   # cambiata cartella: la vecchia scelta non vale più
        self._voci_correnti = []
        for c in cartelle:
            self.listbox.insert(tk.END, f"\U0001F4C1  {c}")
            self._voci_correnti.append((c, True))
        for f in file_validi:
            self.listbox.insert(tk.END, f"      {f}")
            self._voci_correnti.append((f, False))

    def _sali(self):
        parent = os.path.dirname(self.current_dir.rstrip(os.sep))
        if parent and os.path.isdir(parent) and parent != self.current_dir:
            self.current_dir = parent
            self._aggiorna_lista()

    def _vai_a_percorso(self):
        p = os.path.expanduser(self.path_var.get().strip())
        if os.path.isdir(p):
            self.current_dir = p
            self._aggiorna_lista()

    def _voce_selezionata(self):
        """Ritorna (nome, is_dir) della voce scelta, oppure None.
        Prova prima la selezione attuale della Listbox e, se questa risulta
        vuota, ricade sull'ultimo indice scelto dall'utente: così un click
        altrove non fa 'dimenticare' al dialogo quale file era stato scelto."""
        sel = self.listbox.curselection()
        idx = sel[0] if sel else self._ultima_sel
        if idx is None or idx >= len(self._voci_correnti):
            return None
        return self._voci_correnti[idx]

    def _on_select(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        self._ultima_sel = sel[0]
        nome, is_dir = self._voci_correnti[sel[0]]
        if not is_dir and self.mode == "save":
            self.filename_var.set(nome)

    def _on_double_click(self, event=None):
        voce = self._voce_selezionata()
        if voce is None:
            return
        nome, is_dir = voce
        if is_dir:
            self.current_dir = os.path.join(self.current_dir, nome)
            self._aggiorna_lista()
        elif self.mode == "open":
            self.result = os.path.join(self.current_dir, nome)
            self._annulla_grab_e_chiudi()

    def _conferma(self):
        if self.mode == "save":
            nome = self.filename_var.get().strip()
            if not nome:
                return
            if self.defaultextension and not os.path.splitext(nome)[1]:
                nome += self.defaultextension
            self.result = os.path.join(self.current_dir, nome)
            self._annulla_grab_e_chiudi()
            return

        voce = self._voce_selezionata()
        if voce is None:
            # Nessuna riga scelta: se nella barra del percorso c'è un file
            # valido, apri quello invece di non fare assolutamente nulla
            # (prima il pulsante "Apri" sembrava semplicemente non rispondere).
            p = os.path.expanduser(self.path_var.get().strip())
            if os.path.isfile(p):
                self.result = p
                self._annulla_grab_e_chiudi()
            return
        nome, is_dir = voce
        if is_dir:
            self.current_dir = os.path.join(self.current_dir, nome)
            self._aggiorna_lista()
            return
        self.result = os.path.join(self.current_dir, nome)
        self._annulla_grab_e_chiudi()

    def _annulla(self):
        self.result = None
        self._annulla_grab_e_chiudi()

    def _annulla_grab_e_chiudi(self):
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()


def chiedi_file_apertura(parent, initialdir, filetypes, title="Seleziona file"):
    dlg = _FileDialog(parent, initialdir, filetypes, title, mode="open")
    return dlg.result


def chiedi_file_salvataggio(parent, initialdir, filetypes, defaultextension, title="Salva con nome"):
    dlg = _FileDialog(parent, initialdir, filetypes, title, mode="save", defaultextension=defaultextension)
    return dlg.result