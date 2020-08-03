import math

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from django.db.models import Q
from django.template.context_processors import csrf
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime
from boardapp.models import *
from iamport import Iamport

# Create your views here.

# Main, Introduce Page
def main_page(request):
	articles = Boards.objects.all()
	list_count =8
	articles = articles.filter(category__category_code__contains = "webtoon")
	articles = articles.annotate(like_count=Count('boardlikes', distinct=True) ,reply_count=Count('boardreplies', distinct=True)).order_by('-id')[:list_count]

	args = {}
	args.update({"articles":articles})
	
	return render(request, 'main.html', args)

def introduce_page(request):
	return render(request, 'introduce.html')

# User Page
def user_register_page(request):
	return render(request, 'user_register.html')

def user_register_idcheck(request):
	if request.method == "POST":
		username = request.POST['username']
	else:
		username = ''

	idObject = User.objects.filter(username__exact=username)
	idCount = idObject.count()

	if idCount > 0:
		msg = "<font color='red'>이미 존재하는 ID입니다.</font><input type='hidden' name='IDCheckResult' id='IDCheckResult' value=0 />"
	else:
		msg = "<font color='blue'>사용할 수 있는 ID입니다.</font><input type='hidden' name='IDCheckResult' id='IDCheckResult' value=1 />"

	return HttpResponse(msg)

def user_register_result(request):
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		last_name = request.POST['last_name']
		phone = request.POST['phone']
		email = request.POST['email']
		birth_year = int(request.POST['birth_year'])
		birth_month = int(request.POST['birth_month'])
		birth_day = int(request.POST['birth_day'])

	try:
		if username and User.objects.filter(username__exact=username).count() == 0:
			date_of_birth = datetime(birth_year, birth_month, birth_day)

			user = User.objects.create_user(
				username, password, last_name, email, phone, date_of_birth
			)

			redirection_page = '/boardapp/user_register_completed/'
		else:
			redirection_page = '/boardapp/error/'
	except:
		redirection_page = '/boardapp/error/'

	return redirect(redirection_page)

def user_register_completed(request):
	return render(request,  'user_register_completed_page.html')

# Board Page
def board_list_page(request, category=''):
	my_text = ''
	if request.method == "GET":
		search_text = request.GET.get('q')
	else:
		search_text = ''
	school = Schools.objects.all()

	if category:
		articles = Boards.objects.filter(category__category_code=category)
		try:
			board_category = get_object_or_404(BoardCategories,category_code=category)
			list_count = board_category.list_count
		except BoardCategories.DoesNotExist:
			board_category = category
			list_count = 6
	else:
		articles = Boards.objects.all()
		board_category = BoardCategories()
		list_count =10

	list_count = 6
	if search_text:
		variable_column = request.GET.get('fd_name')
		search_type = 'contains'
		filter = variable_column + '__' + search_type
		articles = articles.filter(**{filter: request.GET.get('q')}).order_by('-registered_date')

	articles = articles.annotate(like_count=Count('boardlikes', distinct=True) ,reply_count=Count('boardreplies', distinct=True)).order_by('-id')

	paginator = Paginator(articles, list_count)
	try:
		page = int(request.GET['page'])
	except:
		page = 1
	articles = paginator.get_page(page)

	page_count = 10
	page_list = []
	first_page = (math.ceil(page/page_count)-1)*page_count+1
	last_page = min([math.ceil(page/page_count)*page_count, paginator.num_pages])
	for i in range(first_page, last_page+1):
		page_list.append(i)

	args = {}
	args.update({"articles":articles})
	args.update({"board_category":board_category})
	args.update({"search_text":search_text})
	args.update({"page_list":page_list})
	args.update({"school":school})

	return render(request, 'board_list.html', args)

class BoardView(DetailView):
	model = Boards
	template_name = 'board_view.html'

	def dispatch(self, request, pk):
		obj = self.get_object()

		if request.user != obj.user:
			obj.view_count = obj.view_count + int(1)
			obj.save()

		return render(request, self.template_name, {"object": obj})

@login_required
def board_write_page(request, category):
	args = {}

	board_category = BoardCategories.objects.get(category_code=category)
	args.update({"board_category":board_category})

	return render(request, 'board_write.html', args)

class BoardModifyView(DetailView):
	model = Boards

	template_name = 'board_modify.html'

