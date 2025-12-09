from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json
import logging

from .models import ChatMessage, Conversation
from .ai_model import chat_response   # <-- NEW: using your Python AI model

logger = logging.getLogger(__name__)


# -------------------------------------------------------
# CHAT PAGE
# -------------------------------------------------------
def chat_page(request):
    return render(request, "ai/chat.html")


# -------------------------------------------------------
# LIST ALL CHATS
# -------------------------------------------------------
def conversations_list(request):
    q = request.GET.get("q", "").strip()
    convos = Conversation.objects.all().order_by("-updated_at")

    if q:
        convos = convos.filter(title__icontains=q)

    return JsonResponse({
        "conversations": [
            {
                "id": c.id,
                "title": c.title,
                "created_at": c.created_at.isoformat(),
                "updated_at": c.updated_at.isoformat()
            }
            for c in convos
        ]
    })


# -------------------------------------------------------
# CREATE NEW CHAT
# -------------------------------------------------------
@csrf_exempt
def new_conversation(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    convo = Conversation.objects.create(title="New Chat")

    return JsonResponse({
        "id": convo.id,
        "title": convo.title,
        "created_at": convo.created_at.isoformat()
    })


# -------------------------------------------------------
# LOAD CHAT + MESSAGES
# -------------------------------------------------------
def conversation_detail(request, convo_id):
    convo = get_object_or_404(Conversation, id=convo_id)
    msgs = convo.messages.order_by("timestamp")

    return JsonResponse({
        "conversation": {
            "id": convo.id,
            "title": convo.title
        },
        "messages": [
            {
                "sender": m.sender,
                "message": m.message,
                "timestamp": m.timestamp.isoformat()
            }
            for m in msgs
        ]
    })


# -------------------------------------------------------
# RENAME CHAT
# -------------------------------------------------------
@csrf_exempt
def rename_conversation(request, convo_id):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    convo = get_object_or_404(Conversation, id=convo_id)

    try:
        data = json.loads(request.body.decode("utf-8"))
        new_title = (data.get("title") or "").strip()
    except:
        return HttpResponseBadRequest("Invalid JSON")

    if not new_title:
        return HttpResponseBadRequest("Empty title")

    convo.title = new_title[:100]
    convo.updated_at = timezone.now()
    convo.save()

    return JsonResponse({"ok": True, "title": convo.title})


# -------------------------------------------------------
# DELETE CHAT
# -------------------------------------------------------
@csrf_exempt
def delete_conversation(request, convo_id):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    convo = get_object_or_404(Conversation, id=convo_id)
    convo.delete()

    return JsonResponse({"ok": True})


# -------------------------------------------------------
# CLEAR ALL CHATS
# -------------------------------------------------------
@csrf_exempt
def clear_conversations(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    Conversation.objects.all().delete()
    return JsonResponse({"ok": True})


# -------------------------------------------------------
# MAIN AI MESSAGE HANDLER
# -------------------------------------------------------
@csrf_exempt
def ask_ai(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    try:
        data = json.loads(request.body.decode("utf-8"))
    except:
        return HttpResponseBadRequest("Invalid JSON")

    user_msg = (data.get("message") or "").strip()
    convo_id = data.get("conversation_id")

    if not user_msg:
        return JsonResponse({"reply": "Please enter a message."}, status=400)

    # Load conversation if exists
    conversation = None
    history = []

    if convo_id:
        try:
            conversation = Conversation.objects.get(id=convo_id)

            # Convert past messages to history format
            for m in conversation.messages.order_by("timestamp"):
                if m.sender == "user":
                    history.append({"user": m.message, "bot": ""})
                else:
                    history[-1]["bot"] = m.message

        except Conversation.DoesNotExist:
            conversation = None

    # Create user message entry
    ChatMessage.objects.create(
        sender="user",
        message=user_msg,
        conversation=conversation
    )

    # SYSTEM PROMPT (Similar to ChatGPT behavior)
    SYSTEM_PROMPT = (
        "You are Assist AI, a friendly and short-replying assistant. "
        "Always reply in 1–2 clean English sentences. "
        "Ignore weird symbols, tags, or noise. "
        "If user greets, respond warmly. "
        "If unclear, ask politely for clarification."
    )

    # GENERATE AI RESPONSE
    try:
        reply = chat_response(
            system_msg=SYSTEM_PROMPT,
            history=history,
            user_msg=user_msg
        )
    except Exception as e:
        logger.exception("AI generation failed: %s", e)
        reply = "Something went wrong."

    # Save bot reply
    ChatMessage.objects.create(
        sender="bot",
        message=reply,
        conversation=conversation
    )

    # Auto-title chat from first user message
    if conversation:
        if conversation.title == "New Chat":
            conversation.title = user_msg[:40]
        conversation.updated_at = timezone.now()
        conversation.save()

    return JsonResponse({"reply": reply})