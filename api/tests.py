from api.forms import RegisterForm
from django.test import TestCase


class RegisterFormTest(TestCase):
    def test_invalid_registration(self):
        form_data = {
            'email': 'indeed@indeedblog.net',
            'password': '233333',
            'passwordRepeat': '23333'
        }
        form = RegisterForm(form_data)
        self.assertFalse(form.clean())
        self.assertEqual(form.errors['passwordRepeat'], ['Password not match.'])
