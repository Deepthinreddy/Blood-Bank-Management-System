# Generated for the Donor Registration feature (BBMS-F-001).
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Donor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=150)),
                ("date_of_birth", models.DateField()),
                ("phone_number", models.CharField(max_length=20)),
                ("email", models.EmailField(max_length=254)),
                ("address", models.CharField(max_length=300)),
                ("blood_group", models.CharField(choices=[("A+", "A+"), ("A-", "A-"), ("B+", "B+"), ("B-", "B-"), ("AB+", "AB+"), ("AB-", "AB-"), ("O+", "O+"), ("O-", "O-")], max_length=3)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["full_name", "id"]},
        ),
    ]
