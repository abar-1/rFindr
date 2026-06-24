import os

from db.SupabaseAPI import SupabaseAPI

# Resolve the data file relative to the backend dir so this runs from any cwd.
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINKS_PATH = os.path.join(BACKEND_DIR, "data", "profLinks.txt")

links = []
with open(LINKS_PATH, "r") as f:
    links_without_newlines = f.read().splitlines()
    links.extend(links_without_newlines)
    print(f"Loaded {len(links)} professor links.")
print(len(links))
print(links[:2])

startIndex = 0
endIndex = len(links)

uploader = SupabaseAPI()
for i in range(startIndex, endIndex):
    try:
        print(f"Uploading professor {i+1}/{endIndex}: {links[i]}")
        uploader.upload_prof_embedding(links[i])
    except Exception as e:
        print(f"Failed to upload professor at {links[i]}. Error: {e}")  