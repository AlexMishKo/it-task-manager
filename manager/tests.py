from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from manager.forms import TaskForm
from manager.forms.worker_form import WorkerCreationForm
from manager.models import (Position,
                            TaskType,
                            Worker,
                            Team,
                            Project,
                            Task,
                            Tag)
import datetime


class ModelTests(TestCase):

    def setUp(self):
        self.position = Position.objects.create(name="Developer")
        self.task_type = TaskType.objects.create(name="Bug")
        self.worker = Worker.objects.create_user(
            username="test.worker",
            password="password123",
            first_name="John",
            last_name="Doe",
            position=self.position
        )

    def test_position_str(self):
        self.assertEqual(str(self.position), "Developer")

    def test_worker_str(self):
        self.assertEqual(str(self.worker), "test.worker (John Doe)")

    def test_team_creation_and_str(self):
        team = Team.objects.create(name="Alpha Team")
        team.workers.add(self.worker)
        self.assertEqual(str(team), "Alpha Team")
        self.assertIn(self.worker, team.workers.all())

    def test_project_creation_and_str(self):
        project = Project.objects.create(name="System Upgrade")
        self.assertEqual(str(project), "System Upgrade")

    def test_task_creation_and_str(self):
        project = Project.objects.create(name="New Project")
        deadline = timezone.now().date() + datetime.timedelta(days=1)

        task = Task.objects.create(
            name="Fix Login",
            task_type=self.task_type,
            project=project,
            priority="urgent",
            deadline=deadline
        )
        self.assertEqual(str(task), "Fix Login")
        self.assertEqual(task.priority, "urgent")
        self.assertFalse(task.is_completed)


class ViewTests(TestCase):

    def setUp(self):
        self.position = Position.objects.create(name="Dev")
        self.admin_user = Worker.objects.create_superuser(
            username="admin.user",
            password="adminpassword123"
        )
        self.worker_user = Worker.objects.create_user(
            username="worker.user",
            password="workerpassword123",
            position=self.position
        )

        self.task_type = TaskType.objects.create(name="Feature")
        self.project = Project.objects.create(name="Test Project")
        self.task = Task.objects.create(
            name="Test Task",
            task_type=self.task_type,
            project=self.project,
            deadline=timezone.now().date(),
            priority="medium"
        )

    def test_dashboard_access_logged_in(self):

        self.client.login(username="worker.user", password="workerpassword123")
        response = self.client.get(reverse("manager:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manager/index.html")

    def test_task_list_search_by_name(self):

        self.client.login(username="worker.user", password="workerpassword123")
        url = reverse("manager:task-list")

        response = self.client.get(url, {"name": "Test"})
        self.assertContains(response, "Test Task")


        response = self.client.get(url, {"name": "Missing"})
        self.assertNotContains(response, "Test Task")

    def test_toggle_task_completion_logic(self):

        self.client.login(username="worker.user", password="workerpassword123")
        url = reverse("manager:task-toggle-complete", kwargs={"pk": self.task.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        self.task.refresh_from_db()
        self.assertTrue(self.task.is_completed)

    def test_worker_cannot_delete_project(self):

        self.client.login(username="worker.user", password="workerpassword123")
        url = reverse("manager:project-delete", kwargs={"pk": self.project.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_admin_can_delete_project(self):

        self.client.login(username="admin.user", password="adminpassword123")
        url = reverse("manager:project-delete", kwargs={"pk": self.project.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class FormTests(TestCase):

    def setUp(self):
        self.position = Position.objects.create(name="Designer")
        self.task_type = TaskType.objects.create(name="UI")
        self.project = Project.objects.create(name="Web Design")
        self.tag = Tag.objects.create(name="Experimental")

    def test_worker_creation_form_fields(self):
        form = WorkerCreationForm()
        self.assertIn("position", form.fields)
        self.assertIn("first_name", form.fields)

    def test_task_form_valid(self):
        deadline = timezone.now().date() + datetime.timedelta(days=5)
        form_data = {
            "name": "Design Logo",
            "description": "Create a new brand logo",
            "deadline": deadline,
            "priority": "high",
            "task_type": self.task_type.id,
            "project": self.project.id,
            "tags": [self.tag.id],
            "is_completed": False,
        }
        form = TaskForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_task_form_invalid_deadline(self):

        form = TaskForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("deadline", form.errors)

    def test_task_form_deadline_widget_type(self):
        form = TaskForm()

        self.assertEqual(form.fields["deadline"].widget.input_type, "date")

    def test_worker_form_css_classes(self):
        form = WorkerCreationForm()
        username_class = form.fields["username"].widget.attrs.get("class")
        self.assertIn("input-bordered", username_class)