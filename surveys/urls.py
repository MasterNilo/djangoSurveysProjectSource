from django.urls import path

from surveys.views import SurveyListView
from surveys.views import ThankYouView
from surveys.views import ErrorPageView

from surveys.views import NewSurveyView
from surveys.views import SurveyDeleteView
from surveys.views import SurveyReleaseView
from surveys.views import SurveyShareView
from surveys.views import SurveyProgressView

from surveys.views import SurveyFillOutView

from surveys.views import EditSurveyView
from surveys.views import NewQuestionView
from surveys.views import EditQuestionView
from surveys.views import DeleteQuestionView

urlpatterns = [
    path('', SurveyListView.as_view(), name='survey_list_url'),
    path('thank-you/', ThankYouView.as_view(), name='thank_you_url'),
    path('unexpected-error/', ErrorPageView.as_view(), name='error_url'),
    
    path('new/', NewSurveyView.as_view(), name='new_survey_url'),
    path('<uuid:pk>/delete/', SurveyDeleteView.as_view(), name='survey_delete_url'),
    path('<uuid:pk>/release/', SurveyReleaseView.as_view(), name='survey_release_url'),
    path('<uuid:pk>/share/', SurveyShareView.as_view(), name='survey_share_url'),
    path('<uuid:pk>/', SurveyProgressView.as_view(), name='survey_progress_url'),
    
    path('<uuid:pk>/fill-out/', SurveyFillOutView.as_view(), name='survey_fillout_url'),
    
    path('<uuid:pk>/edit/', EditSurveyView.as_view(), name='edit_survey_url'),
    path('<uuid:pk>/question/new/', NewQuestionView.as_view(), name='new_question_url'),
    path('<uuid:pk>/<int:question>/edit/', EditQuestionView.as_view(), name='edit_question_url'),
    path('<uuid:pk>/<int:id>/delete/', DeleteQuestionView.as_view(), name='delete_question_url'),
]
