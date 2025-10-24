import Utils.ragUtils.SupabaseAPI as SupabaseAPI

links = []
with open("Utils/data/profLinks.txt", "r") as f:
    links_without_newlines = f.read().splitlines()
    links.extend(links_without_newlines)
    print(f"Loaded {len(links)} professor links.")
print(len(links))
print(links[:2])

startIndex = 0
endIndex = len(links)

uploader = SupabaseAPI.SupabaseAPI()
for i in range(startIndex, endIndex):
    try:
        print(f"Uploading professor {i+1}/{endIndex}: {links[i]}")
        uploader.upload_embedding(links[i])
    except Exception as e:
        print(f"Failed to upload professor at {links[i]}. Error: {e}")  