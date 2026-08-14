"""Permite conservar la columna username antigua sin hacerla obligatoria.

El modelo actual autentica por email y ya no utiliza username, pero algunas
bases fueron creadas con AbstractUser, donde username era NOT NULL.
"""

from django.db import migrations


def make_legacy_username_nullable(apps, schema_editor):
    table_name = apps.get_model("users", "User")._meta.db_table
    connection = schema_editor.connection
    columns = {
        column.name
        for column in connection.introspection.get_table_description(connection.cursor(), table_name)
    }

    if "username" not in columns:
        return

    if connection.vendor == "postgresql":
        table = schema_editor.quote_name(table_name)
        username = schema_editor.quote_name("username")
        schema_editor.execute(
            f"ALTER TABLE {table} ALTER COLUMN {username} DROP NOT NULL"
        )


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_repair_legacy_user"),
    ]

    operations = [
        migrations.RunPython(make_legacy_username_nullable, migrations.RunPython.noop),
    ]
