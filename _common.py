"""Shared defaults for the example scripts.

MeshCore's "USA/Canada (Recommended)" preset, per
https://github.com/ripplebiz/MeshCore/blob/main/docs/faq.md §6.1
(the "narrow" channel the project moved to in October 2025):

* 910.525 MHz — inside the 902-928 MHz ISM band
* 62.5 kHz bandwidth
* SF 7 — lower SF for faster transmissions and better SNR headroom
* CR 4/5 — RadioLib's ``LORA_CR=5``
* 16-symbol preamble — matches every board variant's ``radio.begin(...)``
* Sync word 0x1424 — ``RADIOLIB_SX126X_SYNC_WORD_PRIVATE``, the SX126x
  register encoding of the "private" byte 0x12 MeshCore uses to
  distinguish its traffic from LoRaWAN (byte 0x34, encoded 0x3444).
* 20 dBm TX power — MeshCore's compile-time default (see
  ``examples/companion_radio/MyMesh.h``).

If you operate in the EU, swap ``freq_hz`` for ``869_525_000`` (the
EU-equivalent MeshCore channel) and cap ``tx_power_dbm`` at ``14`` to
respect the 868 MHz duty-cycle / ERP rules.
"""

import donglora as dl

MESHCORE_US = dl.LoRaConfig(
    freq_hz=910_525_000,
    sf=7,
    bw=dl.LoRaBandwidth.KHZ_62_5,
    cr=dl.LoRaCodingRate.CR_4_5,
    preamble_len=16,
    sync_word=0x1424,
    tx_power_dbm=20,
    header_mode=dl.LoRaHeaderMode.EXPLICIT,
    payload_crc=True,
    iq_invert=False,
)
