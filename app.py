from flask import request, Flask, render_template, redirect, session
import mysql.connector
import pandas as pd 
import numpy as np
import pickle
import os

app = Flask(__name__) # name for the Flask app (refer to output)
app.secret_key=os.urandom(24)

#connect to db
conn=mysql.connector.connect(host="localhost",user="root",password="",database="carprice")
cursor=conn.cursor()

model1 = pickle.load(open('randomf.pkl', 'rb')) #loading my trained model

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/home')
def home():
    if 'id' in session:
      return render_template('home.html')
    else:
      return redirect('/')

@app.route('/validate_login', methods=['POST'])
def login_validation():
    email=request.form.get('email')
    password=request.form.get('password')

    cursor.execute("""SELECT * FROM `users` WHERE `email` LIKE '{}' AND `password` LIKE '{}'"""
    .format(email,password))
    users=cursor.fetchall()

    if len(users)>0:
      session['id']=users[0][0]
      return redirect('/home')
    else:
      return render_template("login.html")

@app.route('/add_user', methods=['POST'])
def add_user():
    name=request.form.get('uname')
    email=request.form.get('uemail')
    password=request.form.get('password1')

    cursor.execute("""INSERT INTO `users` (`id`,`name`,`email`,`password`) VALUES(NULL,'{}','{}','{}')""".format(name,email,password))
    conn.commit()

    cursor.execute("""SELECT * FROM `users` WHERE `email` LIKE '{}'""".format(email))
    myuser=cursor.fetchall()
    session['id']=myuser[0][0]
    return redirect('/home')

@app.route('/logout')
def logout():
    session.pop('id')
    return redirect('/')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/vehicles')
def vehicles():
    return render_template('vehicles.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/predict',methods=['POST'])
def predict():
    features = request.form
    print(features) 
    Model = features['Model']
    Year = features['Year']
    Transmission = features['Transmission']
    Body = features['Body']
    Fuel = features['Fuel']
    Capacity = features['Capacity']
    Mileage = features['Mileage']
    Fuel_Price = features['Fuel_Price']
    USD_rate = features['USD_rate']
    Crude_Oil_Price = features['Crude_Oil_Price']


    user_input = {'Model':[Model],'Year':[Year],'Transmission':[Transmission],'Body':[Body],'Fuel':[Fuel],'Capacity':[Capacity],'Mileage':[Mileage],'Fuel_Price':[Fuel_Price],'USD_rate':[USD_rate],'Crude_Oil_Price':[Crude_Oil_Price]}
    df = pd.DataFrame(user_input)

    df = pd.concat([df],axis=1)

    print(df)

    prediction = model1.predict(df)

    output = float(np.round(prediction[0], 2))

    print(output)

    return render_template('result.html', prediction_text='Predicted price of car is Rs. {}'.format(output))


if __name__ == "__main__":
    app.run(debug=True)