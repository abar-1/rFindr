from ragUtils import ScrapeProfs


url= "https://www.cs.purdue.edu/people/faculty/aliaga.html"
name, email, details = ScrapeProfs.get_professor_info(url)
print(name)
print(email)
print(details)
