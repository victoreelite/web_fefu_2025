from django.test import TestCase
from django.urls import reverse
from django.http import Http404


class ViewTests(TestCase):

    def test_home_page_status_code(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_about_page_status_code(self):
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 200)

    def test_student_profile_exists(self):
        response = self.client.get('/student/1/')
        self.assertEqual(response.status_code, 200)

    def test_student_profile_not_found(self):
        response = self.client.get('/student/101/')
        self.assertEqual(response.status_code, 404)

    def test_course_page_exists(self):
        response = self.client.get('/course/python-basic/')
        self.assertEqual(response.status_code, 200)