def board_comm_list_page(request, category):
	error_flag = False

	if request.method == "POST" and request.POST['title']:
		title = request.POST['title']
		content = request.POST['content']
		try:
			img_file = request.FILES['img_file']
		except:
			img_file = None


		try:
			board_category = BoardCategories.objects.get(category_code=category)
			if request.user and title and content and request.user.is_superuser >= board_category.authority:
				article = Boards(category=board_category, user=request.user, title=title, content=content, image=img_file)
				article.save()

			else:
				error_flag = True
		except:
			error_flag = True

	articles = Boards.objects.filter(category__category_code=category).order_by('-id')
	board_category = BoardCategories.objects.get(category_code=category)

	paginator = Paginator(articles, board_category.list_count)

	if request.GET.get('page'):
		page = int(request.GET.get('page'))
	else:
		page = 1

	articles = paginator.get_page(page)

	page_count = 10
	page_list = []
	first_page = (math.ceil(page/page_count)-1)*page_count+1
	last_page = min([math.ceil(page/page_count)*page_count, paginator.num_pages])
	for i in range(first_page, last_page+1):
		page_list.append(i)

	args = {}
	args.update({"error_flag": error_flag})
	args.update({"articles":articles})
	args.update({"board_category":board_category})
	args.update({"page_list":page_list})

	return render(request, 'board_comm_list.html', args)

class BoardCommView(DetailView):
	model = Boards

	template_name = 'board_comm_view.html'

class BoardCommModifyView(DetailView):
	model= Boards

	template_name = 'board_comm_modify.html'

@login_required
def board_write_result(request):
	if request.method == "POST":
		title = request.POST['title']
		content = request.POST['content']
		category_id = request.POST['category_id']
		try:
			img_file = request.FILES['img_file']
		except:
			img_file = None
	else:
		title = None

	args={}

	try:
		category = BoardCategories.objects.get(id=category_id)

		if request.user and title and content and request.user.is_superuser >= category.authority:
			article = Boards(category=category, user=request.user, title=title, content=content, image=img_file)
			article.save()

			redirection_page = '/boardapp/board_list/' + category.category_code + '/'

		else:
			redirection_page = '/boardapp/error/'
	except:
		redirection_page = '/boardapp/error/'

	return redirect(redirection_page)

@login_required
def board_modify_result(request):
	if request.method == "POST":
		title = request.POST['title']
		content = request.POST['content']
		article_id = request.POST['id']
		referer = request.POST['referer']
		try:
			img_file = request.FILES['img_file']
		except:
			img_file = None
	else:
		title = None

	args={}

	try:
		article = Boards.objects.get(id=article_id)
		if request.user and title and content and article_id:
			
			if article.user != request.user:
				redirection_page = '/boardapp/error/'
			else:
				article.title=title
				article.content=content
				article.last_update_date=timezone.now()
				
				if img_file:
					article.image = img_file

				article.save()

				if referer == 'board':
					redirection_page = '/boardapp/board_view/' + article_id + '/'
				else:
					redirection_page = '/boardapp/comm_view/' + article_id + '/'

		else:
			redirection_page = '/boardapp/error/'
	except:
		redirection_page = '/boardapp/error/'

	return redirect(redirection_page)

@login_required
def board_delete_result(request):
	if request.method == "POST":
		article_id = request.POST['article_id']
		referer = request.POST['referer']
	else:
		article_id = -1

	args={}

	article = Boards.objects.get(id=article_id)

	if request.user == article.user:
		article.delete()
		
		if referer == "board":
			redirection_page = '/boardapp/board_list/' + article.category.category_code + '/'
		else:
			redirection_page = '/boardapp/comm_list/' + article.category.category_code + '/'
	else:
		redirection_page = '/boardapp/error/'

	return redirect(redirection_page)

def reply_list(request, article):
	replies = BoardReplies.objects.filter(article__id=article).order_by('reference_reply_id','level','id')

	args = {}
	args.update({"replies":replies})

	return render(request, 'reply_list.html', args)

class ReplyModifyView(DetailView):
	model = BoardReplies

	template_name = 'reply_modify.html'

@login_required
def reply_write_result(request):
	if request.method == "POST":
		content = request.POST['content']
		level = request.POST['level']
		id = request.POST['id']
	else:
		content = None

	args={}

	try:
		if request.user and content and id:
			if level == "0":
				article = Boards.objects.get(id=id)
				reply = BoardReplies(article=article, user=request.user, level=level, content=content)
				reply.save()
				reply.reference_reply_id=reply.id
				reply.save()

				redirection_page = '/boardapp/reply_list/' + id + '/'
			else:
				article = BoardReplies.objects.get(id=id).article
				reply = BoardReplies(article=article, user=request.user, level=level, content=content, reference_reply_id=id)
				reply.save()

				redirection_page = '/boardapp/reply_list/' + str(article.id) + '/'

		else:
			redirection_page = '/boardapp/error/'
	except:
		redirection_page = '/boardapp/error/'

	return redirect(redirection_page)

