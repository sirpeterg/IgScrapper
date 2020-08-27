from flask import Flask, render_template, redirect, url_for, request, session
from flask import Flask
import os
from random import randint
import sqlite3
import webbrowser
from threading import Timer

homePath = '/Users/Peterg/code/Igscrapper'
databaseFolder = os.path.join(homePath, 'Database_img')
databasePath = os.path.join(databaseFolder, 'IGdata.db')

app = Flask(__name__, static_folder='./Database_img')
app.config["SECRET_KEY"] = "OCML3BRawWEUeaxcuKHLpw"

def open_browser():
    webbrowser.open_new('http://127.0.0.1:2000/')


def getPhotoData(homePath, databaseFolder, databasePath):
    connection = sqlite3.connect(databasePath)
    cursor = connection.cursor()
    query = '''SELECT * FROM photo WHERE is_downloaded == "True";'''
    result = cursor.execute(query)
    photoData = [dict(zip([key[0] for key in cursor.description], row )) for row in result] # get all the photo metadata in a dict
    connection.close()
    return photoData


def getPhotoName(photoData, index):
        photoName = photoData[index]['photo_name'] + '.jpg' 
        photograperName = photoData[index]['photographer_name'].strip() 
        photoname = os.path.join('/Database_img/', photograperName, photoName)
        return photoname

def getDbStatusAnnotation(homePath, databaseFolder, databasePath):
    connection = sqlite3.connect(databasePath)
    cursor = connection.cursor()
    cursor.execute('''SELECT 
                    manually_confirmed
                    FROM photo;''')
    photoData = cursor.fetchall()
    totalDb = len(photoData)
    confirmed = photoData.count(('Landscape',))
    rejected = photoData.count(('NoLandscape',))
    connection.close()
    return totalDb, confirmed, rejected

def writeClassifierFlag(Flag, photo_id, homePath, databaseFolder, databasePath):
    connection = sqlite3.connect(databasePath)
    cursor = connection.cursor()
    cursor.execute("UPDATE photo SET manually_confirmed = ? WHERE photo_id = ?;", 
        (Flag, photo_id))
    connection.commit()
    connection.close()

def writeManualRating(Flag, photo_id, homePath, databaseFolder, databasePath):
    connection = sqlite3.connect(databasePath)
    cursor = connection.cursor()
    cursor.execute("UPDATE photo SET manual_rating = ? WHERE photo_id = ?;", 
        (Flag, photo_id))
    connection.commit()
    connection.close()

def navBar(photoData, databaseFolder):
    totalEntries = len(photoData)
    if 'nav_button' in request.form:
        if request.form['nav_button'] == '<': # navigate to lower index
            req = request.form
            if int(req['index']) == 0: # index: -1 should turn into index: end
                index = totalEntries - 1 # element 1 has index 0
            else:
                index  = int(req['index']) - int(1)
            session['index'] = index 
            photoname = getPhotoName(photoData, index)
        elif request.form['nav_button'] == '>': # navigate to higher index
            req = request.form
            if int(req['index']) == totalEntries - 1:
                index = 0
            else:
                index  = int(req['index']) + int(1)
            session['index'] = index
            photoname = getPhotoName(photoData, index)
    else:
        index = session['index']
        photoname = getPhotoName(photoData, index)
    return photoname, int(index)


@app.route("/", methods = ["GET","POST"])  
def browser():
    photoData = getPhotoData(homePath, databaseFolder, databasePath)
    if request.method == "GET":
        index = int(0)
        photoname = getPhotoName(photoData, index)
        return render_template("browser.html", 
        photoData = photoData[index],
        user_image = photoname, 
        index = index
        )
    elif request.method == "POST":
        if request.form['nav_button'] == 'browser':
            return redirect(url_for('browser'))
        elif request.form['nav_button'] == 'classifier':
            return redirect(url_for('classifier'))
        photoname, index = navBar(photoData, databaseFolder)
        return render_template("browser.html",
            photoData = photoData[index], 
            user_image = photoname, 
            index = index
            ) 

@app.route("/classifier", methods = ["GET","POST"])
def classifier():
    photoData = getPhotoData(homePath, databaseFolder, databasePath)
    if request.method == "GET":
        totalDb, confirmed, rejected = getDbStatusAnnotation(homePath, databaseFolder, databasePath)
        index = int(0)
        photoname = getPhotoName(photoData, index)
        wRejected = str(round( (float(rejected) / float(totalDb)) * 200.0)) + "px" # 200 is the width of the total loading bar
        wConfirmed = str(round( (float(confirmed+ rejected) / float(totalDb)) * 200.0)) + "px" # 200 is the width of the total loading bar
        return render_template("classifier.html", 
            photoData = photoData[index],
            user_image = photoname, 
            index = index,
            totalDb = totalDb, 
            confirmed = confirmed,
            rejected = rejected,
            widthConfirmed = wConfirmed, 
            widthRejected = wRejected 
            )

    elif request.method == "POST":
        totalDb, confirmed, rejected = getDbStatusAnnotation(homePath, databaseFolder, databasePath)
        if 'nav_button' in request.form:
            if request.form['nav_button'] == 'browser':
                session['index'] = int(0)
                return redirect(url_for('browser'))
            elif request.form['nav_button'] == 'classifier':
                session['index'] = int(0)
                return redirect(url_for('classifier'))        
            photoname, index = navBar(photoData, databaseFolder)
        elif 'submit_button' in request.form:
            if request.form['submit_button'] == 'Landscape' or request.form['submit_button'] == 'NoLandscape':
                classifier = request.form['submit_button']
                writeClassifierFlag(classifier, photoData[session['index']]['photo_id'],  # 7
                    homePath, databaseFolder, databasePath)
                photoData = getPhotoData(homePath, databaseFolder, databasePath)
            elif request.form['submit_button'] == 'Exciting' or request.form['submit_button'] == 'NonExciting':
                classifier = request.form['submit_button']
                writeManualRating(classifier, photoData[session['index']]['photo_id'], # 7
                    homePath, databaseFolder, databasePath)
                photoData = getPhotoData(homePath, databaseFolder, databasePath)
            photoname, index = navBar(photoData, databaseFolder)
        wRejected = str(round( (float(rejected) / float(totalDb)) * 200.0)) + "px" # 200 is the width of the total loading bar
        wConfirmed = str(round( (float(confirmed+ rejected) / float(totalDb)) * 200.0)) + "px" # 200 is the width of the total loading bar
        return render_template("classifier.html", 
            user_image = photoname, 
            index = session['index'],
            photoData = photoData[index],
            totalDb = totalDb, 
            confirmed = confirmed,
            rejected = rejected,
            widthConfirmed =  wConfirmed, 
            widthRejected = wRejected 
            )         


if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run(debug=True, port=2000, use_reloader=False)