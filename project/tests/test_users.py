import json

from project.tests.base import BaseTestCase
from project import db
from project.api.models import User


def add_user(username, email):
    """Add a user."""
    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()
    return user


class TestUserService(BaseTestCase):

    """Tests for the Users service."""

    def test_users(self):
        """Ensure the /ping route behaves correctly."""
        response = self.client.get('/ping')
        data = json.loads(response.data.decode())
        # self.assertEqual(response.status_code, 200)
        self.assert200(
            response,
            message="The /ping route didn't return HTTP status code 200.")
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_fun(self):
        """Ensure the /fun route behaves correctly."""
        response = self.client.get('/fun')
        data = json.loads(response.data.decode())
        self.assert200(
            response,
            message="The /fun route didn't return status code 200.")
        self.assertIn('<h1>Hello, world!</h1>', data['message'])
        self.assertIn('success', data['status'])

    def test_add_user(self):
        """Ensure a new user can be added to the database."""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='forest',
                    email='forest.monsen@gmail.com'
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('forest.monsen@gmail.com was added!', data['message'])
            self.assertIn('success', data['status'])

    def test_add_user_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty."""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict()),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_invalid_json_keys(self):
        """Ensure error is thrown if the JSON object does not have a user."""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(email='forest.monsen@gmail.com')),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_duplicate_user(self):
        """Ensure error is thrown if the e-mail already exists."""
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='forest',
                    email='forest.monsen@gmail.com'
                )),
                content_type='application/json',
            )
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='forest',
                    email='forest.monsen@gmail.com'
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                'Sorry. That e-mail already exists.', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user(self):
        """Ensure the GET of a single user behaves correctly."""
        user = add_user('forest', 'forest.monsen@gmail.com')
        with self.client:
            response = self.client.get(f'/users/{user.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue('created_at' in data['data'])
            self.assertIn('forest', data['data']['username'])
            self.assertIn('forest.monsen@gmail.com', data['data']['email'])
            self.assertIn('success', data['status'])

    def test_single_user_no_id(self):
        """Ensure error is thrown if an ID is not provided."""
        with self.client:
            response = self.client.get('/users/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user_incorrect_id(self):
        """Ensure error is thrown if the id does not exist."""
        with self.client:
            response = self.client.get('/users/999999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_all_users(self):
        """Ensure get all users behaves correctly."""
        add_user('forest', 'forest.monsen@gmail.com')
        add_user('newuser', 'newuser@example.com')
        with self.client:
            response = self.client.get('/users')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['users']), 2)
            self.assertTrue('created_at' in data['data']['users'][0])
            self.assertTrue('created_at' in data['data']['users'][1])
            self.assertIn('forest', data['data']['users'][0]['username'])
            self.assertIn('newuser', data['data']['users'][1]['username'])
            self.assertIn('forest.monsen@gmail.com', data['data']['users'][0]['email'])
            self.assertIn('newuser@example.com', data['data']['users'][1]['email'])
            self.assertIn('success', data['status'])

    def test_main_no_users(self):
        """Ensure the main route behaves correctly when no users have been added to the database."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<h1>All Users</h1>', response.data)
        self.assertIn(b'No users', response.data)

    def test_main_with_users(self):
        """Ensure the main route behaves correctly when users have been added to the database."""
        add_user('forest', 'forest.monsen@gmail.com')
        add_user('maddie', 'maddie@monsenfamily.com')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<h1>All Users</h1>', response.data)
        self.assertNotIn(b'No users', response.data)
        self.assertIn(b'<strong>forest</strong>', response.data)
        self.assertIn(b'<strong>maddie</strong>', response.data)

    def test_main_add_user(self):
        """Ensure a new user can be added to the database using the Web UI."""
        with self.client:
            response = self.client.post(
                '/',
                data=dict(username='forest', email='forest.monsen@gmail.com'),
                follow_redirects=True
            )
