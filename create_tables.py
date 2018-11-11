from database import Base, engine, SESSION

def create_tables():
	Base.metadata.drop_all(engine)
	Base.metadata.create_all(engine)

if __name__ == "__main__":
	print ('Creating tables...')
	create_tables()
	print ('Ready!')