#!/usr/bin/env python3
"""
Avito XML feed generator for automation services.

Generates avito_feed.xml with weekly-rotating IDs.
Weekly rotation = Avito treats listings as new each week = fresh position in search.

Run manually:   python3 generate_feed.py
GitHub Actions: runs automatically every day, commits updated XML.
"""
import json
import os
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET
from xml.dom import minidom

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICES_FILE = os.path.join(SCRIPT_DIR, "services.json")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "avito_feed.xml")


def load_services() -> list:
    with open(SERVICES_FILE, encoding="utf-8") as f:
        return json.load(f)


def week_key(today: datetime) -> str:
    year, week, _ = today.isocalendar()
    return f"{year}w{week:02d}"


def build_feed(services: list, today: datetime) -> bytes:
    ads = ET.Element("Ads", formatVersion="3", target="Avito.ru")

    date_begin = today.strftime("%Y-%m-%d")
    date_end = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    wk = week_key(today)

    for svc in services:
        ad = ET.SubElement(ads, "Ad")

        # ID changes every week => Avito creates a fresh listing each week
        listing_id = f"{svc['id_prefix']}_{wk}"
        ET.SubElement(ad, "Id").text = listing_id
        ET.SubElement(ad, "DateBegin").text = date_begin
        ET.SubElement(ad, "DateEnd").text = date_end
        ET.SubElement(ad, "Fee").text = "Free"
        ET.SubElement(ad, "AllowEmail").text = "Yes"
        ET.SubElement(ad, "Category").text = svc["category"]
        if svc.get("service_type"):
            ET.SubElement(ad, "ServiceType").text = svc["service_type"]
        ET.SubElement(ad, "Title").text = svc["title"]
        ET.SubElement(ad, "Description").text = svc["description"]
        ET.SubElement(ad, "Price").text = str(svc.get("price", 1))
        ET.SubElement(ad, "LocationId").text = str(svc.get("location_id", 621540))
        ET.SubElement(ad, "Address").text = svc.get("address", "Москва")

    rough = ET.tostring(ads, encoding="unicode")
    reparsed = minidom.parseString(rough)
    return reparsed.toprettyxml(indent="  ", encoding="UTF-8")


def main():
    today = datetime.now()
    services = load_services()

    xml_bytes = build_feed(services, today)

    with open(OUTPUT_FILE, "wb") as f:
        f.write(xml_bytes)

    wk = week_key(today)
    print(f"Generated {len(services)} listings | week={wk} | {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
