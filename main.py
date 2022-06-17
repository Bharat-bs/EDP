from flask import Flask, jsonify, render_template, request, json,send_file
from pyresparser import ResumeParser
from flask_cors import CORS, cross_origin
import pandas as pd
import flask
import urllib.request
from werkzeug.utils import secure_filename
import PyPDF2
import requests
import os
import pymongo
from bson import ObjectId

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = "secretkey123"
UPLOAD_FOLDER = 'Resumes/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

print("Starting server...")
ALLOWED_EXTENSIONS = set(['pdf'])
#
print("Connecting to mongodb")
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["findmyjob"]
print("connected")
# mycol = mydb["user_data"]
# mycol.update_many({}, {"$set":{"user_skills": []}})
# mycol.update_many({}, {"$set":{"recived_job":""}})
#
current_user = "123"
user_type = "client"
current_email = ""
current_user_id = ""
current_company_id=""
#
# df2 = pd.read_excel('EDP2.xlsx')
df2 = pd.read_csv('EDP3.csv')
df2 = df2.set_index(df2['Unnamed: 0'])
df2.drop(['Unnamed: 0'], axis=1)
dictt = df2.to_dict()
del dictt['Unnamed: 0']
#
skills_required = {
    "App development": {"java": 5, "kotlin": 8, "android studio": 10, "flutter": 10, "swift": 10, "xamarin": 10,
                        "reactnative": 10},
    "Cloud computing": {"aws": 8, "azure": 8, "gcp": 8, "openstack": 6, "linux": 3, "ubuntu": 3},
    "Database management": {"mysql": 10, "mongodb": 8, "firebase": 8, "PHP": 6, "nosql": 8},
    "Web development": {'react': 10, 'django': 7, 'nodejs': 9, 'reactjs': 10, 'php': 7, 'laravel': 5, 'magento': 5,
                        'wordpress': 6, 'javascript': 7, 'angularjs': 8, 'c#': 7, 'flask': 8, 'angular': 9, "html": 3,
                        "html5": 3, "css": 5, "typescript": 5, "jquery": 5},
    "Internet of things": {"javascript": 4, "python": 4, "nodejs": 4, "eclipseiot": 8, "arduino": 9, "m2mlabs": 6,
                           "m2m": 6, "raspbian": 10, "raspberry": 10},
    "Ui/Ux": {'ux': 6, 'adobexd': 8, 'figma': 8, 'zeplin': 8, 'balsamiq': 7, 'ui': 6, 'prototyping': 6, 'wireframes': 7,
              'storyframes': 7, 'adobephotoshop': 8, 'photoshop': 8, 'editing': 5, 'adobeillustrator': 9,
              'illustrator': 9, 'adobeaftereffects': 8, 'aftereffects': 8, 'adobepremierpro': 8, 'premierpro': 8,
              'adobeindesign': 8, 'indesign': 8, 'wireframe': 7},
    "Machine Learning": {"python": 7, "tensorflow": 9, "spark": 8, "hadoop": 8, "r": 6, "kafka": 7, "weka": 7,
                         "matlab": 5, "pytorch": 9, "jupyter": 7, "watson": 6},
    "data science": {"sas": 5, "spark": 8, "bigml": 7, "d3": 5, "matlab": 4, "excel": 5, "python": 4, "r": 5,
                     "julia": 6, "scala": 7},
    "cyber security": {"linux": 8, "metasploit": 10, "wireshark": 8, "splunk": 6, "nexpose": 6, "nagios": 6,
                       "keepass": 6, "nmap": 8, "ubuntu": 7, "powershell": 8},
    "game development": {"c++": 8, "c#": 7, "lua": 8, "unity": 9, "libgdx": 9, "unrealEngine": 9},
    "Software development": {"javascript": 5, "python": 6, "java": 8, "c++": 8, "mysql": 4},
}

keys = list(skills_required.keys())
#

