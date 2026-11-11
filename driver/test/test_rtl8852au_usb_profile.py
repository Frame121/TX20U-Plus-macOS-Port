#!/usr/bin/env python3
"""Offline regression checks for the TP-Link TX20U Plus RTL8852AU USB profile.

These tests validate source/profile consistency only. They do not emulate USB,
firmware, radio initialization, Wi-Fi scan, or macOS IOKit behavior.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
CHIP = ROOT / "driver/rtw89/src/rtw8852au.c"
SHIM = ROOT / "driver/port/host/usb_shim.c"
PROFILE = ROOT / "driver/docs/LINUX-TX20U-PLUS-2026-11-01.md"


def bulk_out_indices(source: str) -> dict[str, int]:
    """Read symbolic DMA queue -> bulk-out descriptor-index assignments."""
    match = re.search(r"\.bulkout_id\s*=\s*\{(.*?)\n\s*\},", source, re.S)
    if not match:
        raise AssertionError("RTL8852AU bulkout_id table not found")
    pairs = re.findall(r"\[(RTW89_DMA_[A-Z0-9]+)\]\s*=\s*(\d+)", match.group(1))
    return {name: int(index) for name, index in pairs}


class RTL8852AUUSBProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chip = CHIP.read_text(encoding="utf-8")
        cls.shim = SHIM.read_text(encoding="utf-8")
        cls.profile = PROFILE.read_text(encoding="utf-8")

    def test_tx20u_plus_usb_id_is_bound_to_8852au(self):
        self.assertRegex(self.chip, r"USB_DEVICE_AND_INTERFACE_INFO\(0x2357,\s*0x013f,\s*0xff,\s*0xff,\s*0xff\)")
        self.assertIn(".chip = &rtw8852a_chip_info", self.chip)

    def test_8852au_rx_aggregation_alignment_is_eight(self):
        self.assertRegex(self.chip, r"\.rx_agg_alignment\s*=\s*8")

    def test_queue_indices_match_captured_descriptor_order(self):
        indices = bulk_out_indices(self.chip)
        expected = {
            "RTW89_DMA_B0MG": 0, "RTW89_DMA_B0HI": 0,
            "RTW89_DMA_B1MG": 1, "RTW89_DMA_B1HI": 1,
            "RTW89_DMA_H2C": 2, "RTW89_DMA_ACH0": 3,
            "RTW89_DMA_ACH4": 4, "RTW89_DMA_ACH2": 5,
            "RTW89_DMA_ACH6": 6,
        }
        self.assertEqual(indices, expected)
        # Captured physical-adapter order: indices 0..6 -> EP5,6,7,9,10,11,12.
        endpoint_by_index = [5, 6, 7, 9, 10, 11, 12]
        queue_to_endpoint = {queue: endpoint_by_index[index] for queue, index in indices.items()}
        self.assertEqual(queue_to_endpoint["RTW89_DMA_B0MG"], 5)
        self.assertEqual(queue_to_endpoint["RTW89_DMA_B1MG"], 6)
        self.assertEqual(queue_to_endpoint["RTW89_DMA_H2C"], 7)
        self.assertEqual(queue_to_endpoint["RTW89_DMA_ACH0"], 9)
        self.assertEqual(queue_to_endpoint["RTW89_DMA_ACH4"], 10)
        self.assertEqual(queue_to_endpoint["RTW89_DMA_ACH2"], 11)
        self.assertEqual(queue_to_endpoint["RTW89_DMA_ACH6"], 12)

    def test_profile_documents_endpoint_order_and_superspeed_packet_size(self):
        self.assertIn("Bulk IN endpoint: 0x84", self.profile)
        for endpoint in ("0x05", "0x06", "0x07", "0x09", "0x0A", "0x0B", "0x0C"):
            self.assertIn(endpoint, self.profile)
        self.assertIn("1024-byte max packet", self.profile)

    def test_zlp_uses_endpoint_max_packet_size_not_usb2_constant(self):
        self.assertIn("pipe_mps_out[16]", self.shim)
        self.assertRegex(self.shim, r"transfer_buffer_length\s*%\s*pipe_mps_out\[ep\]")
        self.assertNotRegex(self.shim, r"transfer_buffer_length\s*%\s*512")

    def test_probe_fails_closed_when_expected_bulk_pipes_are_missing(self):
        for endpoint in ("pipe_of_in[4]", "pipe_of_out[5]", "pipe_of_out[6]",
                         "pipe_of_out[7]", "pipe_of_out[9]", "pipe_of_out[10]",
                         "pipe_of_out[11]", "pipe_of_out[12]"):
            self.assertIn(endpoint, self.shim)
        self.assertIn("TX20U Plus endpoint set is incomplete; refusing probe", self.shim)


if __name__ == "__main__":
    unittest.main(verbosity=2)
