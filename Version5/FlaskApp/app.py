from flask import Flask,render_template, request,json,redirect,session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

 
app = Flask(__name__)
app.secret_key = "This is the key??"
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask'
 
mysql = MySQL(app)
"""Routes and get methods"""

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/showSignIn')
def showSignIn():
    return render_template('signin.html')

@app.route('/showHome')
def showHome():
    return render_template('index.html')
 
@app.route('/form')
def form():
    return render_template('form.html')
 
@app.route("/" ) 
def main(): 
    return render_template("index.html")

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('user.html')
    else:
        return render_template('index.html')

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
        return "Login via the login Form"
     
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['password']
       
        cursor = mysql.connection.cursor()
        cursor.execute(''' INSERT INTO user VALUES('',%s,'',%s,%s)''',(email,name))
        mysql.connection.commit()
        cursor.close()
        return f"Done!!"

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

app.route('/signUp',methods=['POST','GET'])
def signUp():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate 
        if _name and _email and _password:
            conn = mysql.connect()
            cursor = conn.cursor()
            _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_createUser',(_name,_email,_hashed_password))
            data = cursor.fetchall()

            if len(data) == 0:
                conn.commit()
                return json.dumps({'message':'User created successfully !'})
            else:
                return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        conn.close() 

@app.route('/validateLogin',methods=['POST']) 
def validateLogin():
    try: 
        email = request.form['inputEmail']
        _password = request.form['inputPassword'] 

        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin',(email,))
        data = cursor.fetchall()

        if len(data) > 0:
            if check_password_hash(str(data[0][3]),_password):
                session['user'] = data[0][0]
                return redirect('/userHome')
            else:
                return render_template('error.html',error = 'Wrong Email address or Password.')
        else:
            return render_template('error.html',error = 'Wrong Email address or Password.')
            

    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()


@app.route('/showPhoto')
def showPhoto():
    return render_template('addPhoto.html')

@app.route('/deletePhoto',methods=['POST'])
def deletePhoto():
    try:
        if session.get('user'):
            _id = request.form['id']
            _user = session.get('user')

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_deletePhoto',(_id,_user))
            result = cursor.fetchall()

            if len(result) == 0:
                conn.commit()
                return json.dumps({'status':'OK'})
            else:
                return json.dumps({'status':'An Error occured'})
        else:
            return render_template('error.html',error = 'Unauthorized Access')
    except Exception as e:
        return json.dumps({'status':str(e)})
    finally:
        cursor.close()
        conn.close()


@app.route('/getPhotoById',methods=['POST'])
def getPhotoById():
    try:
        if session.get('user'):
            
            _id = request.form['id']
            _user = session.get('user')
    
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_GetPhotoById',(_id,_user))
            result = cursor.fetchall()

            photo = []
            photo.append({'Id':result[0][0],'Geo_Location':result[0][1],'Capture_Date':result[0][2],'Capture_By':result[0][3],'Album':result[0][4],'photo_link':result[0][5]})

            return json.dumps(photo)
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html',error = str(e))

@app.route('/getPhoto')
def getPhoto():
    try:
        if session.get('user'):
            _user = session.get('user')

            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('sp_GetPhotoByUser',(_user,))
            photos = cursor.fetchall()

            photos_dict = []
            for pic in photos:
                photos_dict = {
                        'Geo_Location': pic[0],
                        'Capture_Date': pic[1],
                        'Capture_By': pic[2],
                        'Album': pic[4],
                        'Photo_Link': pic[5]}
                photos.append(photos_dict)

            return json.dumps(photos)
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error = str(e))

@app.route('/addPhoto',methods=['POST'])
def addPhoto():
    try:
        if session.get('user'):
            _Geo_Location = request.form['Geo_Location']
            _Capture_Date = request.form['Capture_Date']
            _Capture_By = session.get('Capture_By')
            _Album = session.get('Album')
            _Photo_Link = session.get('Photo_Link')

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_addPhoto',(_Geo_Location,_Capture_Date,_Capture_By,_Album,_Photo_Link))
            data = cursor.fetchall()

            if len(data) == 0:
                conn.commit()
                return redirect('/userHome')
            else:
                return render_template('error.html',error = 'An error occurred!')

        else:
            return render_template('error.html',error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/updatePhoto', methods=['POST'])
def updatePhoto():
    try:
        if session.get('user'):
            _Geo_Location = request.form['Geo_Location']
            _Capture_Date = request.form['Capture_Date']
            _Capture_By = session.get('Capture_By')
            _Album = session.get('Album')
            _Photo_Link = session.get('Photo_Link')

            

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_updatePhoto',(_Geo_Location,_Capture_Date,_Capture_By,_Album,_Photo_Link))
            data = cursor.fetchall()

            if len(data) == 0:
                conn.commit()
                return json.dumps({'status':'OK'})
            else:
                return json.dumps({'status':'ERROR'})
    except Exception as e:
        return json.dumps({'status':'Unauthorized access'})
    finally:
        cursor.close()
        conn.close()

 
app.run(host='localhost', port=5000)
