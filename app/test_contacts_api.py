import unittest
import json
import os
from app import app
from db import mysql
from contacts import contacts


class ApiRoutesTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.environ['FLASK_ENV'] = 'testing'
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config['ENV'] = 'testing'
        app.register_blueprint(contacts)
        cls.client = app.test_client()

    def setUp(self):
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM contacts")
            mysql.connection.commit()

            cur.execute(
                "INSERT INTO contacts (fullname, phone, email, notes, is_favorite) VALUES (%s, %s, %s, %s, %s)",
                ("Initial API User", "1234567890", "api_initial@example.com", "Initial API notes.", 0)
            )
            mysql.connection.commit()
            cur.execute("SELECT id FROM contacts WHERE email = %s", ("api_initial@example.com",))
            self.test_contact_id = cur.fetchone()['id']
            cur.close()

    def tearDown(self):
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM contacts")
            mysql.connection.commit()
            cur.close()

    def test_api_update_contact_success(self):
        payload = {
            "fullname": "Updated API User",
            "phone": "9998887777",
            "email": "updated_api@example.com",
            "notes": "Updated notes for the API user",
            "is_favorite": 1
        }
        response = self.client.put(f'/api/contacts/{self.test_contact_id}', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('contact', data)
        self.assertEqual(data['contact']['fullname'], payload['fullname'])
        self.assertEqual(data['contact']['email'], payload['email'])
        self.assertEqual(data['contact']['notes'], payload['notes'])
        self.assertEqual(data['contact']['is_favorite'], payload['is_favorite'])

        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM contacts WHERE id = %s", (self.test_contact_id,))
            db_contact = cur.fetchone()
            cur.close()
            self.assertEqual(db_contact['fullname'], payload['fullname'])
            self.assertEqual(db_contact['is_favorite'], payload['is_favorite'])

    def test_api_update_contact_missing_required(self):
        payload = {"notes": "Only notes"}
        response = self.client.put(f'/api/contacts/{self.test_contact_id}', json=payload)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("Missing required fields", data['message'])

    def test_api_update_contact_not_found(self):
        payload = {
            "fullname": "Nonexistent",
            "phone": "0000000000",
            "email": "noone@example.com",
            "notes": "",
            "is_favorite": 0
        }
        response = self.client.put('/api/contacts/9999999', json=payload)
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['message'], "Contact not found")

    def test_api_update_contact_invalid_json(self):
        response = self.client.put(f'/api/contacts/{self.test_contact_id}', data="not a json", headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data['message'], "Invalid JSON")


    def test_api_partial_update_contact_success(self):
        patch_data = {
            "notes": "Partially updated notes via API",
            "is_favorite": 1
        }
        response = self.client.patch(f'/api/contacts/{self.test_contact_id}', json=patch_data)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('contact', data)
        self.assertEqual(data['contact']['notes'], patch_data['notes'])
        self.assertEqual(data['contact']['is_favorite'], patch_data['is_favorite'])
        self.assertEqual(data['contact']['fullname'], "Initial API User")

        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM contacts WHERE id = %s", (self.test_contact_id,))
            db_contact = cur.fetchone()
            cur.close()
            self.assertEqual(db_contact['notes'], patch_data['notes'])
            self.assertEqual(db_contact['is_favorite'], patch_data['is_favorite'])
            self.assertEqual(db_contact['fullname'], "Initial API User")

    def test_api_partial_update_contact_no_fields(self):
        response = self.client.patch(f'/api/contacts/{self.test_contact_id}', json={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("No fields to update", data['message'])

    def test_api_partial_update_contact_not_found(self):
        patch_data = {"fullname": "Ghost Contact"}
        response = self.client.patch('/api/contacts/9999999', json=patch_data)
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['message'], "Contact not found")

    def test_api_partial_update_contact_invalid_json(self):
        response = self.client.patch(f'/api/contacts/{self.test_contact_id}', data="not a json", headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data['message'], "Invalid JSON")

    def test_api_add_contact_success(self):
        payload = {
            "fullname": "New API Contact",
            "phone": "1112223333",
            "email": "new_api@example.com",
            "notes": "Notes for new API contact",
            "is_favorite": 0
        }
        response = self.client.post('/api/contacts', json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('contact', data)
        self.assertEqual(data['contact']['fullname'], payload['fullname'])
        self.assertEqual(data['contact']['email'], payload['email'])

        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM contacts WHERE id = %s", (data['contact']['id'],))
            db_contact = cur.fetchone()
            cur.close()
            self.assertIsNotNone(db_contact)
            self.assertEqual(db_contact['email'], payload['email'])

    def test_api_add_contact_missing_fields(self):
        payload = {"phone": "1112223333"}
        response = self.client.post('/api/contacts', json=payload)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("Missing required fields", data['message'])

    def test_api_add_contact_invalid_json(self):
        response = self.client.post('/api/contacts', data="not a json", headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data['message'], "Invalid JSON")


    def test_api_get_favorite_contacts_success(self):
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute("UPDATE contacts SET is_favorite = 1 WHERE id = %s", (self.test_contact_id,))
            mysql.connection.commit()
            cur.close()

        response = self.client.get('/api/contacts/favorites')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('favorites', data)
        self.assertTrue(any(c['id'] == self.test_contact_id for c in data['favorites']))

    def test_api_get_favorite_contacts_empty(self):
        response = self.client.get('/api/contacts/favorites')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['favorites'], [])


    def test_api_delete_contact_success(self):
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO contacts (fullname, phone, email, notes, is_favorite) VALUES (%s, %s, %s, %s, %s)",
                ("To Be Deleted", "0000000000", "delete_me@example.com", "", 0)
            )
            mysql.connection.commit()
            cur.execute("SELECT id FROM contacts WHERE email = %s", ("delete_me@example.com",))
            delete_id = cur.fetchone()['id']
            cur.close()

        response = self.client.delete(f'/api/contacts/{delete_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"message": "Contact removed successfully"})


        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute("SELECT id FROM contacts WHERE id = %s", (delete_id,))
            self.assertIsNone(cur.fetchone())
            cur.close()

    def test_api_delete_contact_not_found(self):
        response = self.client.delete('/api/contacts/9999999')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['message'], "Contact not found")


if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)