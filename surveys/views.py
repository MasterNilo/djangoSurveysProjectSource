from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.db import transaction
from django.forms import formset_factory
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView

# HomepageView and AboutView should have been created on a pages django app. It
# is done here for simplicity.
from django.views.generic import UpdateView

from surveys.forms import EditQuestionForm
from surveys.forms import FillQuestionForm
from surveys.forms import NewQuestionForm
from surveys.forms import OptionForm
from surveys.models import Answer
from surveys.models import Option
from surveys.models import Question
from surveys.models import Submission
from surveys.models import Survey


class HomepageView(TemplateView):
    template_name = '../templates/homepage.html'


class AboutView(TemplateView):
    template_name = '../templates/about.html'


class SurveyListView(LoginRequiredMixin, ListView):
    model = Survey
    context_object_name = 'survey_list'
    template_name = 'surveys/survey_list.html'
    redirect_field_name = 'next_stop_is'
    
    def get_context_data(self, *args, object_list=None, **kwargs):
        # Calling the base implementation first to get the context
        context = super().get_context_data(**kwargs)
        # Adding in a filtered QuerySet of all surveys created by the requesting user
        context['survey_list'] = Survey.objects.filter(author=self.request.user)
        return context


class ThankYouView(TemplateView):
    template_name = 'surveys/thank_you.html'


class ErrorPageView(TemplateView):
    template_name = 'surveys/error.html'


class NewSurveyView(LoginRequiredMixin, CreateView):
    model = Survey
    fields = ('title',)
    template_name = 'surveys/new_survey.html'
    
    def form_valid(self, form):
        # Assigning the requesting user as the survey author if the form is valid.
        form.instance.author = self.request.user
        permission = Permission.objects.get(codename='survey_author')
        self.request.user.user_permissions.add(permission)
        # Adding the 'survey_author' permission, even though there is no use for
        # it at this time.
        return super().form_valid(form)


class SurveyDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Survey
    template_name = 'surveys/delete_survey.html'
    permission_required = 'surveys.survey_author'
    success_url = reverse_lazy('survey_list_url')
    context_object_name = 'survey'
    
    def dispatch(self, request, *args, **kwargs):
        # Making sure the requesting user is the author of the survey
        survey = self.get_object()
        if survey.author != self.request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class SurveyReleaseView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Survey
    fields = ['status', ]
    context_object_name = 'survey'
    permission_required = 'surveys.survey_author'
    template_name = 'surveys/release_survey.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Making sure the requesting user is the author of the survey
        survey = self.get_object()
        if survey.author != self.request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        if request.POST['status'] == Survey.UNRELEASED:
            survey = Survey.objects.get(id=kwargs['pk'])
            survey.set_status(Survey.UNRELEASED)
            survey.save()
            
            return redirect('edit_survey_url', kwargs['pk'])
        elif request.POST['status'] == Survey.RELEASED:
            survey = Survey.objects.get(id=kwargs['pk'])
            if survey.ready_to_release():
                survey.set_status(Survey.RELEASED)
                survey.save()
            
                return redirect('survey_share_url', kwargs['pk'])
            else: # If the survey is not ready to be released
                return redirect('edit_survey_url', kwargs['pk'])


