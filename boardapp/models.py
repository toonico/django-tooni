from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
#from awsdjangoproj.storage_backends import MediaStorage
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from boardapp.iamport import *
import time
import random
import hashlib
from django.db.models.signals import post_save
class UserManager(BaseUserManager):
	def create_user(self, username, password, last_name, email, phone, date_of_birth):
		user = self.model(
			username=username,
			last_name=last_name,
			email=self.normalize_email(email),
			phone=phone,
			date_of_birth=date_of_birth,
			date_joined=timezone.now(),
			is_superuser=0,
			is_staff=0,
			is_active=1
		)

		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, username, last_name, email, phone, date_of_birth, password):
		user = self.create_user(
			username=username,
			password=password,
			last_name=last_name,
			email=email,
			phone=phone,
			date_of_birth=date_of_birth
		)
		user.is_superuser=1
		user.is_staff=5
		user.save(using=self._db)
		return user
		
class User(AbstractBaseUser):
    password = models.CharField(max_length=128)
    username = models.CharField(unique=True, max_length=150)
    is_superuser = models.IntegerField()
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=254)
    date_of_birth = models.DateTimeField()
    date_joined = models.DateTimeField()
    last_login = models.DateTimeField(blank=True, null=True)
    is_staff = models.IntegerField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    schools = models.ManyToManyField('Schools',through= 'schoolusers', blank=True)
    onlineclass = models.ManyToManyField('Onlineclass',through='onlineuser',blank=True)
    coupon = models.ManyToManyField('Coupon', through = 'couponuser', blank=True)
    #onmovie = models.ManyToManyField('Onlinemovie',through='onlineuser',blank=True)
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['last_name', 'phone', 'email', 'date_of_birth']

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    class Meta:
        db_table = 'auth_user'
        verbose_name = "사용자"
        verbose_name_plural = "사용자"


# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class BoardCategories(models.Model):
    category_type = models.CharField(max_length=45)
    category_code = models.CharField(max_length=100)
    category_name = models.CharField(max_length=100)
    category_desc = models.CharField(max_length=200)
    list_count = models.IntegerField(blank=True, null=True)
    authority = models.IntegerField(blank=True, null=True)
    creation_date = models.DateTimeField(default = timezone.now)
    last_update_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
	    return '%s (%s)' % (self.category_name, self.category_code)
    class Meta:
        managed = False
        db_table = 'board_categories'


class Boards(models.Model):
    category = models.ForeignKey(BoardCategories, models.DO_NOTHING)
    user = models.ForeignKey('User', models.DO_NOTHING)
    title = models.CharField(max_length=300)
    content = models.TextField()
    registered_date = models.DateTimeField(auto_now_add=True)
    last_update_date = models.DateTimeField(auto_now=True)
    view_count = models.IntegerField(default = 0)
    bookdata = models.CharField(max_length=100 , default = None)
    doc = models.FileField(upload_to="documents/%Y/%m/%d",blank=True)
    image = models.ImageField(upload_to="images/%Y/%m/%d", blank=True)
    image_thumbnail = ImageSpecField(source='image',
									 processors=[ResizeToFill(273, 170)],
									 format = 'JPEG' ,
									 options = {'quality' : 60})

    def __str__(self):
	    return '[%d] %.40s' % (self.id,self.title)

    class Meta:
        managed = False
        db_table = 'boards'


class BoardReplies(models.Model):
    article = models.ForeignKey(Boards, models.DO_NOTHING)
    user = models.ForeignKey('User', models.DO_NOTHING)
    level = models.IntegerField(blank=True, null=True)
    content = models.TextField()
    reference_reply_id = models.IntegerField(blank=True, null=True)
    registered_date = models.DateTimeField(default=timezone.now)
    last_update_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
	    return '[%d] %.40s - [%d] %.40s' % (self.article.id, self.article.title, self.id, self.content)

    class Meta:
        managed = False
        db_table = 'board_replies'


class BoardLikes(models.Model):
    article = models.ForeignKey(Boards, models.DO_NOTHING)
    user = models.ForeignKey('User', models.DO_NOTHING)
    registered_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
	    return '[%d] %.40s - %s ' % (self.article.id, self.article.title, self.user.last_name)

    class Meta:
        managed = False
        db_table = 'board_likes'

class Schools(models.Model):
    school_region = models.CharField(max_length=20)
    school_id = models.CharField(max_length=10)
    school_name = models.CharField(max_length=255)

    def __str__(self):
	    return '[%s] - [%s] %.40s' % (self.school_region, self.school_id, self.school_name)

    class Meta:
        managed = False
        db_table = 'schools'
        ordering = ['school_region' , 'school_id' , 'school_name']
        verbose_name = "학교목록"
        verbose_name_plural = "학교목록"



class Schoolusers(models.Model):
    user = models.ForeignKey('User', models.DO_NOTHING)
    school = models.ForeignKey(Schools, models.DO_NOTHING)

    def __str__(self):
        return '%s %s - %s' % (self.user.last_name ,"강사님",self.school.school_name)

    class Meta:
        managed = False
        db_table = 'schoolusers'


class Booklist(models.Model):
    bookname = models.CharField(max_length=50)

    def __str__(self):
	    return '%s' % (self.bookname)

    class Meta:
        managed = False
        db_table = 'booklist'

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Onlineclass(models.Model):
    catename = models.CharField(max_length=100)
    catenum = models.IntegerField(default = 1)

    def __str__(self):
        return '%s _ %s' % (self.catenum , self.catename)

    class Meta:
        managed = False
        db_table = 'onlineclass'
        ordering = ['catenum']
        verbose_name = "온라인-주제"
        verbose_name_plural = "온라인-주제"

