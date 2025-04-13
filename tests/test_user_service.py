import unittest
from app import create_app, db
from services import user_service


class UserServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_all_users(self):
        user_service.create_user('TestUser1', 'FirstName1', 'LastName1', '1234567890', 'Location1', 'Address1', 'City1',
                                 'Company1', 'test1@example.com', 'Password123!')
        user_service.create_user('TestUser2', 'FirstName2', 'LastName2', '0987654321', 'Location2', 'Address2', 'City2',
                                 'Company2', 'test2@example.com', 'Password123!')
        users = user_service.get_all_users()
        self.assertEqual(len(users), 2)

    def test_create_user(self):
        response = user_service.create_user('TestUser', 'FirstName', 'LastName', '1234567890', 'Location', 'Address',
                                            'City', 'Company', 'test@example.com', 'Password123!')
        self.assertIn('message', response)
        self.assertEqual(response['message'], 'User account created successfully.')
        self.assertIn('user', response)
        self.assertEqual(response['user']['nick_name'], 'TestUser')
        self.assertEqual(response['user']['email'], 'test@example.com')

    def test_get_user_by_email(self):
        user_service.create_user('TestUser', 'FirstName', 'LastName', '1234567890', 'Location', 'Address', 'City',
                                 'Company', 'test@example.com', 'Password123!')
        user = user_service.get_user_by_email('test@example.com')
        self.assertIsNotNone(user)
        self.assertEqual(user['nick_name'], 'TestUser')
        self.assertEqual(user['email'], 'test@example.com')

    def test_reset_password(self):
        user_service.create_user('TestUser', 'FirstName', 'LastName', '1234567890', 'Location', 'Address', 'City',
                                 'Company', 'test@example.com', 'Password123!')
        response = user_service.reset_password('test@example.com', 'Password123!', 'NewPassword123!')
        self.assertIn('message', response)
        self.assertEqual(response['message'], 'Password reset successfully.')
        is_valid = user_service.validate_user('test@example.com', 'NewPassword123!')
        self.assertTrue(is_valid)

    def test_is_valid_password(self):
        self.assertTrue(user_service.is_valid_password('Password123!'))
        self.assertFalse(user_service.is_valid_password('short'))
        self.assertFalse(user_service.is_valid_password('nouppercase123!'))
        self.assertFalse(user_service.is_valid_password('NOLOWERCASE123!'))
        self.assertFalse(user_service.is_valid_password('NoSpecialChar123'))

    def test_is_valid_email(self):
        self.assertTrue(user_service.is_valid_email('test@example.com'))
        self.assertFalse(user_service.is_valid_email('invalid-email'))
        self.assertFalse(user_service.is_valid_email('missing@domain'))
        self.assertFalse(user_service.is_valid_email('missing@.com'))


if __name__ == '__main__':
    unittest.main()
