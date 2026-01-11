from django.test import TestCase
from django.utils import timezone
from manager.models import (Position,
                            TaskType,
                            Worker,
                            Team,
                            Project,
                            Task)
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