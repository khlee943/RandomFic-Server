# RandomFic-Server

__Tech Stack__

+ Selenium & Chromedriver for web scraping
+ Pandas & VADER for sentiment analysis
+ Flask (w/ Python)
+ Flask-Talisman for security config
+ Postgresql & SQLAlchemy for database
+ Docker to containerize

__Deployment__

+ Clone repository
+ Configure ENV variables in the dockerfile to include SUPABASE_URL, SUPABASE_API_KEY, and SUPABASE_DB_CONNECTION
+ *Development only*: Change app.py to relax security settings
  + `talisman = Talisman(app, content_security_policy=None, force_https=False)`
+ *Development only*: Change Dockerfile to build app locally
  + `CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]`
+ Run `docker build -t fanficapp .`
+ run `docker run -p 8080:8080 fanficapp`
+ Open [http://localhost:8080](http://localhost:3000) with your browser to see the result.

Hosted on Render.

DB hosted on Supabase.
