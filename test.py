import json
import os
import unittest
from io import BytesIO

from app import app


class URLShortenerTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        app.config['TESTING'] = True

    def tearDown(self):
        if os.path.exists('urls.json'):
            os.remove('urls.json')
        with self.app.session_transaction() as sess:
            sess.clear()

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'URL Shortener', response.data)

    def test_create_url(self):
        response = self.app.post('/your-url', data=dict(
            code='example',
            url='http://example.com'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<h2>example</h2>', response.data)

        with open('urls.json') as urls_file:
            urls = json.load(urls_file)
            self.assertIn('example', urls)
            self.assertEqual(urls['example']['url'], 'http://example.com')

    def test_create_file(self):
        data = {
            'code': 'examplefile'
        }
        data['file'] = (BytesIO(b"dummy data"), 'testfile.txt')

        response = self.app.post('/your-url', data=data, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<h2>examplefile</h2>', response.data)

        with open('urls.json') as urls_file:
            urls = json.load(urls_file)
            self.assertIn('examplefile', urls)
            self.assertIn('file', urls['examplefile'])

        saved_file_path = os.path.join(app.static_folder, 'user_files', 'examplefiletestfile.txt')
        self.assertTrue(os.path.exists(saved_file_path))

    def test_redirect_to_url(self):
        with open('urls.json', 'w') as urls_file:
            json.dump({'example': {'url': 'http://example.com'}}, urls_file)

        response = self.app.get('/example')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'http://example.com')

    def test_redirect_to_file(self):
        file_path = os.path.join(app.static_folder, 'user_files', 'examplefiletestfile.txt')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(b'dummy data')

        with open('urls.json', 'w') as urls_file:
            json.dump({'examplefile': {'file': 'examplefiletestfile.txt'}}, urls_file)

        response = self.app.get('/examplefile')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/static/user_files/examplefiletestfile.txt', response.location)

    def test_session_api(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['example'] = True

            response = client.get('/api')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'example', response.data)

    def test_404(self):
        response = self.app.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Page Not Found', response.data)


if __name__ == '__main__':
    unittest.main()
