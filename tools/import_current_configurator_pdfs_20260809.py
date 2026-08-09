from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/master"
LEDGER = ROOT / "project/sources/dacia-pl-configurator-native-pdf-page-ledger-20260809.json"
REPORT = ROOT / "data/reporting/dacia_configurator_pdf_canonical_import_20260809.json"
DATE = "2026-08-09"


def read_csv(name: str):
    with (MASTER / name).open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames or []), list(r)


def write_csv(name: str, fields, rows):
    with (MASTER / name).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def next_id(rows):
    return max((int(r["id"]) for r in rows), default=0) + 1


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "").replace("\u00a0", " ")
    return re.sub(r"\s+", " ", s.strip())


def ncase(s: str) -> str:
    return norm(s).casefold()


def scalar(s: str, kind="decimal"):
    x = norm(s).replace(",", ".")
    m = re.fullmatch(r"-?\d+(?:\.\d+)?", x)
    if not m: return None
    if kind == "integer" and "." in x: return None
    if kind == "integer": return str(int(x))
    return x.rstrip("0").rstrip(".") if "." in x else x


def strip_price(s: str) -> str:
    return re.sub(r"\s+\d[\d ]*\s*zł\s*$", "", norm(s), flags=re.I).strip()


def wheel_values(label: str):
    label = strip_price(label)
    m = re.search(r'(\d+)"', label)
    if not m: return {}
    low = label.casefold()
    material = "alloy" if ("alumini" in low or "stopu metali lekkich" in low) else "steel" if ("stal" in low or "flexwheel" in low) else ""
    design = re.sub(r'^\d+"\s+(?:felgi|stalowe obręcze kół typu|stalowe obręcze kół|obręcze kół ze stopu metali lekkich)\s*', "", label, flags=re.I)
    design = re.sub(r"^(?:stalowe|aluminiowe)\s+", "", design, flags=re.I).strip(" -")
    out = {"wheel_size": f'{m.group(1)}"'}
    if material: out["wheel_material"] = material
    if design and design != label: out["wheel_design"] = design
    return out


def split_label_value(line: str):
    line = norm(line)
    rules = [
        r'^(1000 m ze startu zatrzymanego \(s\))\s+(.+)$',
        r'^(400 m ze startu zatrzymanego \(s\))\s+(.+)$',
        r'^(EV - zasięg w cyklu mieszanym WLTP E-TECH \(km\))\s+(.+)$',
        r'^(EV - zużycie energii elektrycznej w cyklu mieszanym WLTP \(kWh/100 km\))\s+(.+)$',
        r'^(Emisja CO2 cykl mieszany WLTP\*LPG \(g/km\))\s+(.+)$',
        r'^(Emisja CO2 cykl mieszany WLTP \(g/km\))\s+(.+)$',
        r'^(Zużycie paliwa cykl mieszany WLTP\*LPG \(l/100km\))\s+(.+)$',
        r'^(Zużycie paliwa cykl mieszany WLTP \(l/100 km\))\s+(.+)$',
        r'^(pojemność zbiornika paliwa \(l\))\s+(.+)$',
        r'^(Prędkość maksymalna \(km/h\))\s+(.+)$',
        r'^(Przyspieszenie 0-100 km/h \(s\))\s+(.+)$',
        r'^(Średnica zawracania \(m\))\s+(.+)$',
        r'^(Maksymalna masa całkowita zespołu pojazdów \(kg\))\s+(.+)$',
        r'^(Maksymalna masa przyczepy bez hamulca \(kg\))\s+(.+)$',
        r'^(Maksymalna masa przyczepy z hamulcem \(kg\))\s+(.+)$',
        r'^(Maksymalna ładowność \(kg\))\s+(.+)$',
        r'^(Minimalna masa pojazdu gotowego do jazdy \(bez opcji\) \(kg\))\s+(.+)$',
        r'^(Maksymalna masa całkowita pojazdu \(kg\))\s+(.+)$',
        r'^(Pojemność skokowa \(cm3\))\s+(.+)$',
        r'^(Poziom hałasu przy 50 km/h \(dB\))\s+(.+)$',
        r'^(Wysokość pojazdu nieobciążonego z relingami \(mm\))\s+(.+)$',
        r'^(Moc maksymalna kW \(KM\))\s+(.+)$',
        r'^(Maksymalny moment obrotowy w Nm)\s+(.+)$',
        r'^(Rodzaj napędu)\s+(.+)$', r'^(Rodzaj nadwozia)\s+(.+)$',
        r'^(Rodzaj paliwa)\s+(.+)$', r'^(Norma emisji spalin)\s+(.+)$',
        r'^(Rodzaj skrzyni biegów)\s+(.+)$', r'^(Typ techniczny)\s+(.+)$',
        r'^(Długość całkowita)\s+(.+)$', r'^(Rozstaw osi)\s+(.+)$',
        r'^(Zwis przedni)\s+(.+)$', r'^(Zwis tylny)\s+(.+)$',
        r'^(Szerokość całkowita z lusterkami zewnętrznymi)\s+(.+)$',
        r'^(Szerokość całkowita)\s+(.+)$',
        r'^(Wysokość całkowita)\s+(.+)$', r'^(Prześwit pojazdu)\s+(.+)$',
        r'^(Opony standardowe)\s+(.+)$',
        r'^(Liczba zaworów)\s+(.+)$', r'^(Liczba cylindrów)\s+(.+)$',
        r'^(Liczba miejsc siedzących)\s+(.+)$', r'^(Liczba biegów do przodu)\s+(.+)$',
        r'^(Liczba drzwi)\s+(.+)$', r'^(napięcie nominalne)\s+(.+)$',
        r'^(pojemność akumulatora)\s+(.+)$', r'^(ładowanie AC)\s+(.+)$',
    ]
    for rule in rules:
        m = re.match(rule, line, re.I)
        if m: return norm(m.group(1)), norm(m.group(2))
    return None, None


