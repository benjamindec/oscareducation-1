# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.response import TemplateResponse

from django.views import View

import json

from algebra.engine import Expression, ExpressionError, Equation, Inequation, EquationSystem

# Create your views here.

class List(View):

	def get(self, request):
		return TemplateResponse(request, "algebra/list.haml")


class ExerciceCreation(View):
	
	def _parse(self, json):
		
		if not all(k in json.keys() for k in ("expression",
			"type", "solution", "level")):
			raise ValueError()
		if json["expression"] not in globals().keys():
			raise ValueError()
		
		expr = globals()[json["type"].title().replace(" ", "")](
			json["expression"]
		)

		solution = globals[json["type"].title().replace(" ", "")](
			json["solution"]
		)

		if (expr != solution):
			raise ExpressionError()

		return expr, solution

	def get(self, request):

		if request.content_type is "application/json":
			return HttpResponse(status=415)
		elif request.content_type is "text/html":
			return TemplateResponse(request, "algebra/exercice_creation.haml")
		else:
			return HttpResponse(status=415)

	def post(self, request):
		
		if request.content_type is not "application/json":
			return HttpResponse(status=415)

		try:
			
			expr, solution = self._parse(json.loads(request.body))
			expr.model.save()
			
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
				'message': 'Malformed algebrraic expression or solution'	
			}, status=422)


class AssessmentCreation(View):

	def get(self, request):
		return TemplateResponse(request, "algebra/assessment_creation.haml")