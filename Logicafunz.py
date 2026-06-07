import os
import json

# ---------- I/O base ----------
def leggi_nota(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def scrivi_nota(path, contenuto):
    with open(path, "w", encoding="utf-8") as f:
        f.write(contenuto)

# ---------- Template ----------
def template_markdown():
    return "# Nuovo documento Markdown\n\nScrivi qui..."

def template_html():
    return "<!DOCTYPE html>\n<html>\n<body>\n\n<p>Nuovo documento HTML</p>\n\n</body>\n</html>"

def template_mnote():
    # Nuovo template vuoto in formato ricco (JSON)
    return serializza_mnote(
        {"text": "", "ranges": []},
        {"text": "", "ranges": []},
    )

# ---------- Formato .mnote ricco ----------
# Struttura:
# {
#   "version": 2,
#   "sinistra": {"text": "...", "ranges": [{"tag": "bold", "start": "1.0", "end": "1.4"}, ...]},
#   "destra":   {"text": "...", "ranges": [...]}
# }
#
# tag supportati: bold, italic, underline, strike, highlight,
#                 align_left, align_center, align_right,
#                 size_<n>  (es. size_18),
#                 font_<nome>  (es. font_Arial)

MNOTE_MAGIC = "MNOTE_JSON_V2"

def serializza_mnote(left, right):
    payload = {
        "version": 2,
        "sinistra": left,
        "destra": right,
    }
    return MNOTE_MAGIC + "\n" + json.dumps(payload, ensure_ascii=False, indent=2)

def parse_mnote(data):
    """
    Ritorna (left_dict, right_dict) dove ogni dict ha 'text' e 'ranges'.
    Supporta:
      - nuovo formato JSON (MNOTE_JSON_V2)
      - vecchio formato --sinistra-- / --destra--
    """
    data = data.lstrip("\ufeff")
    if data.startswith(MNOTE_MAGIC):
        try:
            body = data.split("\n", 1)[1] if "\n" in data else "{}"
            obj = json.loads(body)
            left = obj.get("sinistra", {"text": "", "ranges": []})
            right = obj.get("destra", {"text": "", "ranges": []})
            left.setdefault("ranges", [])
            right.setdefault("ranges", [])
            left.setdefault("text", "")
            right.setdefault("text", "")
            return left, right
        except Exception:
            pass

    # fallback formato vecchio
    if "--sinistra--" in data and "--destra--" in data:
        left_text = data.split("--sinistra--", 1)[1].split("--destra--", 1)[0].strip("\n")
        right_text = data.split("--destra--", 1)[1].strip("\n")
        return (
            {"text": left_text, "ranges": []},
            {"text": right_text, "ranges": []},
        )

    return {"text": "", "ranges": []}, {"text": "", "ranges": []}
