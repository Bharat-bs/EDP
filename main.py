from flask import Flask, jsonify, render_template, request, json
from pyresparser import ResumeParser
from flask_cors import CORS, cross_origin
import flask
import urllib.request
from werkzeug.utils import secure_filename
import PyPDF2
import requests
import os
import pymongo

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
#
current_user = "123"
user_type = "client"
current_email = ""
current_user_id = ""
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
        global current_email,current_user,current_user_id,user_type
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
        global current_email,current_user,current_user_id,user_type
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
    print(request.files)
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
        return resp
    if success:
        resp = jsonify({'message': 'Files successfully uploaded'})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify(errors)
        resp.status_code = 500
        return resp


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
    print(current_email,current_user)
    data = ResumeParser('Resumes/' + current_email + "_resume.pdf").get_extracted_data()
    # data = ResumeParser('Resumes/BHARAT_RESUME.pdf').get_extracted_data()
    print(data)
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
             'Robotics': 0,
             'Software development': 0,
             'cyber security': 0,
             'data science': 0,
             'game development': 0,
             'software testing': 0,
             'Web development': 0}

    for i in user_skills:
        i = parse_string(i)
        for j in keys:
            if i in skills_required[j]:
                indvidual_score = skills_required[j][i]
                score[j] += indvidual_score
    max_value = 0
    max_key = ""
    sorted_dict = list(dict(sorted(score.items(), key=lambda item: item[1])))
    sorted_dict.reverse()

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
    print(sorted_dict)
    # return "bharat"
    return jsonify(send_jobs)


# calculate_skills()


@app.route("/applied", methods=['POST'])
@cross_origin(origin='*')
def applied():
    data = request.json
    data['current_user_id']=str(current_user_id)
    mycol = mydb["applied_job"]
    x = mycol.insert_one(data)
    return "kjwdv"


if __name__ == "__main__":
    app.run(debug=True)
