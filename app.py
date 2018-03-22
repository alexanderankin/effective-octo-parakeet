import json, hashlib, uuid, string, random, re

from flask import Flask, request, jsonify, redirect, session
app = Flask(__name__)

app.secret_key = b"cookie secret"
secret = b"secret"

from sqlalchemy import create_engine
# engine = create_engine('sqlite:///file.db')
engine = create_engine('sqlite:///:memory:')

connection = engine.connect()
connection.execute("""
  create table student (
    id integer primary key autoincrement,
    name text,
    username varchar(30),
    password varchar(32),
    email text
    );
  """)
connection.execute("""
  create table instructor (
    id integer primary key autoincrement,
    name text,
    username varchar(30),
    password varchar(32),
    email text
    );
  """)
connection.execute("""
  create table signup (
    id integer primary key autoincrement,
    type_ integer,
    code varchar(36),

    name text,
    username varchar(30),
    password varchar(32),
    email text
    );
  """)
connection.execute("create unique index u_email_signup on signup(email);")
connection.execute("""
  create table class (
    id integer primary key autoincrement,
    name varchar(30)
    );
  """)
connection.execute("""
  create table student_class (
    student integer,
    class integer
    );
  """)
connection.execute("""
  create table instructor_class (
    student integer,
    class integer
    );
  """)
connection.execute("""
  create table group_ (
    id integer primary key autoincrement,
    class integer,
    name text
    );
  """)
connection.execute("""
  create table group_student (
    group_ integer,
    student integer
    );
  """)
connection.close()


# connection = engine.connect()
# res = connection.execute("select ? as 'a', ? as 'b';", 2, 5)
# rows = res.fetchall()
# print(rows)
# connection.close()

students = [
  { 'id': 1, 'name': 'Alice', 'username': 'ali', 'password': hashlib.md5(b"a" + secret).hexdigest()},
  { 'id': 2, 'name': 'Bobby', 'username': 'bob', 'password': hashlib.md5(b"b" + secret).hexdigest()},
  { 'id': 3, 'name': 'Carol', 'username': 'crl', 'password': hashlib.md5(b"c" + secret).hexdigest()},
  { 'id': 4, 'name': 'Danny', 'username': 'dan', 'password': hashlib.md5(b"d" + secret).hexdigest()},
  { 'id': 5, 'name': 'Edith', 'username': 'edi', 'password': hashlib.md5(b"e" + secret).hexdigest()},
]

c = engine.connect()
for s in students:
  c.execute("""
    insert into student (name, username, password) values (?, ?, ?);""",
    s['name'], s['username'], s['password']);
c.close()

instructors = [
  { 'id': 1, 'name': 'Jack', 'username': 'jacka', 'password': hashlib.md5(b"nope" + secret).hexdigest()},
  { 'id': 2, 'name': 'Jill', 'username': 'jillb', 'password': hashlib.md5(b"sure" + secret).hexdigest()}
]

c = engine.connect()
for i in instructors:
  c.execute("""
    insert into instructor (name, username, password) values (?, ?, ?);""",
    i['name'], i['username'], i['password']);
c.close()

classes = [
  { 'id': 1, 'name': 'CS 1555 MW', 'students': [] },
  { 'id': 2, 'name': 'CS 1555 TT', 'students': [] },
]

@app.route("/")
def hello():
  return "Hello World!"

@app.route("/api/login/user", methods=['POST'])
def api_login_user():
  username = request.form.get('username')
  
  c = engine.connect()
  response = c.execute("select * from student where username = ?;", username)
  data = response.fetchall()
  if len(data) == 1:
    c.close()
    u = dict(data[0])
    del u['password']
    return jsonify(u)

  response = c.execute("select * from instructor where username = ?;", username)
  data = response.fetchall()
  if len(data) == 1:
    c.close()
    u = dict(data[0])
    del u['password']
    return jsonify(u)
  

  c.close()
  return jsonify({ 'err': 'Unspecified error' })

