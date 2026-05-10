from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0002_add_image_url_to_groceryitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groceryitem',
            name='image_url',
            field=models.CharField(max_length=500, blank=True, default=''),
        ),
    ]
