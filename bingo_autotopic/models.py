from django.db import models
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from django.db.models.signals import pre_save
from django.dispatch import receiver
from bingo.models import Game
from bingo import times


class GameDescription(models.Model):
    start_time = models.DateTimeField(
        help_text=_("Game started after this time"))
    end_time = models.DateTimeField(
        help_text=_("Game started before this time"))
    description = models.CharField(
        max_length=255,
        help_text=_("Description, which is added to matching games."))
    site = models.ForeignKey(Site)

    def clean(self):
        super(GameDescription, self).clean()
        for i in ("site", "end_time", "start_time", "description"):
            if not hasattr(self, i):
                return
        if self.end_time < self.start_time:
            raise ValidationError(
                _("end time is before start time."))
        game_descs = GameDescription.objects.filter(
            site=self.site,
            start_time__lte=self.end_time,
            end_time__gte=self.start_time,
            )
        if game_descs.count() > 0 and not game_descs[0].pk == self.pk:
            raise ValidationError(
                _("Interval overlaps with another description."))

    def __unicode__(self):
       return u"Game Description for {start:s} (site: {site:s})".format(start=self.start_time.strftime("%Y-%m-%d %H:%M"), site=self.site)


@receiver(pre_save, sender=Game)
def set_description(sender, instance, **kwargs):
    if not instance.description and \
            not hasattr(instance, "set_description_called"):

        current_time = times.now()
        game_descs = GameDescription.objects.filter(
            site=instance.site,
            start_time__lte=current_time,
            end_time__gte=current_time
            )
        # it should be 0 or 1,
        # but with >= 1 we avoid not setting the desc if there are more objects
        if game_descs.count() >= 1:
            instance.description = game_descs[0].description
        instance.set_description_called = True
