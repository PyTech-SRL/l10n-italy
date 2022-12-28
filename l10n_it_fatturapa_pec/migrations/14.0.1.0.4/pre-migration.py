from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(
        env,
        # Recreate the group entirely. Was not migrated correctly in the past.
        ["l10n_it_fatturapa_out.group_force_e_inv_export_state"],
    )
    openupgrade.rename_xmlids(
        env.cr,
        [
            (
                "l10n_it_sdi_channel.sdi_pec_first_address",
                "l10n_it_fatturapa_pec.sdi_pec_first_address",
            ),
            (
                "l10n_it_sdi_channel.sdi_channel_pec",
                "l10n_it_fatturapa_pec.sdi_channel_pec",
            ),
        ],
    )
