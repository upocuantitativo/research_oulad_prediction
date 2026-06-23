# -*- coding: utf-8 -*-
"""Add red in-text figure references (Figure 1/2/3) in Sections 5.2/5.3/5.4.
Idempotent: skips if the reference is already present. Usage: python 08_add_figrefs.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.normpath(os.path.join(HERE, "..", "manuscrito", "MANUSCRITO_MPI_OULAD.md"))
txt = open(MD, encoding="utf-8").read()

edits = [
    ("as theory predicts on engagement and timeliness (Table 2).",
     "as theory predicts on engagement and timeliness (Table 2; {{Figure 1}}).", "fig1"),
    ("prior attempts, credits) present (Table 3).",
     "prior attempts, credits) present (Table 3; {{Figure 2}}).", "fig2"),
    ("test ROC-AUC rises steadily across the course (Table 4).",
     "test ROC-AUC rises steadily across the course (Table 4; {{Figure 3}}).", "fig3"),
]
for old, new, label in edits:
    if new in txt:
        print(f"skip {label} (already present)"); continue
    n = txt.count(old)
    if n != 1:
        print(f"!! anchor '{label}' matched {n} times (expected 1) -- ABORTING"); sys.exit(1)
    txt = txt.replace(old, new, 1); print(f"ok  {label}")

open(MD, "w", encoding="utf-8").write(txt)
print("WROTE", MD)
