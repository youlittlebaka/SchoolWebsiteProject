from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Day, Lessons, Period, Stage


def _ensure_days_and_periods():
    day_values = [
        ("Monday", 1),
        ("Tuesday", 2),
        ("Wednesday", 3),
        ("Thursday", 4),
        ("Saturday", 5),
        ("Sunday", 6),
    ]
    period_values = [
        ("First Period", 1),
        ("Second Period", 2),
        ("Third Period", 3),
        ("Fourth Period", 4),
    ]

    for day_name, day_order in day_values:
        day_obj, _ = Day.objects.get_or_create(name=day_name, defaults={"order": day_order})
        if day_obj.order != day_order:
            day_obj.order = day_order
            day_obj.save(update_fields=["order"])

    for period_name, period_order in period_values:
        period_obj = Period.objects.filter(order=period_order).order_by("id").first()
        if period_obj is None:
            Period.objects.create(name=period_name, order=period_order)
        elif period_obj.name != period_name:
            period_obj.name = period_name
            period_obj.save(update_fields=["name"])

    days = Day.objects.filter(name__in=[item[0] for item in day_values]).order_by("order")
    periods = Period.objects.filter(order__in=[1, 2, 3, 4]).order_by("order", "id")[:4]
    return days, periods


def lessons_home(request):
    stages = Stage.objects.all().order_by("name")
    return render(request, "lessons_home.html", {"stages": stages})



def edit_stage_schedule(request, stage_id):
    if not request.user.is_authenticated:
        messages.error(request, "Login first")
        return redirect("core:home")
    if not (request.user.is_teacher or request.user.is_admin or request.user.is_superuser):
        messages.error(request, "You do not have permission for this action.")
        return redirect("core:home")
    stage = get_object_or_404(Stage, pk=stage_id)
    days, periods = _ensure_days_and_periods()
    can_edit = request.user.is_teacher or request.user.is_admin or request.user.is_superuser

    existing_lessons = {
        (lesson.day_id, lesson.period_id): lesson
        for lesson in Lessons.objects.filter(stage=stage, day__in=days, period__in=periods)
    }

    if request.method == "POST":
        if not can_edit:
            messages.error(request, "You do not have permission to edit this schedule.")
            return redirect("lessons:edit_stage_schedule", stage_id=stage.id)

        for day in days:
            for period in periods:
                field_name = f"slot_{day.id}_{period.id}"
                lesson_name = request.POST.get(field_name, "").strip()
                current_lesson = existing_lessons.get((day.id, period.id))

                if lesson_name:
                    if current_lesson:
                        if current_lesson.lesson_name != lesson_name:
                            current_lesson.lesson_name = lesson_name
                            current_lesson.save(update_fields=["lesson_name"])
                    else:
                        Lessons.objects.create(
                            stage=stage,
                            day=day,
                            period=period,
                            lesson_name=lesson_name,
                        )
                elif current_lesson:
                    current_lesson.delete()

        messages.success(request, "Class schedule saved.")
        return redirect("students:classroom_detail", stage_id=stage.id)

    grid_rows = []
    for day in days:
        row_cells = []
        for period in periods:
            existing = existing_lessons.get((day.id, period.id))
            row_cells.append(
                {
                    "field_name": f"slot_{day.id}_{period.id}",
                    "value": existing.lesson_name if existing else "",
                }
            )
        grid_rows.append({"day": day, "cells": row_cells})

    return render(
        request,
        "classroom.html",
        {"stage": stage, "periods": periods, "grid_rows": grid_rows, "can_edit": can_edit},
    )

