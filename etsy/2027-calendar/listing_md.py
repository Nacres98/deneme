#!/usr/bin/env python3
"""Write upload/<listing>/LISTING.md (copy-paste ready Etsy text) from listings.json."""
import json, os
from pathlib import Path
ROOT = Path(__file__).resolve().parent
for k, v in json.loads((ROOT / "listings.json").read_text()).items():
    t = v["tags"]
    assert len(t) == 13 and all(len(x) <= 20 for x in t) and len(v["title"]) <= 140, k
    up = ROOT / "upload" / k
    imgs, files = sorted(os.listdir(up / "images")), sorted(os.listdir(up / "files"))
    (up / "LISTING.md").write_text("\n".join([
        f"# {v['title']}\n",
        f"**Price:** ${v['price_usd']:.2f}  \n**Title ({len(v['title'])}/140):**\n\n```\n{v['title']}\n```\n",
        "**Tags (13, max 20 chars each):**\n\n```\n" + ", ".join(t) + "\n```\n",
        f"**Materials:** {v['materials']}\n",
        "**Description:**\n\n```\n" + v["description"] + "\n```\n",
        "**Images (upload in this order; 01 = thumbnail):** " + ", ".join(f"`images/{i}`" for i in imgs) + "\n",
        "**Digital files (max 5):** " + ", ".join(f"`files/{f}`" for f in files) + "\n"]))
    print("ok", k)
