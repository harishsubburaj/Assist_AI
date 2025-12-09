from django.urls import path
from . import views

urlpatterns = [
    # UI page
    path('', views.chat_page, name='chat_page'),

    # Conversation system
    path('conversations/', views.conversations_list, name='conversations_list'),
    path('conversation/<int:convo_id>/', views.conversation_detail, name='conversation_detail'),
    path('new/', views.new_conversation, name='new_conversation'),

    # Rename & Delete (ChatGPT style)
    path('rename/<int:convo_id>/', views.rename_conversation, name='rename_conversation'),
    path('delete/<int:convo_id>/', views.delete_conversation, name='delete_conversation'),

    # Optional: Clear all chats
    path('clear/', views.clear_conversations, name='clear_conversations'),

    # AI reply endpoint
    path('ask/', views.ask_ai, name='ask_ai'),
]