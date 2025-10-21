from backend.src.db.database import Base, engine
from backend.src.models.models import User, UserEmbedding, Professor, ProfessorEmbedding, ChatLog

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Done.")
