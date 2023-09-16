from flask import Flask, request,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.sql import text
# from flask_jwt_extended import JWTManager,jwt_required,create_access_token,decode_token
import jwt
import os
import datetime
app=Flask(__name__)

basedir=os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///'+os.path.join(basedir,"user.db")
# app.config["JWT_SECRET_KEY"]="secretKey"
key="secretKey"
db=SQLAlchemy(app)
# jwt=JWTManager(app)
@app.cli.command('db_create')
def db_create():
    db.create_all()
    print("DB Created")

@app.cli.command("db_delete")
def db_delete():
    db.drop_all()
    os.remove(os.path.join(basedir,"user.db"))
    print("DB Deleted")

@app.cli.command("db_seed")
def db_seed():
    user10=Users(name="user10",age="10")
    user11=Users(name="user11",age="11")
    student10=Students(id=1,name="user10",age="10",email="email1@email.com",password="password1")
    student11=Students(id=2,name="user11",age="11",email="email2@email.com",password="password2")
    db.session.add(user10)
    db.session.add(user11)
    db.session.add(student10)
    db.session.add(student11)
    db.session.commit()
    print("DB seeded")

@app.route("/users/<int:id>/<string:name>/<int:age>",methods=["PUT"])
def update_user(id:int,name:str,age:int):
    result=db.session.execute(text("SELECT * FROM USERS WHERE ID="+str(id)+";"))
    found=False
    for row in result:
        print(row[0])
        found=True
    print(name,age)
    if found:
        db.session.execute(text("UPDATE USERS SET NAME='"+name+"' , AGE="+str(age)+" WHERE ID="+str(id)+";"))
        db.session.commit()
        return "Record Updated"
    else:
        return "Data not found",200
    
@app.route("/users/<int:id>",methods=["DELETE"])
def delete_user(id:int):
    result=db.session.execute(text("SELECT * FROM USERS WHERE ID="+str(id)+";"))
    found=False
    for row in result:
        print(row[0])
        found=True
    # print(name,age)
    if found:
        db.session.execute(text("DELETE FROM USERS WHERE ID="+str(id)+";"))
        db.session.commit()
        return "Record Deleted"
    else:
        return "Data not found",200

@app.route("/users",methods=["GET","POST"])
def users():
    if request.method=="GET":
        user_list=[]
        result=db.session.execute(text('SELECT * FROM USERS;'))
        for row in result:
            user_list.append([row[1],row[2]])
        print(user_list)
        return jsonify(data=user_list),200
    if request.method=="POST":
        try:
            name=request.form["name"]
            age=request.form["age"]
            user_list=[name,age]
            db.session.execute(text("INSERT INTO USERS (name,age) VALUES ('"+name+"','"+str(age)+"');"))
            db.session.commit()
            return "Added user",201
        except:
            return jsonify("Enter all fields"),404
        
@app.route("/login",methods=["POST"])
def login():
    email=request.form["email"]
    password=request.form["password"]
    res=db.session.execute(text("Select * from Students where email='"+email+"' and password='"+password+"';"))
    found=False
    for row in res:
        found=True
    if found:
        payload_data={"email":email}
        return jsonify(message="login successful",access_token=jwt.encode({"exp":datetime.datetime.now(tz=datetime.timezone.utc),"email":email},key=key,algorithm="HS256")),200
    else:
        return jsonify(message="Bad email or password"),401
    

access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY4NjEyMDczOCwianRpIjoiNzVhMmM3OGYtZjllNS00ZDBhLTk0YTAtOTk5NWZlNWI5NTk4IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImVtYWlsMUBlbWFpbC5jb20iLCJuYmYiOjE2ODYxMjA3MzgsImV4cCI6MTY4NjEyMTYzOH0.tFxuwkDw4gmLda_OPHtUQ-SzeWGfpRo32Mpzto5NyhI"

@app.route("/decode_jwt",methods=["POST"])
def decode_jwt():
    token=request.form["token"]
    try:
        email=jwt.decode(token,key=key,algorithms=["HS256"])["email"]
        print(email)
        return jsonify(email,jwt.get_unverified_header(token)["alg"])
    except jwt.ExpiredSignatureError as e:
        print(e)
        return "expired token"
    # return "In progress"

@app.route("/sample_json_response")
def sample_json_response():
    resp=[
        {
            "name":"shubham",
            "age":25,
            "languages":[
                "english",
                "hindi"
            ]
        }
    ]
    return jsonify(result=resp)

@app.route("/get_json_data",methods=["POST"])
def get_json_data():
    raw_data=request.get_json()
    print(type(raw_data))
    print(raw_data)
    return "processed"

@app.route("/get_request_args",methods=["GET"])
def get_request_args():
    vals=request.args
    form_type=request.form
    for x in vals.keys():
        print(x,vals[x])
    print(form_type["x"])
    return vals

class Users(db.Model):
    __tablename__="users"
    id=Column(Integer,primary_key=True)
    name=Column(String,nullable=False)
    age=Column(Integer,nullable=False)
    

class Students(db.Model):
    __tablename__="students"
    id=Column(Integer,ForeignKey('users.id'),primary_key=True)
    name=Column(String,nullable=False)
    age=Column(Integer,nullable=False)
    email=Column(String,nullable=False)
    password=Column(String,nullable=False)

if __name__=="__main__":
    app.run(debug=True,port=2500)