class Onlinemovie(models.Model):
    movie = models.CharField(max_length=100)
    onclass = models.ForeignKey('Onlineclass', models.DO_NOTHING)
    amount = models.PositiveIntegerField(default = 0)
    merchant_id = models.CharField(max_length=100)
    image = models.ImageField(upload_to="images/%Y/%m/%d", blank=True)
    image_thumbnail = ImageSpecField(source='image',
                                     processors=[ResizeToFill(250, 160)],
                                     format='JPEG',
                                     options={'quality': 60})

    def __str__(self):
        return '%s : %.15s ..., %s : %.15s ...' % ("주제",self.onclass.catename ,"영상제목",self.movie)

    class Meta:
        managed = False
        db_table = 'onlinemovie'
        verbose_name = "동영상목록"
        verbose_name_plural = "동영상목록"

class Onlineuser(models.Model):
    user = models.ForeignKey('User', models.DO_NOTHING)
    class_name = models.ForeignKey(Onlineclass, models.DO_NOTHING, db_column='class_id')  # Field renamed because it was a Python reserved word.
    movie = models.ForeignKey(Onlinemovie,models.DO_NOTHING)

    def __str__(self):
        return '%s %s%s' % (self.class_name.catename, self.user.last_name, "님 수강중")
    class Meta:
        managed = False
        db_table = 'onlineuser'

class OnlineorderManager(models.Manager):
    # 새로운 트랜젝션 생성
    def create_new(self, user, amount, pay_type, success=None, transaction_status=None):
        if not user:
            raise ValueError("유저가 확인되지 않습니다.")
        short_hash = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:2]
        time_hash = hashlib.sha1(str(int(time.time())).encode('utf-8')).hexdigest()[-3:]
        base = str(user.email).split("@")[0]
        key = hashlib.sha1((short_hash + time_hash + base).encode('utf-8')).hexdigest()[:10]
        new_order_id = "%s" % (key)

        # 아임포트 결제 사전 검증 단계
        validation_prepare(new_order_id, amount)

        # 트랜젝션 저장
        new_trans = self.model(
            user=user,
            order_id=new_order_id,
            amount=amount,
            pay_type=pay_type
        )

        if success is not None:
            new_trans.success = success
            new_trans.transaction_status = transaction_status

        new_trans.save(using=self._db)
        return new_trans.order_id

    # 생선된 트랜잭션 검증
    def validation_trans(self, merchant_id):
        result = get_transaction(merchant_id)

        if result['status'] != 'paid':
            return result
        else:
            return None

    def all_for_user(self, user):
        return super(OnlineorderManager, self).filter(user=user)

    def get_recent_user(self, user, num):
        return super(OnlineorderManager, self).filter(user=user)[:num]


class Onlineorder(models.Model):
    user = models.ForeignKey('User', models.DO_NOTHING)
    transaction_id = models.CharField(max_length=100)
    order_id = models.CharField(max_length=100)
    amount = models.IntegerField(default = 0)
    success = models.BooleanField(default=False)
    transaction_status = models.CharField(max_length=100)
    pay_type = models.CharField(max_length=10)
    crated_time = models.DateTimeField(default=timezone.now)

    objects = OnlineorderManager()

    def __str__(self):
        return '%s %s' % (self.transaction_id , self.order_id)

    class Meta:
        db_table = 'onlineorder'
        verbose_name = "결제정보"
        verbose_name_plural = "결제정보"

import time
import random
import hashlib
from django.db.models.signals import post_save

def new_point_trans_validation(sender, instance, created, *args, **kwargs):
    if instance.transaction_id:
        # 거래 후 아임포트에서 넘긴 결과
        v_trans = Onlineorder.objects.validation_trans(
            merchant_id=instance.order_id
        )

        res_merchant_id = v_trans['merchant_id']
        res_imp_id = v_trans['imp_id']
        res_amount = v_trans['amount']

        # 데이터베이스에 실제 결제된 정보가 있는지 체크
        r_trans = Onlineorder.objects.filter(
            order_id=res_merchant_id,
            transaction_id=res_imp_id,
            amount=res_amount
        ).exists()

        if not v_trans or not r_trans:
            raise ValueError('비정상적인 거래입니다.')


post_save.connect(new_point_trans_validation, sender=Onlineorder)


class Coupon(models.Model):
    #user = models.ForeignKey('User', models.DO_NOTHING)
    cp_name = models.CharField(max_length=100)
    dis_amount = models.IntegerField()
    create_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '%s - %s' % (self.cp_name , self.dis_amount)

    class Meta:
        managed = False
        db_table = 'coupon'
        verbose_name = "쿠폰-일반"
        verbose_name_plural = "쿠폰-일반"


class CouponUser(models.Model):
    user = models.ForeignKey('User', models.DO_NOTHING)
    coupon = models.ForeignKey(Coupon, models.DO_NOTHING)

    def __str__(self):
        return '%s %s' % (self.coupon.cp_name , self.user.last_name)


    class Meta:
        managed = False
        db_table = 'coupon_user'


class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'cart'
        ordering = ['created']
    def __str__(self):
        return self.cart_id


class Cartitem(models.Model):
    movie = models.ForeignKey(Onlinemovie, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    avtive = models.BooleanField(default=True)
    class Meta:
        managed = False
        db_table = 'cartitem'
    def sub_total(self):
        return self.movie.amount * self.quantity

    def __str__(self):
        return self.movie.movie