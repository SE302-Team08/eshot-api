from django.db import models
from django.contrib.postgres.fields import ArrayField

# http://stackoverflow.com/a/29088221/2926992
def to_dict(instance):
    opts = instance._meta
    data = {}
    for f in opts.concrete_fields + opts.many_to_many:
        if isinstance(f, models.ManyToManyField):
            if instance.pk is None:
                data[f.name] = []
            else:
                data[f.name] = list(f.value_from_object(instance).values_list('pk', flat=True))
        else:
            data[f.name] = f.value_from_object(instance)
    return data

# Create your models here.
class Stop(models.Model):
    """
    Showing bus stops in İzmir.
    """

    code = models.PositiveIntegerField(
        unique=True,
        primary_key=True,
        verbose_name="Code"
    )

    label = models.CharField(
        null=False,
        blank=False,
        max_length=64,
        verbose_name="Label"
    )

    coor = ArrayField(
        models.FloatField(),
        size=2,
        verbose_name="Coordination"
    )

    class Meta:
        verbose_name = "Stop"
        verbose_name_plural = "Stops"
        ordering = ["label"]

    def __str__(self):
        return self.label

class Route(models.Model):
    """
    Bus routes of İzmir.
    """

    code = models.PositiveSmallIntegerField(
        unique=True,
        primary_key=True,
        verbose_name="Code"
    )

    stops = models.ManyToManyField(
        Stop,
        null=True,
        blank=True,
        related_name="routes",
        verbose_name="Stops"
    )

    terminals = ArrayField(
        models.CharField(
            null=False,
            blank=False,
            max_length=32,
        ),
        size=2,
        default=[],
        verbose_name="Terminals"
    )

    departure_times = ArrayField(
        ArrayField(
            models.TimeField(
                null=False,
                blank=False
            ),
            null=True,
            default=[]
        ),
        default=[],
        size=6,
        verbose_name="Departure Times"
    )

    class Meta:
        verbose_name = "Route"
        verbose_name_plural = "Routes"
        ordering = ["code"]

    def __str__(self):
        return "{}: {} - {}".format(str(self.code), self.terminals[0], self.terminals[1])