"""The designed title and date on the day look (engine/UPGRADE-HOWTO.md section Y): demo_titles.py with the day
palette (navy, gold accents, a soft white glow) over a bright sky."""
import os

os.environ["TITLES_LOOK"] = "day"
from songs.demo_titles import *  # noqa: E402,F401,F403
