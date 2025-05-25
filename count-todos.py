import csv
import datetime
import re
import sys
from pathlib import Path

MARKERS = ["TODO", "RITA", "DAVID", "SEBASTIAN", "JAN", "CSANAD"]

out = csv.writer(sys.stdout)
out.writerow(["Date", "Chapter"] + MARKERS)
today = datetime.date.today()
for path in sorted(
    list(Path(".").rglob("chapter*.asciidoc"))
    + list(Path(".").rglob("appendix*.asciidoc"))
):
    chapter_name = str(path).replace(".asciidoc", "")
    contents = path.read_text()
    todos = [len(re.findall(rf"\b{thing}\b", contents)) for thing in MARKERS]
    out.writerow([today.isoformat(), chapter_name] + todos)
