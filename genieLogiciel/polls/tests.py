from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured

class UserTest(TestCase):
    def setUp(self):
        self.user_data = {
            'mail': 'john.doe@gmail.com',
            'password': 'testpassword',
            'nom': 'Doe',
            'prenom': 'John',
            'role': 'etudiant'
        }
        try:
            self.user = get_user_model().objects.create_user(**self.user_data)
            print("Connexion à la base de données réussie.")
        except ImproperlyConfigured:
            print("Échec de la connexion à la base de données.")
            raise

    def test_create_user(self):
        self.assertIsNotNone(self.user, "Failed to create User.")

    def test_get_user(self):
        user = get_user_model().objects.get(mail=self.user_data['mail'])
        self.assertIsNotNone(user, "Failed to retrieve User.")

    def test_update_user(self):
        new_mail = 'jane.doe@gmail.com'
        self.user.mail = new_mail
        self.user.save()
        user = get_user_model().objects.get(mail=new_mail)
        self.assertEqual(user.mail, new_mail, "Failed to update User.")

    def test_delete_user(self):
        user_mail = self.user.mail
        self.user.delete()
        with self.assertRaises(get_user_model().DoesNotExist):
            get_user_model().objects.get(mail=user_mail)