from django.contrib import admin
from boardapp.models import *

# Register your models here.

class SchoolsInline(admin.TabularInline) :
    model = Schoolusers

class OnlineuserInline(admin.TabularInline) :
    model = Onlineuser

class OnlinemovieInline(admin.TabularInline) :
    model = Onlinemovie

class UserInline(admin.TabularInline) :
    model = User

class CouponuserInline(admin.TabularInline) :
    model = CouponUser

class userAdmin(admin.ModelAdmin) :
    list_display = ('username','last_name', 'date_joined','is_staff')
    inlines = [SchoolsInline , OnlineuserInline , CouponuserInline]

class onlineclassAdmin(admin.ModelAdmin) :
    list_display = ( 'catename' , 'catenum')
    inlines = [OnlineuserInline , OnlinemovieInline]

class onlinemovieAdmin(admin.ModelAdmin) :
    list_display = ('movie','amount')
    #inlines = [UserInline]
class onlineorderAdmin(admin.ModelAdmin) :
    list_display = ( 'transaction_id' , 'user' , 'crated_time')

admin.site.register(User,userAdmin)
admin.site.register(Boards)
admin.site.register(BoardCategories)
admin.site.register(BoardReplies)
admin.site.register(BoardLikes)
admin.site.register(Schools)
admin.site.register(Schoolusers)
admin.site.register(Booklist)
admin.site.register(Onlineclass,onlineclassAdmin)
admin.site.register(Onlineuser)
admin.site.register(Onlinemovie,onlinemovieAdmin)
admin.site.register(Onlineorder,onlineorderAdmin)
admin.site.register(Coupon)
admin.site.register(CouponUser)
admin.site.register(Cart)
admin.site.register(Cartitem)