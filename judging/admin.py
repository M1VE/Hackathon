from django.contrib import admin
from .models import Criterion, Judge, JudgeAssignment, Score

admin.site.register(Criterion)
admin.site.register(Judge)
admin.site.register(JudgeAssignment)
admin.site.register(Score)