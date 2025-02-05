from django.contrib import admin
from .models import Conversation, ConversationParticipant , Message, User 
# Register your models here.



admin.site.register([ConversationParticipant,Conversation, Message, User])