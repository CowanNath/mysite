from django.shortcuts import render,get_object_or_404
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Count
from .models import Blog, BlogType
from read_statistics.utils import read_statistics_once_read

# Create your views here.
def get_blog_list_common_data(blogs_all_list,request):
    paginator = Paginator(blogs_all_list, settings.BLOGS_OF_EACH_PAGE) #将每4篇文章分成一页
    page_num = request.GET.get('page', 1) # 获取url页面参数（GET请求）
    page_of_blogs = paginator.get_page(page_num)
    current_num = page_of_blogs.number #获取当前页码
    # 获取当前页码的前后两个的范围
    page_range = list(range(max(current_num - 2, 1),current_num)) + list(range(current_num, min(current_num + 2, paginator.num_pages) + 1))
    # 增加页码省略号标记
    if page_range[0] - 1 >= 2:
        page_range.insert(0,"...")
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append("...")
    #增加首尾两个页码
    if page_range[0] != 1:
        page_range.insert(0,1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    #获取博客分类对应博客的数量
    # 获取博客分类方法一：
    # blog_types = BlogType.objects.all()
    # blog_types_list = []
    # for blog_type in blog_types:
    #     blog_type.blog_count = Blog.objects.filter(blog_type = blog_type).count()
    #     blog_types_list.append(blog_type)
    # 获取博客分类方法二：使用annotate方法
    # BlogType.objects.annotate(blog_count = Count('blog'))

    # 获取分日期统计相对于的博客数量：
    blog_dates = Blog.objects.dates('create_time','month',order='DESC')
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(create_time__year=blog_date.year, create_time__month=blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count

    context = {}
    context["page_of_blogs"] = page_of_blogs
    context["page_range"] = page_range
    context['blogs'] = page_of_blogs.object_list
    context["blog_types"] = BlogType.objects.annotate(blog_count = Count('blog')).order_by('blog_count')
    context["blog_dates"] = blog_dates_dict
    return context

def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = get_blog_list_common_data(blogs_all_list,request)
    return render(request, 'blog_list.html', context)

def blogs_with_type(request, blogs_type_pk):
    blog_type = get_object_or_404(BlogType, pk = blogs_type_pk)
    blogs_all_list = Blog.objects.filter(blog_type = blog_type)
    context = get_blog_list_common_data(blogs_all_list,request)
    context['blog_type'] = blog_type
    return render(request, 'blogs_with_type.html', context)

def blogs_with_date(request, year, month):
    blogs_all_list = Blog.objects.filter(create_time__year=year, create_time__month=month)
    context = get_blog_list_common_data(blogs_all_list,request)
    context["blog_with_date"] = '%s年%s月' % (year, month)
    return render(request, 'blogs_with_date.html', context)

def blog_detail(request, blog_pk):
    blog = get_object_or_404(Blog, pk = blog_pk)
    read_cookie_key = read_statistics_once_read(request, blog)

    context = {}
    context['previous_blog'] = Blog.objects.filter(create_time__gt = blog.create_time).last()
    context['next_blog'] = Blog.objects.filter(create_time__lt = blog.create_time).first()
    context['blog'] = blog
    response = render(request, 'blog_detail.html', context)
    response.set_cookie(read_cookie_key, 'true') # 阅读cookie标记
    return response
