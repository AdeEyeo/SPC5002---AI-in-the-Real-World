"""
agreement.py
The annotator exercise. Everyone in the room codes the same ten comment
strings, and this works out where you disagreed.

There is no correct answer file. Nobody has one. The comments were written by
field researchers at Palmer Station between 2007 and 2009 and nobody asked them
what they meant, because by the time anyone needed to know, the answer was a
decade old and in somebody's field notebook.

Usage

    python src/agreement.py                     # code the ten on your own
    python src/agreement.py --room              # a demonstrator types the hand count
    python src/agreement.py votes/*.json        # pool saved files

Coding on your own saves votes/me.json, which maps each comment id to a letter.
The hand count saves votes/room.json, which holds how many hands went up for
each letter on each comment. Both kinds of file can be pooled.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CATEGORIES = {
    "A": "Never attempted. Nobody tried to take this measurement.",
    "B": "Collection failed. Somebody tried and did not get a usable sample.",
    "C": "Processing failed. A sample existed and the lab work did not work.",
    "D": "Result lost. A value was produced and did not reach the dataset.",
    "E": "Not a reason for a missing value at all.",
}

# the ten distinct strings in the Comments column, with how many rows carry each
COMMENTS = {
    "c01": ("Nest never observed with full clutch.", 34),
    "c02": ("Not enough blood for isotopes.", 7),
    "c03": ("Sexing primers did not amplify.", 4),
    "c04": ("No blood sample obtained.", 2),
    "c05": ("No blood sample obtained for sexing.", 2),
    "c06": ("Adult not sampled.", 1),
    "c07": ("Nest never observed with full clutch. Not enough blood for isotopes.", 1),
    "c08": ("Sexing primers did not amplify. Not enough blood for isotopes.", 1),
    "c09": ("Adult not sampled. Nest never observed with full clutch.", 1),
    "c10": ("No delta15N data received from lab.", 1),
}


def prompt() -> dict:
    print("Ten comments. One letter each.\n")
    for k, v in CATEGORIES.items():
        print(f"  {k}  {v}")
    print()
    out = {}
    for cid, (text, n) in COMMENTS.items():
        while True:
            ans = input(f"{cid}  ({n:>2} rows)  {text}\n     > ").strip().upper()
            if ans in CATEGORIES:
                out[cid] = ans
                break
            print("     one of A B C D E")
        print()
    return out


def count_room() -> dict:
    """The hand count. For each comment, how many hands went up for each letter."""
    print("For each comment, read it out, ask for hands letter by letter, and type\n"
          "the number of hands. Press Enter alone for none.\n")
    counts = {}
    for cid, (text, n) in COMMENTS.items():
        print(f"{cid}  ({n:>2} rows)  {text}")
        row = {}
        for k in CATEGORIES:
            while True:
                ans = input(f"     hands for {k} > ").strip()
                if ans == "" or ans.isdigit():
                    row[k] = int(ans or 0)
                    break
                print("     a whole number")
        counts[cid] = row
        print()
    return counts


def tally(files: dict[str, dict]) -> dict[str, Counter]:
    """Turn saved files into one Counter of letters per comment.

    A file from one coder maps an id to a letter. A file from the hand count maps
    an id to a count per letter. Both add up the same way.
    """
    picks = {cid: Counter() for cid in COMMENTS}
    for data in files.values():
        for cid, v in data.items():
            if cid not in picks:
                continue
            if isinstance(v, dict):
                picks[cid].update({k: int(n) for k, n in v.items() if int(n) > 0})
            else:
                picks[cid][v] += 1
    return picks


def pairwise_agreement(picks: dict[str, Counter]) -> float:
    """Of every pair of coders on every comment, the share that chose the same
    letter. Crude and adequate, and it needs only the counts."""
    agree = total = 0
    for c in picks.values():
        m = sum(c.values())
        total += m * (m - 1) // 2
        agree += sum(k * (k - 1) // 2 for k in c.values())
    return agree / total if total else float("nan")


def report(picks: dict[str, Counter]) -> None:
    n = max((sum(c.values()) for c in picks.values()), default=0)
    print(f"\n{n} coder{'s' if n != 1 else ''}\n")
    print(f"{'id':4s} {'rows':>5s}  {'split':22s} agreed  comment")
    print("-" * 96)

    contested = []
    for cid, (text, rows) in COMMENTS.items():
        c = picks[cid]
        if not c:
            continue
        top_n = c.most_common(1)[0][1]
        frac = top_n / sum(c.values())
        split = " ".join(f"{k}:{v}" for k, v in sorted(c.items()))
        print(f"{cid:4s} {rows:5d}  {split:22s} {frac:5.0%}  {text[:44]}")
        if frac < 0.8:
            contested.append((cid, text))

    if n < 2:
        print("\nOne coder always agrees with themselves. The room's answers are\n"
              "pooled after everyone has finished.")
        return

    print(f"\noverall pairwise agreement  {pairwise_agreement(picks):.0%}")

    if contested:
        print(f"\n{len(contested)} of {len(COMMENTS)} comments split the room:")
        for cid, text in contested:
            print(f"  {cid}  {text}")
        print("\nThese are the ones to argue about. Whatever the room settles on\n"
              "becomes the ground truth that every later number is measured against,\n"
              "and nothing in the dataset records that you settled it.")
    else:
        print("\nNo comment split the room, which is worth being suspicious about.")


def main() -> None:
    args = sys.argv[1:]
    out = ROOT / "votes"
    if args == ["--room"]:
        counts = count_room()
        out.mkdir(exist_ok=True)
        (out / "room.json").write_text(json.dumps(counts, indent=2) + "\n")
        print("saved to votes/room.json")
        files = {"room": counts}
    elif args:
        files = {Path(p).stem: json.loads(Path(p).read_text()) for p in args}
    else:
        mine = prompt()
        out.mkdir(exist_ok=True)
        (out / "me.json").write_text(json.dumps(mine, indent=2) + "\n")
        print("saved to votes/me.json")
        print("your letters  " + "  ".join(f"{cid} {v}" for cid, v in mine.items()))
        files = {"me": mine}
    report(tally(files))


if __name__ == "__main__":
    main()
