#!/usr/bin/env python3
"""
Genera un archivo SQL con todas las traducciones ES para importar en PostgreSQL.
Lee los messages_es.csv de todos los módulos y produce INSERTs para meta_translation.
"""
import csv
import os
import re

BASE = '/home/alvarto/bitacora/www/axelor'
OUTPUT_SQL = '/home/alvarto/bitacora/www/axelor/translations_es.sql'

MODULES = [
    'axelor-account', 'axelor-bank-payment', 'axelor-base', 'axelor-budget',
    'axelor-cash-management', 'axelor-client-portal', 'axelor-contract',
    'axelor-crm', 'axelor-fleet', 'axelor-gdpr', 'axelor-helpdesk',
    'axelor-human-resource', 'axelor-intervention', 'axelor-maintenance',
    'axelor-marketing', 'axelor-mobile-settings', 'axelor-production',
    'axelor-project', 'axelor-purchase', 'axelor-quality', 'axelor-sale',
    'axelor-stock', 'axelor-supplier-management', 'axelor-supplier-portal',
    'axelor-supplychain', 'axelor-talent',
]

def escape_sql(s):
    """Escapa comillas simples para SQL."""
    return s.replace("'", "''")

def is_untranslated(key, value):
    """Devuelve True si el valor es idéntico a la clave (sin traducción útil)."""
    if not value or not value.strip():
        return True
    # Si empieza con % (formato técnico) y no tiene traducción real
    if key.strip().startswith('%') and value.strip() == key.strip():
        return True
    return False

def collect_translations():
    """Lee todos los messages_es.csv y devuelve lista de (key, value)."""
    seen_keys = set()
    rows = []
    total_files = 0
    total_strings = 0
    skipped = 0

    for module in MODULES:
        es_path = f"{BASE}/{module}/src/main/resources/i18n/messages_es.csv"
        if not os.path.exists(es_path):
            print(f"  SKIP (sin archivo): {module}")
            continue

        total_files += 1
        module_count = 0

        with open(es_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, quotechar='"', skipinitialspace=True)
            for i, row in enumerate(reader):
                if i == 0:  # header
                    continue
                if len(row) < 2:
                    continue

                key = row[0].strip()
                value = row[1].strip()

                if not key:
                    continue

                # Limitar a 1024 chars (límite de la columna)
                if len(key) > 1024 or len(value) > 1024:
                    skipped += 1
                    continue

                # Omitir strings sin traducción real
                if is_untranslated(key, value):
                    skipped += 1
                    continue

                # Deduplicar por clave
                if key in seen_keys:
                    continue
                seen_keys.add(key)

                rows.append((key, value))
                module_count += 1
                total_strings += 1

        print(f"  {module}: {module_count} strings")

    print(f"\nTotal: {total_files} módulos, {total_strings} traducciones ({skipped} omitidas)")
    return rows

def generate_sql(rows, start_id=17347):
    """Genera el archivo SQL con INSERTs."""
    lines = []
    lines.append("-- Traducciones al español para Axelor Open Suite")
    lines.append("-- Generado automáticamente por inject_translations.py")
    lines.append("")
    lines.append("BEGIN;")
    lines.append("")
    lines.append("-- Eliminar traducciones ES previas (si existen)")
    lines.append("DELETE FROM meta_translation WHERE language = 'es';")
    lines.append("")

    current_id = start_id
    batch = []

    for key, value in rows:
        k = escape_sql(key)
        v = escape_sql(value)
        batch.append(
            f"({current_id}, 0, 'es', '{k}', '{v}')"
        )
        current_id += 1

        # Escribir en batches de 500
        if len(batch) >= 500:
            lines.append(
                "INSERT INTO meta_translation (id, version, language, message_key, message_value) VALUES"
            )
            lines.append(",\n".join(batch) + ";")
            lines.append("")
            batch = []

    if batch:
        lines.append(
            "INSERT INTO meta_translation (id, version, language, message_key, message_value) VALUES"
        )
        lines.append(",\n".join(batch) + ";")
        lines.append("")

    lines.append("COMMIT;")
    lines.append("")
    lines.append(f"-- Total insertado: {current_id - start_id} traducciones")

    return "\n".join(lines)

print("Recolectando traducciones desde messages_es.csv...\n")
rows = collect_translations()

print("\nGenerando SQL...")
sql = generate_sql(rows)

with open(OUTPUT_SQL, 'w', encoding='utf-8') as f:
    f.write(sql)

print(f"Archivo generado: {OUTPUT_SQL}")
print(f"Listo para importar con: docker compose exec -T postgres psql -U axelor -d axelor < translations_es.sql")
