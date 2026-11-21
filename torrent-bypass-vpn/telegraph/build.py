"""Build Telegraph content from article.html.

Outputs (next to this script):
  content.json  - Telegraph Node array; images as "img/<name>.png" placeholders
  preview.html  - local preview with Telegraph-like styling
"""
import json
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).parent
ALLOWED = {"a", "aside", "b", "blockquote", "br", "code", "em", "figcaption", "figure",
           "h3", "h4", "hr", "i", "iframe", "img", "li", "ol", "p", "pre", "s",
           "strong", "u", "ul", "video"}
VOID = {"br", "hr", "img"}
TITLE = "Как пустить торрент-клиент мимо VPN в Happ и INCY"


class ToNodes(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = {"children": []}
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        if tag not in ALLOWED:
            raise ValueError(f"Tag <{tag}> is not allowed in Telegraph")
        node = {"tag": tag}
        a = {k: v for k, v in attrs if k in ("href", "src")}
        if a:
            node["attrs"] = a
        self.stack[-1]["children"].append(node)
        if tag not in VOID:
            node["children"] = []
            self.stack.append(node)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        top = self.stack.pop()
        assert top["tag"] == tag, f"mismatched </{tag}> vs <{top['tag']}>"

    def handle_data(self, data):
        parent = self.stack[-1]
        if parent is self.root or parent.get("tag") in ("ol", "ul", "figure"):
            if not data.strip():
                return  # whitespace between block elements
        data = " ".join(data.split("\n")) if data.strip() else data
        if data:
            parent["children"].append(data)


def build():
    src = (HERE / "article.html").read_text(encoding="utf-8")
    p = ToNodes()
    p.feed(src)
    assert len(p.stack) == 1, "unclosed tags"
    nodes = p.root["children"]
    (HERE / "content.json").write_text(json.dumps(nodes, ensure_ascii=False, indent=1), encoding="utf-8")
    size = len(json.dumps(nodes, ensure_ascii=False).encode())
    imgs = [m for m in src.split('src="')[1:]]
    css = """body{font-family:Georgia,serif;max-width:732px;margin:40px auto;padding:0 21px;font-size:18px;line-height:1.58;color:#000}
h1{font-family:Lucida Grande,Arial,sans-serif;font-size:32px;line-height:1.2}
h3{font-family:Lucida Grande,Arial,sans-serif;font-size:24px;margin:32px 0 12px}
img{max-width:100%;display:block;margin:0 auto}figure{margin:16px 0}
figcaption{text-align:center;color:#79828b;font-size:15px;margin-top:8px}
blockquote{border-left:3px solid #000;margin:16px 0;padding-left:20px;font-style:italic}
code{background:#f0f0f0;padding:1px 4px;font-size:15px}hr{border:0;text-align:center;margin:28px 0}
hr:after{content:"***";letter-spacing:12px}a{color:#000}"""
    (HERE / "preview.html").write_text(
        f'<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8"><title>{TITLE}</title>'
        f"<style>{css}</style></head><body><h1>{TITLE}</h1>{src}</body></html>",
        encoding="utf-8")
    print(f"nodes={len(nodes)} bytes={size} (limit 65536) images={len(imgs)}")


if __name__ == "__main__":
    build()
