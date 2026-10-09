from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Project, Task, TaskComment

User = get_user_model()


class TasksAPITests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email="lead@example.com", username="teamlead", password="Password123!"
        )
        self.user2 = User.objects.create_user(
            email="dev@example.com", username="developer2", password="Password123!"
        )

        self.project = Project.objects.create(
            name="Core Platform v1",
            description="Initial launch platform",
            owner=self.user1,
        )

        self.task1 = Task.objects.create(
            title="Setup PostgreSQL Indexing",
            description="Add composite index on status and priority",
            project=self.project,
            creator=self.user1,
            assignee=self.user2,
            status="TODO",
            priority="HIGH",
        )

    def test_list_projects_authenticated(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("project-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_create_task(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("task-list")
        data = {
            "title": "Build DRF Swagger docs",
            "description": "Integrate drf-spectacular for OpenAPI 3",
            "project": self.project.id,
            "status": "IN_PROGRESS",
            "priority": "MEDIUM",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Build DRF Swagger docs")
        self.assertEqual(response.data["creator"]["email"], self.user1.email)

    def test_filter_tasks_by_status(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("task-list")
        response = self.client.get(f"{url}?status=TODO")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

        response_none = self.client.get(f"{url}?status=DONE")
        self.assertEqual(response_none.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_none.data["results"]), 0)

    def test_task_status_transition_action(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("task-change-status", kwargs={"pk": self.task1.id})
        response = self.client.post(url, {"status": "DONE"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, "DONE")

    def test_permission_non_owner_cannot_delete(self):
        # user2 is not the project owner
        self.client.force_authenticate(user=self.user2)
        url = reverse("project-detail", kwargs={"pk": self.project.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_comment_to_task(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse("comment-list")
        data = {
            "task": self.task1.id,
            "content": "Work is underway, indexing tested locally.",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["author"]["email"], self.user2.email)
