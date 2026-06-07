def compila_markdown(path):
    with open(path, "r", encoding="utf-8") as f:
        righe = f.readlines()

    output = []
    in_lista = False

    for riga in righe:
        riga = riga.rstrip("\n")

        # immagini
        if riga.startswith("!"):
            try:
                alt = riga.split("[", 1)[1].split("]", 1)[0]
                url = riga.split("(", 1)[1].split(")", 1)[0]
                output.append(f"<img src='{url}' alt='{alt}'>")
                continue
            except Exception:
                pass

        # liste
        if riga.startswith("- "):
            if not in_lista:
                output.append("<ul>")
                in_lista = True
            contenuto = riga[2:]
            output.append(f"<li>{contenuto}</li>")
            continue
        else:
            if in_lista:
                output.append("</ul>")
                in_lista = False

        # titoli
        if riga.startswith("#### "):
            output.append(f"<h4>{riga[5:]}</h4>"); continue
        if riga.startswith("### "):
            output.append(f"<h3>{riga[4:]}</h3>"); continue
        if riga.startswith("## "):
            output.append(f"<h2>{riga[3:]}</h2>"); continue
        if riga.startswith("# "):
            output.append(f"<h1>{riga[2:]}</h1>"); continue

        # link
        if "[" in riga and "]" in riga and "(" in riga and ")" in riga:
            try:
                testo = riga.split("[", 1)[1].split("]", 1)[0]
                url = riga.split("(", 1)[1].split(")", 1)[0]
                riga = riga.replace(f"[{testo}]({url})", f"<a href='{url}'>{testo}</a>")
            except Exception:
                pass

        # grassetto
        while "**" in riga:
            parts = riga.split("**", 2)
            if len(parts) < 3:
                break
            riga = f"{parts[0]}<strong>{parts[1]}</strong>{parts[2]}"

        # corsivo
        while "*" in riga:
            parts = riga.split("*", 2)
            if len(parts) < 3:
                break
            riga = f"{parts[0]}<em>{parts[1]}</em>{parts[2]}"

        if riga.strip():
            output.append(f"<p>{riga}</p>")

    if in_lista:
        output.append("</ul>")

    return "\n".join(output)
