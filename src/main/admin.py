from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from main.models import *

# Register your models here.
class PersonAdmin(admin.ModelAdmin):
    #fields = ('Username', 'Nom', 'email', 'Né le', 'Nationalité')
    list_display = ('user', 'get_fullname', 'get_email', 'birthday', 'nationality')

    def get_email(self, obj):
        return obj.user.email
    
    def get_fullname(self, obj):
        return obj.user.get_full_name()

admin.site.register(User, UserAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Requisition)
admin.site.register(State)
admin.site.register(Complaint)
admin.site.register(Demarcation)
admin.site.register(Report)
admin.site.register(Coordinate)
admin.site.register(landDeed)
admin.site.register(Mutation)
admin.site.register(Sale)