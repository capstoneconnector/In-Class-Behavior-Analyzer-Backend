from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from api.models import *
from faculty.forms import ClassForm, SurveyQuestionForm, SurveyForm, ClassEnrollmentForm


@login_required
def dashboard(request):
    classes = Class.objects.filter(admin=request.user)
    students = Class.objects.filter()
    return render(request, 'faculty/dashboard.html', {'students': students, 'classes': classes, 'student_form': ClassEnrollmentForm()})



@login_required
def student_view_table(request, class_id):
    current_class = Class.objects.filter(id=class_id)
    students = Class.objects.filter()
    return render(request, 'faculty/student_view_table.html', {'class': current_class, 'students': students})


@login_required
def positions_dashboard(request):
    positions = Position.objects.filter()
    return render(request, 'faculty/positions_dashboard.html', {'positions': positions})


@login_required
def survey_dashboard(request):
    responses = SurveyResponse.objects.filter()
    surveys = Survey.objects.filter()
    questions = SurveyQuestion.objects.filter()
    if 'survey' in request.GET:
        survey_form = SurveyForm(instance=Survey.objects.get(id=request.GET['survey']))
    else:
        survey_form = SurveyForm()

    return render(request, 'faculty/survey_dashboard.html', {'responses': responses, 'questions': questions, 'surveys': surveys, 'survey_form': survey_form, 'survey_question_form': SurveyQuestionForm()})


@login_required
def survey_questions(request, survey_id):
    questions = SurveyQuestion.objects.filter()
    survey = Survey.objects.get(id=survey_id)
    survey_for_class = survey.associated_class.objects.all()
    return_data = {'survey': survey, 'survey_for_class': survey_for_class, 'questions': questions}

    if 'error' in request.GET:
        return_data['error_message'] = request.GET['error']
    return render(request, 'faculty/survey_questions.html', return_data)


@login_required
def survey_responses(request, survey_id):
    responses = SurveyResponse.objects.filter()
    survey = Survey.objects.get(id=survey_id)
    survey_for_class = survey.associated_class.objects.all()
    return_data = {'survey': survey, 'survey_for_class': survey_for_class, 'responses': responses}

    if 'error' in request.GET:
        return_data['error_message'] = request.GET['error']
    return render(request, 'faculty/survey_responses.html', return_data)


@login_required
def feedback(request):
    feed = Feedback.objects.filter()
    return render(request, 'faculty/feedback.html', {'feed': feed})


@login_required
def register(request):
    return render(request, 'faculty/register.html')


@login_required
def forgot_password(request):
    return render(request, 'faculty/forgot_password.html')


@login_required
def class_overview(request, class_id):
    classes = Class.objects.filter(id=class_id)
    return_data = {'classes': classes}

    if 'error' in request.GET:
        return_data['error_message'] = request.GET['error']

    return render(request, 'faculty/dashboard.html', return_data)


@login_required
def class_edit(request, class_id):
    current_class = Class.objects.get(id=class_id)
    form = ClassForm(instance=current_class)
    return render(request, 'faculty/dashboard.html', {'form': form, 'class': current_class})


@login_required
def class_remove(request, class_id):
    current_class = Class.objects.get(id=class_id)
    current_class.delete()
    return redirect('dashboard')


@login_required
def class_create(request):
    return render(request, 'faculty/dashboard.html', {'form': ClassForm()})


@login_required
def survey_question_create(request):
    return render(request, 'faculty/survey_dashboard.html', {'survey_form': SurveyQuestionForm()})


@login_required
def student_enrollment_create(request):
    return render(request, 'faculty/dashboard.html', {'student_form': ClassEnrollmentForm()})


@login_required
def survey_save_form(request):
    if 'survey' in request.GET:
        survey_form = SurveyForm(request.POST, instance=Survey.objects.get(id=request.GET['survey']))
    else:
        survey_form = SurveyForm(request.POST)

    if not survey_form.is_valid():
        print(survey_form.errors)

    current_survey = survey_form.save(commit=False)
    current_survey.admin = request.user

    current_survey.save()
    survey_form.save_m2m()

    return redirect('survey_dashboard')


