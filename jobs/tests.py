from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from jobs.models import Job, JobApplication

User = get_user_model()

class JobsModelAndSignalTests(TestCase):
    def setUp(self):
        self.employer = User.objects.create_user(username='employer', password='Password123!')
        self.applicant = User.objects.create_user(username='applicant', password='Password123!')

    def test_create_job(self):
        job = Job.objects.create(
            title='Python Developer',
            company='TechCorp',
            location='Remote',
            industry='Software',
            posted_by=self.employer
        )
        self.assertEqual(str(job), 'Python Developer at TechCorp')
        self.assertTrue(job.is_active)

    def test_job_application_unique_constraint(self):
        job = Job.objects.create(
            title='Frontend Dev',
            company='WebCo',
            location='Kalaburagi',
            posted_by=self.employer
        )
        app1 = JobApplication.objects.create(job=job, applicant=self.applicant)
        self.assertEqual(str(app1), 'applicant -> Frontend Dev')
        self.assertEqual(app1.status, 'pending')

class JobsViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.employer = User.objects.create_user(username='employer', password='Password123!', industry='Software')
        self.applicant = User.objects.create_user(username='applicant', password='Password123!', core_skills='Python, Django')
        
        self.job = Job.objects.create(
            title='Django Developer',
            company='A1 Tech',
            location='Remote',
            industry='Software',
            required_skills='Django, Python',
            posted_by=self.employer
        )

    def test_job_list_requires_login(self):
        response = self.client.get(reverse('jobs:job_list'))
        self.assertEqual(response.status_code, 302)

    def test_job_list_authenticated(self):
        self.client.login(username='applicant', password='Password123!')
        response = self.client.get(reverse('jobs:job_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django Developer')

    def test_job_detail_view(self):
        self.client.login(username='applicant', password='Password123!')
        response = self.client.get(reverse('jobs:job_detail', kwargs={'job_id': self.job.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A1 Tech')

    def test_post_job_view(self):
        self.client.login(username='employer', password='Password123!')
        response = self.client.post(reverse('jobs:post_job'), {
            'title': 'Full Stack Engineer',
            'company': 'Innovate LLC',
            'location': 'Hybrid',
            'industry': 'Software',
            'required_skills': 'React, Python',
            'salary_range': '₹12 LPA',
            'description': 'Building next-gen platforms.'
        })
        self.assertRedirects(response, reverse('jobs:job_list'))
        self.assertTrue(Job.objects.filter(title='Full Stack Engineer').exists())

    def test_apply_to_job(self):
        self.client.login(username='applicant', password='Password123!')
        response = self.client.get(reverse('jobs:apply_to_job', kwargs={'job_id': self.job.id}))
        self.assertRedirects(response, reverse('jobs:job_detail', kwargs={'job_id': self.job.id}))
        self.assertTrue(JobApplication.objects.filter(job=self.job, applicant=self.applicant).exists())

    def test_withdraw_application(self):
        JobApplication.objects.create(job=self.job, applicant=self.applicant)
        self.client.login(username='applicant', password='Password123!')
        response = self.client.post(reverse('jobs:withdraw_application', kwargs={'job_id': self.job.id}))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "withdrawn", "message": "Application withdrawn."})
        self.assertFalse(JobApplication.objects.filter(job=self.job, applicant=self.applicant).exists())

    def test_employer_manage_application(self):
        app = JobApplication.objects.create(job=self.job, applicant=self.applicant)
        self.client.login(username='employer', password='Password123!')
        response = self.client.get(reverse('jobs:manage_app', kwargs={'app_id': app.id, 'action': 'accept'}))
        self.assertRedirects(response, reverse('jobs:job_detail', kwargs={'job_id': self.job.id}))
        app.refresh_from_db()
        self.assertEqual(app.status, 'accepted')

    def test_edit_job_owner(self):
        self.client.login(username='employer', password='Password123!')
        response = self.client.post(reverse('jobs:edit_job', kwargs={'job_id': self.job.id}), {
            'title': 'Lead Django Architect',
            'company': 'A1 Tech',
            'location': 'Remote',
            'industry': 'Software',
            'required_skills': 'Django, Python, PostgreSQL',
            'description': 'Updated job description.'
        })
        self.assertRedirects(response, reverse('jobs:job_detail', kwargs={'job_id': self.job.id}))
        self.job.refresh_from_db()
        self.assertEqual(self.job.title, 'Lead Django Architect')

    def test_delete_job_owner(self):
        self.client.login(username='employer', password='Password123!')
        response = self.client.post(reverse('jobs:delete_job', kwargs={'job_id': self.job.id}))
        self.assertRedirects(response, reverse('jobs:my_posted_jobs'))
        self.assertFalse(Job.objects.filter(id=self.job.id).exists())
