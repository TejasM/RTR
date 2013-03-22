from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.utils import timezone

from rtr.models import Session, Series, Stats, Question, Stat


def index(request):
    if request.session.get('type') is not None:
        if request.session.get('type') == 'creater':
            return HttpResponseRedirect('profDisplay')
    return render(request, 'rtr/index.html')


@login_required()
def end_session(request):
    request.session.clear()
    return redirect(reverse('rtr:index'))


@login_required()
def audience_display(request):
    if request.session.get('session') is not None:
        statids = request.session.get('statids')
        if statids[-1] == ',':
            statids = statids[:len(statids) - 1]
        statids = statids.split(',')
        labels = []
        for ids in statids:
            labels.append(Stats.objects.get(pk=int(ids)).name)
        return render(request, 'rtr/audience_view.html', {'labels': labels, 'size': range(len(labels))})
    else:
        return redirect(request, 'rtr/index.html')


@login_required()
def ask_question(request):
    Question.objects.create(question=request.POST['question'], session=request.session.get('session'),
                            time_asked=timezone.now())


@login_required()
def updateStats(request):
    statids = request.session.get('statids').split(',')
    for i, stats in enumerate(statids):
        Stat.objects.create(change=request.POST['value' + str(i)], timestamp=timezone.now(),
                            stats=Stats.objects.get(pk=stats))


def calculate_stats(stats_per_user):
    result = 0
    for user_stat in stats_per_user:
        changes_by_user = Stat.objects.filter(stats=user_stat)
        total_user_change = 0
        for single_stat in changes_by_user:
            total_user_change += single_stat.change
        result += total_user_change
    result /= len(stats_per_user)
    return result


@login_required()
def get_stats(request):
    if request.session.get('type') == 'creater':
        #Why are we getting stat object
        session = Session.objects.get(pk=request.session.get('session'))
        stats = session.stats_on.split(",")
        percentages = []
        for stat_on in stats:
            stats_per_user = Stats.objects.filter(session=request.session.get('session'), name=stat_on)
            percentages.append(calculate_stats(stats_per_user))
        return percentages
    else:
        return redirect(request, 'rtr/index.html')


@login_required()
def get_questions(request):
    if request.session.get('type') == 'creater':
        return Question.objects.filter(session=request.session.get('session'))
    else:
        return redirect(request, 'rtr/index.html')


@login_required()
def prof_display(request):
    if request.session.get('type') == 'creater':
        session = Session.objects.get(pk=request.session.get('session'))
        if session.stats_on is ("" or None):
            return redirect(reverse("rtr:prof_settings"))
        stats_on = session.stats_on.split(',')
        context = {}
        labels = []
        for i, stat in enumerate(stats_on):
            labels.append(stat.title())
        context['labels'] = labels
        return render(request, 'rtr/ProfData.html', context)
    else:
        return redirect(request, 'rtr/index.html')


@login_required()
def prof_start_display(request):
    session = Session.objects.get(pk=request.session.get('session'))
    if session.stats_on is ("" or None):
        try:
            _ = request.POST['understanding_toggle']
            session.stats_on += 'Understanding,'
        except Exception as _:
            pass
        try:
            _ = request.POST['interest_toggle']
            session.stats_on += 'Interest,'
        except Exception as _:
            pass
        if not session.stats_on.__contains__('understanding') and not session.stats_on.__contains__('interest'):
            return redirect(reverse("rtr:prof_settings"), {"error_message": "Select at least one of the stats"})
        session.save()
    return prof_display(request)


@login_required()
def prof_settings(request):
    if request.session.get('type') == 'creater':
        return render(request, 'rtr/prof_settings.html')
    else:
        return redirect(request, 'rtr/index.html')


def login(request):
    if request.session.get('type') is not None:
        if request.session.get('type') == 'creater':
            return redirect(reverse("rtr:prof_display"))
    username = request.POST['username']
    password = request.POST['password']
    session = request.POST['session']
    typeSession = request.POST['type_session']
    typeLogin = request.POST['optionLogin']
    if typeSession == "create":
        user = authenticate(username=username, password=password)
        if user is not None:
            try:
                series = Series.objects.get(series_id=session, live=False)
                series.live = True
                series.save()
                newSession = Session.objects.create(series=series, create_time=timezone.now(), stats_on="")
            except Series.DoesNotExist:
                try:
                    series = Series.objects.get(series_id=session)
                    return render(request, 'rtr/index.html', {"error_message": "Session already in progress"})
                except Series.DoesNotExist:
                    newSeries = Series.objects.create(series_id=session)
                    newSession = Session.objects.create(
                        series=newSeries, create_time=timezone.now(), stats_on="")
            request.session.__setitem__('session', str(newSession.id))
            request.session.__setitem__('type', 'creater')
            return HttpResponseRedirect(reverse("rtr:prof_settings"))
        else:
            return render(request, 'rtr/index.html', {"error_message": "Incorrect Username and/or Password"})
    else:
        try:
            Series.objects.get(series_id=session, live=True)
            session = Session.objects.latest('create_time')
            stats = session.stats_on.split(",")
            stat_ids = ""
            for stat in stats:
                newStats = Stats.objects.create(session=session, name=stat)
                stat_ids += str(newStats.id) + ","
            request.session.__setitem__('session', str(session.id))
            request.session.__setitem__('type', 'joiner')
            request.session.__setitem__('statids', stat_ids)
            return redirect(reverse('rtr:audience_display'))
        except Series.DoesNotExist:
            return render(request, 'rtr/index.html', {"error_message": "Incorrect session, not currently running"})