skills = {'java', 'kotlin', 'android studio', 'flutter', 'swift', 'xamarin', 'reactnative', 'aws', 'azure', 'gcp',
          'openstack', 'linux', 'ubuntu', 'mysql', 'mongodb', 'firebase', 'PHP', 'nosql', 'react', 'django', 'nodejs',
          'reactjs', 'php', 'laravel', 'magento', 'wordpress', 'javascript', 'angularjs', 'c#', 'flask', 'angular',
          'html', 'html5', 'css', 'typescript', 'jquery', 'javascript', 'python', 'nodejs', 'eclipseiot', 'arduino',
          'm2mlabs', 'm2m', 'raspbian', 'raspberry', 'ux', 'adobexd', 'figma', 'zeplin', 'balsamiq', 'ui',
          'prototyping', 'wireframes', 'storyframes', 'adobephotoshop', 'photoshop', 'editing', 'adobeillustrator',
          'illustrator', 'adobeaftereffects', 'aftereffects', 'adobepremierpro', 'premierpro', 'adobeindesign',
          'indesign', 'wireframe', 'python', 'tensorflow', 'spark', 'hadoop', 'r', 'kafka', 'weka', 'matlab', 'pytorch',
          'jupyter', 'watson', 'sas', 'spark', 'bigml', 'd3', 'matlab', 'excel', 'python', 'r', 'julia', 'scala',
          'linux', 'metasploit', 'wireshark', 'splunk', 'nexpose', 'nagios', 'keepass', 'nmap', 'ubuntu',
          'powershell', 'c++', 'c#', 'lua', 'unity', 'libgdx', 'unrealEngine'}


#
def parse_string(s):
    s = s.strip()
    s = s.lower()
    return s.replace(" ", "")


#

##
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")  # this sets the route to this page
def home():
    return render_template("login.html")


#

@app.route("/login1", methods=['POST'])
def loginn():
    email_id = request.form["email"]
    password = request.form["password"]
    mycol = mydb["user_data"]
    for x in mycol.find({"email": email_id, "password": password}):
        global current_email, current_user, current_user_id, user_type
        current_user = x["name"]
        current_email = email_id
        current_user_id = x["_id"]
        user_type = "employee"
        return render_template("home.html")
    return render_template("login1.html")


@app.route("/login2", methods=['POST'])
def loginnn():
    email_id = request.form["email"]
    password = request.form["password"]
    mycol = mydb["employer_data"]
    for x in mycol.find({"email": email_id, "password": password}):
        global current_email, current_user, current_user_id, user_type
        current_user = x["name"]
        current_email = email_id
        current_user_id = x["_id"]
        user_type = "employer"
        return render_template("home.html")
    return render_template("login2.html")


@app.route("/getuserdetails", methods=['GET'])
def get_details():
    return jsonify({'user': current_user, 'type': user_type})


@app.route("/update_resume", methods=['POST'])
def update():
    pass


@app.route("/post_job", methods=['POST'])
def upload_job():
    job_title = request.form["jobtitle"]
    job_category = request.form["jobcategory"]
    job_company = request.form["jobcompany"]
    job_salary = request.form["jobsalary"]
    job_type = request.form["type"]
    job_location = request.form["location"]
    mycol = mydb["jobs"]
    mydict = {'job_title': job_title, 'job_category': job_category, 'job_company': job_company,
              'job_salary': job_salary, 'job_type': job_type, 'job_location': job_location, 'job_status': 1}
    print(mydict)
    x = mycol.insert_one(mydict)
    return render_template('post.html')


