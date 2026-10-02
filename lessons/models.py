from django.db import models

DAY_CHOICES = [
    ("Monday", "Monday"),
    ("Tuesday", "Tuesday"),
    ("Wednesday", "Wednesday"),
    ("Thursday", "Thursday"),
    ("Saturday", "Saturday"),
    ("Sunday", "Sunday"),
]


class Stage(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Day(models.Model):
    name = models.CharField(max_length=20, choices=DAY_CHOICES, unique=True)
    order = models.PositiveIntegerField(default=0)  # For sorting

    class Meta:
        ordering = ["order"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(name__in=[choice[0] for choice in DAY_CHOICES]),
                name="day_name_without_friday",
            )
        ]

    def __str__(self):
        return self.name


class Period(models.Model):
    name = models.CharField(max_length=20)  # e.g., "First Period", "Second Period"
    order = models.PositiveIntegerField(default=0)  # For sorting

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class Lessons(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name="lessons" , default=1)
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name="lessons" , default=1)
    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name="lessons", null=True, blank=True)
    lesson_name = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["stage", "day", "period"], name="unique_stage_day_period")
        ]

    def __str__(self):
        return f"{self.lesson_name} ({self.stage} - {self.day} - {self.period})"

