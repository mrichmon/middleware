# Copyright (c) - iXsystems Inc. dba TrueNAS
#
# Licensed under the terms of the TrueNAS Enterprise License Agreement
# See the file LICENSE.IX for complete terms and conditions

import middlewared.sqlalchemy as sa

from middlewared.service import private, Service


class SyntheticEnclosureModel(sa.Model):
    __tablename__ = "enclosure_synthetic"

    id = sa.Column(sa.Integer(), primary_key=True)
    pci = sa.Column(sa.String(20), unique=True)  # e.g., "0:0:2:0"
    enabled = sa.Column(sa.Boolean(), default=True)
    model = sa.Column(sa.String(200), default='SyntheticHBA')
    name = sa.Column(sa.String(200))  # e.g., "Internal SSDs (Broadcom HBA)"
    slot_prefix = sa.Column(sa.String(50), default='Slot')  # e.g., "Internal", "HBA Slot"
    show_empty_slots = sa.Column(sa.Boolean(), default=False)  # Show empty/unpopulated slots


class SyntheticEnclosureService(Service):
    class Config:
        namespace = "enclosure.synthetic"
        cli_namespace = "storage.enclosure.synthetic"
        private = True

    @private
    async def get_config(self, pci_address):
        """Get synthetic enclosure configuration for a specific PCI address.

        Args:
            pci_address: PCI address like "0:0:2:0"

        Returns:
            dict with config or None if not found
        """
        results = await self.middleware.call(
            "datastore.query",
            "enclosure.synthetic",
            [["pci", "=", pci_address]]
        )
        if results:
            return results[0]
        return None

    @private
    async def should_create_synthetic(self, pci_address):
        """Determine if synthetic Array Device Slots should be created for this enclosure.

        Returns:
            tuple: (should_create: bool, config: dict or None)

        Config dict contains:
            - enabled: bool - Whether to create synthetic slots
            - model: str - Model name for the synthetic enclosure
            - name: str - Display name for the enclosure
            - slot_prefix: str - Prefix for slot descriptors
            - show_empty_slots: bool - Whether to show empty/unpopulated slots (default: False)
        """
        config = await self.get_config(pci_address)

        if config:
            # Explicit configuration exists
            return (config['enabled'], config)
        else:
            # No config - use automatic mode (enabled by default, only populated slots)
            return (True, None)

    @private
    async def get_all_configs(self):
        """Get all synthetic enclosure configurations."""
        return await self.middleware.call("datastore.query", "enclosure.synthetic")
