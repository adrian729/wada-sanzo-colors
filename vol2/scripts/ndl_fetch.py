"""Download NDL IIIF page images politely: one at a time, with backoff on 503.

python ndl_fetch.py <out_dir> <size e.g. 200, or full> <pages e.g. 1-15 or 3,5,7> <pid> [<pid> ...]
Files: <out_dir>/m<NN>_r<RR>.jpg, NN = position of the pid in the list (1-based).
"""
import sys, time, urllib.request, urllib.error
from pathlib import Path

out, size, pages, pids = Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4:]
page_list = list(range(int(pages.split("-")[0]), int(pages.split("-")[1]) + 1)) if "-" in pages else [int(p) for p in pages.split(",")]
out.mkdir(parents=True, exist_ok=True)
region = "full/full" if size == "full" else f"full/{size},"
for m, pid in enumerate(pids, 1):
    for r in page_list:
        dest = out / f"m{m:02d}_r{r:02d}.jpg"
        if dest.exists() and dest.stat().st_size > 1000:
            continue
        url = f"https://dl.ndl.go.jp/api/iiif/{pid}/R{r:07d}/{region}/0/default.jpg"
        for attempt in range(8):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "colour-research-script"})
                data = urllib.request.urlopen(req, timeout=60).read()
                dest.write_bytes(data)
                break
            except urllib.error.HTTPError as e:
                wait = 5 * 2 ** attempt
                print(f"{dest.name}: HTTP {e.code}, retry in {wait}s", flush=True)
                time.sleep(wait)
            except Exception as e:
                print(f"{dest.name}: {e}, retry", flush=True)
                time.sleep(5)
        time.sleep(0.7)
    print(f"volume {m} done", flush=True)
print("ALL DONE", flush=True)
