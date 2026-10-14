#!/usr/bin/env python3
"""Download Binance BTCUSDT 15m monthly kline archives into ./data for backtest.py.

Uses data.binance.vision (Binance's public archive). api.binance.com is not needed.
Usage: python download_data.py [--start 2017-08] [--end 2026-09]
"""
import argparse
import urllib.error
import urllib.request
from pathlib import Path

URL = 'https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-{}.zip'


def months(start, end):
    y, m = map(int, start.split('-'))
    ey, em = map(int, end.split('-'))
    while (y, m) <= (ey, em):
        yield f'{y}-{m:02d}'
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--start', default='2017-08')
    ap.add_argument('--end', default='2026-09')
    args = ap.parse_args()
    out = Path(__file__).resolve().parent / 'data'
    out.mkdir(exist_ok=True)
    for month in months(args.start, args.end):
        target = out / f'BTCUSDT-15m-{month}.zip'
        if target.exists():
            continue
        try:
            urllib.request.urlretrieve(URL.format(month), target)
            print('downloaded', target.name)
        except urllib.error.HTTPError as e:
            print('skipped', month, e.code)


if __name__ == '__main__':
    main()