@app.route("/user_details", methods=['POST'])
@cross_origin(origin='*')
def store_user_details():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]
    mycol = mydb["user_data"]

    mydict = {"name": name, "email": email, "password": password, "resume": email + "_resume.pdf"}
    mydict["user_skills"] = []
    mydict["recived_job"] = ""
    x = mycol.insert_one(mydict)
    if 'files[]' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp
    files = request.files.getlist('files[]')
    errors = {}
    success = False
    for file in files:
        if file and allowed_file(file.filename):
            filename = email + "_resume.pdf"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            success = True
        else:
            errors[file.filename] = 'File type is not allowed'

    if success and errors:
        errors['message'] = 'File(s) successfully uploaded'
        resp = jsonify(errors)
        resp.status_code = 500
        return render_template('login1.html')
    if success:
        resp = jsonify({'message': 'Files successfully uploaded'})
        resp.status_code = 201
        return render_template('login1.html')
    else:
        resp = jsonify(errors)
        resp.status_code = 500
        return render_template('login1.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files[]' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp
    files = request.files.getlist('files[]')
    errors = {}
    success = False
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            success = True
        else:
            errors[file.filename] = 'File type is not allowed'

    if success and errors:
        errors['message'] = 'File(s) successfully uploaded'
        resp = jsonify(errors)
        resp.status_code = 500
        return resp
    if success:
        resp = jsonify({'message': 'Files successfully uploaded'})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify(errors)
        resp.status_code = 500
        return resp


def load_file():
    print("email : " + current_email, "name : " + current_user)
    data = ResumeParser('Resumes/' + current_email + "_resume.pdf").get_extracted_data()
    # data = ResumeParser('Resumes/BHARAT_RESUME.pdf').get_extracted_data()
    print("skills : ", data['skills'])
    user_skills = data['skills']
    return user_skills


@app.route('/getscore', methods=['GET'])
@cross_origin(origin='*')
def calculate_skills():
    user_skills = load_file()
    score = {'App development': 0,
             'Cloud computing': 0,
             'Database management': 0,
             'Infrastructure': 0,
             'Internet of things': 0,
             'Machine Learning': 0,
             'Maintenance and repair': 0,
             'Networks': 0,
             'Ui/Ux': 0,
             'Robotics': 0,
             'Software development': 0,
             'cyber security': 0,
             'data science': 0,
             'game development': 0,
             'software testing': 0,
             'Web development': 0
             }
    recogonised_skills = set()
    for i in user_skills:
        i = parse_string(i)
        for j in keys:
            if i in dictt[j]:
                recogonised_skills.add(i)
                indvidual_score = dictt[j][i]
                score[j] += indvidual_score
    sorted_dict = list(dict(sorted(score.items(), key=lambda item: item[1])))
    sorted_dict.reverse()
    recogonised_skills = list(recogonised_skills)
    print(recogonised_skills)
    mycol2 = mydb["user_data"]
    mycol2.update_one({'_id': current_user_id}, {"$set": {"user_skills": recogonised_skills}})
    mycol = mydb["jobs"]
    jobs_list = []
    send_jobs = []
    query = mycol.find({'job_status': 1})
    for i in query:
        i["_id"] = str(i["_id"])
        jobs_list.append(i)

    for i in sorted_dict:
        for j in jobs_list:
            cate = j['job_category']
            if i == cate:
                send_jobs.append(j)

    print("user strength : ", sorted_dict[0:2])
    print("Recomendation category : ", sorted_dict)

    return jsonify(send_jobs)


print(current_user_id)


# calculate_skills()


@app.route("/applied", methods=['POST'])
@cross_origin(origin='*')
def applied():
    data = request.json
    data['current_user_id'] = str(current_user_id)
    mycol = mydb["applied_job"]
    mycol2 = mydb["jobs"]
    id = data["job_id"]
    x = mycol.insert_one(data)
    x1 = mycol2.update_one({"_id": ObjectId(id)}, {"$set": {"job_status": 0}})
    print(x1.raw_result)
    return "kjwdv"


@app.route("/getapplied", methods=['GET'])
@cross_origin(orgin="*")
def getapplied():
    mycol = mydb["applied_job"]
    jobs_list = []
    print(current_user_id)
    # {'current_user_id': current_user_id}
    # query = mycol.find({'current_user_id': str(current_user_id)})
    query = mycol.find()
    # query = mycol.find()
    for i in query:
        i["_id"] = str(i["_id"])
        jobs_list.append(i)
        user = i["current_user_id"]
        query2 = mydb["user_data"].find_one({'_id':ObjectId(user)})
        print(query2)
        i["user_name"]=query2["name"]
        i["user_email"]=query2["email"]
        i["user_resume"]=query2["resume"]
    print(jobs_list)
    return jsonify(jobs_list)


@app.route("/updateapplied", methods=['POST'])
@cross_origin(orgin="*")
def updateapplied():
    mycol = mydb["applied_job"]
    data = request.json
    id = str(data["_id"])
    print(id)
    id2 = str(data["job_id"])
    mycol.delete_one({'_id': ObjectId(id)})
    mycol2 = mydb["jobs"]
    x1 = mycol2.update_one({"_id": ObjectId(id2)}, {"$set": {"job_status": 1}})
    return "123"


@app.route("/selected", methods=['POST'])
def update_selected():
    data = request.json
    mycol = mydb["user_data"]
    print(data)
    user = data["user_id"]
    user = str(user)
    print(user)
    mycol2 = mydb["applied_jobs"]

    job_cat = data["job_category"]
    print(current_user_id)
    query = mycol.find_one({"_id": ObjectId(user)})
    print(query['user_skills'])
    df3 = pd.read_csv('EDP3.csv')
    df3 = df3.set_index(df3['Unnamed: 0'])
    df3.drop(['Unnamed: 0'], axis=1)
    dict3 = df3.to_dict()
    del dict3['Unnamed: 0']
    for i in query['user_skills']:
        df3[job_cat][i] += 1
        print(df3[job_cat][i])
    df3.to_csv('EDP3.csv')
    return 123

@app.route('/downfile/<path:filename>', methods=['GET','POST'])
def downfile(filename):
    uploads = UPLOAD_FOLDER + filename
    return send_file(uploads,as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
