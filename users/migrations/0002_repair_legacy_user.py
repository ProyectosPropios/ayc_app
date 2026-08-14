"""Compatibilidad con bases creadas con el usuario anterior de Django.

La migración 0001 fue recreada cuando el modelo pasó de AbstractUser al
usuario basado en correo. En algunas bases esa migración ya aparecía como
aplicada, aunque la columna ``role`` todavía no existía físicamente.
"""

from django.db import migrations


def add_missing_role_column(apps, schema_editor):
    table_name = apps.get_model("users", "User")._meta.db_table
    connection = schema_editor.connection
    existing_columns = {
        column.name
        for column in connection.introspection.get_table_description(connection.cursor(), table_name)
    }

    if "role" in existing_columns:
        return

    table = schema_editor.quote_name(table_name)
    role_column = schema_editor.quote_name("role")
    schema_editor.execute(
        f"ALTER TABLE {table} ADD COLUMN {role_column} varchar(20) NOT NULL DEFAULT 'tecnico'"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_missing_role_column, migrations.RunPython.noop),
    ]
