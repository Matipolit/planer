from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from planer_app.models import UserProfile


class Command(BaseCommand):
    help = "Create UserProfile for all users that don't have one"

    def handle(self, *args, **options):
        users = User.objects.all()
        created_count = 0
        existing_count = 0

        self.stdout.write("Checking all users for profiles...")

        for user in users:
            if hasattr(user, "profile"):
                existing_count += 1
                self.stdout.write(f"  ✓ User '{user.username}' already has a profile")
            else:
                UserProfile.objects.create(user=user)
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  + Created profile for user '{user.username}'"
                    )
                )

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(f"Total users: {users.count()}")
        self.stdout.write(self.style.SUCCESS(f"Profiles created: {created_count}"))
        self.stdout.write(f"Profiles already existed: {existing_count}")
        self.stdout.write("=" * 60)

        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✓ Successfully created {created_count} user profile(s)!"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("\n✓ All users already have profiles!")
            )
