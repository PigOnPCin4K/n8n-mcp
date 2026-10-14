#!/usr/bin/env python3
"""Turn downloaded transcripts into analysis inputs for the research agents.

Usage:
    python build_corpus.py --corpus corpus [--cap 900] [--packs 8]

Reads corpus/txt/*.txt and corpus/meta.txt (from fetch_transcripts.py) and writes:
    corpus/term_trends.md   mentions per 100k words of each tracked term, by year
    corpus/rich/<id>.txt    the highest-signal ~60s passages of each video (about --cap words)
    corpus/rules.tsv        date, id, ~50-word window around every explicit rule statement
    corpus/index.tsv        date, id, title, words, extracted words
    corpus/packs/eraN.txt   rich passages in date order, split into equal-size packs (one per analyst agent)
"""
import argparse
import bisect
import collections
import os
import re

TERMS = {
    'support/resistance': r'support|resistance', 'trendline': r'trend ?line',
    'sma/ma': r'\b(sma|moving average)s?\b', '200ma': r'\b200\b.{0,15}(ma|moving|ema|sma|day|week)',
    'stochastics': r'stochastic|\bstoch\b', 'rsi': r'\brsi\b', 'macd': r'\bmacd\b', 'divergence': r'divergen',
    'golden/death_cross': r'golden cross|death cross', 'fib': r'\bfib(onacci|s)?\b|golden pocket',
    'volume_profile/poc': r'point of control|\bpoc\b|volume profile|high volume node|value area', 'bookmap': r'bookmap',
    'liquidity': r'liquidity', 'head_shoulders': r'head and shoulder|shoulder head', 'double_top/bottom': r'double (top|bottom)',
    'wedge/triangle': r'wedge|triangle|pennant', 'bull_bear_flag': r'(bull|bear)(ish)? flag',
    'weekly_close': r'weekly close|weekly candle', 'cme_gap': r'cme gap|\bcme\b',
    'stop_loss': r'stop ?loss|\bstops?\b', 'take_profit': r'take profit|taking profit|profit target', 'break_even': r'break ?even',
    'leverage': r'leverage', 'risk': r'\brisk', 'hedge': r'\bhedg', 'scalp': r'scalp', 'long': r'\blong\b', 'short': r'\bshort',
    'dxy': r'\bdxy\b|dollar index', 'fed/fomc/cpi': r'\bfomc\b|\bfed\b|powell|rate cut|rate hike|\bcpi\b', 'etf': r'\betfs?\b',
    'btc_dominance': r'dominance', 'alts': r'\balts?\b|altcoin', 'xrp': r'\bxrp\b', 'fear_greed': r'fear (and|&) greed',
    'psychology': r'patience|discipline|emotion|fomo|revenge',
}
TERMS_RE = {k: re.compile(v, re.I) for k, v in TERMS.items()}
SIGNAL_TERMS = ('stochastics', 'sma/ma', 'golden/death_cross', 'break_even', 'stop_loss', 'take_profit', 'leverage', 'hedge',
                'risk', 'liquidity', 'volume_profile/poc', 'divergence', 'rsi', 'weekly_close', 'bookmap')
# Phrases that usually mean he is describing a trade plan or method
METHOD_RE = re.compile(
    r"(my rule|the rule|rule number|rule is|golden rule|never (ever )?(trade|long|short|use|go)|always (use|have|set|take|wait)|"
    r"i (only|never) |here'?s (how|what) i|the way i trade|my strategy|my system|my setup|the setup|entry (is|at|here)|my entry|"
    r"stop (loss )?(is|at|goes|below|above)|my stop|invalidat|target (is|at)|targets? are|take profit|risk[- ]?(to|reward)|"
    r"percent of (my|your) (account|portfolio)|position size|how much (i|you) risk|leverage (i use|is)|"
    r"i'?m (going )?(long|short|flipping)|opened (a|the|my) (long|short)|closed (a|the|my) (long|short)|"
    r"if we (lose|break|close|hold)|confirmation|wait for (the )?(close|retest|confirmation)|retest)", re.I)
