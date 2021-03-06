import datetime
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from blog.models import Blog
from .models import ReadNum, ReadDetail


def read_statistics_once_read(request, obj):
    ct = ContentType.objects.get_for_model(obj)
    key = "%s_%s_read" % (ct.model, obj.pk)

    if not request.COOKIES.get(key): 
        # 总阅读数 + 1
        readnum, created = ReadNum.objects.get_or_create(content_type = ct, object_id = obj.pk)
        readnum.read_num += 1
        readnum.save()

        # 当天阅读数 +1
        date = timezone.now().date()
        readDetail, created = ReadDetail.objects.get_or_create(content_type = ct, object_id = obj.pk, read_date = date)
        readDetail.read_num += 1
        readDetail.save()
    return key

def get_seven_days_read_data(content_type):
    today = timezone.now().date()
    dates = []
    read_nums = []
    for i in range(7, 0 ,-1):
        date = today - datetime.timedelta(days = i)
        dates.append(date.strftime('%m-%d'))
        read_details = ReadDetail.objects.filter(content_type = content_type, read_date = date)
        result = read_details.aggregate(read_num_sum = Sum('read_num'))
        read_nums.append(result['read_num_sum'] or 0)
    return dates, read_nums

def get_today_hot_data(content_type):
    today = timezone.now().date()
    read_details = ReadDetail.objects.filter(content_type = content_type, read_date = today) \
                                     .order_by('-read_num')
    return read_details[:7]

def get_yeaterday_hot_data(content_type):
    today = timezone.now().date()
    yesterday = today - datetime.timedelta(days = 1)
    read_details = ReadDetail.objects.filter(content_type = content_type, read_date = yesterday) \
                             .order_by('-read_num')
    return read_details[:7]

# def get_seven_days_hot_data(content_type):
#     today = timezone.now().date()
#     seven_day = today - datetime.timedelta(days = 7)
#     read_details = ReadDetail.objects.filter(content_type = content_type, read_date__lt = today, read_date__gte = seven_day) \
#                                      .order_by('-read_num')
#     return read_details[:7]

def get_seven_days_hot_data():
    today = timezone.now().date()
    seven_day = today - datetime.timedelta(days = 7)
    read_details =  Blog.objects.filter(read_detail__read_date__lt = today, read_detail__read_date__gte = seven_day) \
                                .values('id','title') \
                                .annotate(read_num_sum = Sum('read_detail__read_num')) \
                                .order_by('-read_num_sum')
    return read_details[:7]
