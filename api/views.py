from datetime import datetime
import decimal
import json

from django.db.models.base import ModelState
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.views.decorators.http import require_POST

from common.models import User, UserItem, Item
from common.utils import get_time_milliseconds
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
        result['errors'] = form.errors
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
    result['errors'] = form.errors
    # #  except Exception as e:
    # return JsonResponse({'errorMessage': "%s" % e}, 500)
    return JsonResponse(result)


def check_login(request):
    try:
        if not request.session.has_key('user_id'):
            raise User.DoesNotExist()
        user = User.objects.get(pk=request.session['user_id'])
        result = model_to_dict(user)
        result['signed_in'] = True
        if result.has_key('password_hash'):
            del result['password_hash']
    except User.DoesNotExist:
        return JsonResponse({'signed_in': False})
    return JsonResponse(result)


def get_items(request):
    try:
        start_form = request.GET.get('start_form', 0)
        item_count = request.GET.get('item_count', 10)
        user = User.objects.get(pk=request.session['user_id'])
        user_items_set = UserItem.objects.filter(owner_id=user.id).filter(pk__gt=start_form).select_related('item')[
                         :item_count]
        user_items = []
        ids = []
        for user_item in user_items_set:
            ids.append(user_item.item_id)
        items_set = Item.objects.filter(id__in=ids)
        id_to_item = dict()
        for item in items_set:
            id_to_item[item.id] = item
        for item in user_items_set:
            dict_item = model_to_dict(item)
            dict_item['item'] = model_to_dict(id_to_item[item.item_id])
            user_items.append(dict_item)
        result = user_items
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
        result['errors'] = form.errors
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
        if request.session.has_key('user_id'):
            user = User.objects.get(pk=request.session['user_id'])
        else:
            raise User.DoesNotExist()
        form = forms.PickItemForm(form_data)
        if form.is_valid():
            result = model_to_dict(form.pick(user))
        result['errors'] = form.errors
    except User.DoesNotExist:
        return JsonResponse({'errorMessage': 'Please login first.'}, 403)
    return JsonResponse(result)


def delete_user_item(request):
    try:
        form_data = json.loads(request.body)
    except:
        return JsonResponse({'errorMessage': 'Bad JSON format.'}, 400)
    try:
        result = {}
        user = User.objects.get(pk=request.session['user_id'])
        form = forms.DeleteUserItemForm(form_data, user)
        if form.is_valid():
            form.delete()
        result['errors'] = form.errors
    except User.DoesNotExist:
        return JsonResponse({'errorMessage': 'Please login first.'}, 403)
    return JsonResponse(result)


def finish_user_item(request):
    try:
        form_data = json.loads(request.body)
    except:
        return JsonResponse({'errorMessage': 'Bad JSON format.'}, 400)
    try:
        result = {}
        user = User.objects.get(pk=request.session['user_id'])
        form = forms.FinishUserItem(form_data, user)
        if form.is_valid():
            result = model_to_dict(form.finish())
        result['errors'] = form.errors
    except User.DoesNotExist:
        return JsonResponse({'errorMessage': 'Please login first.'}, 403)
    return JsonResponse(result)


def unfinish_user_item(request):
    try:
        form_data = json.loads(request.body)
    except:
        return JsonResponse({'errorMessage': 'Bad JSON format.'}, 400)
    try:
        result = {}
        user = User.objects.get(pk=request.session['user_id'])
        form = forms.UnfinishUserItem(form_data, user)
        if form.is_valid():
            result = model_to_dict(form.unfinish())
        result['errors'] = form.errors
    except User.DoesNotExist:
        return JsonResponse({'errorMessage': 'Please login first.'}, 403)
    return JsonResponse(result)


def get_public_items(request):
    finished_set = set()
    picked_set = set()
    try:
        if request.session.has_key('user_id'):
            user = User.objects.get(pk=request.session['user_id'])
            user_items = UserItem.objects.filter(owner_id=user.id)
            for user_item in user_items:
                picked_set.add(user_item.item_id)
                if user_item.finished:
                    finished_set.add(user_item.item_id)
    except User.DoesNotExist:
        pass
    source = request.GET.get('source', None)
    start_from = int(request.GET.get('start_form', 0))
    item_count = int(request.GET.get('item_count', 10))
    mgr = Item.objects.all().order_by('-created_on')
    if source is not None:
        mgr = mgr.filter(source=source)
    items = mgr.all()[start_from: (start_from + item_count)]
    result = []
    for item in items:
        model_dict = model_to_dict(item)
        model_dict['meta'] = json.loads(model_dict['meta'])
        if model_dict['id'] in picked_set:
            model_dict['picked'] = True
        if model_dict['id'] in finished_set:
            model_dict['finished'] = True
        result.append(model_dict)
    return JsonResponse(result)


def get_item(request):
    id = None
    try:
        id = request.GET.get('id', None)
    except:
        return JsonResponse({'errorMessage': 'Invalid id.'}, 400)
    try:
        item = Item.objects.get(pk=id)
    except Item.DoesNotExist:
        return JsonResponse({'errorMessage': 'Item not found.'}, 404)
    return JsonResponse(model_to_dict(item))