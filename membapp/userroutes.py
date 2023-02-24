#import from 3rd party
import requests
import os, json,random,string
from sqlalchemy import or_
from flask import render_template, redirect, flash, session,request, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import text

#import from local file


from membapp import app,db,csrf

from membapp.forms import ContactForm

from membapp.models import Party, Comments, Topics,State,Lga,User, Contact, Donation,Payment ##check it oot



def generate_name():
    #will return a list
    filename=random.sample(string.ascii_lowercase,10)
    #will join the members of the list
    return ''.join(filename)#join every member of the list filename
#3.........................................................................................................................

@app.route('/check_username', methods=['POST'])
def check_username():

    email = request.form.get('email')
    
    data = db.session.query(User).filter(User.user_email == email).first()

    if data==None:
        sendback = {'status': 1,'feedback': "Email is available, please register"}
        return json.dumps(sendback)
    else:
        sendback = {'status': 0,'feedback': "You have registered already, click here to login"}
        return json.dumps(sendback)

@app.route('/load_lga/<stateid>')

def load_lga(stateid):
    lgas = db.session.query(Lga).filter(Lga.lga_stateid==stateid).all()
    data2send="<select class='Form-control border-success'>"

    for s in lgas:
        data2send = data2send+"<option>"+s.lga_name+"</option>"
    
    data2send= data2send +"</select>"
    return data2send

@app.route("/")
def home():
    contact=ContactForm()
    #convert to the endpoint to get the list of properties in json format
    #convert to python dictionary and pass it to our template

    # response = requests.get("http://127.0.0.1:8000/api/v1.0/listall") 
    # if response:
    #     rspjson = json.loads(response.text)
    # else:
    #     rspjson={}    #nice........................................................................................................
    return render_template('user/home.html', contact=contact) 
#create an instance of contactform

@app.route("/ajaxcontact", methods=['POST']) 
def contact_ajax():
    email = request.form.get('email')
    msg= request.form.get('msg')
    return f"{email} and{msg}"



@app.route("/user/signup" ,methods=['POST','GET'])
def user_signup():
    #fetch all the party from party table so that we can display in a select drop down
    p = db.session.query(Party).all()
     #party.query.all()
    return render_template("user/signup.html", p=p)
    
    

#TO DO within the signup.html loopovear p and isplay in dropdown submit by post

#ass: this is where the signup form will be submitted.. follow the exaample of the admin signuphat we did in the mprnig

@app.route("/register", methods=['POST'])
def register():
    #TO DO: retrieve all the form data and insert into the user table
    #set a session  session['user]=keep the email
    #redit=rect them to profile/dashboard
    party = request.form.get('party_id')
    email = request.form.get('email')
    pwd = request.form.get('pwd')
    
    hashed_pwd= generate_password_hash(pwd)
    if party !='' and email !='' and pwd !='':
        #insert into database using ORM Method
        u = User( user_email=email, user_pwd=hashed_pwd, user_partyid=party)
        db.session.add(u)
        db.session.commit()
        #create session
        userid = u.user_id #use user id because it is a unique identifier
        session['user'] = userid #keep
        
        return redirect (url_for('dashboard')) #create function dashboard
    else:
        flash('you must complete all fields')
        return redirect(url_for(user_signup)) 

@app.route("/user/login" ,methods =['GET', 'POST'])
def user_login():
    if request.method =='GET':
        return render_template('user/login.html')
    else: 
        
        #retieve the data
        email= request.form.get('email')
        pwd = request.form.get('pwd')
        #run a query to know if the username existson the database
        deets = db.session.query(User).filter(User.user_email == email).first()#loooooooooooooooooooooooooooooooooooooooo
        #compare the password coming from the form with the hases password in db

        if deets!= None:
            pwd_indb = deets.user_pwd
            #compare with the plain password from the form
            chk = check_password_hash(pwd_indb, pwd)
            if chk:
                #we should log the person in
                id = deets.user_id
                session['user'] =id 
                return redirect (url_for("dashboard"))
            else:
                flash("Invalid password")
                return redirect (url_for('user_login'))
        else:
            flash("Invalid Username")
            return redirect(url_for('user_login'))
        #if the password check above is right, we should
        #by  keeping their details (user_id in session[user])
        #and redirect them to the dashboard

