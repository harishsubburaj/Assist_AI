from django.db import models


class Conversation(models.Model):
    title = models.CharField(max_length=200, blank=True, default="New Chat")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or f"Conversation {self.id}"
    

class ChatMessage(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
        null=True,        # keeps compatibility with old chat messages
        blank=True,
        default=None
    )
    sender = models.CharField(max_length=10)  # 'user' / 'bot'
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        preview = self.message[:25].replace("\n", " ")
        return f"{self.sender}: {preview}"