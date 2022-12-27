# Copyright 2020 Marco Colombo <https://github.com/TheMule71>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from psycopg2 import sql

invoice_data = (
    ("protocol_number"),
    ("tax_representative_id"),
    ("intermediary"),
    ("sender"),
    ("carrier_id"),
    ("transport_vehicle"),
    ("transport_reason"),
    ("number_items"),
    ("description"),
    ("unit_weight"),
    ("gross_weight"),
    ("net_weight"),
    ("pickup_datetime"),
    ("transport_date"),
    ("delivery_address"),
    ("delivery_datetime"),
    ("ftpa_incoterms"),
    ("related_invoice_code"),
    ("related_invoice_date"),
    ("vehicle_registration"),
    ("total_travel"),
    ("efatt_stabile_organizzazione_indirizzo"),
    ("efatt_stabile_organizzazione_civico"),
    ("efatt_stabile_organizzazione_cap"),
    ("efatt_stabile_organizzazione_comune"),
    ("efatt_stabile_organizzazione_provincia"),
    ("efatt_stabile_organizzazione_nazione"),
    ("efatt_rounding"),
    ("art73"),
)

invoice_line_data = (
    "admin_ref",
    "ftpa_line_number",
)


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(env.cr, "account_move", "old_invoice_id"):
        openupgrade.logged_query(
            env.cr,
            sql.SQL(
                """UPDATE account_move m
                   SET {}
                   FROM account_invoice i
                   WHERE m.old_invoice_id = i.id
                """
            ).format(
                sql.SQL(", ").join(
                    sql.Composed(
                        [
                            sql.Identifier(col),
                            sql.SQL(" = "),
                            sql.SQL("i."),
                            sql.Identifier(col),
                        ]
                    )
                    for col in invoice_data
                )
            ),
        )
    # check if it is a migration from 13.0
    elif openupgrade.table_exists(env.cr, "account_invoice"):
        # rely on move_id, usually for not ('draft' or 'cancel')
        openupgrade.logged_query(
            env.cr,
            sql.SQL(
                """UPDATE account_move m
                                   SET {}
                                   FROM account_invoice i
                                   WHERE i.move_id = m.id
                                """
            ).format(
                sql.SQL(", ").join(
                    sql.Composed(
                        [
                            sql.Identifier(col),
                            sql.SQL(" = "),
                            sql.SQL("i."),
                            sql.Identifier(col),
                        ]
                    )
                    for col in invoice_data
                )
            ),
        )

    # check if it is a migration from 12.0
    if openupgrade.table_exists(
        env.cr, "account_invoice_line"
    ) and openupgrade.column_exists(env.cr, "account_move_line", "old_invoice_line_id"):
        openupgrade.logged_query(
            env.cr,
            sql.SQL(
                """UPDATE account_move_line ml
                   SET {}
                   FROM account_invoice_line il
                   WHERE ml.old_invoice_line_id = il.id
                """
            ).format(
                sql.SQL(", ").join(
                    sql.Composed(
                        [
                            sql.Identifier(col),
                            sql.SQL(" = "),
                            sql.SQL("il."),
                            sql.Identifier(col),
                        ]
                    )
                    for col in invoice_line_data
                )
            ),
        )
    # check if it is a migration from 13.0
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

        openupgrade.logged_query(
            env.cr,
            sql.SQL(
                """UPDATE account_move_line ml
                       SET {0}
                       FROM account_invoice_line il
                       JOIN account_invoice i ON (i.id = il.invoice_id)
                       JOIN account_move m ON (m.id = i.move_id)
                       WHERE ml.move_id = m.id AND {1}
                    """
            ).format(
                sql.SQL(", ").join(
                    sql.Composed(
                        [
                            sql.Identifier(col),
                            sql.SQL(" = "),
                            sql.SQL("il."),
                            sql.Identifier(col),
                        ]
                    )
                    for col in invoice_line_data
                ),
                sql.SQL(move_line_where),
            ),
        )
