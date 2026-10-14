#!/usr/bin/env python3
"""Download Crypto Lifer stream/video transcripts (YouTube auto-captions) as timestamped text.

Usage:
    pip install yt-dlp curl_cffi
    python fetch_transcripts.py --out corpus            # list channel, then download
    python fetch_transcripts.py --out corpus --sample 5 # every 5th video first, then the rest

Writes:
    corpus/catalog.txt         id|title|duration for every stream and upload
    corpus/meta.txt            id|upload_date|duration|views|title for downloaded videos
    corpus/txt/<id>.txt        one line per ~60 seconds: "[h:mm:ss] text"
    corpus/nosubs.txt          videos without English captions

YouTube rate-limits caption downloads per IP (HTTP 429 and "confirm you're not a bot").
The downloader runs sequentially and backs off exponentially (up to 1 hour) instead of
recording those videos as failures, so it can be left running and resumed at any time.
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import tempfile
import time

CHANNEL = 'https://www.youtube.com/@CryptoLifer'
# The android_vr client kept working after the web clients were bot-walled.
YTDLP_ARGS = ['--impersonate', 'chrome', '--extractor-args', 'youtube:player_client=android_vr']


def list_channel(out):
    rows = []
    for tab in ('streams', 'videos'):
        res = subprocess.run(['yt-dlp', '--flat-playlist', '--print', '%(id)s|%(title)s|%(duration)s', f'{CHANNEL}/{tab}'],
                             capture_output=True, text=True, check=True)
        rows += [line for line in res.stdout.splitlines() if line.strip()]
    with open(f'{out}/catalog.txt', 'w') as f:
        f.write('\n'.join(rows) + '\n')
    return [r.split('|', 1)[0] for r in rows]


def json3_to_text(path):
    """Group caption events into ~60 second lines prefixed with a timestamp."""
    events = json.load(open(path)).get('events', [])
    segments = []
    for e in events:
        text = ''.join(s.get('utf8', '') for s in e.get('segs') or []).replace('\n', ' ').strip()
        if text:
            segments.append((e.get('tStartMs', 0) // 1000, text))
    lines, buf, start = [], [], 0
    for t, text in segments:
        if t - start >= 60 and buf:
            lines.append(f'[{start // 3600}:{start % 3600 // 60:02d}:{start % 60:02d}] ' + ' '.join(buf))
            buf, start = [], t
        buf.append(text)
    if buf:
        lines.append(f'[{start // 3600}:{start % 3600 // 60:02d}:{start % 60:02d}] ' + ' '.join(buf))
    return '\n'.join(lines) + '\n'


def stratified_order(ids, step):
    first = ids[::step] if step > 1 else []
    seen, order = set(), []
    for vid in first + ids:
        if vid not in seen:
            seen.add(vid)
            order.append(vid)
    return order


def download(out, queue, delay):
    os.makedirs(f'{out}/txt', exist_ok=True)
    nosubs_path = f'{out}/nosubs.txt'
    nosubs = set(open(nosubs_path).read().split()) if os.path.exists(nosubs_path) else set()
    backoff = 60
    for vid in queue:
        if os.path.exists(f'{out}/txt/{vid}.txt') or vid in nosubs:
            continue
        while True:
            tmp = tempfile.mkdtemp()
            res = subprocess.run(['yt-dlp', '-q', '--no-warnings', *YTDLP_ARGS, '--skip-download', '--write-auto-subs', '--write-subs',
                                  '--sub-langs', 'en', '--sub-format', 'json3',
                                  '--print-to-file', '%(id)s|%(upload_date)s|%(duration)s|%(view_count)s|%(title)s', f'{out}/meta.txt',
                                  '-o', f'{tmp}/%(id)s', f'https://www.youtube.com/watch?v={vid}'], capture_output=True, text=True)
            subs = glob.glob(f'{tmp}/*.json3')
            if subs:
                with open(f'{out}/txt/{vid}.txt', 'w') as f:
                    f.write(json3_to_text(subs[0]))
                backoff = 60
            elif '429' in res.stderr or 'confirm you' in res.stderr:
                shutil.rmtree(tmp, ignore_errors=True)
                print(f'rate limited on {vid}; sleeping {backoff}s', flush=True)
                time.sleep(backoff)
                backoff = min(backoff * 2, 3600)
                continue
            else:
                with open(nosubs_path, 'a') as f:
                    f.write(vid + '\n')
            shutil.rmtree(tmp, ignore_errors=True)
            break
        time.sleep(delay)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', default='corpus')
    ap.add_argument('--sample', type=int, default=5, help='download every Nth video first so early results span all years')
    ap.add_argument('--delay', type=float, default=5, help='seconds between downloads')
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    catalog = f'{args.out}/catalog.txt'
    ids = [l.split('|', 1)[0] for l in open(catalog)] if os.path.exists(catalog) else list_channel(args.out)
    print(f'{len(ids)} videos in catalog', flush=True)
    download(args.out, stratified_order(ids, args.sample), args.delay)


if __name__ == '__main__':
    main()
