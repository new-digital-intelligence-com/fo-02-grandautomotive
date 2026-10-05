"""Saves the official Renault and Dacia dealer networks in Greece, as renault.gr and dacia.gr show them.

Both sites' dealer locators read a Makolab service (dealers.svc): /dealers/<country> lists every dealer with address,
phone, e-mail, position and services, /services/<country> names the services. The data is saved as it comes, in
dealers_renault.json and dealers_dacia.json, for build_knowledge_base.py.

The service's certificate chain is incomplete, which Python's own check refuses; curl (Windows certificate store)
accepts it, so the requests go through curl.

Usage: python collect_dealers.py
"""
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCES = {
    # brand: (service, country code) — from the data-serviceurl / data-countrycode of each site's dealer-locator page
    "renault": ("https://rsidealerlocator.makolab.pl/service/dealers.svc", "gr"),
    "dacia": ("https://dsi-dl.makolab.pl/service/dealers.svc", "DACIA_GR"),
}


def get(url: str):
    result = subprocess.run(["curl", "-sSL", "--max-time", "60", "-A", "Mozilla/5.0", url], capture_output=True, check=True)
    return json.loads(result.stdout.decode("utf-8-sig"))


def main() -> None:
    for brand, (service, country) in SOURCES.items():
        data = {"source": f"{service}/dealers/{country}"}
        for part in ("dealers", "services", "website"):
            data[part] = get(f"{service}/{part}/{country}")
        with open(os.path.join(HERE, f"dealers_{brand}.json"), "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=1)
        print(f"{brand}: {len(data['dealers'])} dealers")


if __name__ == "__main__":
    main()
