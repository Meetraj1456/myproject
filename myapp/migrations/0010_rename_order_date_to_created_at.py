# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_order_orderitem'),
    ]

    operations = [
        # Rename order_date to created_at
        migrations.RenameField(
            model_name='order',
            old_name='order_date',
            new_name='created_at',
        ),
        # Rename order_id to payment_order_id
        migrations.RenameField(
            model_name='order',
            old_name='order_id',
            new_name='payment_order_id',
        ),
        # Add items_json field
        migrations.AddField(
            model_name='order',
            name='items_json',
            field=models.JSONField(default=list),
        ),
        # Update existing fields to match current model
        migrations.AlterField(
            model_name='order',
            name='payment_id',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_order_id',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='sub_total',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='order',
            name='shipping',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(max_length=20, default='paid'),
        ),
        # Remove address-related fields
        migrations.RemoveField(
            model_name='order',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='order',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='order',
            name='email',
        ),
        migrations.RemoveField(
            model_name='order',
            name='address',
        ),
        migrations.RemoveField(
            model_name='order',
            name='country',
        ),
        migrations.RemoveField(
            model_name='order',
            name='state',
        ),
        migrations.RemoveField(
            model_name='order',
            name='zip_code',
        ),
        # Delete OrderItem model (no longer needed)
        migrations.DeleteModel(
            name='OrderItem',
        ),
    ]
