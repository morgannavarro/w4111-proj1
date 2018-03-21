#!/usr/bin/env python2.7

"""
To run locally:

    python server.py

Go to http://localhost:8111 in your browser.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
import psycopg2

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

DATABASEURI = "postgresql://msn2139:Messi272@35.231.44.137/proj1part2"

#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)


@app.before_request
def before_request():

  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):

  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
def index():

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)

  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html")

@app.route('/full_list')
def full_list():
	cursor = g.conn.execute("SELECT * FROM player")
	rows = cursor.fetchall()
	results = []
	results.append("{}    {}    {}    {}    {}    {}    {}    {}".format("player_id", "name", "position", "hometown", "dob", "height", "number", "team_id"))
	for row in rows:
		results.append(row)
	cursor.close()
	context = dict(data = results)
	return render_template("full_list.html", **context)

@app.route('/team_list')
def team_list():
	cursor = g.conn.execute("SELECT * FROM team")
	rows = cursor.fetchall()
	results = []
	results.append("{}    {}    {}    {}    {}    {}".format("team_id", "name", "league", "mascot", "city_name", "gm_id"))
	for row in rows:
		results.append(row)
	cursor.close()
	context = dict(data = results)
	return render_template("team_list.html", **context)

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
  return redirect('/')

@app.route('/search', methods=['POST'])
def search():
	name = request.form['name']
	cursor = g.conn.execute('SELECT player.name, team.name, team.city_name FROM player, team WHERE player.name=%s AND player.team_id=team.team_id', name)
	rows = cursor.fetchall()
	results = []
	results.append("{}    {}    {}".format("player_name", "team_name", "team_city"))
	for row in rows:
		results.append(row)
	cursor.close()
	context = dict(data = results)
	return render_template("index.html", **context)

@app.route('/sortplayers', methods=['POST'])
def sortplayers():
	sortby = request.form['sortplayer']
	
	if(sortby=='team'):
		cursor = g.conn.execute('SELECT teams.name, player.name, player.dob, player.height FROM (SELECT DISTINCT name, team_id FROM team) AS teams LEFT JOIN player ON teams.team_id=player.team_id ORDER BY teams.name')
	elif(sortby=='position'):
		cursor = g.conn.execute('SELECT positions.position, player.name, player.dob, player.height FROM (SELECT DISTINCT position FROM player) AS positions LEFT JOIN player ON positions.position = player.position ORDER BY positions.position')
	elif(sortby=='height'):
		cursor = g.conn.execute('SELECT player.name, player.height FROM player ORDER BY player.height ASC')
	elif(sortby=='dob'):
		cursor = g.conn.execute('SELECT player.name, player.dob FROM player ORDER BY player.dob ASC')
		
	rows = cursor.fetchall()
	results = []
	for row in rows:
		results.append(row)
	cursor.close()
	context = dict(datasort = results)
	return render_template("index.html", **context)

@app.route('/averages', methods=['POST'])
def averages():
	calcavg = request.form['average']
	
	if(calcavg=='Average Height per Team'):
		cursor = g.conn.execute('SELECT team.name, ROUND(AVG(height),1) FROM player LEFT JOIN team ON player.team_id = team.team_id GROUP BY team.name')
	elif(calcavg=='Average Height per Position'):
		cursor = g.conn.execute('SELECT positions.position, ROUND(AVG(height),1) FROM (SELECT DISTINCT position FROM player) AS positions LEFT JOIN player ON positions.position = player.position GROUP BY positions.position ORDER BY positions.position')

	rows = cursor.fetchall()
	results = []
	for row in rows:
		results.append(row)
	cursor.close()
	context = dict(dataavg = results)
	return render_template("index.html", **context)

@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on {}:{}".format(HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
