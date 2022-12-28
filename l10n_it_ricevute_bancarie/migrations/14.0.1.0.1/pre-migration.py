from openupgradelib import openupgrade  # pylint: disable=W7936


@openupgrade.migrate()
def migrate(env, installed_version):
    openupgrade.delete_records_safely_by_xml_id(
        env,
        # View type changed. Simply drop and recreate
        ["l10n_it_ricevute_bancarie.action_wizard_riba_file_export"],
    )
    openupgrade.logged_query(
        env.cr,
        """
    ALTER TABLE invoice_unsolved_line_rel
        DROP CONSTRAINT IF EXISTS invoice_unsolved_line_rel_invoice_id_fkey;
    """,
    )
    openupgrade.logged_query(
        env.cr,
        """
    ALTER TABLE invoice_unsolved_line_rel
        RENAME COLUMN invoice_id TO move_id;
    """,
    )

    openupgrade.logged_query(
        env.cr,
        """
    update invoice_unsolved_line_rel iulr
    set
        move_id = am.id
    from account_invoice inv
        join account_move am on am.id = inv.move_id
    where
        iulr.move_id = inv.id;
    """,
    )
