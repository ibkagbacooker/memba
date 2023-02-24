from flask import render_template, redirect, flash, session,request, url_for
from sqlalchemy.sql import text #import text for rendering queries
from sqlalchemy import desc
from membapp import app,db
from werkzeug.security import generate_password_hash, check_password_hash
from membapp.models import Party,Topics



@app.route('/admin/update_topic', methods=['POST'])
def update_topic():
    if session.get('loggedin') !=None: #...............................................................
        newstatus = request.form.get('status')
        topicid = request.form.get('topicid')
        t = Topics.query.get(topicid)
        t.topic_status = newstatus
        db.session.commit()
        flash('')
        return redirect('/admin/topics')

        #Retrieve the id of the topic and update the new status on your table
        

@app.route('/admin/topics/')
def all_topics():
    if session.get("loggedin") == None:
        return redirect('/admin/login')
    else:
        posts = db.session.query(Topics).all()
        return render_template("admin/alltopics.html",posts=posts)

@app.route('/admin/topic/edit/<id>')
def edit_topic(id):
    if session.get('loggedin') != None:
        #write the query to fetch the name
        topic_deets = Topics.query.get(id)
        return render_template('admin/edit_topic.html', topic_deets=topic_deets)
    else:
        return redirect(url_for('login'))


@app.route('/admin/topic/delete/<id>')
def delete_post(id):
    topicobj = Topics.query.get_or_404(id) #..............................................................
    db.session.delete(topicobj)
    db.session.commit()
    flash('Successfully deleted')
    return redirect(url_for('all_topics'))


@app.route("/admin", methods=['POST','GET'])
def admin_home():
    if request.method=='GET':
        return render_template("admin/adminreg.html")
    else:
        #TO DO retreive the data coming from the form and save in variables
        #retrieving data from form
        data = request.form
        username=data.get('username') 
        pwd=data.get('pwd')
        #hashing the password
        
        hashed_pwd= generate_password_hash(pwd)
        
        if username !='' or pwd!="":
           
            query =f"insert into admin set admin_username ='{username}', admin_pwd='{hashed_pwd}'"   
            db.session.execute(text(query))
            db.session.commit()
            flash(f"registration sucessful login here")
            return redirect('/admin')
        else:
            #redirect the person to the login page and ask the person to login
            flash("username and password must be supplied")
            return redirect("/admin") 

@app.route("/admin/login" , methods=['POST','GET'])
def login():
    #let this route accept both post and get
    #in the get, display the template
    #in the post, retieve the data and wait for us
    if request.method=='GET':
        return render_template("admin/adminlogin.html")
    else:
        #TO DO retreive the data coming from the form and save in variables
        #retrieving data from form
        data = request.form
        username=data.get('username')
        pwd=data.get('pwd')
        #wrute query

        query = f"select * from admin where admin_username='{username}'"

        result= db.session.execute(text(query))#text....................................
        total=result.fetchone() #fetchone() or fetchmany(1)
        if total: #the login details are correct
            #save in session
            pwd_indb = total[2] #hashed pwd frm the database, now compare with pwd from form
            chk= check_password_hash(pwd_indb,pwd) #returns true or false
            if chk==True: #login is sucessful, save in session
                session['loggedin'] =username
                return redirect("/admin/dashboard") #create this route
            else:
                flash("invalid credentials")
                return redirect ("/admin/login")
        
@app.route("/admin/dashboard")
def admin_dashboard():
    # This protects our page page
    if session.get('loggedin') != None:
        return render_template("admin/index.html")
    else:
        return redirect("/admin/login")

@app.route("/admin/logout")
def admin_logout():
    if session.get('loggedin') != None:
        session.pop("loggedin", None) #pops session redirects to login 
    return redirect('/admin/login')

@app.route("/admin/party", methods=['POST','GET'])
def add_party():
    if session.get('loggedin') !=None:
        if request.method=="GET":

            return render_template('admin/addparty.html')

        else:
            partyname= request.form.get('partyname')
            code = request.form.get('partycode')
            contact = request.form.get('partycontact')
            #INSERT INTO THE PARTY USING ORM METHOD
            #step1:create an instance of party(ensure party is imported from models) obj = Classname(column1=value,column2=value)
            p =Party(party_name=partyname,party_shortcode=code, party_contact=contact)
            #step2: add to session
            db.session.add(p)
            #step3: commit the session
            db.session.commit()
            flash("party added")
            return redirect('/admin/parties')
    else:
        return  redirect('/admin/login')    

@app.route("/admin/parties")
def parties():
    #protect always protect
    if session.get('loggedin') !=None:
        #we will fetch from db using ORM Method
        data = db.session.query(Party).order_by((Party.party_name))#fri1..................................
        return render_template('/admin/allparties.html',data=data)
    else:
        return redirect('/admin/login')