@app.route('/dashboard' ,methods=['GET','POST'])
def dashboard():
    #protect the route so that only logged in user can get here

    if session.get('user') !=None:
        #retrieve the details of our logged in user
        id =session['user']
        deets=db.session.query(User).get(id)                                #try this..............................................
        return render_template('user/dashboard.html', deets=deets)
    else:
        return redirect(url_for('user_login'))


#ds.session.query(classname).filter(classname.column=='value')
@app.route("/demo")
def demo():
    #data = db.session.query(User,Party).join(Party).all() ######query 1
    #data = db.session.query(User.user_fullname, Party.party_name, Party.party_contact, Party.party_shortcode).join(Party).all()#checkout demooooooo
   #query specifying the keyss data=db.session.query(User,Party).join(Party, User.user_partyid==Party.party_id).all()
   #or_
    
    #data = User.query.join(Party).filter(or_ (Party.party_name=='labour party',Party.party_name=="people's Democatic party")).add_columns(Party).all()
    #.get erturns onevalue
    #data = db.session.query(Party).filter(Party.party_id>1,Party.party_id <=6).all()
    # data = db.session.query(Party).filter(Party.party_id>1).filter(Party.party_id <=6).all()
    #classwork #f"Select * from user where user_email='{email}' and user_pwd ='{pwd}'"
    #db.session.query(User).filter(User.user_email == email, User.user_pwd==pwd).first()
    #.first() #none if nothing is found
    #.all() [] if nothing is found

    #data= db.session.query(Party).filter(Party.party_id==4).first()
    data= db.session.query(User).get(1) 
    #the above displays party instances and relationships
    return render_template("user/test.html", data=data)

@app.route('/logout')
def user_logout():
    if session.get('user') != None:
        session.pop('user',None)
    return redirect('/')

@app.route('/profile', methods=['POST','GET'])
def profile():
    id = session.get('user')
    if id:
        if request.method=="GET":
            allstates = db.session.query(State).all()
            deets = db.session.query(User).get(id)
            #or db.session.query(user).filter(User.user_id==id).first()
            return render_template('user/profile.html', deets=deets)
        else: #form was submitted
            #to do: retreive form data(fullname and phone), save them in respective variables and wait for us
            fullname=request.form.get('fullname')
            phone = request.form.get('phone')
            #update query
            #update the db using ORM
            userobj = db.session.query(User).get(id)
            userobj.user_fullname = fullname
            userobj.user_phone = phone
            db.session.commit()
            return 'uploaded'
    else:
        return redirect(url_for('user_login')) 

 
@app.route('/profile/picture', methods=['POST', 'GET'])
def profile_picture():
    if session.get('user') == None:
        return redirect(url_for('user_login')) 
    else: 
        if request.method=='GET':
            return render_template('user/profile_picture.html') 
        else:
            #retrieve file
            file = request.files['pix']
            #to know the filename
            filename = file.filename #original file name
            filetype=file.mimetype
            allowed =['.png','.jpg','.jpeg']
            if filename !="":
                name,ext = os.path.splitext(filename)    #do not understand......................................................
                #this saves files in new name
                newname=generate_name()+ext
                if ext.lower() in allowed:
                    file.save("membapp/static/uploads/"+newname) #it will upload the picture and save it as a picture.png, save it as the original fil
                    #update the table using ORM
                    id= session.get('user')
                    user_obj= db.session.query(User).get(id)
                    user_obj.user_pix = newname 
                    db.session.commit()

                    flash("file Uploaded")
                    return redirect(url_for('dashboard'))
            else:
                flash('please choose a file')
                return "form was not submitted properly"


@app.route('/blog')
def blog():
   #gets all the blogs
    articles=db.session.query(Topics).filter(Topics.topic_status=='1').all()

    return render_template('user/blog.html' ,articles=articles)

@app.route('/blog/<id>/', methods=['GET','POST']) #id object
def blog_details(id): #............................................................................................
   #gets all the blogs
   #TO DO: write a query that will fetch the topic with id
   #create blog_details.html and pass the blog deets to it
   blog_deets= db.session.query(Topics).filter(Topics.topic_id==id).first()  
   #method 2 
   #blog_deets=db.session.query(Topics).get(id)
   #blog_deets = Topics.query.get(id) 

   #if blog_deets or use query.get_or_404(id) 


   #blog_details, use blog html to save as
   return render_template('user/blog_details.html', blog_deets=blog_deets) 

