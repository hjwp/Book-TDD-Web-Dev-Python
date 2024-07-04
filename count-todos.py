import csv
import sys
from pathlib import Path

MARKERS = ["TODO", "RITA", "DAVID", "SEBASTIAN", "JAN", "CSANAD"]

out = csv.writer(sys.stdout)
out.writerow(["Chapter"]  + MARKERS)
for path in sorted(Path(".").rglob("chapter*.asciidoc")):
    chapter_name = str(path).replace(".asciidoc", "")
    todos = [
        path.read_text().count(thing)
        for thing in MARKERS
    ]
    out.writerow([chapter_name] + todos)