@login_required
def reply_modify_result(request):
	if request.method == "POST":
		content = request.POST['content']
		reply_id = request.POST['id']
	else:
		content = None

	try:
		if request.user and content and reply_id:
			reply = BoardReplies.objects.get(id=reply_id)
			reply.content = content
			reply.save()
			
			redirection_page = '/boardapp/reply_list/' + str(reply.article.id) + '/'

		else:
			redirection_page = '/boardapp/error/'
	except:
		redirection_page = '/boardapp/error/'

	return redirect(redirection_page)

@login_required
def reply_delete_result(request):
	if request.method == "POST":
		reply_id = request.POST['reply_id']
	else:
		reply_id = -1

	reply = BoardReplies.objects.get(id=reply_id)

	if request.user == reply.user:
		reply.delete();
		redirection_page = '/boardapp/reply_list/' + str(reply.article.id) + '/'

	else:
		redirection_page = '/boardapp/error/'

	return redirect(redirection_page)

def board_like(request, article):
	args={}

	like_count = BoardLikes.objects.filter(article__id=article).count()
	user_count = BoardLikes.objects.filter(article__id=article).filter(user=request.user).count()

	args.update({"like_count": like_count})
	args.update({"user_count": user_count})
	args.update({"article_id": article})

	return render(request, 'board_like.html', args)

def board_like_result(request):
	if request.method == "POST":
		article_id = request.POST['article_id']
	else:
		article_id = -1

	article = Boards.objects.get(id=article_id)
	like_confirm = BoardLikes.objects.filter(article=article)
	like_already_chk = like_confirm.filter(user=request.user).count()

	args = {}
	if article.user == request.user:
		args.update({"like_err_msg":"본인의 게시물에는 추천할 수 없습니다."})
	elif like_already_chk == 1:
		args.update({"like_err_msg":"이미 추천하였습니다."})
	else:
		boardlike = BoardLikes(article=article, user=request.user)
		boardlike.save()

	args.update({"article_id":article_id})

	return JsonResponse(args)

def error_page(request):
	return render(request, 'error.html')

def search_page(request) :

	if request.method == "GET":
		search_text = request.GET.get('q')
	else:
		search_text = ''

#카테고리 받아오기   html에서 관리
	articles = Boards.objects.all()
	board_category = BoardCategories.objects.all()
	list_count =10
#검색 부분
	if search_text :
		articles = articles.filter(Q(title__contains = search_text) | Q(content__contains = search_text) |
								   Q(user__last_name__contains = search_text)).order_by('-registered_date').distinct()
	args = {}
	args.update({"articles": articles})
	args.update({"board_category": board_category})
	args.update({"search_text" : search_text})

	return render(request, 'search_all.html',args)


def upload_page(request) :

	schoolname = Schools.objects.all()
	scuser = Schoolusers.objects.all()
	bookname = Booklist.objects.all()

	args={}
	args.update({"schoolname" : schoolname})
	args.update({"scuser" : scuser})
	args.update({"bookname" : bookname})

	return render(request, 'upload.html',args)

@login_required
def upload_result(request):
	if request.method == "POST":
		unit = request.POST['unit']
		Category = request.POST['category_id']
		bkname = request.POST['bookname']
		scname = request.POST['fd_name2']
		try:
			img_file = request.FILES['img_file']
		except:
			img_file = None
	else:
		title = None
	content = bkname + " " + scname + " " + unit + "주차"
	title = scname + " " + unit + "주차"


	category = BoardCategories.objects.get(category_code=Category)
	if request.user and title and content and img_file:
		for item in request.FILES.getlist('img_file') :
			article = Boards(category=category, user=request.user, title=title, content=content, image=item )
			article.save()

		redirection_page = '/boardapp/board_list/' +  category.category_code + '/'

	else:
		redirection_page = '/boardapp/'

	return redirect(redirection_page)

