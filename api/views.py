from datetime import datetime
import decimal
import json

from common.models import User, UserItem, Item
from common.utils import get_time_milliseconds
from django.db.models.base import ModelState
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.views.decorators.http import require_POST
import forms


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return get_time_milliseconds(obj)
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, ModelState):
            return None
        else:
            return json.JSONEncoder.default(self, obj)


class JsonResponse(HttpResponse):
    def __init__(self, data, code=200):
        super(JsonResponse, self).__init__(json.dumps(data, cls=DateTimeEncoder), content_type="application/json",
                                           status=code)


@require_POST
def register(request):
    try:
        form_data = json.loads(request.body)
    except:
        return JsonResponse({'errorMessage': 'Bad JSON format.'}, 400)
    try:
        form = forms.RegisterForm(form_data)
        result = {}
        if form.is_valid():
            result = model_to_dict(form.register(request))
        result['error'] = form.errors
        if result.has_key('password_hash'):
            del result['password_hash']
    except Exception as e:
        return JsonResponse({'errorMessage': "%s" % e}, 500)
    return JsonResponse(result)


@require_POST
def login(request):
    try:
        form_data = json.loads(request.body)
    except:
        return JsonResponse({'errorMessage': 'Bad JSON format.'}, 400)
        # try:
    form = forms.LoginForm(form_data)
    result = {}
    if form.is_valid():
        result = model_to_dict(form.login(request))
    if result.has_key('password_hash'):
        del result['password_hash']
    result['error'] = form.errors
    # #  except Exception as e:
    # return JsonResponse({'errorMessage': "%s" % e}, 500)
    return JsonResponse(result)


def get_items(request, start_form=0, item_count=10):
    try:
        user = User.objects.get(pk=request.session['user_id'])
        user_items_set = UserItem.objects.filter(owner_id=user.id).filter(pk__gt=start_form).select_related()[
                         :item_count]
        items = []
        ids = []
        for item in user_items_set:
            items.append(model_to_dict(item))
            ids.append(item.item_id)
        items_set = Item.objects.filter(id__in=ids)
        i = 0
        for item in items_set:
            items[i]['item'] = model_to_dict(item)
        result = items
    except User.DoesNotExist:
        return JsonResponse({'errorMessage': "Please login first."}, 403)
    return JsonResponse(result)


def create_item(request):
    try:
        form_data = json.loads(request.body)
    except:
        return JsonResponse({'errorMessage': 'Bad JSON format.'}, 400)
    try:
        result = {}
        user = User.objects.get(pk=request.session['user_id'])
        form = forms.CreateItemForm(form_data)
        if form.is_valid():
            result = model_to_dict(form.save(user))
        result['error'] = form.errors
    except User.DoesNotExist:
        return JsonResponse({'errorMessage': 'Please login first.'}, 403)
    return JsonResponse(result)


def pick_item(request):
    try:
        form_data = json.loads(request.body)
    except:
        return JsonResponse({'errorMessage': 'Bad JSON format.'}, 400)
    try:
        result = {}
        user = User.objects.get(pk=request.session['user_id'])
        form = forms.PickItemForm(form_data)
        if form.is_valid():
            result = model_to_dict(form.pick(user))
        result['error'] = form.errors
    except User.DoesNotExist:
        return JsonResponse({'errorMessage': 'Please login first.'}, 403)
    return JsonResponse(result)
