from flask import Flask,jsonify, request,send_file,render_template;
from flask_mysqldb import MySQL
import pandas as pd
app=Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='pass'
app.config['MYSQL_DB']='spottabl'
mysql=MySQL(app)

@app.route("/")
def index():
        return render_template("index.html")

#Query data from Database
@app.route("/queryData",methods=['GET','POST'])
def queryData():
    if request.method=='GET':
        return render_template("output.html")
    else:
        cur=mysql.connection.cursor()
        query1= '''(SELECT  SUBSTRING_INDEX(SUBSTRING_INDEX(registrations.email, '@', -1),'.',1) AS 'clientcode', COUNT(DISTINCT registrations.email) AS 'Number of users on spottabl' FROM registrations GROUP BY clientcode);'''
        query2='''SELECT clientuserinvites.clientcode ,count(DISTINCT clientuserinvites.email) AS 'Number of users invited from spottabl' FROM clientuserinvites GROUP BY clientuserinvites.clientcode'''
        query3='''SELECT clientuserinvites.clientcode,count( DISTINCT clientuserinvites.email) AS 'Number of users who have accepted invite' FROM clientuserinvites WHERE clientuserinvites.accepted="true"  GROUP BY clientuserinvites.clientcode'''
        query4='''SELECT SUBSTRING_INDEX(SUBSTRING_INDEX(inviter, '@', -1),'.',1) AS 'domain', COUNT(distinct email) AS 'Number of users invited from spottabl user' FROM clientuserinvites GROUP BY domain'''
        
        que1_res=cur.execute(query1)
        if que1_res>0:
            que1_data=cur.fetchall()
            que1_data=pd.DataFrame(que1_data,columns=['Client Code',"Number of users on spottabl"])
            que1_data.set_index("Client Code",inplace=True)


        que2_res=cur.execute(query2)
        if que2_res>0:
            que2_data=cur.fetchall()
            que2_data=pd.DataFrame(que2_data,columns=['Client Code',"Number of users invited from spottabl"])
            que2_data.set_index("Client Code",inplace=True)


        que3_res=cur.execute(query3)
        if que3_res>0:
            que3_data=cur.fetchall()
            que3_data=pd.DataFrame(que3_data,columns=['Client Code',"Number of users who have accepted invite"])
            que3_data.set_index("Client Code",inplace=True)

    
        que4_res=cur.execute(query4)
        if que4_res>0:
            que4_data=cur.fetchall()
            que4_data=pd.DataFrame(que4_data,columns=['Client Code',"Number of users invited from spottabl user"])
            que4_data.set_index("Client Code",inplace=True)


        data = pd.concat([que1_data, que2_data,que3_data,que4_data] , axis=1, sort=False)
        data=data.fillna(0)
        data = data.astype({"Number of users on spottabl":"int","Number of users invited from spottabl":"int","Number of users who have accepted invite":"int","Number of users invited from spottabl user":"int"})


        data.to_csv("output.csv")
        return send_file('output.csv',
                        mimetype='text/csv',
                        attachment_filename='output.csv',
                        as_attachment=True)


#for inserting data to Database  if required
@app.route("/addRegistrationData",methods=['POST'])
def addRegistrationData():
    emailData=request.form.get("email")
    enabledData=request.form.get("enabled")
    registrationtypeData=request.form.get("registrationtype")
    usertypeData=request.form.get("usertype")
    cur=mysql.connection.cursor()
    query=f"INSERT INTO registrations(email,enabled,registrationtype,usertype) VALUES('{emailData}','{enabledData}','{registrationtypeData}','{usertypeData}')"
    cur.execute(query)
    mysql.connection.commit()
    cur.close()
    return("data added To Registration Table")

@app.route("/addClientuserinvitesData",methods=['POST'])
def addClientuserinvitesData():
    emailData = request.form.get("email")
    clientcodeData = request.form.get("clientcodel")
    userTypeData = request.form.get("userType")
    acceptedData = request.form.get("accepted")
    roleData = request.form.get("role")
    inviterData = request.form.get("inviter")
    cur=mysql.connection.cursor()
    query=f"INSERT INTO registrations(email,clientcode,userType,accepted,role,inviter) VALUES('{emailData}','{clientcodeData}','{userTypeData}','{acceptedData},'{roleData}','{inviterData}')"
    cur.execute(query)
    mysql.connection.commit()
    cur.close()
    return("data added To Clientuserinvites Table")


    


if __name__=="__main__":
    app.run(debug=True)