@app.route('/sendcomment')
def sendcomment():
    if session.get('user'):
        #retrieve the data coming from the request
        usermessage = request.args.get('message')
        #we can insert into db
        user = request.args.get('userid')
        topic = request.args.get('topicid')
        comment = Comments(comment_text=usermessage,comment_userid=user,comment_topicid=topic)
        db.session.add(comment)
        db.session.commit()
        commenter = comment.commentby.user_fullname
        dateposted = comment.comment_date
        sendback = f"{usermessage}<br> by {commenter} on {dateposted}"
        return sendback
    else:
        return "Comment was not posted, you need to be logged in"
   
   
@app.route('/newtopic', methods = ['GET','POST'])
def newtopic():
    if session.get('user') !=None:
        if request.method == 'GET':

            return render_template('user/newtopic.html')
        else:
            #retieve form data
            content = request.form.get('content') #your textarea name = content
            if len(content)>0:
                t= Topics(topic_title=content,topic_userid=session['user'])
                db.session.add(t)
                db.session.commit()
                if t.topic_id: 
                    flash("post successfully submitted for approval")
                else:
                    flash("oops, something broke")
                
            else:
                flash("you cannot submit an empty post")
               
            return redirect(url_for('blog'))
    else:
        return redirect(url_for('user_login')) 







@app.route("/donate", methods=["POST","GET"])
def donate():
    if session.get('user') !=None:
        deets=User.query.get(session.get('user')) #............................................
    else:
        deets=None
    if request.method=='GET':
        return render_template('user/donation_form.html', deets=deets)
    else:
        amount= request.get('amount')
        fullname= request.get('fullname')
        
        d = Donation(don_donor=fullname, don_amt=amount, don_userid=session.get('user'))
        db.session.add(d);db.session.commit()
        session['donation_id'] = d.don_id
        #Generate the ref no and insert into table
        refno = int(random.random()*10000000) #.....................................................
        session['reference']=refno
        
        return redirect("/confirm")

@app.route("/confirm", methods=['GET','POST'])

def confirm():
    if session.get('donation_id') != None:

        if request.method=='GET':
            
            
            donor= db.session.query(Donation).get(session['donation_id'])
            return render_template('user/confirm.html', donor=donor, refno=session['reference'])
        else:
            p = Payment(pay_donid=session.get('donation_id'), pay_ref=session['reference'])
            db.session.add(p);db.session.commit()

            don = Donation.query.get(session['donation_id'])#details of donation
            donor_name = don.don_donor
            amount=don.don_amt * 100

            headers={"content-Type": "application/json", "Authorization":"Bearer sk_test_3763298y943832y93ydhdbi23hdbi283"}
            data={"amount":500, "reference":session['reference'], "email":"abc@yahoo.com" }
            response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, data=json.dumps(data))
            rspjson = json.loads(response.text)
            if rspjson['status']==True:

                url=rspjson['data']['authorization_url']
                return redirect(url)
            else:
                return redirect('/confirm')
    else:
        return redirect('/donate')
    
@app.route('/paystack')
def paystack():
    refid = session.get('reference')
    if refid ==None:
        return redirect('/')
    else:
        #connect to paystack verify
        headers={"Content-Type": "application/json","Authorization":"Bearer sk_test_3c5244cfb8965dd000f07a4cfa97185aab2e88d5"}
        verifyurl= "https://api.paystack.co/transaction/verify/"+str(refid)
        response= requests.get(verifyurl, headers=headers)
        rspjson = json.loads(response.text)
        if rspjson['status']== True:
            #payment was successful
            return rspjson
        else:
            #payment was not successful
            return "payment was not successful" 


#for the contact us form csrf file
@app.route('/contact',methods=['GET','POST'])
def contact_us():
    contact = ContactForm()
    if request.method == 'GET':
        return render_template('user/contact_us.html',contact=contact)
    else:
        if contact.validate_on_submit():
            #retrieve form data and insert into db
            upload = contact.screenshot.data #request.files.get('screenshot)
            email = request.form.get('email')
            msg = contact.message.data
            #insert into database
            m = Contact(msg_email=email,msg_content=msg)
            db.session.add(m)
            db.session.commit()
            flash("Thank you for contacting us")
            return redirect(url_for('contact_us'))
        else:
            return render_template('user/contact_us.html',contact=contact)


