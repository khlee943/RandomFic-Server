# RandomFic-Server

__Tech Stack__

+ Selenium & Chromedriver for web scraping
+ Pandas & VADER for sentiment analysis
+ Flask (w/ Python)
+ Flask-Talisman for security config
+ Postgresql & SQLAlchemy for database
+ Docker to containerize

__Deployment__

For development:

+ Clone repository
+ Run `docker build -t myapp .`
+ run `docker run -p 8080:8080 myapp`
+ Open [http://localhost:8080](http://localhost:3000) with your browser to see the result.

For production:

+ Same as development instructions

Hosted on Render.

DB hosted on CockroachDB.
