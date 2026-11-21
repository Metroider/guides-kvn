"""Publish the guide to Telegraph (telegra.ph). Python 3.8+, no extra packages.

Telegraph no longer accepts image uploads, so images are referenced by direct
links. images.json already points to the PNGs in ../img of the GitHub repo; to
host them elsewhere, replace the links (each must open as a picture, not a page):

    {
      "happ-pc-1-tun.png": "https://example.com/happ-pc-1-tun.png",
      ...
    }

Run:
    python publish.py                    # creates a new Telegraph account and the page
    python publish.py --author "MyVPN"   # author name shown under the title

The account token is saved to telegraph_token.txt. Keep it: with it you can edit
the page later (python publish.py --edit <page path>).

    python publish.py --list    # pages of the account and their paths
    python publish.py --login   # one-time link to edit pages in the browser

"""
import argparse
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
API = "https://api.telegra.ph"
TITLE = "Как пустить торрент-клиент мимо VPN в Happ и INCY"


def call(method, **params):
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(f"{API}/{method}", data=data, timeout=30) as r:
        res = json.load(r)
    if not res.get("ok"):
        sys.exit(f"Telegraph error in {method}: {res.get('error')}")
    return res["result"]


def fill_images(nodes, mapping, missing):
    for n in nodes:
        if isinstance(n, dict):
            if n.get("tag") == "img":
                name = n["attrs"]["src"].split("/")[-1]
                if name in mapping and mapping[name].startswith("http"):
                    n["attrs"]["src"] = mapping[name]
                else:
                    missing.append(name)
            fill_images(n.get("children", []), mapping, missing)


def saved_token(token_file):
    if not token_file.exists():
        sys.exit("telegraph_token.txt not found: publish the page first (python publish.py)")
    return token_file.read_text().strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--author", default="")
    ap.add_argument("--edit", help="path of an existing page to overwrite, e.g. Kak-pustit-...-11-21")
    ap.add_argument("--login", action="store_true",
                    help="print a one-time link (valid 5 min) that logs this browser into the Telegraph account")
    ap.add_argument("--list", action="store_true", help="list pages of the Telegraph account")
    args = ap.parse_args()
    token_file = HERE / "telegraph_token.txt"

    if args.login:
        acc = call("getAccountInfo", access_token=saved_token(token_file), fields='["auth_url"]')
        print("Open within 5 minutes (one use):", acc["auth_url"])
        return
    if args.list:
        res = call("getPageList", access_token=saved_token(token_file), limit=200)
        for p in res["pages"]:
            print(f'{p["path"]}  |  {p["title"]}  |  views: {p.get("views", 0)}')
        return

    nodes = json.loads((HERE / "content.json").read_text(encoding="utf-8"))
    mapping_file = HERE / "images.json"
    mapping = json.loads(mapping_file.read_text(encoding="utf-8")) if mapping_file.exists() else {}
    missing = []
    fill_images(nodes, mapping, missing)
    if missing:
        sys.exit("No direct links in images.json for: " + ", ".join(sorted(set(missing))))

    if token_file.exists():
        token = token_file.read_text().strip()
    else:
        acc = call("createAccount", short_name=(args.author or "guide")[:32], author_name=args.author)
        token = acc["access_token"]
        token_file.write_text(token)
        print("New Telegraph account; token saved to", token_file)

    author = args.author
    if args.edit and not author:  # keep the page's current author instead of clearing it
        author = call(f"getPage/{args.edit}").get("author_name", "")
    params = dict(access_token=token, title=TITLE, author_name=author,
                  content=json.dumps(nodes, ensure_ascii=False), return_content="false")
    page = call(f"editPage/{args.edit}", **params) if args.edit else call("createPage", **params)
    print("Done:", page["url"])


if __name__ == "__main__":
    main()
