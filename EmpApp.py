from flask import Flask, render_template,request
from datetime import datetime
from pymysql import connections
from config import *
import boto3

app = Flask(__name__)
app.secret_key = "magiv"

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)

output = {}
table = 'employee'


#MAIN PAGE
@app.route("/")
def home():
    
    return render_template("home.html",date=datetime.now())
    
#ADD EMPLOYEE DONE
@app.route("/addemp/",methods=['GET','POST'])
def addEmp():
    return render_template("AddEmp.html",date=datetime.now())

#EMPLOYEE OUTPUT
@app.route("/addemp/results",methods=['GET','POST'])
def Emp():

    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location,))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)



   
    

#Get Employee DONE
@app.route("/getemp/")
def getEmp():
    
    return render_template('GetEmp.html',date=datetime.now())


#Get Employee Results
@app.route("/getemp/results",methods=['GET','POST'])
def Employee():
    
     #Get Employee
     emp_id = request.form['emp_id']
    # SELECT STATEMENT TO GET DATA FROM MYSQL
     select_stmt = "SELECT * FROM employee WHERE emp_id = %(emp_id)s"

     
     cursor = db_conn.cursor()
        
     try:
         cursor.execute(select_stmt, { 'emp_id': int(emp_id) })
         # #FETCH ONLY ONE ROWS OUTPUT
         for result in cursor:
            print(result)
        

     except Exception as e:
        return str(e)
        
     finally:
        cursor.close()
    

     return render_template("GetEmpOutput.html",result=result,date=datetime.now())

 #Edit Employee DONE
@app.route("/editemp/")
def editEmp():
    
    return render_template('EditEmp.html',date=datetime.now())


#edit Employee Results
@app.route("/editemp/results",methods=['GET','POST'])
def editEmployee():
    
     #Get Employee
     emp_id = request.form['emp_id']
    # SELECT STATEMENT TO GET DATA FROM MYSQL
     
     update_stmt = "SELECT * FROM employee WHERE emp_id = %(emp_id)s"

     
     cursor = db_conn.cursor()
        
     try:
         cursor.execute(update_stmt, { 'emp_id': int(emp_id) })
         # #FETCH ONLY ONE ROWS OUTPUT
         for result in cursor:
            print(result)
        

     except Exception as e:
        return str(e)
        
     finally:
        cursor.close()
    

     return render_template("EditEmpOutput.html",result=result,date=datetime.now())
    
    
@app.route("/editemp/done",methods=['GET','POST'])
def editEmpdone():

    emp_id=request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
  
    UPDATE_sql = "UPDATE employee SET emp_id=%s, first_name=%s, last_name=%s, pri_skill=%s, location=%s WHERE emp_id = %(emp_id)s"
    cursor = db_conn.cursor()
    cursor.execute(UPDATE_sql, (emp_id, first_name, last_name, pri_skill, location,))
    db_conn.commit()
    emp_name = "" + first_name + " " + last_name



    print("all modification done...")
    return render_template('editDone.html', name=emp_name)

#delete Employee DONE
@app.route("/deleteemp/")
def deleteEmp():
    
    return render_template('deleteEmp.html',date=datetime.now())


#delete Employee Results
@app.route("/deleteemp/results",methods=['GET','POST'])
def deleteEmployee():
    
     #Get Employee
     emp_id = request.form['emp_id']
    # SELECT STATEMENT TO GET DATA FROM MYSQL
     select_stmt = "SELECT * FROM employee WHERE emp_id = %(emp_id)s"

     
     cursor = db_conn.cursor()
        
     try:
         cursor.execute(select_stmt, { 'emp_id': int(emp_id) })
         # #FETCH ONLY ONE ROWS OUTPUT
         for result in cursor:
            print(result)
        

     except Exception as e:
        return str(e)
        
     finally:
        cursor.close()
    

     return render_template("deleteEmpOutput.html",result=result,date=datetime.now())

#delete emply
@app.route("/deleteempdone/",methods=['GET','POST'])
def deletedelete():
    emp_id = request.form['emp_id']
    # SELECT STATEMENT TO GET DATA FROM MYSQL
    delete_stmt = "DELETE FROM employee WHERE emp_id = %(emp_id)s"
    cursor = db_conn.cursor()  
    cursor.execute(delete_stmt, { 'emp_id': int(emp_id) })
         # #FETCH ONLY ONE ROWS OUTPUT
     
    return render_template("deleteEmpDone.html",date=datetime.now())       
    

#About Us
@app.route("/aboutus/")
def Aboutus():
    return render_template("index.html",date=datetime.now())


# RMB TO CHANGE PORT NUMBER
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True) # or setting host to '0.0.0.0'
