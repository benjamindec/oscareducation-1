# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.response import TemplateResponse
from datetime import datetime

from django.views import View

import json

from algebra.engine import Expression, ExpressionError, Equation, Inequation, EquationSystem
from algebra.models import AlgebraicExercice
from random import choice


# Create your views here.

class List(View):

    def get(self, request):
        expressions = AlgebraicExercice.objects.all()
        context = {
            'expressions': [expression.__dict__ for expression in expressions]
        }
        return TemplateResponse(request, "algebra/list.haml", context)

class TrainingSession(View):

    def get(self, request):
	expressions = AlgebraicExercice.objects.filter(level=1)
	#expressions = AlgebraicExercice.objects.get(id=5)
	#expressions = AlgebraicExercice.objects.all()

	number = expressions.count()

	i=0
	tab = []
	while i!=10 :
		myrandom = choice(range(0, number-1))
		while myrandom in tab:
			myrandom = choice(range(0, number-1))
		tab.append(myrandom)
		i+=1
	print tab

	i=0
	TabExpressions = []
	for expression in expressions:
		if i in tab:
			print i
			TabExpressions.append(expression)
		i+=1

	'''for expression in expressions:
		print expression.id'''
	#print expressions.id
        context = {
            'expressions': TabExpressions
        }
        return TemplateResponse(request, "algebra/training_session_student.haml", context)


class ExerciceCreation(View):

    def _parse(self, json):

        if not all(k in json.keys() for k in ("expression",
            "type", "solution", "level")):
            raise ValueError()
        if json["type"] not in globals().keys():
            raise ValueError()

        expr = globals()[json["type"].title().replace(" ", "")](
            json["expression"]
        )

        solution = globals()[json["type"].title().replace(" ", "")](
            json["solution"]
        )

        if (expr.solution != solution.solution):
            raise ExpressionError()

        return expr, solution

    def get(self, request):

        if request.content_type is "application/json":
            return HttpResponse(status=415)
        else:
            return TemplateResponse(request, "algebra/exercice_creation.haml")

    def post(self, request):

        if request.content_type != "application/json":
            return HttpResponse(status=415)

        try:

            expr, solution = self._parse(json.loads(request.body))
            created = datetime.now()
            db_expr = AlgebraicExercice(
                expression=str(expr),
                expression_type=expr._db_type,
                created=created,
                updated=created,
                solution=str(expr.solution),
                level=1
            )
            db_expr.save()

            return JsonResponse({
                'status': True,
                'message': "Ok"
            }, status=200)

        except ValueError as e:

            return JsonResponse({
                'status': False,
                'message': 'Malformed or incomplete request body'
            }, status=422)

        except ExpressionError as e:

            return JsonResponse({
                'status': False,
                'message': 'Malformed algebraic expression or solution'
            }, status=422)


class AssessmentCreation(View):

    def get(self, request):
        return TemplateResponse(request, "algebra/assessment_creation.haml")
