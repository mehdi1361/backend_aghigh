import datetime
from random import randint
from celery import shared_task
from django.db.models import Q
from celery.utils.log import get_task_logger

from apps.question.models.questions import Question
from apps.question.models.managment import Advisor, AdvisorQuestion

logger = get_task_logger(__name__)


@shared_task
def add_question_to_cartable_random_expert():
    time_threshold = datetime.datetime.now() - datetime.timedelta(hours=3)
    questions = Question.objects.filter(~Q(state='cartable'), create_datetime__lte=time_threshold, state="expert")
    count_of_advisor = Advisor.objects.filter(state='expert').count()
    for question in questions:
        random_number = randint(0, count_of_advisor - 1)
        advisor_question = AdvisorQuestion()
        advisor_question.question = question
        advisor_question.status = 'waiting'
        advisor_question.user = Advisor.objects.all()[random_number]
        advisor_question.save()
        question.state = "cartable"
        question.save()


# @shared_task
# def remove_question_from_cartable_expert():
#     time_threshold = datetime.datetime.now() - datetime.timedelta(days=7)
#     questions = Question.objects.filter(state='cartable', create_datetime__lte=time_threshold)
    # count_of_advisor = Advisor.objects.filter(state='expert').count()
    # for question in questions:
    #     random_number = randint(0, count_of_advisor - 1)
    #     advisor_question = AdvisorQuestion()
    #     advisor_question.question = question
    #     advisor_question.status = 'waiting'
    #     advisor_question.user = Advisor.objects.all()[random_number]
    #     advisor_question.save()
    #     question.state = "cartable"
    #     question.save()