@login_required
def enrollment_save_form(request):
    if 'class' in request.GET:
        student_form = ClassEnrollmentForm(request.POST, instance=ClassEnrollment.objects.get(id=request.GET['class']))
    else:
        student_form = ClassEnrollmentForm(request.POST)

    if not student_form.is_valid():
        print(student_form.errors)

    current_enrollment = student_form.save(commit=False)
    current_enrollment.admin = request.user

    current_enrollment.save()
    student_form.save_m2m()

    return redirect('dashboard')


@login_required
def class_save_form(request):
    if 'class' in request.GET:
        class_form = ClassForm(request.POST, instance=Class.objects.get(id=request.GET['class']))
    else:
        class_form = ClassForm(request.POST)

    current_class = class_form.save(commit=False)
    current_class.admin = request.user

    if current_class.start_time > current_class.end_time:
        return redirect('dashboard?%s' % 'error=Start time after end time')

    current_class.save()
    class_form.save_m2m()

    return redirect('dashboard')


@login_required
def question_save_form(request):
    if 'survey' in request.GET:
        survey_form = SurveyQuestionForm(request.POST, instance=SurveyQuestion.objects.get(id=request.GET['survey']))
    else:
        survey_form = SurveyQuestionForm(request.POST)

    if not survey_form.is_valid():
        print(survey_form.errors)

    current_survey = survey_form.save(commit=False)
    current_survey.admin = request.user

    current_survey.save()
    survey_form.save_m2m()

    return redirect('survey_dashboard')


@login_required
def question_form(request):
    if 'survey' in request.GET:
        survey_question_form = SurveyQuestionForm(instance=SurveyQuestion.objects.get(id=request.GET['survey']))
    else:
        survey_question_form = SurveyQuestionForm()
    return render(request, 'faculty/survey_question_form.html', {'survey_question_form': survey_question_form})


@login_required
def add_students_specific_class(request, class_id, first_name, last_name):
    try:
        current_class = Class.objects.get(id=class_id)
        add_student = ClassEnrollment.objects.get(student__user__first_name=first_name, student__user__last_name=last_name)
        current_class.classenrollment_set.add(add_student)

        return redirect('/faculty/' + str(class_id) + '/view_student')
    except ClassEnrollment.DoesNotExist:
        return redirect('/faculty/' + str(class_id) + '/view_student?%s' % 'error=Student does not exist: ' + first_name + ' ' + last_name)


@login_required
def class_view(request, class_id):
    current_class = Class.objects.get(id=class_id)
    students = current_class.classenrollment_set.all()
    return_data = {'class': current_class, 'students': students}

    if 'error' in request.GET:
        return_data['error_message'] = request.GET['error']

    return render(request, 'faculty/student_view_table.html', return_data)


@login_required
def questions_view(request):
    questions = SurveyQuestion.objects.filter()
    return render(request, 'faculty/survey_questions.html', {'questions': questions})


@login_required
def responses_view(request):
    return render(request, 'faculty/survey_responses.html')


@login_required
def add_survey_question(request, survey_id):
    survey = Survey.objects.get(id=survey_id)
    add_question = SurveyQuestion.objects.get(id=survey_id)
    survey.associated_class.add(add_question)
    return redirect('/faculty/' + str(survey_id) + '/view_survey')


@login_required
def survey_view(request, survey_id):
    survey = Survey.objects.get(id=survey_id)
    survey_for_class = survey.associated_class.objects.all()
    return_data = {'survey': survey, 'survey_for_class': survey_for_class}

    if 'error' in request.GET:
        return_data['error_message'] = request.GET['error']

    return render(request, 'faculty/survey_dashboard.html', return_data)


@login_required
def student_view_form(request):
    if 'student' in request.GET:
        student_form = ClassEnrollmentForm(instance=ClassEnrollment.objects.get(id=request.GET['student']))
    else:
        student_form = ClassEnrollmentForm()
    return render(request, 'faculty/student_enrollment_form.html', {'student_form': student_form})