def online_main(request,subject=""):
	articles = Boards.objects.all()
	list_count = 10
	articles = articles.filter(category__category_code__contains="webtoon")
	articles = articles.annotate(like_count=Count('boardlikes', distinct=True),
								 reply_count=Count('boardreplies', distinct=True)).order_by('-id')[:list_count]
	onlinemovie = Onlinemovie.objects.all()
	onlineclass = Onlineclass.objects.all()
	if subject:
		list_count = 8
	movie_name = "boardapp/assets/videos/sample_video.mp4"

	args = {}
	args.update({"subject": subject})
	args.update({"onlinemovie":onlinemovie})
	args.update({"onlineclass":onlineclass})
	args.update({"movie_name":movie_name})

	return render (request, 'online_main.html',args)

@login_required
def payment(request) :
	if request.method == "POST" :
		dis_amount = request.POST.get('dis_amount')
		dis_amount = int(dis_amount)
	else :
		dis_amount = 0
	puser = request.user
	args = {}

	onmovie = Onlinemovie.objects.get(merchant_id = "AAA1004")

	onclass = Onlinemovie.objects.all()
	onclass = onclass.filter(merchant_id__contains = "AAA1004")

	if request.method == "POST" :
		dis_amount = request.POST.get('dis_amount')
		dis_amount = int(dis_amount)

		if dis_amount <= 100:
			amount = onmovie.amount
			rat = (100 - dis_amount) / 100
			amount = rat * amount
			args.update({'amount': amount})
		elif dis_amount > 101.0:
			amount = onmovie.amount
			amount = amount - dis_amount
		else:
			amount = onmovie.amount

		print(dis_amount)
		# 할인률 계산

		print(amount)

	else :
		dis_amount = 0

	args.update({"puser" : puser})
	args.update({"onclass":onclass})
	args.update({'amount': onmovie.amount})
	return render (request,'payment.html',args)

@login_required
def payment_resView(request):
	if request.method == "POST" :
		user = request.user
		merchant_id = request.POST.get('merchant_id')
		imp_id = request.POST.get('imp_id')
		amount = request.POST.get('amount')
		status = request.POST.get('status')

		print(amount,imp_id)
		print(merchant_id , status)

		trans = Onlineorder.objects.get(order_id = merchant_id,amount = amount,user = user)

	if trans is not None :
		trans.transaction_id = imp_id
		trans.transaction_status = status
		trans.success = True
		trans.save()

		data = {
			"works": True
		}
		return JsonResponse(data)
	else:
		return JsonResponse({}, status=401)

@login_required
def payment_checkoutView(request) :
	if request.method == "POST" :
		pay_type = request.POST.get('type_id')
		amount = request.POST.get('amount_id')
		user = request.user
	print(amount)
	print(pay_type)

	trans = Onlineorder.objects.create_new(
		user = user,
		amount = amount,
		pay_type = pay_type
	)



	if trans is not None:
		data = {
			"works" : True,
			"merchant_id": trans
		}
		return JsonResponse(data)
	else:
		return JsonResponse({},status = 401)


def coupon_use(request) :
	muser = request.user
	coupon = CouponUser.objects.all()
	#coupon = CouponUser.objects.get(user = muser)
	coupon = coupon.filter(user__last_name__contains = muser.last_name)
	product = Onlinemovie.objects.filter()
	args = {}
	onmovie = Onlinemovie.objects.get(merchant_id="AAA1004")
	amount = onmovie.amount
	args = ({"amount" : amount })




	onmovie = Onlinemovie.objects.get(merchant_id="AAA1004")


	args.update({"coupon" : coupon })
	return render(request,'coupon_use.html',args)



from django.core.exceptions import ObjectDoesNotExist

def _cart_id(request) :
	cart = request.session.session_key
	if not cart:
		cart = request.session.create()
	return cart

def add_cart(request,product_id) :
	product = Onlinemovie.objects.get(id=product_id)
	try :
		cart = Cart.objects.get(cart_id = _cart_id(request))
	except Cart.DoesNotExist :
		cart = Cart.objects.create(
			cart_id = _cart_id(request)
		)
		cart.save()


	cart_item = Cartitem.objects.create(
			movie = product,
			cart = cart
		)
	cart_item.save()

	return redirect('cart_detail')

def cart_detail(request,total=0,cart_items = None) :

	cart = Cart.objects.get(cart_id = _cart_id(request))
	cart_items = Cartitem.objects.filter(cart__cart_id__contains = cart.cart_id)
	for cart_item in cart_items:
		total += cart_item.movie.amount

	print(total,cart_items)


	return render(request, 'mycart.html', dict(cart_items = cart_items, total = total))