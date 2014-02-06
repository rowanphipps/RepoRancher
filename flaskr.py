from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, abort
from engine import monster
# import threading
from multiprocessing import Process, Pipe
import json
import httplib2
import time
import random
import math

DEBUG = True

TOKEN = "032bd3c4b552f50a114727aadd13e30037635a6d"

app = Flask(__name__)

def normalise(log):
	out = "\n".join(log)
	return out #+ "<br>"

def multi_threaded_request(conn, mon):
	mon.requestInfo()
	conn.send(mon)

	conn.close()

# @app.route('/')
# def home():
#     return 'Hello World!3'

@app.route('/')
def home():
	return render_template('basic.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/help')
def help_page():
	return render_template('help.html')

@app.route('/fight', methods=['POST', 'GET'])
def display():
	#abort(418)
	print "button pressed"
	m1 = monster(request.form['user1'], request.form['repo1'])
	m2 = monster(request.form['user2'], request.form['repo2'])

	parent_conn_m1, m1_child = Pipe()
	parent_conn_m2, m2_child = Pipe()

	m1Thread = Process(target=multi_threaded_request, name="m1 info getting", args=(m1_child, m1))
	m2Thread = Process(target=multi_threaded_request, name="m2 info getting", args=(m2_child, m2))

	m1Thread.start()
	m2Thread.start()

	m1Thread.join(timeout=2)
	m2Thread.join(timeout=2)

	m1 = parent_conn_m1.recv()
	m2 = parent_conn_m2.recv()

	# m1.requestInfo()
	# m2.requestInfo()
	try:
		m1.printStats()
	except:
		print "m1 vanished during threading operations!"
		abort(400)

	# try:
	battleLog, result = m1.fight(m2)
	# except:
	# 	print "fighting error"
	# 	abort(418)

	# print "finished fighting"
	# battleLog = ['hjdf']
	# winner = "not working"

	out = normalise(battleLog)

	return render_template('fight.html', m1=m1, m2=m2, log=out, result=result)
	# return render_template('mock.html', 
	# 	user1=request.form['user1'],
	# 	user2=request.form['user2'],
	# 	repo1=request.form['repo1'],
	# 	repo2=request.form['repo2'])

if __name__ == '__main__':

    app.run(debug=True)


    		