def is_bifuel(config: str):
    return "ecog" in config or "hybridg" in config


def simple_fuel_pair(value: str):
    """Return [(fuel,value)] only when the source explicitly identifies LPG."""
    v = norm(value).replace(",", ".")
    # e.g. 10.1 (LPG) / 11.1
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*\(LPG\)\s*/\s*(\d+(?:\.\d+)?)", v, re.I)
    if m: return [("lpg", m.group(1)), ("petrol", m.group(2))]
    # e.g. 90 (122) LPG / 84 (114)
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*\([^)]*\)\s*LPG\s*/\s*(\d+(?:\.\d+)?)\s*\([^)]*\)", v, re.I)
    if m: return [("lpg", m.group(1)), ("petrol", m.group(2))]
    # e.g. 84 (114) ben. / 90 (122) LPG
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*\([^)]*\)\s*ben\.?\s*/\s*(\d+(?:\.\d+)?)\s*\([^)]*\)\s*LPG", v, re.I)
    if m: return [("petrol", m.group(1)), ("lpg", m.group(2))]
    # e.g. 84/90 LPG (114/122 LPG)
    m = re.fullmatch(r"(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)\s*LPG\s*\([^)]*\)", v, re.I)
    if m: return [("petrol", m.group(1)), ("lpg", m.group(2))]
    return []


