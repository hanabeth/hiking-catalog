from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Location, HikingTrail

engine = create_engine('sqlite:///hiking.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


location1 = Location(country='Peru')
session.add(location1)
session.commit()

location2 = Location(country='Spain')
session.add(location2)
session.commit()

location3 = Location(country='France')
session.add(location3)
session.commit()

location4 = Location(country='United States')
session.add(location4)
session.commit()



hikingEntry1 = HikingTrail(trailName='Inca Trail to Machu Picchu',
						description='Inca Trail to Machu Picchu consists of three overlapping trails: Mollepata, Classic, and One Day.',
						website='http://www.incatrail.org/',
						province='Various',
						park='Machu Picchu',
						location=location1)
session.add(hikingEntry1)
session.commit()


hikingEntry2 = HikingTrail(trailName='The Cares Route',
						description='The Cares Route is in the heart of Picos de Europa.',
						website='https://www.larutadelcares.es/en/ruta/',
						province='Leon',
						park='Picos de Europa',
						location=location2)
session.add(hikingEntry2)
session.commit()


hikingEntry3 = HikingTrail(trailName='Le Chemin des Rognes',
						description='Le Chemin des Rognes is a challenging mountainous route that begins in Bellevue and ends in Baraque des Rognes and takes three to four hours. Although it\'s difficult, this hike offers wonderful views of the Chamonix Valley, the Aiguille du Midi, and the Aravis Mountain Range.',
						website='http://www.planetware.com/france/top-rated-hiking-trails-in-france-f-1-3.htm',
						province='Courmayeur, Les Houches, and Chamonix',
						park='Tour du Mont Blanc',
						location=location3)
session.add(hikingEntry3)
session.commit()


hikingEntry4 = HikingTrail(trailName='John Muir Trail',
						description='The John Muir Trail is the premier hiking trail in the United States.The trail starts in America\'s treasure, Yosemite National Park, and continues 215 miles through the Ansel Adams Wilderness, Sequoia National Park, King\'s Canyon National Park, and ends at the highest peak in continental United States, Mount Whitney at 14,496 ft.',
						website='http://johnmuirtrail.org/index.html',
						province='California',
						park='Yosemite/Mount Whitney',
						location=location4)
session.add(hikingEntry4)
session.commit()


hikingEntry5 = HikingTrail(trailName='Continental Divide Trail',
						description='The John Muir Trail is the premier hiking trail in the United States.The trail starts in America\'s treasure, Yosemite National Park, and continues 215 miles through the Ansel Adams Wilderness, Sequoia National Park, King\'s Canyon National Park, and ends at the highest peak in continental United States, Mount Whitney at 14,496 ft.',
						website='http://www.continentaldividetrail.org',
						province='New Mexico, Colorado, Wyoming, Idaho and Montana',
						park='Rocky Mountains',
						location=location4)
session.add(hikingEntry5)
session.commit()


