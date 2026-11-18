from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pelicanconf import *

SITEURL = FEED_DOMAIN = 'https://terencez127.github.io'
RELATIVE_URLS = False