# Explicit rule statements, collected corpus-wide for the rules agent
RULE_RE = re.compile(
    r"(my rule|the rule is|rule number|golden rule|number one rule|never ever|i never (trade|long|short|use|risk|go)|"
    r"i always (use|set|take|wait|have)|you (should )?always (use|have|set|take|wait)|never (use|trade|risk|go) (more than|with|without|over)|"
    r"percent of (my|your) (account|portfolio|bag)|how much (i|you) risk|risk management|max(imum)? leverage|the way i trade|"
    r"my strategy|my system is|how i trade|how i scalp|my trading plan)", re.I)


def load_meta(corpus):
    meta = {}
    for line in open(f'{corpus}/meta.txt', errors='ignore'):
        parts = line.rstrip('\n').split('|', 4)
        if len(parts) == 5:
            meta[parts[0]] = {'date': parts[1], 'title': parts[4]}
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--corpus', default='corpus')
    ap.add_argument('--cap', type=int, default=900, help='approximate words of passages kept per video')
    ap.add_argument('--packs', type=int, default=8)
    args = ap.parse_args()
    C = args.corpus
    meta = load_meta(C)
    os.makedirs(f'{C}/rich', exist_ok=True)
    os.makedirs(f'{C}/packs', exist_ok=True)
    year_counts, year_words, year_docs = collections.defaultdict(collections.Counter), collections.Counter(), collections.Counter()
    index = []
    with open(f'{C}/rules.tsv', 'w') as rules_out:
        for fn in sorted(os.listdir(f'{C}/txt')):
            vid = fn[:-4]
            m = meta.get(vid, {'date': 'NA', 'title': '?'})
            year = m['date'][:4]
            lines = open(f'{C}/txt/{fn}', errors='ignore').read().split('\n')
            text = ' '.join(lines)
            words = len(text.split())
            if words < 200:
                continue
            year_words[year] += words
            year_docs[year] += 1
            for k, rx in TERMS_RE.items():
                year_counts[year][k] += len(rx.findall(text))

            scored = sorted(((len(METHOD_RE.findall(l)) * 3 + sum(1 for k in SIGNAL_TERMS if TERMS_RE[k].search(l)), i)
                             for i, l in enumerate(lines)), reverse=True)
            keep, kept_words = [], 0
            for score, i in scored:
                if score < 4 or kept_words > args.cap:
                    break
                keep.append(i)
                kept_words += len(lines[i].split())
            passages = [lines[i] for i in sorted(keep)]
            with open(f'{C}/rich/{vid}.txt', 'w') as f:
                f.write(f"# {m['title']} | {m['date']} | {vid}\n" + '\n'.join(passages) + '\n')

            tokens = text.split()
            starts = [w.start() for w in re.finditer(r'\S+', text)]
            for hit in RULE_RE.finditer(text):
                pos = bisect.bisect_right(starts, hit.start()) - 1
                rules_out.write(f"{m['date']}\t{vid}\t{' '.join(tokens[max(0, pos - 20):pos + 30])}\n")
            index.append((m['date'], vid, m['title'], words, sum(len(p.split()) for p in passages)))

    index.sort()
    with open(f'{C}/index.tsv', 'w') as f:
        f.writelines('\t'.join(map(str, row)) + '\n' for row in index)

    years = sorted(year_words)
    totals = collections.Counter()
    for y in years:
        totals.update(year_counts[y])
    with open(f'{C}/term_trends.md', 'w') as f:
        f.write('| term | ' + ' | '.join(f'{y} (n={year_docs[y]})' for y in years) + ' |\n|' + '---|' * (len(years) + 1) + '\n')
        for k, _ in totals.most_common():
            f.write(f'| {k} | ' + ' | '.join(f'{1e5 * year_counts[y][k] / year_words[y]:.0f}' for y in years) + ' |\n')

    # Equal-size packs in date order, one per era analyst
    rows = [r for r in index if r[4] > 50]
    per_pack = sum(r[4] for r in rows) / args.packs
    pack, acc, out = 0, 0, None
    for row in rows:
        if out is None or (acc > per_pack * pack and pack < args.packs):
            pack += 1
            out = open(f'{C}/packs/era{pack}.txt', 'w')
        out.write(open(f'{C}/rich/{row[1]}.txt').read() + '\n')
        acc += row[4]
    print(f'{len(index)} transcripts, {sum(year_words.values())} words, {pack} packs')


if __name__ == '__main__':
    main()
