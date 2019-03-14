from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from api.models import *
from faculty.forms import ClassForm


@login_required
def dashboard(request):
    return render(request, 'faculty/dashboard.html')


@login_required
def class_overview(request):
    classes = Class.objects.filter(admin=request.user)
    return_data = {'classes': classes}

    if 'error' in request.GET:
        return_data['error_message'] = request.GET['error']

    return render(request, 'faculty/class/overview.html', return_data)


@login_required
def class_view(request, class_id):
    current_class = Class.objects.get(id=class_id)
    students = current_class.students.all()
    return_data = {'class': current_class, 'students': students}

    if 'error' in request.GET:
        return_data['error_message'] = request.GET['error']

    return render(request, 'faculty/class/view.html', return_data)


@login_required
def class_remove_student(request, class_id, student_id):
    current_class = Class.objects.get(id=class_id)
    remove_student = Student.objects.get(id=student_id)
    current_class.students.remove(remove_student)
    return redirect('/faculty/class/' + str(class_id) + '/view')


@login_required
def class_add_student(request, class_id, first_name, last_name):
    try:
        current_class = Class.objects.get(id=class_id)
        add_student = Student.objects.get(user__first_name=first_name, user__last_name=last_name)
        current_class.students.add(add_student)
        return redirect('/faculty/class/' + str(class_id) + '/view')
    except Student.DoesNotExist:
        return redirect('/faculty/class/' + str(class_id) + '/view?%s' % 'error=Student does not exist: ' + first_name + ' ' + last_name)


@login_required
def class_edit(request, class_id):
    current_class = Class.objects.get(id=class_id)
    form = ClassForm(instance=current_class)
    return render(request, 'faculty/class/form.html', {'form': form, 'class': current_class})


@login_required
def class_create(request):
    return render(request, 'faculty/class/form.html', {'form': ClassForm()})


@login_required
def class_save_form(request):
    if 'class' in request.GET:
        class_form = ClassForm(request.POST, instance=Class.objects.get(id=request.GET['class']))
    else:
        class_form = ClassForm(request.POST)

    current_class = class_form.save(commit=False)
    current_class.admin = request.user

    if current_class.start_time > current_class.end_time:
        return redirect('/faculty/class/overview?%s' % 'error=Start time after end time')

    current_class.save()
    class_form.save_m2m()

    return redirect('/faculty/class/overview')


@login_required
def class_remove(request, class_id):
    current_class = Class.objects.get(id=class_id)
    current_class.delete()
    return redirect('/faculty/class/overview')


@login_required
def class_remove_confirm(request, class_id):
    current_class = Class.objects.get(id=class_id)
    return render(request, 'faculty/class/remove.html', {'class': current_class})