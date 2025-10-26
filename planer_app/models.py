from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Task(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    frequency = models.IntegerField(default=1)


def validate_date_range(start_date, end_date):
    if start_date > end_date:
        raise ValidationError(
            "The end date must be greater or equal than the start date."
        )


class Week(models.Model):
    # no mask for now
    start_date = models.DateField(unique=True, null=False, blank=False)
    end_date = models.DateField(
        unique=True, null=False, blank=False, validators=[validate_date_range]
    )


class Purchase(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    price = models.DecimalField(
        max_digits=18, decimal_places=2, null=False, blank=False
    )
    amount = models.IntegerField(default=1)
    # basic user for now
    locator_id = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    @property
    def sum_price(self):
        return self.price * self.amount


class Debt(models.Model):
    purchase_id = models.ForeignKey(
        Purchase, on_delete=models.CASCADE, null=False, blank=False
    )
    # basic user for now
    locator_id = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, blank=False
    )
    is_paid = models.BooleanField(default=False, null=False, blank=False)
    owed_amount = models.DecimalField(
        max_digits=18, decimal_places=2, null=False, blank=False
    )


class TasksInWeek(models.Model):
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE, null=False, blank=False)
    week_id = models.ForeignKey(Week, on_delete=models.CASCADE, null=False, blank=False)
    locator_id = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, blank=False
    )
    is_done = models.BooleanField(default=False, null=False, blank=False)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None


# Create UserProfile automatically when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, "profile"):
        instance.profile.save()


class GalleryPhoto(models.Model):
    CATEGORY_CHOICES = [
        ("events", "Events & Celebrations"),
        ("food", "Food & Cooking"),
        ("home", "Home & Improvements"),
        ("pets", "Pets & Animals"),
        ("travel", "Travel & Adventures"),
        ("people", "People & Portraits"),
        ("nature", "Nature & Outdoors"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to="gallery/", null=False, blank=False)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="other",
        null=False,
        blank=False,
    )
    uploaded_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, blank=False
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.title or 'Untitled'} by {self.uploaded_by.username}"
