def bind_shortcuts(root, editor_left, editor_right, app):
    editors = (editor_left, editor_right)

    def _run(ed, fn):
        """Imposta il focus sull'editor corretto, salva la selezione, chiama fn."""
        app._last_focus = ed          # focused_editor() ritorna l'editor giusto
        app._save_selection_from(ed)  # salva sel prima che la shortcut la perda
        fn()
        return "break"

    # ---------- clipboard ----------
    root.bind_all("<Control-c>", lambda e: app.focused_editor().event_generate("<<Copy>>"))
    root.bind_all("<Control-v>", lambda e: app.focused_editor().event_generate("<<Paste>>"))
    root.bind_all("<Control-x>", lambda e: app.focused_editor().event_generate("<<Cut>>"))

    # ---------- file ----------
    root.bind_all("<Control-s>",       lambda e: app.scrivi_nota())
    root.bind_all("<Control-Shift-S>", lambda e: app.salva_con_nome())
    root.bind_all("<Control-n>",       lambda e: app.nuovo_file())
    root.bind_all("<Control-o>",       lambda e: app.scegli_file())

    # ---------- undo/redo ----------
    root.bind_all("<Control-z>", lambda e: app.focused_editor().event_generate("<<Undo>>"))
    root.bind_all("<Control-y>", lambda e: app.focused_editor().event_generate("<<Redo>>"))

    # ---------- ricerca / caratteri speciali ----------
    root.bind_all("<Control-f>",       lambda e: app.apri_ricerca())
    root.bind_all("<Control-Shift-O>", lambda e: app.apri_caratteri_speciali())

    # ---------- formattazione: bind sugli editor con "break" ----------
    for ed in editors:
        ed.bind("<Control-b>",         lambda e: _run(e.widget, app.bold_text))
        ed.bind("<Control-i>",         lambda e: _run(e.widget, app.italic_text))
        ed.bind("<Control-u>",         lambda e: _run(e.widget, app.underline_text))
        ed.bind("<Control-h>",         lambda e: _run(e.widget, app.highlight_text))
        ed.bind("<Control-Shift-p>",   lambda e: _run(e.widget, app.clear_formatting))
        ed.bind("<Control-Shift-Up>",  lambda e: _run(e.widget, app.superscript_text))
        ed.bind("<Control-Shift-Down>",lambda e: _run(e.widget, app.subscript_text))