from django import forms

from surveys.models import Question


class FillQuestionForm(forms.Form):
    # Not my best work, but it gets the job done...
    def __init__(self, *args, **kwargs):
        self.question = kwargs.pop('question')
        self.lbl = kwargs.pop('lbl')
        self.q_text = self.question.text
        super(FillQuestionForm, self).__init__(*args, **kwargs)
        
        # Populate the choices based on the question options.
        choices = []
        options = self.question.options.all()
        for i in range(len(options)):
            choices.append((options[i], options[i]))
       
       # The self.lbl+'option' name is used to identify each field individually
        # based on their respective question.
        self.fields[f'{self.lbl}option'] = forms.CharField(
            widget=forms.RadioSelect(
                choices=choices,
            ),
            label=self.q_text, # Using the question text as the label in order
                               # to use it on an html easily.
        )


class OptionForm(forms.Form):
    value = forms.CharField(
        max_length=250,
        required=True,
        label="Option",
        widget=forms.TextInput(attrs={
            'placeholder': "Option text"
        }),
    )


class NewQuestionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(NewQuestionForm, self).__init__(*args, **kwargs)
        
        self.fields['text'] = forms.CharField(
            max_length=250,
            required=True,
            widget=forms.TextInput(attrs={'placeholder': 'Question text'}),
        )
        self.fields['type'] = forms.ChoiceField(
            choices=Question.QUESTION_TYPE,
            required=True,
            initial=Question.TRUE_OR_FALSE,
        )


class EditQuestionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.question = kwargs.pop('question', None)
        super(EditQuestionForm, self).__init__(*args, **kwargs)
        
        self.fields['text'] = forms.CharField(
            max_length=250,
            required=True,
            initial=self.question.text or '',
            widget=forms.TextInput(attrs={'placeholder': 'Question text'}),
        )
        self.fields['type'] = forms.ChoiceField(
            choices=Question.QUESTION_TYPE,
            required=True,
            initial=self.question.type or Question.TRUE_OR_FALSE,
        )