@app.route("/api/login/credentials", methods=['POST'])
def api_login_credentials():
  f = request.form
  username, password = f.get('username'), f.get('password')
  password = password.encode('utf-8')
  password_hash = hashlib.md5(password + secret).hexdigest()

  c = engine.connect()
  response = c.execute("""
    select * from student where username = ? and password = ?;""",
    username, password_hash
    )
  data = response.fetchall()
  if len(data) == 1:
    c.close()
    u = dict(data[0])
    del u['password']
    u['redirect_to'] = '/students'
    session['userid'] = dict(data[0])['id']
    return jsonify(u)

  response = c.execute("""
    select * from instructor where username = ? and password = ?;""",
    username, password_hash
    )
  data = response.fetchall()
  if len(data) == 1:
    c.close()
    u = dict(data[0])
    u['redirect_to'] = '/instructors'
    del u['password']
    session['userid'] = dict(data[0])['id']
    return jsonify(u)

  c.close()
  return jsonify({ 'err': 'Unspecified error' })

last_code = None
@app.route("/api/login/signup", methods=['POST'])
def api_login_signup():
  # print(request.form.get('type'))
  type_ = 0 if request.form.get('type') == 'student' else 1
  # print(type_)
  code = str(uuid.uuid4())
  global last_code
  last_code = code

  username = request.form.get('username')
  email = request.form.get('email')
  name = request.form.get('name')

  if name is None or username is None or email is None:
    return jsonify({ 'err': 'Unspecified error' })

  password = b""
  for count in range(32):
    next_i = random.randrange(len(string.ascii_letters))
    password += string.ascii_letters[next_i].encode('utf-8')
  password_hash = hashlib.md5(password + secret).hexdigest()

  c = engine.connect()
  r = c.execute("""
    select count(*)
    from (select * from student union select * from instructor)
    where email=?;""",
    email
    )
  if r.scalar() != 0:
    c.close()
    return jsonify({ 'err': 'Unspecified error' })

  try:
    send_email(email, username, password, code)
  except Exception as e:
    return jsonify({ 'err': 'Unspecified error' })

  try:
    response = c.execute("""
      insert into signup (type_, code, name, username, password, email)
      values (?, ?, ?, ?, ?, ?);""",
      type_, code, name, username, password_hash, email
      )
  except Exception as e:
    return jsonify({ 'err': 'Unspecified error' })

  c.close()
  return jsonify({ 'status': 'success' })

@app.route("/signup", methods=['GET'])
def email_code_submit():
  code = request.args.get('code')
  if not code:
    return "No code submitted"

  c = engine.connect()
  response = c.execute("select * from signup where code = ?", code)
  data = response.fetchall()
  if len(data) != 1:
    c.close()
    return "Unique code not found"

  # print("len(data) == 1")
  c.execute("delete from signup where code = ?", data[0]['code'])
  # print(type(data[0]['type_']))
  # print(data[0]['type_'])
  table = 'student' if data[0]['type_'] == 0 else 'instructor'
  response = c.execute("""
    insert into %s (name, username, password, email)
    values (?, ?, ?, ?);""" % table,
    data[0]['name'],
    data[0]['username'],
    data[0]['password'],
    data[0]['email']
    )

  c.close()
  dest = '/students' if data[0]['type_'] == 0 else '/instructors'
  return redirect(dest)

@app.route("/logout", methods=['GET'])
def logout():
  session['userid'] = None
  return redirect('/')

@app.route("/students", methods=['GET'])
def student_home():
  if session['userid']:
    return str(session['userid'])
  return "student home"

@app.route("/instructors", methods=['GET'])
def instructor_home():
  return "instructor home"

@app.route("/api/students/", methods=['GET'])
def students_data():
  pass

if __name__ == '__main__':
  app.run()

def send_email(email, username, password, code):
  if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
    raise Exception("Could not send to this email")
