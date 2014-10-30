from django.db.models import Q
from rest_framework import viewsets, permissions, mixins
from rest_utils.permissions import DenyCreateOnPutPermission

from .models import Question, Answer
from .serializers import (QuestionSerializer, CondensedQuestionSerializer,
                          AnswerSerializer)


class IsQuestionCreatorOrShared(permissions.BasePermission):
    """ Deny access to question if user does not have permission. """
    def has_object_permission(self, request, view, obj):
        if not hasattr(obj, 'shared_users'):
            # NOTE: Obj was an Answer object
            obj = obj.question
        return obj.user_has_permission(request.user)


class IsQuestionCreator(permissions.BasePermission):
    """ Deny access to question if user does not have permission. """
    def has_permission(self, request, view):
        question = Question.objects.get(pk=view.kwargs['question'])
        return question.user_has_permission(request.user)


class IsCreatorAndQuestionOpenOrReadOnly(permissions.BasePermission):
    """ Allow creator update and destroy if question is open. """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        try:
            question_is_open = obj.open
        except AttributeError:
            # NOTE: Obj is an Answer object
            question_is_open = obj.question.open

        if question_is_open and obj.created_by == request.user:
            return True


class QuestionViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                      mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin, viewsets.GenericViewSet):
    model = Question
    permission_classes = (permissions.IsAuthenticated,
                          DenyCreateOnPutPermission, IsQuestionCreatorOrShared,
                          IsCreatorAndQuestionOpenOrReadOnly)

    def get_queryset(self):
        if 'pk' not in self.kwargs:
            kwargs = {}
            if self.request.GET.get('organization', None):
                kwargs['organization'] = self.request.GET['organization']
            args = (Q(shared_users=self.request.user) |
                    Q(shared_organizations__members=self.request.user), )
            return Question.objects.filter(*args, **kwargs).distinct()
        else:
            return super(QuestionViewSet, self).get_queryset()

    def get_serializer_class(self):
        if self.request.method == 'GET' and 'pk' not in self.kwargs:
            return CondensedQuestionSerializer
        else:
            return QuestionSerializer

    def pre_save(self, obj):
        if not obj.created_by_id:
            obj.created_by = self.request.user


class AnswerViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                    mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin, viewsets.GenericViewSet):
    model = Answer
    serializer_class = AnswerSerializer
    permission_classes = (permissions.IsAuthenticated,
                          DenyCreateOnPutPermission, IsQuestionCreatorOrShared,
                          IsCreatorAndQuestionOpenOrReadOnly,
                          IsQuestionCreator)

    def get_queryset(self):
        return Answer.objects.filter(question=self.kwargs['question'])

    def pre_save(self, obj):
        if not obj.question_id:
            obj.question = Question.objects.get(pk=self.kwargs['question'])
        if not obj.created_by_id:
            obj.created_by = self.request.user
