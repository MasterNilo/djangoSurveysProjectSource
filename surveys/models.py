import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse


class Survey(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    RELEASED = 'RL'
    UNRELEASED = 'UR'
    STATUS_CHOICES = [
        (RELEASED, 'Released'),
        (UNRELEASED, 'Unreleased'),
    ]
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=UNRELEASED
    )
    date_created = models.DateField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_created']
        permissions = [('survey_author', 'Survey full permission')]
        # This permission is not used to its intended purpose for now.
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('edit_survey_url', kwargs={'pk': str(self.pk)})

    def set_status(self, status):
        self.status = status
        
    def ready_to_release(self):
        # Surveys cannot be released if they have no questions, or if any of its
        # questions has no options. When question types are implemented properly
        # Open Ended questions will need an empty textarea field.
        if self.questions.count()<1:
            return False
        for question in self.questions.all():
            if question.options.count()<1:
                return False
        return True


class Question(models.Model):
    TRUE_OR_FALSE = 'TF'
    SINGLE_CHOICE = 'SC'
    MULTIPLE_CHOICE = 'MC'
    OPEN_ENDED = 'OE'
    RATING_SCALE = 'RS'
    MATRIX_QUESTION = 'MQ'
    LIKERT_SCALE = 'LS'  # un/satisfied, dis/agree, un/helpful -> 5 variants for each
    DROPDOWN_QUESTION = 'DQ'
    QUESTION_TYPE = [
        (TRUE_OR_FALSE, 'True or False'),
        (SINGLE_CHOICE, 'Single Choice'),
        (MULTIPLE_CHOICE, 'Multiple Choice'),
        (OPEN_ENDED, 'Open Ended'),
        (RATING_SCALE, 'Rating Scale'),
        (MATRIX_QUESTION, 'Matrix Question'),
        (LIKERT_SCALE, 'Likert Scale'),
        (DROPDOWN_QUESTION, 'Dropdown Question'),
    ]
    type = models.CharField(
        max_length=2,
        choices=QUESTION_TYPE,
        default=TRUE_OR_FALSE
    )
    text = models.CharField(max_length=250)
    survey = models.ForeignKey(Survey, related_name='questions', on_delete=models.CASCADE)
    # The related_name='something' helps by not using the default django name
    # 'modelname_set' when referenced. In this case, the default name would have
    # been 'question_set', and from Survey would have been referred to as
    # 'surveys.question_set'. When doing queries and stuff, it can be used nicely.
    # On html files, when a survey is sent as context, then it is easier to just
    # type 'survey.questions' instead of 'surveys.question_set'. This is the
    # same for all other 'related_name=' argument on the other ForeignKey model
    # fields.
    
    def __str__(self):
        return self.text
    
    def get_absolute_url(self):
        return reverse('edit_survey_url', kwargs={'pk': str(self.survey.pk)})


class Submission(models.Model):
    SUBMITTED = 'SM'
    NOT_SUBMITTED = 'NS'
    STATUS = [
        (SUBMITTED, 'Submitted'),
        (NOT_SUBMITTED, 'Not Submitted'),
    ]
    status = models.CharField(
        max_length=2,
        choices=STATUS,
        default=NOT_SUBMITTED
    )
    survey = models.ForeignKey(Survey, related_name='submissions', on_delete=models.CASCADE, blank=True)


class Option(models.Model):
    value = models.CharField(max_length=250)
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    chosen = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.value
    
    def get_absolute_url(self):
        return reverse('edit_survey_url', kwargs={'pk': str(self.question.survey.pk)})
    
    def get_chosen(self):
        return str(self.chosen)
    
    def increment_chosen(self):
        self.chosen += 1


class Answer(models.Model):
    text = models.CharField(max_length=250)
    submission = models.ForeignKey(Submission, related_name='answers', on_delete=models.CASCADE)
    option = models.ForeignKey(
        Option,
        related_name='answers',
        on_delete=models.CASCADE,
        blank=True,
    )
    
    def __str__(self):
        return self.text
