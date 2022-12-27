# Copyright 2020 Marco Colombo <https://github.com/TheMule71>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from psycopg2 import sql

# account_invoice -> account_move migration
i_m_columns = (
    ("fatturapa_payment_data", "invoice_id"),
    ("welfare_fund_data_line", "invoice_id"),
    ("withholding_data_line", "invoice_id"),
    ("discount_rise_price", "invoice_id"),
    ("fatturapa_related_document_type", "invoice_id"),
    ("fatturapa_activity_progress", "invoice_id"),
    ("fatturapa_attachments", "invoice_id"),
    ("fatturapa_related_ddt", "invoice_id"),
    ("fatturapa_summary_data", "invoice_id"),
)

# account_invoice_line -> account_move_line migration
il_ml_columns = (
    ("discount_rise_price", "invoice_line_id"),
    ("fatturapa_related_document_type", "invoice_line_id"),
    ("fatturapa_related_ddt", "invoice_line_id"),
)


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(
        env.cr,
        [
            ("faturapa.activity.progress", "fatturapa.activity.progress"),
            ("faturapa.summary.data", "fatturapa.summary.data"),
        ],
    )
    openupgrade.rename_tables(
        env.cr,
        [
            ("faturapa_activity_progress", "fatturapa_activity_progress"),
            ("faturapa_summary_data", "fatturapa_summary_data"),
        ],
    )

    for table, column in i_m_columns + il_ml_columns:
        openupgrade.logged_query(
            env.cr,
            sql.SQL(
                """ALTER TABLE {0}
                DROP CONSTRAINT IF EXISTS {1};""",
            ).format(
                sql.Identifier(table),
                sql.Identifier(f"{table}_{column}_fkey"),
            ),
        )
    if openupgrade.column_exists(env.cr, "account_move", "old_invoice_id"):
        for table, column in i_m_columns:
            openupgrade.logged_query(
                env.cr,
                sql.SQL(
                    """UPDATE {0} t
                SET {1} = m.id
                FROM account_move m
                WHERE m.old_invoice_id = t.{1}"""
                ).format(
                    sql.Identifier(table),
                    sql.Identifier(column),
                ),
            )

    elif openupgrade.table_exists(env.cr, "account_invoice"):
        # rely on move_id, usually for not ('draft' or 'cancel')
        for table, column in i_m_columns:
            openupgrade.logged_query(
                env.cr,
                sql.SQL(
                    """UPDATE {0} t
                SET {1} = i.move_id
                FROM account_invoice i
                WHERE t.{1} = i.id and i.move_id is NOT NULL"""
                ).format(
                    sql.Identifier(table),
                    sql.Identifier(column),
                ),
            )

    if openupgrade.table_exists(
        env.cr, "account_invoice_line"
    ) and openupgrade.column_exists(env.cr, "account_move_line", "old_invoice_line_id"):
        for table, column in il_ml_columns:
            openupgrade.logged_query(
                env.cr,
                sql.SQL(
                    """UPDATE {0} t
                SET {1} = ml.id
                FROM account_move_line ml
                WHERE ml.old_invoice_line_id = t.{1}"""
                ).format(
                    sql.Identifier(table),
                    sql.Identifier(column),
                ),
            )

    elif openupgrade.table_exists(env.cr, "account_invoice_line"):
        move_line_where = """
        ml.tax_line_id IS NULL
                AND ml.account_id <> i.account_id
                AND il.quantity = ml.quantity
                AND ((il.product_id IS NULL AND ml.product_id IS NULL)
                    OR il.product_id = ml.product_id)
                AND ((il.uom_id IS NULL AND ml.product_uom_id IS NULL)
                    OR il.uom_id = ml.product_uom_id)
                """

        # rely on move_id, usually for not ('draft' or 'cancel')
        for table, column in il_ml_columns:
            openupgrade.logged_query(
                env.cr,
                sql.SQL(
                    """UPDATE {0} t
                SET {1} = ml.id
                FROM account_move_line ml
                JOIN account_move m ON (m.id = ml.move_id)
                JOIN account_invoice i ON (i.move_id = m.id)
                JOIN account_invoice_line il ON (il.invoice_id = i.id)
                WHERE t.{1} = il.id AND {2}"""
                ).format(
                    sql.Identifier(table),
                    sql.Identifier(column),
                    sql.SQL(move_line_where),
                ),
            )
