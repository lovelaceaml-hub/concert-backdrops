"""When the people of the two expressions are on screen (live seconds), shared by s03_people.py (which acts them),
people.py (which renders them) and overlay2.py (which places them). Plain Python, no imports.
No em dash or en dash anywhere in this file."""
# (label, variant, act start, act end): the act begins about a second before the words are readable
ACT_TIMES = [("Apology", "comfort", 27.6, 38.0), ("Encouragement", "shoulder", 223.4, 233.8)]
PRE, POST = 1.6, 1.6
WINDOWS = [(a[2] - PRE - 0.4, a[3] + POST + 1.2) for a in ACT_TIMES]
