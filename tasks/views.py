from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Project, Task, TaskComment
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    ProjectSerializer,
    TaskCommentSerializer,
    TaskDetailSerializer,
    TaskListSerializer,
    TaskStatusUpdateSerializer,
)


class ProjectViewSet(viewsets.ModelViewSet):
    """API endpoint for managing Projects."""

    queryset = Project.objects.select_related("owner").prefetch_related("tasks").all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "name"]
    ordering = ["-created_at"]


class TaskViewSet(viewsets.ModelViewSet):
    """API endpoint for managing workflow Tasks."""

    queryset = (
        Task.objects.select_related("project", "creator", "assignee")
        .prefetch_related("comments__author")
        .all()
    )
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "priority", "project", "assignee", "creator"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "due_date", "priority", "status"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return TaskListSerializer
        if self.action == "change_status":
            return TaskStatusUpdateSerializer
        return TaskDetailSerializer

    @action(detail=True, methods=["post"], url_path="status")
    def change_status(self, request, pk=None):
        """Dedicated action to change task status."""
        task = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task.status = serializer.validated_data["status"]
        task.save(update_fields=["status", "updated_at"])
        return Response(TaskDetailSerializer(task).data, status=status.HTTP_200_OK)


class TaskCommentViewSet(viewsets.ModelViewSet):
    """API endpoint for managing comments on tasks."""

    queryset = TaskComment.objects.select_related("task", "author").all()
    serializer_class = TaskCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["task"]

    def get_queryset(self):
        qs = super().get_queryset()
        task_id = self.request.query_params.get("task")
        if task_id:
            qs = qs.filter(task_id=task_id)
        return qs
