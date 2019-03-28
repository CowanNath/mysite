from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from read_statistics.utils import get_seven_days_read_data, get_today_hot_data, get_yeaterday_hot_data, get_seven_days_hot_data
from blog.models import Blog
from django.contrib import auth

def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_seven_days_read_data(blog_content_type)

    # 获取7天热门博客的缓存数据
    seven_days_hot_data = cache.get('seven_days_hot_data')
    if seven_days_hot_data is None:
        seven_days_hot_data = get_seven_days_hot_data()
        cache.set('seven_days_hot_data', seven_days_hot_data, 3600)

    context = {}
    context['dates'] = dates
    context['read_nums'] = read_nums
    context['today_hot_blogs'] = get_today_hot_data(blog_content_type)
    context['yeaterday_hot_blogs'] = get_yeaterday_hot_data(blog_content_type)
    context['seven_days_hot_data'] = seven_days_hot_data
    return render(request, 'home.html', context)

def login(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(request, username=username, password=password)
    if user is not None:
        auth.login(request, user)
        return redirect('/')
    else:
        return render(request, 'error.html', {'message':'用户名或者密码不正确'})