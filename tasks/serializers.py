from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Project, Task, TaskComment

User = get_user_model()


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]


class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSimpleSerializer(read_only=True)
    task_count = serializers.IntegerField(source="tasks.count", read_only=True)

    class Meta:
        model = Project
        fields = ["id", "name", "slug", "description", "owner", "task_count", "created_at", "updated_at"]
        read_only_fields = ["id", "slug", "owner", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)


class TaskCommentSerializer(serializers.ModelSerializer):
    author = UserSimpleSerializer(read_only=True)

    class Meta:
        model = TaskComment
        fields = ["id", "task", "author", "content", "created_at"]
        read_only_fields = ["id", "author", "created_at"]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class TaskListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for task list queries."""

    creator = UserSimpleSerializer(read_only=True)
    assignee = UserSimpleSerializer(read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "project",
            "project_name",
            "creator",
            "assignee",
            "status",
            "priority",
            "due_date",
            "created_at",
        ]


class TaskDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with nested comments and writeable relations."""

    creator = UserSimpleSerializer(read_only=True)
    assignee_detail = UserSimpleSerializer(source="assignee", read_only=True)
    project_detail = ProjectSerializer(source="project", read_only=True)
    comments = TaskCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "project",
            "project_detail",
            "creator",
            "assignee",
            "assignee_detail",
            "status",
            "priority",
            "due_date",
            "comments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "creator", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)


class TaskStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Task.STATUS_CHOICES)