def build(apply=False):
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    names = ["attributes.csv","sources.csv","source_configurations.csv","configuration_attribute_values.csv","configuration_attribute_value_ranges.csv","configuration_attribute_availability.csv","configuration_prices.csv"]
    tables = {n: read_csv(n) for n in names}
    attrs = {r["code"]: r for r in tables["attributes.csv"][1]}
    sources = {r["code"] for r in tables["sources.csv"][1]}
    source_configs = {(r["source_code"],r["configuration_code"]) for r in tables["source_configurations.csv"][1]}
    values = tables["configuration_attribute_values.csv"][1]
    ranges = tables["configuration_attribute_value_ranges.csv"][1]
    availability = tables["configuration_attribute_availability.csv"][1]
    prices = tables["configuration_prices.csv"][1]
    value_id, range_id, av_id, price_id = map(next_id, (values,ranges,availability,prices))
    counters=Counter(); deferred=Counter(); examples=defaultdict(list)

    def record_defer(kind, text, reason):
        key=f"{kind}:{reason}"; deferred[key]+=1
        if len(examples[key])<12: examples[key].append(text)

    def add_value(config, attr, value, source, page, raw, fuel="", gear=""):
        nonlocal value_id
        if attr not in attrs:
            record_defer("value", raw, f"attribute_missing:{attr}"); return False
        value=str(value)
        same = [r for r in values if r["configuration_code"]==config and r["attribute_code"]==attr and r.get("fuel_type_code","")==fuel and r.get("gear_number","")==gear]
        if any(r["value"]==value for r in same): counters["values_already_covered"]+=1; return False
        code=f"{config}_{attr}_{fuel or 'all'}_20260809_cfgpdf"
        if any(r["code"]==code for r in values): counters["values_code_existing"]+=1; return False
        values.append({"id":str(value_id),"code":code,"configuration_code":config,"attribute_code":attr,"fuel_type_code":fuel,"gear_number":gear,"value":value,"observation_date":DATE,"source_code":source,"notes":f"Exact saved configurator PDF, page {page}: {raw}"})
        value_id+=1; counters["values_added"]+=1; return True

    def add_range(config, attr, lo, hi, source, page, raw, fuel=""):
        nonlocal range_id
        if attr not in attrs:
            record_defer("range", raw, f"attribute_missing:{attr}"); return False
        lo,hi=str(lo),str(hi)
        same=[r for r in ranges if r["configuration_code"]==config and r["attribute_code"]==attr and r.get("fuel_type_code","")==fuel]
        if any(r["minimum_value"]==lo and r["maximum_value"]==hi for r in same): counters["ranges_already_covered"]+=1; return False
        code=f"{config}_{attr}_{fuel or 'all'}_range_20260809_cfgpdf"
        if any(r["code"]==code for r in ranges): return False
        ranges.append({"id":str(range_id),"code":code,"configuration_code":config,"attribute_code":attr,"fuel_type_code":fuel,"minimum_value":lo,"maximum_value":hi,"lower_inclusive":"true","upper_inclusive":"true","observation_date":DATE,"source_code":source,"notes":f"Exact saved configurator PDF, page {page}: {raw}"})
        range_id+=1; counters["ranges_added"]+=1; return True

    def add_standard(config, attr, source, raw):
        nonlocal av_id
        if attr not in attrs:
            record_defer("availability",raw,f"attribute_missing:{attr}"); return False
        same=[r for r in availability if r["configuration_code"]==config and r["attribute_code"]==attr and r["availability_status"]=="standard"]
        if same: counters["availability_already_covered"]+=1; return False
        code=f"{config}_{attr}_standard_20260809_cfgpdf"
        if any(r["code"]==code for r in availability): return False
        availability.append({"id":str(av_id),"code":code,"configuration_code":config,"attribute_code":attr,"availability_status":"standard","observation_date":DATE,"source_code":source,"notes":f"Exact saved configurator PDF standard-equipment statement: {raw}"})
        av_id+=1; counters["availability_added"]+=1; return True

    def add_price(config, amount, source, raw):
        nonlocal price_id
        same=[r for r in prices if r["configuration_code"]==config and r["market"]=="PL" and r["price_type"]=="catalog_gross"]
        if any(r["amount"]==amount for r in same): counters["prices_already_covered"]+=1; return False
        code=f"{config}_pl_20260809_cfgpdf"
        if any(r["code"]==code for r in prices): return False
        prices.append({"id":str(price_id),"code":code,"configuration_code":config,"market":"PL","price_type":"catalog_gross","amount":amount,"currency_code":"PLN","price_date":DATE,"source_code":source,"notes":f"Exact saved configurator PDF selected configuration price: {raw}"})
        price_id+=1; counters["prices_added"]+=1; return True

    # Exact positive standard-equipment aliases. Negative/base-state wording is deliberately not projected to not_available.
    standard_aliases = {
      "światła automatyczne, wycieraczki automatyczne":["automatic_headlights","rain_sensing_wipers"],
      "regulator-ogranicznik prędkości":["cruise_control","speed_limiter"],
      "regulator i ogranicznik prędkości":["cruise_control","speed_limiter"],
      "światła przednie eco led":["led_headlights"],
      "tylna kanapa składana i podnoszona w układzie 1/3-2/3":["rear_seat_folding"],
      "lusterka boczne regulowane elektrycznie, podgrzewane":["side_mirrors_electric_adjustment","side_mirrors_heated"],
      "lusterka boczne regulowane i składane elektrycznie, podgrzewane":["side_mirrors_electric_adjustment","side_mirrors_heated","side_mirrors_folding"],
      "kolorowy wyświetlacz komputera 7\"":["instrument_cluster_colour_7"],
      "kolorowy wyświetlacz komputera 10,1\"":["instrument_cluster_colour_10_1"],
      "system multimedialny nowy media display 10\"":["media_display_system","touchscreen"],
      "nowy system multimedialny media display (dotykowy ekran 10\"":["media_display_system","touchscreen"],
      "nowy system multimedialny media nav live 10\"":["navigation_system","touchscreen","connected_services"],
      "system multimedialny nowy media nav 10\"":["navigation_system","touchscreen"],
      "system multimedialny media control":["media_control_system","bluetooth_connectivity"],
      "nowy system multimedialny media control":["media_control_system","bluetooth_connectivity"],
      "system multiview kamera":["360_camera_system"],
      "automatyczna dwustrefowa klimatyzacja":["automatic_climate_control","dual_zone_climate_control"],
      "dach panoramiczny otwierany elektrycznie":["glass_sunroof"],
      "adaptacyjny regulator-ogranicznik prędkości":["adaptive_cruise_control"],
      "aktywny regulator prędkości (acc)":["adaptive_cruise_control"],
      "fotel kierowcy regulowany elektrycznie":["driver_seat_electric_adjustment"],
      "fotel kierowcy z regulacją lędźwi":["driver_seat_lumbar_adjustment"],
      "wspomaganie parkowania tyłem":["rear_parking_sensors"],
      "ogrzewanie tylnej szyby":["heated_rear_window"],
      "tylna wycieraczka":["rear_wiper"],
      "konsola środkowa ze schowkiem i podłokietnikiem":["front_centre_armrest"],
      "tylne oparcie kanapy składane 40/20/40 z systemem easy fold":["rear_seat_easy_fold"],
    }

    technical_simple = {
      "Długość całkowita":("overall_length","integer"),
      "EV - zasięg w cyklu mieszanym WLTP E-TECH (km)":("combined_range","integer"),
      "EV - zużycie energii elektrycznej w cyklu mieszanym WLTP (kWh/100 km)":("electric_energy_consumption","decimal"),
      "Liczba biegów do przodu":("gear_count","integer"),
      "Liczba cylindrów":("cylinder_count","integer"),
      "Liczba drzwi":("number_of_doors","integer"),
      "Liczba miejsc siedzących":("number_of_seats","integer"),
      "Liczba zaworów":("total_valve_count","integer"),
      "Maksymalna masa całkowita pojazdu (kg)":("gross_vehicle_weight","integer"),
      "Maksymalna masa całkowita zespołu pojazdów (kg)":("gross_train_weight","integer"),
      "Maksymalna masa przyczepy bez hamulca (kg)":("unbraked_trailer_weight","integer"),
      "Maksymalna masa przyczepy z hamulcem (kg)":("braked_trailer_weight","integer"),
      "Maksymalna ładowność (kg)":("maximum_payload","integer"),
      "Minimalna masa pojazdu gotowego do jazdy (bez opcji) (kg)":("minimum_kerb_weight","integer"),
      "Opony standardowe":("standard_tyre_specification","string"),
      "Pojemność skokowa (cm3)":("engine_displacement","integer"),
      "Poziom hałasu przy 50 km/h (dB)":("noise_level_at_50_kmh","decimal"),
      "Prędkość maksymalna (km/h)":("top_speed","integer"),
      "Rozstaw osi":("wheelbase","integer"),
      "Zwis przedni":("front_overhang","integer"),
      "Zwis tylny":("rear_overhang","integer"),
      "pojemność zbiornika paliwa (l)":("fuel_tank_capacity","decimal"),
      "Średnica zawracania (m)":("turning_circle","decimal"),
    }

    # Existing exact literal -> standard attribute mappings are trusted only when unique.
    literal_map=defaultdict(set)
    for r in availability:
        if r.get("availability_status")!="standard": continue
        note=r.get("notes","")
        if ": " in note:
            lit=note.split(": ",1)[1].strip()
            if len(lit)>=5: literal_map[ncase(lit)].add(r["attribute_code"])
    literal_map={k:next(iter(v)) for k,v in literal_map.items() if len(v)==1}

    for doc in ledger["documents"]:
        config=doc["configuration_code"]; source=doc["source_code"]; family=doc["family"]
        if source not in sources: raise RuntimeError(f"unregistered source {source}")
        if (source,config) not in source_configs: raise RuntimeError(f"unlinked source/config {source} {config}")
        pages={p["page"]:p["text"] for p in doc["pages_ledger"]}
        summary="\n".join(pages.get(i,"") for i in (1,2))
        m=re.search(r"Cena wybranej konfiguracji\s*\n\s*([0-9 ]+)\s*zł",summary,re.I)
        if m: add_price(config,re.sub(r"\s+","",m.group(1)),source,m.group(0).replace("\n"," "))
        else: record_defer("price",config,"not_parsed")
        lines=[x.strip() for x in summary.splitlines() if x.strip()]
        selected={}
        for label in ("Kolor","Felgi","Tapicerka"):
            try: i=lines.index(label)
            except ValueError: continue
            if i+1<len(lines): selected[label]=lines[i+1]
        if "Kolor" in selected: add_value(config,"exterior_color",strip_price(selected["Kolor"]),source,2,selected["Kolor"])
        if "Felgi" in selected:
            for attr,val in wheel_values(selected["Felgi"]).items(): add_value(config,attr,val,source,2,selected["Felgi"])
        if "Tapicerka" in selected:
            val=re.sub(r"^tapicerka\s+","",strip_price(selected["Tapicerka"]),flags=re.I)
            add_value(config,"upholstery_variant",val,source,2,selected["Tapicerka"])

        standard_text="\n".join(p["text"] for p in doc["pages_ledger"] if "standard_equipment" in p.get("sections",[]))
        std=ncase(standard_text)
        for lit,attr in literal_map.items():
            if lit in std: add_standard(config,attr,source,lit)
        for alias,alist in standard_aliases.items():
            if ncase(alias) in std:
                for attr in alist: add_standard(config,attr,source,alias)
        # Positive scalar/string facts embedded in standard equipment.
        if "opony całoroczne" in std: add_value(config,"seasonal_tyre_type","all-season",source,3,"opony całoroczne")
        elif "opony letnie" in std: add_value(config,"seasonal_tyre_type","summer",source,3,"opony letnie")
        if "tylna kanapa składana i podnoszona w układzie 1/3-2/3" in std: add_value(config,"rear_seat_folding","1/3-2/3",source,3,"tylna kanapa składana i podnoszona w układzie 1/3-2/3")
        if "tylne oparcie kanapy składane 40/20/40" in std: add_value(config,"rear_seat_folding","40/20/40",source,3,"tylne oparcie kanapy składane 40/20/40")
        if "tylne oparcie kanapy składane 40/60" in std: add_value(config,"rear_seat_folding","40/60",source,3,"tylne oparcie kanapy składane 40/60")
        if "fotele kubełkowe" in std: add_value(config,"front_seat_type","bucket",source,3,"fotele kubełkowe")
        if "elektryczne wspomaganie kierownicy" in std: add_value(config,"steering_type","electric",source,3,"elektryczne wspomaganie kierownicy")
        if "dwusprzęgłowa skrzynia biegów 6-biegowa, model dw2" in std: add_value(config,"gearbox_code","DW2",source,3,"dwusprzęgłowa skrzynia biegów 6-biegowa, model DW2")
        if re.search(r"(?:media display|media nav(?: live)?) 10\"",std): add_value(config,"infotainment_screen_size","10",source,3,"10-inch multimedia display explicitly stated")

        seen=set()
        for p in doc["pages_ledger"]:
            if "technical" not in p.get("sections",[]): continue
            for raw in p["text"].splitlines():
                label,val=split_label_value(raw)
                if not label: continue
                key=(ncase(label),ncase(val))
                if key in seen: counters["technical_duplicate_page_rows"]+=1; continue
                seen.add(key)
                page=p["page"]
                if label in technical_simple:
                    attr,kind=technical_simple[label]
                    if kind=="string": add_value(config,attr,norm(val),source,page,raw); continue
                    x=scalar(val,kind)
                    if x is not None: add_value(config,attr,x,source,page,raw)
                    elif ncase(val)!="nie dotyczy": record_defer("technical",raw,"non_scalar")
                    continue
                if label in ("Emisja CO2 cykl mieszany WLTP (g/km)","Zużycie paliwa cykl mieszany WLTP (l/100 km)"):
                    attr="co2_emissions" if label.startswith("Emisja") else "fuel_consumption_combined"
                    x=scalar(val)
                    if x is not None: add_value(config,attr,x,source,page,raw,"petrol" if is_bifuel(config) else "")
                    else: record_defer("technical",raw,"non_scalar")
                    continue
                if label in ("Emisja CO2 cykl mieszany WLTP*LPG (g/km)","Zużycie paliwa cykl mieszany WLTP*LPG (l/100km)"):
                    attr="co2_emissions" if label.startswith("Emisja") else "fuel_consumption_combined"
                    x=scalar(val)
                    if x is not None: add_value(config,attr,x,source,page,raw,"lpg")
                    else:
                        mrange=re.fullmatch(r"(\d+(?:[.,]\d+)?)\s*[-/]\s*(\d+(?:[.,]\d+)?)",norm(val))
                        if mrange: add_range(config,attr,mrange.group(1).replace(',','.'),mrange.group(2).replace(',','.'),source,page,raw,"lpg")
                        else: record_defer("technical",raw,"non_scalar")
                    continue
                if label in ("Przyspieszenie 0-100 km/h (s)","1000 m ze startu zatrzymanego (s)"):
                    attr="acceleration_0_100" if label.startswith("Przyspieszenie") else "standing_km"
                    x=scalar(val)
                    if x is not None: add_value(config,attr,x,source,page,raw)
                    else:
                        pairs=simple_fuel_pair(val)
                        if pairs:
                            for fuel,x in pairs: add_value(config,attr,scalar(x) or x,source,page,raw,fuel)
                        else: record_defer("technical",raw,"fuel_pair_or_complex")
                    continue
                if label=="Moc maksymalna kW (KM)":
                    pairs=simple_fuel_pair(val)
                    if pairs:
                        for fuel,x in pairs: add_value(config,"engine_power",scalar(x) or x,source,page,raw,fuel)
                    else:
                        mnum=re.match(r"^(\d+(?:[.,]\d+)?)\s*\(",norm(val))
                        if mnum:
                            attr="electric_motor_power" if family=="spring" else "hybrid_system_power_total" if ("hybrid155" in config or "hybridg150" in config) else "engine_power"
                            add_value(config,attr,scalar(mnum.group(1)) or mnum.group(1),source,page,raw)
                        else: record_defer("technical",raw,"power_complex")
                    continue
                if label=="Maksymalny moment obrotowy w Nm":
                    v=norm(val).replace(",",".")
                    if "/" not in v:
                        mtor=re.match(r"^(\d+(?:\.\d+)?)(?:\s+przy\s+(\d+)(?:-(\d+))?)?",v,re.I)
                        if mtor:
                            attr="electric_motor_torque" if family=="spring" else "engine_torque"
                            add_value(config,attr,scalar(mtor.group(1)) or mtor.group(1),source,page,raw)
                            if mtor.group(2):
                                if mtor.group(3): add_range(config,"max_torque_rpm",mtor.group(2),mtor.group(3),source,page,raw)
                                else: add_value(config,"max_torque_rpm",mtor.group(2),source,page,raw)
                        else: record_defer("technical",raw,"torque_complex")
                    else: record_defer("technical",raw,"torque_multicomponent")
                    continue
                if label=="Norma emisji spalin":
                    ev={"euro 6e bis":"euro_6e_bis","euro6e bis":"euro_6e_bis","euro 6e":"euro_6e","euro6":"euro_6","euro 6":"euro_6","nie dotyczy":"ev"}.get(ncase(val))
                    if ev: add_value(config,"emission_standard",ev,source,page,raw)
                    else: record_defer("technical",raw,"enum_unmapped")
                    continue
                if label=="Rodzaj paliwa":
                    mapping={"benzyna":"petrol","benzyna + lpg":"lpg_petrol","benzyna full hybrid":"hybrid","benzyna hybrid":"hybrid","benzyna mild hybrid":"mhev","elektryczny":"electric","energia elektryczna":"electric"}
                    x=mapping.get(ncase(val))
                    if x: add_value(config,"fuel_type",x,source,page,raw)
                    else: record_defer("technical",raw,"fuel_enum_unmapped")
                    continue
                if label=="Rodzaj napędu":
                    add_value(config,"drive_layout",norm(val),source,page,raw); continue
                if label=="Szerokość całkowita":
                    v=norm(val)
                    if re.fullmatch(r"\d+",v): add_value(config,"overall_width",v,source,page,raw)
                    elif "Stepway" in v and "/" in v:
                        nums=re.findall(r"\d+",v)
                        if len(nums)>=2: add_value(config,"overall_width",nums[1] if family=="sandero_stepway" else nums[0],source,page,raw)
                    elif not v.startswith("z lusterkami"): record_defer("technical",raw,"width_composite")
                    continue
                if label=="Szerokość całkowita z lusterkami zewnętrznymi":
                    nums=re.findall(r"\d+",val)
                    if len(nums)==1: add_value(config,"overall_width_with_mirrors",nums[0],source,page,raw)
                    elif len(nums)>=2 and "rozłożone" in val: add_value(config,"overall_width_with_mirrors",nums[-1],source,page,raw)
                    else: record_defer("technical",raw,"mirror_width_composite")
                    continue
                if label=="Wysokość całkowita":
                    v=norm(val); nums=re.findall(r"\d+",v)
                    if family=="spring" and len(nums)==1: add_value(config,"overall_height",nums[0],source,page,raw)
                    elif family in ("sandero","sandero_stepway") and len(nums)>=2: add_value(config,"overall_height",nums[1] if family=="sandero_stepway" else nums[0],source,page,raw)
                    else: record_defer("technical",raw,"height_layout_dependent")
                    continue
                if label=="Wysokość pojazdu nieobciążonego z relingami (mm)":
                    nums=re.findall(r"\d+",val)
                    if family in ("duster","bigster") and nums: add_value(config,"roof_height_with_rails",nums[0],source,page,raw)
                    elif family in ("jogger_5","jogger_7") and len(nums)>=2: add_value(config,"roof_height_with_rails",nums[0] if family=="jogger_5" else nums[1],source,page,raw)
                    elif family=="sandero_stepway" and nums: add_value(config,"roof_height_with_rails",nums[0],source,page,raw)
                    else: record_defer("technical",raw,"height_with_rails_not_applicable_or_ambiguous")
                    continue
                if label=="Prześwit pojazdu":
                    nums=[x.replace(',','.') for x in re.findall(r"\d+(?:[.,]\d+)?",val)]
                    if len(nums)>=2 and all('.' not in x for x in nums[:2]):
                        add_value(config,"ground_clearance_laden",nums[0],source,page,raw)
                        add_value(config,"ground_clearance_unladen",nums[1],source,page,raw)
                    else: record_defer("technical",raw,"ground_clearance_context_or_decimal")
                    continue
                if label.startswith("Prześwit pojazdu 130-160"):
                    if family in ("sandero","sandero_stepway"):
                        lo,hi=("170","200") if family=="sandero_stepway" else ("130","160")
                        add_value(config,"ground_clearance_laden",lo,source,page,raw); add_value(config,"ground_clearance_unladen",hi,source,page,raw)
                    continue
                if label=="napięcie nominalne" and family=="spring":
                    m=re.search(r"\d+",val)
                    if m: add_value(config,"traction_battery_voltage",m.group(),source,page,raw)
                    continue
                if label=="pojemność akumulatora":
                    m=re.search(r"\d+(?:[.,]\d+)?",val)
                    if m:
                        x=m.group().replace(',','.')
                        if family=="spring": record_defer("technical",raw,"traction_battery_capacity_unqualified")
                        else: add_value(config,"hybrid_battery_capacity_source_stated",x,source,page,raw)
                    continue
                if label=="ładowanie AC" and family=="spring":
                    m=re.search(r"\d+(?:[.,]\d+)?",val)
                    if m: add_value(config,"onboard_charger_power",m.group().replace(',','.'),source,page,raw)
                    continue
                if label in ("Rodzaj nadwozia","Rodzaj skrzyni biegów","Typ techniczny"):
                    record_defer("technical",raw,"no_safe_existing_canonical_mapping"); continue
                record_defer("technical",raw,"unhandled_label")

    summary=dict(counters)
    summary.update({"documents":len(ledger["documents"]),"pages":ledger["summary"]["pages"],"deferred_total":sum(deferred.values())})
    out={"kind":"dacia_current_configurator_pdf_canonical_import","observed_date":DATE,"mode":"apply" if apply else "dry-run","summary":summary,"deferred_by_reason":dict(sorted(deferred.items())),"deferred_examples":dict(sorted(examples.items()))}
    REPORT.parent.mkdir(parents=True,exist_ok=True); REPORT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if apply:
        for n in names:
            if n in ("attributes.csv","sources.csv","source_configurations.csv"): continue
            write_csv(n,*tables[n])
    return out


def main():
    p=argparse.ArgumentParser(); p.add_argument("--apply",action="store_true"); a=p.parse_args()
    out=build(a.apply); print(json.dumps(out["summary"],ensure_ascii=False,indent=2))

if __name__=="__main__": main()
