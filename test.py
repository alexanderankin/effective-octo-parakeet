import json
import unittest
import sys
from six.moves.urllib.parse import urlparse

import app


class Test(unittest.TestCase):
  def setUp(self):
    self.app = app.app.test_client()
  def test_example(self):
    response = self.app.get('/')
    assert(2 == 2)


@unittest.skip("Development")
class LoginTest(unittest.TestCase):
  """This is testing the endpoints in /api/login"""
  def setUp(self):
    self.app = app.app.test_client()

  def test_user_malformed(self):
    response = self.app.post('/api/login/user', data={ 'username_': 'miss' })
    body = json.loads(response.get_data(as_text=True))
    self.assertEqual({ 'err': 'Unspecified error' }, body)

  def test_user_missing(self):
    response = self.app.post('/api/login/user', data={ 'username': 'miss' })
    body = json.loads(response.get_data(as_text=True))
    self.assertEqual({ 'err': 'Unspecified error' }, body)

  def test_student_user_present(self):
    response = self.app.post('/api/login/user', data={ 'username': 'ali' })
    body = json.loads(response.get_data(as_text=True))
    expected = {
      u'username': u'ali',
      u'email': None,
      u'name': u'Alice',
      u'id': 1
      }
    self.assertEqual(expected, body)

  def test_instructor_user_present(self):
    response = self.app.post('/api/login/user', data={ 'username': 'jacka' })
    body = json.loads(response.get_data(as_text=True))
    expected = {
      u'username': u'jacka',
      u'email': None,
      u'name': u'Jack',
      u'id': 1
      }
    self.assertEqual(expected, body)

  def test_credentials_bad(self):
    data = {
      'username': b'whoami',
      'password': b'idkfam',
    }
    response = self.app.post('/api/login/credentials', data=dict(data))
    body = json.loads(response.get_data(as_text=True))
    self.assertEqual({ 'err': 'Unspecified error' }, body)

  def test_credentials_bad_password(self):
    data = {
      'username': 'ali',
      'password': 'idkfam',
    }
    response = self.app.post('/api/login/credentials', data=dict(data))
    body = json.loads(response.get_data(as_text=True))
    self.assertEqual({ 'err': 'Unspecified error' }, body)

  def test_student_credentials(self):
    data = {
      'username': b'ali',
      'password': b'a',
    }
    response = self.app.post('/api/login/credentials', data=dict(data))
    body = json.loads(response.get_data(as_text=True))
    expected = {
      'username': 'ali',
      'redirect_to': '/students',
      'email': None,
      'name': 'Alice',
      'id': 1
      }
    self.assertEqual(expected, body)
    # print(expected, body)

  def test_instructor_credentials(self):
    data = {
      'username': b'jacka',
      'password': b'nope',
    }
    response = self.app.post('/api/login/credentials', data=dict(data))
    body = json.loads(response.get_data(as_text=True))
    expected = {
      'username': 'jacka',
      'redirect_to': '/instructors',
      'email': None,
      'name': 'Jack',
      'id': 1
      }
    self.assertEqual(expected, body)
    # print(expected, body)

  def test_signup_missing(self):
    response = self.app.post('/api/login/signup', data=None)
    body = json.loads(response.get_data(as_text=True))
    self.assertEqual({'err': 'Unspecified error'}, body)

  def test_signup_bad_email(self):
    data = {
      'username': 'test',
      'email': 'invalidemail',
      'name': 'Test User'
    }
    response = self.app.post('/api/login/signup', data=dict(data))
    body = json.loads(response.get_data(as_text=True))
    self.assertEqual({'err': 'Unspecified error'}, body)

  def test_signup_duplicate_email(self):
    data = {
      'username': 'test',
      'email': 'invalidemail',
      'name': 'Test User'
    }
    response = self.app.post('/api/login/signup', data=dict(data))
    body = json.loads(response.get_data(as_text=True))
    self.assertEqual({'err': 'Unspecified error'}, body)

  def test_signup(self):
    data = {
      'username': 'test',
      'email': 'test@example.com',
      'name': 'Test User'
    }
    response = self.app.post('/api/login/signup', data=dict(data))
    body = json.loads(response.get_data(as_text=True))
    self.assertEqual({ 'status': 'success' }, body)

  def test_signup_no_code(self):
    response = self.app.get('/signup')
    self.assertEqual("No code submitted", response.get_data(as_text=True))

  def test_signup_bad_code(self):
    response = self.app.get('/signup?code=helloworld')
    self.assertEqual("Unique code not found", response.get_data(as_text=True))


@unittest.skip("Development")
class SignupTest(unittest.TestCase):
  def setUp(self):
    self.app = app.app.test_client()

  def test_finish_signup_duplicate_signup(self):
    data = {
      'username': 'test',
      'email': 'test2@example.com',
      'name': 'Test User',
      'type': 'student'
    }
    response = self.app.post('/api/login/signup', data=dict(data))
    body = json.loads(response.get_data(as_text=True))
    self.assertEqual({ 'status': 'success' }, body)
    # print({ 'status': 'success' }, body)

    data = {
      'username': 'test',
      'email': 'test2@example.com',
      'name': 'Test User',
      'type': 'student'
    }
    response = self.app.post('/api/login/signup', data=dict(data))
    body = json.loads(response.get_data(as_text=True))
    self.assertEqual({ 'err': 'Unspecified error' }, body)
    # print({ 'err': 'Unspecified error' }, body)


    """this happens after send_email(email, username, password, code)"""
  def test_finish_signup_duplicate_user(self):
    data = {
      'username': 'test',
      'email': 'test@example.com',
      'name': 'Test User - already signed up',
      'type': 'student'
    }
    response = self.app.post('/api/login/signup', data=dict(data))
    body = json.loads(response.get_data(as_text=True))
    self.assertEqual({ 'err': 'Unspecified error' }, body)

    """this happens after send_email(email, username, password, code)"""
  def test_finish_signup_instructor(self):
    data = {
      'username': 'test',
      'email': 'test1@example.com',
      'name': 'Test User',
      # 'type': 'student'
    }
    response = self.app.post('/api/login/signup', data=dict(data))
    body = json.loads(response.get_data(as_text=True))
    self.assertEqual({ 'status': 'success' }, body)

    connection = app.engine.connect()
    code = connection.execute("""
      select code from signup
      where username = ? and email = ? and name = ?;""",
      data['username'],
      data['email'],
      data['name']
      ).fetchall()[0]['code']
    # print(code)

    response = self.app.get('/signup?code=%s' % code)
    redirected = urlparse(response.location)[2]
    self.assertEqual('/instructors', redirected)

# @unittest.skip("Development")
class StudentPanelTest(unittest.TestCase):
  def setUp(self):
    self.app = app.app.test_client()
    self.login()

  # def tearDown(self):
  #   logout()

  def login(self):
    data = dict({ 'username':'ali', 'password':'a' })
    result = self.app.post('/api/login/credentials', data=data)

  def logout(self):
    self.app.get('/logout')

  def test_session(self):
    print(self.app.get('/students').get_data(as_text=True))

if __name__ == '__main__':
  unittest.main(verbosity=2)