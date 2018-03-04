from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Location, HikingTrail

engine = create_engine('sqlite:///hikingtrailscatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


location1 = Location(country="Peru", province="Various", city="TBA")
session.add(location1)
session.commit()

location2 = Location(name="United States", province="Georgia", city="TBA")
session.add(location2)
session.commit()



hikingEntry1 = HikingTrail(trailName="Inca Trail to Machu Picchu",
						description="Inca Trail to Machu Picchu consists of three overlapping trails: Mollepata, Classic, and One Day.",
						website="http://www.incatrail.org/information/",
						location=location1)
session.add(hikingEntry1)
session.commit()


hikingEntry2 = HikingTrail(trailName="Vanilla",
						description="The Appalachian National Scenic Trail, generally known as the Appalachian Trail or simply the A.T., is a marked hiking trail in the Eastern United States extending between Springer Mountain in Georgia and Mount Katahdin in Maine.",
						website="http://www.appalachiantrail.org",
						location=location2)
session.add(hikingEntry2)
session.commit()