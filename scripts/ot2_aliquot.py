#!/usr/bin/env python
"""Opentrons OT‑2 protocol: aliquot 50 µL from A1 to A2‑A9."""
from opentrons import protocol_api

metadata = {
    "apiLevel": "2.15",
    "protocolName": "PCR Aliquot Demo",
}

def run(ctx: protocol_api.ProtocolContext):
    plate   = ctx.load_labware("corning_96_wellplate_360ul_flat", 1)
    tiprack = ctx.load_labware("opentrons_96_tiprack_300ul", 2)
    p300    = ctx.load_instrument("p300_single", "right", tip_racks=[tiprack])

    src = plate.wells()[0]            # A1
    dests = plate.wells()[1:9]        # A2–A9
    p300.pick_up_tip()

    for d in dests:
        p300.aspirate(50, src)
        p300.dispense(50, d)
    p300.drop_tip()