class SurveyShareView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Survey
    permission_required = 'surveys.survey_author'
    template_name = 'surveys/share_survey.html'
    context_object_name = 'survey'
    
    def dispatch(self, request, *args, **kwargs):
        # Making sure the requesting user is the author of the survey
        survey = self.get_object()
        if survey.author != self.request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class SurveyProgressView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Survey
    context_object_name = 'survey'
    template_name = 'surveys/survey_progress.html'
    permission_required = 'surveys.survey_author'
    
    def dispatch(self, request, *args, **kwargs):
        # Making sure the requesting user is the author of the survey
        survey = self.get_object()
        if survey.author != self.request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class SurveyFillOutView(TemplateView):
    template_name = 'surveys/fill_survey.html'
    
    def get(self, request, *args, **kwargs):
        survey = Survey.objects.get(id=self.kwargs['pk'])
        questions = survey.questions.all()
        
        # Creating a list of all question forms needed with all the questions
        # for the given survey.
        question_forms = []
        for i in range(len(questions)):
            question_form = FillQuestionForm(
                question=questions[i],
                lbl=f'Q{i}_' # This label will be used to identify each question
                             # and its options easily.
            )
            question_forms.append(question_form)
        context = {
            'survey': survey,
            'question_forms': question_forms,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        survey = Survey.objects.get(id=self.kwargs['pk'])
        submission = Submission.objects.create(
            status=Submission.NOT_SUBMITTED,
            survey=survey,
        )
        questions = survey.questions.all()
        
        question_forms = []
        answers = []
        invalid_form = True
        # This will be used to check if any of the forms was False, which is
        # used to check if answers can be created in bulk. This is probably too
        # extra since the html has a bunch of input with the 'required' keyword.
        # Which means that no form will come in invalid, since they all are
        # readioselect forms.
        for i in range(len(questions)):
            question_form = FillQuestionForm(
                request.POST,
                question=questions[i],
                lbl=f'Q{i}_' # This label will be used to identify each question
                             # and its options easily.
            )
            question_forms.append(question_form)
            
            if question_form.is_valid():
                chosen = question_form.cleaned_data.get(f'Q{i}_option')
                if chosen:
                    option = questions[i].options.get(value=chosen)
                    option.increment_chosen()
                    option.save()
                    answers.append(
                        Answer(
                            text=option.value,
                            submission=submission,
                            option=option,
                        )
                    )
                invalid_form = False
            else:
                invalid_form = True
                break
        if not invalid_form:
            try:
                with transaction.atomic():
                    Answer.objects.bulk_create(answers)
                    # Creating and saving a bunch of answers.
                    
                    # Messages are not used in the server, they are here as a just-in-case.
                    messages.success(request, 'Successfully answered the survey.')
                submission.status = submission.SUBMITTED
                submission.save()
                
                return redirect(reverse_lazy('thank_you_url'))
            except IntegrityError:
                messages.error(request, 'There was an error submitting your answers.')
                
                return redirect(reverse('error_url'))
        context = {
            'survey': survey,
            'question_forms': question_forms,
        }
        return render(request, self.template_name, context)


class EditSurveyView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Survey
    fields = ('title',)
    template_name = 'surveys/edit_survey.html'
    permission_required = 'surveys.survey_author'
    context_object_name = 'survey'
    
    def dispatch(self, request, *args, **kwargs):
        # Making sure the requesting user is the author of the survey
        survey = self.get_object()
        if survey.author != self.request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class NewQuestionView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'surveys/new_question.html'
    permission_required = 'surveys.survey_author'
    action = 'update'
    
    def get(self, request, *args, **kwargs):
        survey = Survey.objects.get(id=self.kwargs['pk'])
        if survey.author != self.request.user:
        # Making sure the requesting user is the author of the survey
            raise PermissionError
        
        OptionFormSet = formset_factory(OptionForm)
        # Formsets allow the generation of forms dynamically right on the page
        # with the help of JavaScript.
        
        question_form = NewQuestionForm()
        option_formset = OptionFormSet()
        
        context = {
            'question_form': question_form,
            'option_formset': option_formset,
            'survey_title': survey.title,
            'survey_pk': survey.pk,
            'action': self.action,
        }
        return render(
            request,
            self.template_name,
            context,
        )
    
    def post(self, request, *args, **kwargs):
        survey = Survey.objects.get(id=self.kwargs['pk'])
        if survey.author != self.request.user:
        # Making sure the requesting user is the author of the survey
            raise PermissionError
        
        NewOptionFormSet = formset_factory(OptionForm)
        # Formsets allow the generation of forms dynamically right on the page
        # with the help of JavaScript.
        
        question_form = NewQuestionForm(request.POST)
        option_formset = NewOptionFormSet(request.POST)
        
        if question_form.is_valid() and option_formset.is_valid():
            qtype = question_form.cleaned_data.get('type')
            qtext = question_form.cleaned_data.get('text')
            
            new_question = Question.objects.create(
                type=qtype,
                text=qtext,
                survey=survey
            )
            new_question.save()
            
            options = []
            for option_form in option_formset:
                value = option_form.cleaned_data.get('value')
                options.append(Option(value=value, question=new_question))
            try:
                with transaction.atomic():
                    Option.objects.bulk_create(options)
                return redirect(reverse('edit_survey_url', kwargs=self.kwargs))
            except IntegrityError:
                return redirect(reverse('edit_survey_url', kwargs=self.kwargs))
        
        context = {
            'question_form': question_form,
            'option_formset': option_formset,
            'survey_title': survey.title,
            'survey_pk': survey.pk,
            'action': self.action,
        }
        return render(
            request,
            self.template_name,
            context,
        )


class EditQuestionView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'surveys/new_question.html'
    permission_required = 'surveys.survey_author'
    action = 'update'
    
    def get(self, request, *args, **kwargs):
        survey = Survey.objects.get(id=self.kwargs['pk'])
        if survey.author != self.request.user:
        # Making sure the requesting user is the author of the survey
            raise PermissionError
        question = Question.objects.get(id=self.kwargs['question'])
        
        EditOptionFormSet = formset_factory(OptionForm)
        
        q_options = Option.objects.filter(question=question)
        options_data = [{'value': option.value} for option in q_options]
        # Pre-populating the options with the previous information on them.
        
        question_form = EditQuestionForm(question=question)
        option_formset = EditOptionFormSet(initial=options_data)
        # Setting the pre-populated options as the initial data.
        
        context = {
            'question_form': question_form,
            'option_formset': option_formset,
            'survey_title': survey.title,
            'survey_pk': survey.pk,
            'action': self.action,
        }
        return render(
            request,
            self.template_name,
            context,
        )
    
    def post(self, request, *args, **kwargs):
        survey = Survey.objects.get(id=self.kwargs['pk'])
        if survey.author != self.request.user:
        # Making sure the requesting user is the author of the survey
            raise PermissionError
        question = Question.objects.get(id=self.kwargs['question'])
        
        EditOptionFormSet = formset_factory(OptionForm)
        
        q_options = Option.objects.filter(question=question)
        options_data = [{'value': option.value} for option in q_options]
        # Pre-populating the options with the previous information on them.
        
        question_form = EditQuestionForm(request.POST, question=question)
        option_formset = EditOptionFormSet(request.POST, initial=options_data)
        # Setting the pre-populated options as the initial data.
        
        if question_form.is_valid() and option_formset.is_valid():
            qtype = question_form.cleaned_data.get('type')
            qtext = question_form.cleaned_data.get('text')
            
            question.text = qtext
            question.type = qtype
            
            question.save()
            
            options = []
            for option_form in option_formset:
                # Getting the options set from the forms in formset
                value = option_form.cleaned_data.get('value')
                if value:
                    options.append(Option(value=value, question=question))
            try:
                with transaction.atomic():
                    Option.objects.filter(question=question).delete()
                    Option.objects.bulk_create(options)
                    
                    messages.success(request, 'Question updated.')
                return redirect(reverse('edit_survey_url', kwargs={'pk': self.kwargs['pk']}))
            
            except IntegrityError:
                messages.error(request, 'There was an error saving the question.')
                return redirect(reverse('edit_survey_url', kwargs={'pk': self.kwargs['pk']}))
        
        context = {
            'question_form': question_form,
            'option_formset': option_formset,
            'survey_title': survey.title,
            'survey_pk': survey.pk,
            'action': self.action,
        }
        return render(
            request,
            self.template_name,
            context,
        )


class DeleteQuestionView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Question
    template_name = 'surveys/delete_question.html'
    permission_required = 'surveys.survey_author'
    
    def dispatch(self, request, *args, **kwargs):
        # Making sure the requesting user is the author of the survey
        question = self.get_object()
        if question.survey.author != self.request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('edit_survey_url', kwargs={'pk': self.kwargs['pk']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['survey'] = Survey.objects.get(id=self.kwargs['pk'])
        context['question'] = Question.objects.get(id=self.kwargs['id'])
        return context
    
    def get_object(self, queryset=None):
        id = self.kwargs.get('id')
        question = get_object_or_404(Question, id=id)
        
        return question