
from db.SupabaseAPI import SupabaseAPI


url= "https://www.cs.purdue.edu/people/faculty/aliaga.html"
# name, email, details = scrape_professor_page(url)
# print(name)
# print(email)
# print(details)

uploader = SupabaseAPI()
uploader.upload_prof_embedding("https://www.cs.purdue.edu/people/faculty/aliaga.html")


