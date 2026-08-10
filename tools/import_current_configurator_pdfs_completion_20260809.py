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
REPORT = ROOT / "data/reporting/dacia_configurator_pdf_completion_import_20260809.json"
DATE = "2026-08-09"


def read_csv(name):
    with (MASTER / name).open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames or []), list(r)


def write_csv(name, fields, rows):
    with (MASTER / name).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def norm(s):
    s = unicodedata.normalize("NFKC", s or "").replace("\u00a0", " ")
    return re.sub(r"\s+", " ", s.strip())


def ncase(s):
    return norm(s).casefold()


def next_id(rows):
    return max((int(r["id"]) for r in rows), default=0) + 1


def stitched_lines(text):
    raw = [x.strip() for x in text.splitlines() if x.strip()]
    continuations = re.compile(r"^(?:m\.\)|l\)\(7-m\.\)|\d{3,5}(?:\(benzyna\))?|\d+\s+\d+)$", re.I)
    out=[]; i=0
    while i < len(raw):
        cur=raw[i]
        if i+1 < len(raw) and continuations.match(raw[i+1]) and (
            cur.endswith("-") or "Pojemność przestrzeni bagażowej" in cur or "Maksymalny moment obrotowy" in cur or "Moc maksymalna" in cur
        ):
            nxt=raw[i+1]
            if cur.endswith("-") or nxt.startswith("l)") or nxt.startswith("m.)"):
                cur += nxt
            else:
                cur += " " + nxt
            i += 1
        out.append(cur); i += 1
    return out


def build(apply=False):
    ledger=json.loads(LEDGER.read_text(encoding="utf-8"))
    attrs_fields, attrs = read_csv("attributes.csv")
    val_fields, values = read_csv("configuration_attribute_values.csv")
    range_fields, ranges = read_csv("configuration_attribute_value_ranges.csv")
    av_fields, availability = read_csv("configuration_attribute_availability.csv")
    ctx_fields, contexts = read_csv("configuration_cargo_volume_contexts.csv")
    attrs_by_code={r["code"]:r for r in attrs}
    counters=Counter(); deferred=Counter(); examples=defaultdict(list)
    value_id=next_id(values); range_id=next_id(ranges); av_id=next_id(availability); ctx_id=next_id(contexts)

    def defer(reason, raw):
        deferred[reason]+=1
        if len(examples[reason])<15: examples[reason].append(raw)

    def add_attr(code, category, name, dtype, unit, description):
        nonlocal attrs_by_code
        if code in attrs_by_code: return
        row={"id":str(next_id(attrs)),"code":code,"category":category,"name":name,"data_type":dtype,"unit":unit,"description":description,"status":"active"}
        attrs.append(row); attrs_by_code[code]=row; counters["attributes_added"]+=1

    new_attrs = [
      ("standing_400m","Performance","Standing 400 metres","decimal","s","Time required to cover 400 metres from standstill as stated by the source."),
      ("body_style_source_stated","Exterior","Source-stated body style","string","","Body-style wording exactly as stated by the source without remapping to a project taxonomy."),
      ("technical_type_code","Powertrain","Technical type code","string","","Manufacturer or homologation technical type code exactly as stated by the source."),
      ("gearbox_source_description","Transmission","Source-stated gearbox description","string","","Transmission description exactly as stated by the source."),
      ("traction_battery_capacity_source_stated","Electric System","Source-stated traction battery capacity","decimal","kWh","Traction-battery capacity exactly as stated without classifying it as gross, net or usable."),
      ("cargo_floor_width","Dimensions","Cargo floor width","integer","mm","Width of the lower part of the luggage compartment exactly as stated by the source."),
      ("height_with_tailgate_open","Dimensions","Height with tailgate open","integer","mm","Overall source-stated vehicle height with the rear tailgate open."),
      ("overall_height_source_stated","Dimensions","Source-stated overall height","string","","Complete overall-height wording retained when a source gives multiple contextual values in one field."),
      ("homologation_procedure_code","Emissions","Homologation procedure code","string","","Source-stated homologation procedure identifier."),
      ("homologation_protocol","Emissions","Homologation protocol","string","","Source-stated homologation protocol, such as WLTP."),
      ("ac_charging_time_20_100_source_stated","Electric System","AC charge time 20-100% source-stated","string","","Exact source-stated AC charging duration from 20% to 100%."),
      ("electric_motor_torque_rpm","Electric System","Electric motor maximum torque RPM","integer","rpm","Source-stated electric-motor speed corresponding to maximum stated torque."),
      ("reversing_lights_count","Lighting","Reversing lights count","integer","","Number of reversing lamps explicitly stated for the configuration."),
      ("factory_speed_limit","Performance","Factory speed limit","integer","km/h","Explicit source-stated vehicle speed limitation."),
      ("second_row_lighting","Lighting","Second-row lighting","boolean","","Dedicated lighting for the second seating row."),
      ("rear_headrest_count","Seats","Rear headrest count","integer","","Number of rear head restraints explicitly stated by the source."),
      ("cargo_cover","Capacities","Cargo cover","boolean","","Roller blind or parcel cover for the luggage compartment."),
      ("factory_lpg_system","Engine","Factory LPG system","boolean","","Factory-installed LPG system explicitly stated by the source."),
      ("steering_wheel_material","Steering","Steering wheel material","string","","Source-stated steering-wheel covering or material."),
      ("centre_console_variant","Seats","Centre console variant","string","","Source-stated centre-console construction or storage arrangement."),
      ("key_count","Doors","Supplied key count","integer","","Number of vehicle keys explicitly stated as supplied."),
      ("boot_floor_carpet","Capacities","Boot floor carpet","boolean","","Carpet or trim covering on the luggage-compartment floor."),
      ("roof_type_source_stated","Exterior","Source-stated roof type","string","","Roof construction wording exactly as stated by the source."),
      ("cooled_centre_armrest","HVAC","Cooled centre armrest storage","boolean","","Centre armrest or its storage compartment has cooling functionality."),
      ("dust_seals","Exterior","Dust seals","boolean","","Additional dust seals explicitly stated by the source."),
      ("seatback_pockets","Seats","Seatback pockets","boolean","","Storage pockets on the rear of seat backs."),
      ("speaker_count","Infotainment","Speaker count","integer","","Number of loudspeakers explicitly stated for the multimedia system."),
      ("dab_radio","Infotainment","DAB radio","boolean","","Digital Audio Broadcasting radio explicitly stated by the source."),
      ("interface_language_source_stated","Infotainment","Source-stated interface language","string","","Vehicle interface or message language explicitly stated by the source."),
    ]
    for a in new_attrs: add_attr(*a)

    # Spring uses decimal clearances. Widening integer -> decimal preserves every existing integer observation.
    for code in ("ground_clearance_laden","ground_clearance_unladen"):
        if code in attrs_by_code and attrs_by_code[code]["data_type"]=="integer":
            attrs_by_code[code]["data_type"]="decimal"; counters["attribute_types_widened"]+=1

    def add_value(config, attr, value, source, page, raw, fuel="", suffix="cfgpdf2", force_distinct=False):
        nonlocal value_id
        if attr not in attrs_by_code:
            defer("missing_attribute", f"{attr}: {raw}"); return None
        value=str(value).replace(",",".") if attrs_by_code[attr]["data_type"] in ("integer","decimal") else str(value)
        base=f"{config}_{attr}_{fuel or 'all'}_20260809_{suffix}"
        existing={r["code"] for r in values}
        if force_distinct and base in existing:
            counters["values_already_covered"]+=1; return base
        if not force_distinct:
            same=[r for r in values if r["configuration_code"]==config and r["attribute_code"]==attr and r.get("fuel_type_code","")==fuel and r["value"]==value]
            if same: counters["values_already_covered"]+=1; return same[-1]["code"]
        code=base; n=2
        while code in existing: code=f"{base}_{n}"; n+=1
        row={"id":str(value_id),"code":code,"configuration_code":config,"attribute_code":attr,"fuel_type_code":fuel,"gear_number":"","value":value,"observation_date":DATE,"source_code":source,"notes":f"Exact saved configurator PDF, page {page}: {raw}"}
        values.append(row); value_id+=1; counters["values_added"]+=1; return code

    def add_range(config, attr, lo, hi, source, page, raw, fuel=""):
        nonlocal range_id
        lo=str(lo).replace(',','.'); hi=str(hi).replace(',','.')
        same=[r for r in ranges if r["configuration_code"]==config and r["attribute_code"]==attr and r.get("fuel_type_code","")==fuel and r["minimum_value"]==lo and r["maximum_value"]==hi]
        if same: counters["ranges_already_covered"]+=1; return same[-1]["code"]
        code=f"{config}_{attr}_{fuel or 'all'}_range_20260809_cfgpdf2"
        if any(r["code"]==code for r in ranges): code += f"_{range_id}"
        ranges.append({"id":str(range_id),"code":code,"configuration_code":config,"attribute_code":attr,"fuel_type_code":fuel,"minimum_value":lo,"maximum_value":hi,"lower_inclusive":"true","upper_inclusive":"true","observation_date":DATE,"source_code":source,"notes":f"Exact saved configurator PDF, page {page}: {raw}"})
        range_id+=1; counters["ranges_added"]+=1; return code

    def add_standard(config, attr, source, raw):
        nonlocal av_id
        if attr not in attrs_by_code: defer("missing_equipment_attribute", f"{attr}: {raw}"); return
        if any(r["configuration_code"]==config and r["attribute_code"]==attr and r["availability_status"]=="standard" for r in availability):
            counters["availability_already_covered"]+=1; return
        code=f"{config}_{attr}_standard_20260809_cfgpdf2"
        if any(r["code"]==code for r in availability): return
        availability.append({"id":str(av_id),"code":code,"configuration_code":config,"attribute_code":attr,"availability_status":"standard","observation_date":DATE,"source_code":source,"notes":f"Exact saved configurator PDF standard-equipment statement: {raw}"})
        av_id+=1; counters["availability_added"]+=1

    def add_context(value_code, basis, second="", third="", compartment="main_luggage_compartment", spare="", kit="", note=""):
        nonlocal ctx_id
        if not value_code: return
        if any(r["configuration_attribute_value_code"]==value_code and r["measurement_basis_code"]==basis and r["second_row_state_code"]==second and r["third_row_state_code"]==third and r["spare_wheel_state_code"]==spare and r["tyre_repair_kit_state_code"]==kit for r in contexts):
            counters["cargo_contexts_already_covered"]+=1; return
        code=f"cargo_context_{value_code}_{ctx_id}"
        contexts.append({"id":str(ctx_id),"code":code,"configuration_attribute_value_code":value_code,"measurement_basis_code":basis,"second_row_state_code":second,"third_row_state_code":third,"compartment_code":compartment,"spare_wheel_state_code":spare,"tyre_repair_kit_state_code":kit,"double_floor_state_code":"","notes":note})
        ctx_id+=1; counters["cargo_contexts_added"]+=1

    def add_cargo(config, source, page, raw, state):
        txt=norm(raw)
        # Sandero/Stepway: VDA values depend on spare wheel vs repair kit, ordinary litre shown for repair kit.
        m=re.search(r"(\d+)\s+z kołem\s*/\s*(\d+)\s*\((\d+)\s*l\)\s*z zestawem",txt,re.I)
        if m:
            for val,basis,spare,kit,attr,tag in [
                (m.group(1),"vda_iso_3832","present","","boot_capacity","spare_vda"),
                (m.group(2),"vda_iso_3832","","present","boot_capacity","kit_vda"),
                (m.group(3),"ordinary_litre","","present","boot_capacity","kit_litre"),
            ]:
                vc=add_value(config,attr,val,source,page,raw,suffix=f"cargo_{state}_{tag}",force_distinct=True)
                add_context(vc,basis,state,"","source_stated_total" if state=="folded" else "main_luggage_compartment",spare,kit,raw)
            return True
        # Jogger shared 5-seat / 7-seat table.
        m=re.search(r"(\d+)\s*dm3\s*\((\d+)\s*l\)\(5-m\.\)\s*/\s*(\d+)\s*dm3\s*\((\d+)\s*l\)\(7-m\.\)",txt,re.I)
        if m:
            is7="jogger_7" in config
            vda=m.group(3) if is7 else m.group(1); litre=m.group(4) if is7 else m.group(2)
            third="upright" if (is7 and state=="upright") else "folded" if (is7 and state=="folded") else ""
            for val,basis,attr,tag in [(vda,"vda_iso_3832","boot_capacity","vda"),(litre,"ordinary_litre","boot_capacity","litre")]:
                vc=add_value(config,attr,val,source,page,raw,suffix=f"cargo_{state}_{tag}",force_distinct=True)
                add_context(vc,basis,state,third,"source_stated_total" if state=="folded" else "main_luggage_compartment",note=raw)
            return True
        # Most Bigster/Duster/Spring rows: VDA dm3 plus ordinary litre.
        m=re.search(r"(\d+)\s*dm3\s*/\s*(\d+)\s*l",txt,re.I)
        if m:
            for val,basis,attr,tag in [(m.group(1),"vda_iso_3832","boot_capacity","vda"),(m.group(2),"ordinary_litre","boot_capacity","litre")]:
                vc=add_value(config,attr,val,source,page,raw,suffix=f"cargo_{state}_{tag}",force_distinct=True)
                add_context(vc,basis,state,"","source_stated_total" if state=="folded" else "main_luggage_compartment",note=raw)
            return True
        # A source may state only one dm3 figure.
        m=re.search(r"(\d+)\s*dm3",txt,re.I)
        if m:
            vc=add_value(config,"boot_capacity",m.group(1),source,page,raw,suffix=f"cargo_{state}_vda",force_distinct=True)
            add_context(vc,"vda_iso_3832",state,"","source_stated_total" if state=="folded" else "main_luggage_compartment",note=raw)
            return True
        defer("cargo_unparsed", raw); return False

    def parse_power(config, source, page, raw):
        s=norm(raw).replace(",",".")
        # Component hybrid power: source explicitly gives two kW components and total hp only.
        m=re.search(r"Moc maksymalna kW \(KM\)\s*(\d+)\s*\+\s*(\d+)\s*\((\d+)\)",s,re.I)
        if m:
            add_value(config,"engine_power",m.group(1),source,page,raw)
            add_value(config,"electric_motor_power",m.group(2),source,page,raw)
            return True
        # LPG / petrol with explicit rpm ranges, including stitched wrapped rows.
        m=re.search(r"Moc maksymalna kW \(KM\)\s*(\d+)\s+przy\s+(\d+)-(\d+)\s*\(LPG\)\s*/\s*(\d+)\s+przy\s+(\d+)-(\d+)\s*\(?benzyna\)?",s,re.I)
        if m:
            add_value(config,"engine_power",m.group(1),source,page,raw,"lpg")
            add_range(config,"max_power_rpm",m.group(2),m.group(3),source,page,raw,"lpg")
            add_value(config,"engine_power",m.group(4),source,page,raw,"petrol")
            add_range(config,"max_power_rpm",m.group(5),m.group(6),source,page,raw,"petrol")
            return True
        return False

    def parse_torque(config, source, page, raw):
        s=norm(raw).replace(",",".")
        tail=re.sub(r"^Maksymalny moment obrotowy w Nm\s*","",s,flags=re.I)
        # petrol / LPG simple pair: 190 / 200 (LPG)
        m=re.fullmatch(r"(\d+)\s*/\s*(\d+)\s*\(LPG\)",tail,re.I)
        if m:
            add_value(config,"engine_torque",m.group(1),source,page,raw,"petrol")
            add_value(config,"engine_torque",m.group(2),source,page,raw,"lpg"); return True
        # LPG first, petrol second, optional rpm ranges.
        m=re.fullmatch(r"(\d+)\s+przy\s+(\d+)(?:-(\d+))?\s*\(LPG\)\s*/\s*(\d+)\s+przy\s+(\d+)(?:-(\d+))?(?:\s*\(?benzyna\)?)?",tail,re.I)
        if m:
            add_value(config,"engine_torque",m.group(1),source,page,raw,"lpg")
            if m.group(3): add_range(config,"max_torque_rpm",m.group(2),m.group(3),source,page,raw,"lpg")
            else: add_value(config,"max_torque_rpm",m.group(2),source,page,raw,"lpg")
            add_value(config,"engine_torque",m.group(4),source,page,raw,"petrol")
            if m.group(6): add_range(config,"max_torque_rpm",m.group(5),m.group(6),source,page,raw,"petrol")
            else: add_value(config,"max_torque_rpm",m.group(5),source,page,raw,"petrol")
            return True
        # ICE + electric motor pair.
        m=re.fullmatch(r"(\d+)\s+przy\s+(\d+)\s*/\s*(\d+)\s+przy\s+(\d+)\s*\(ELEK\.\)",tail,re.I)
        if m:
            add_value(config,"engine_torque",m.group(1),source,page,raw)
            add_value(config,"max_torque_rpm",m.group(2),source,page,raw)
            add_value(config,"electric_motor_torque",m.group(3),source,page,raw)
            add_value(config,"electric_motor_torque_rpm",m.group(4),source,page,raw)
            return True
        return False

    for doc in ledger["documents"]:
        config=doc["configuration_code"]; source=doc["source_code"]; family=doc["family"]
        tech_pages=[p for p in doc["pages_ledger"] if "technical" in p.get("sections",[])]
        # Charge duration is a two-line statement in Spring.
        for p in tech_pages:
            text=norm(p["text"])
            m=re.search(r"ładowanie z Walboxa 7 kW z 20% do 100%\s*w 3 godziny 20 minut",text,re.I)
            if m: add_value(config,"ac_charging_time_20_100_source_stated","3 godziny 20 minut",source,p["page"],m.group(0))

        for p in tech_pages:
            for raw in stitched_lines(p["text"]):
                page=p["page"]; s=norm(raw); low=ncase(s)
                m=re.match(r"400 m ze startu zatrzymanego \(s\)\s+([0-9.,]+)$",s,re.I)
                if m: add_value(config,"standing_400m",m.group(1),source,page,raw); continue
                m=re.match(r"Rodzaj nadwozia\s+(.+)$",s,re.I)
                if m: add_value(config,"body_style_source_stated",m.group(1),source,page,raw); continue
                m=re.match(r"Typ techniczny\s+([A-Z0-9]+)$",s,re.I)
                if m: add_value(config,"technical_type_code",m.group(1),source,page,raw); continue
                m=re.match(r"Rodzaj skrzyni biegów\s+(.+)$",s,re.I)
                if m:
                    desc=m.group(1); add_value(config,"gearbox_source_description",desc,source,page,raw)
                    enum="manual" if "manual" in ncase(desc) else "automatic" if "automat" in ncase(desc) else ""
                    if enum: add_value(config,"gearbox_type",enum,source,page,raw)
                    continue
                m=re.match(r"Procedura homologacji\s+(.+)$",s,re.I)
                if m: add_value(config,"homologation_procedure_code",m.group(1),source,page,raw); continue
                m=re.match(r"Protokół homologacji\s+(.+)$",s,re.I)
                if m: add_value(config,"homologation_protocol",m.group(1),source,page,raw); continue
                m=re.match(r"Szerokość dolnej części bagażnika\s+(\d+)$",s,re.I)
                if m: add_value(config,"cargo_floor_width",m.group(1),source,page,raw); continue
                m=re.match(r"Wysokość bez obciążenia z otwartą klapą tylną\s+(.+)$",s,re.I)
                if m:
                    v=m.group(1); nums=re.findall(r"\d+",v)
                    if len(nums)==1: add_value(config,"height_with_tailgate_open",nums[0],source,page,raw)
                    elif family in ("sandero","sandero_stepway") and len(nums)>=2: add_value(config,"height_with_tailgate_open",nums[1] if family=="sandero_stepway" else nums[0],source,page,raw)
                    else: defer("tailgate_height_composite",raw)
                    continue
                m=re.match(r"Wysokość całkowita\s+(.+)$",s,re.I)
                if m:
                    v=m.group(1); add_value(config,"overall_height_source_stated",v,source,page,raw)
                    nums=re.findall(r"\d+",v)
                    if family in ("jogger_5","jogger_7") and len(nums)>=2: add_value(config,"overall_height",nums[0] if family=="jogger_5" else nums[1],source,page,raw)
                    elif len(nums)==1: add_value(config,"overall_height",nums[0],source,page,raw)
                    continue
                m=re.match(r"Prześwit pojazdu\s+([0-9.,]+)\s*/\s*([0-9.,]+).*obciążon.*nieobciążon",s,re.I)
                if m:
                    add_value(config,"ground_clearance_laden",m.group(1),source,page,raw)
                    add_value(config,"ground_clearance_unladen",m.group(2),source,page,raw); continue
                m=re.match(r"Rodzaj paliwa\s+benzyna mild hybrid \+ LPG$",s,re.I)
                if m: add_value(config,"fuel_type","lpg_petrol",source,page,raw); continue
                m=re.match(r"pojemność akumulatora\s+([0-9.,]+)\s*kWh$",s,re.I)
                if m and family=="spring": add_value(config,"traction_battery_capacity_source_stated",m.group(1),source,page,raw); continue
                m=re.match(r"Emisja CO2 cykl mieszany WLTP \(g/km\)\s+0\s*g/km$",s,re.I)
                if m: add_value(config,"co2_emissions","0",source,page,raw); continue
                if s.startswith("Moc maksymalna kW (KM)") and parse_power(config,source,page,raw): continue
                if s.startswith("Maksymalny moment obrotowy w Nm") and parse_torque(config,source,page,raw): continue
                if s.startswith("Pojemność przestrzeni bagażowej min. (dm3)"):
                    add_cargo(config,source,page,raw,"upright"); continue
                if s.startswith("Pojemność przestrzeni bagażowej maks. po złożeniu kanapy (dm3)"):
                    add_cargo(config,source,page,raw,"folded"); continue

        # Complete positive standard-equipment semantics. Negative/base wording is represented only as exact state values where safe, never as not_available capability.
        std="\n".join(p["text"] for p in doc["pages_ledger"] if "standard_equipment" in p.get("sections",[]))
        st=ncase(std)
        bool_patterns={
          "dwa światła cofania":("reversing_lights_count","2"), "jedno światło cofania":("reversing_lights_count","1"),
          "ograniczenie prędkości do 180 km/h":("factory_speed_limit","180"), "światło w drugim rzędzie":("second_row_lighting","true"),
          "3 zagłówki w drugim rzędzie":("rear_headrest_count","3"), "zwijana roleta bagażnika":("cargo_cover","true"),
          "fabryczna instalacja lpg":("factory_lpg_system","true"), "kierownica z pianki":("steering_wheel_material","foam"),
          "tapicerka podłogi bagażnika":("boot_floor_carpet","true"), "normalny dach":("roof_type_source_stated","normalny dach"),
          "uszczelki przeciwpyłowe":("dust_seals","true"), "kieszenie w tylnej części oparcia foteli":("seatback_pockets","true"),
          "komunikaty w języku polskim":("interface_language_source_stated","polski"),
        }
        for pat,(attr,val) in bool_patterns.items():
            if pat in st: add_value(config,attr,val,source,3,pat)
        if "2 kluczyki z 3 przyciskami" in st: add_value(config,"key_count","2",source,3,"2 kluczyki z 3 przyciskami")
        elif "kluczyk z 3 przyciskami" in st: add_value(config,"key_count","1",source,3,"kluczyk z 3 przyciskami")
        for pat,val in [
          ("niska konsola środkowa z otwartym schowkiem bez podłokietnika","low open storage without armrest"),
          ("niska konsola środkowa z otwartym schowkiem","low open storage"),
          ("konsola środkowa ze schowkiem i podłokietnikiem","storage with armrest"),
          ("wysoka konsola środkowa z chłodzonym podłokietnik","high console with cooled armrest"),
          ("panel centralny z otwartym schowkiem bez podłokietnika","open storage without armrest"),
        ]:
            if pat in st:
                add_value(config,"centre_console_variant",val,source,3,pat)
                break
        if "wysoka konsola środkowa z chłodzonym podłokietnik" in st: add_standard(config,"cooled_centre_armrest",source,"wysoka konsola środkowa z chłodzonym podłokietnik")
        if "szyby tylne otwierane ręcznie" in st or "tylne szyby opuszczane ręcznie" in st: add_value(config,"rear_windows_power","false",source,3,"rear windows manually operated")
        if "ręcznie sterowane lusterka" in st or "lusterka boczne regulowane ręcznie" in st: add_value(config,"side_mirrors_electric_adjustment","false",source,3,"side mirrors manually adjusted")
        if "brak regulacji wysokości fotela pasażera" in st: add_value(config,"passenger_seat_height_adjustment","false",source,3,"brak regulacji wysokości fotela pasażera")
        if "fotel kierowcy z regulacją wzdłużną bez regulacji wysokości" in st:
            add_value(config,"driver_seat_adjustment","longitudinal",source,3,"fotel kierowcy z regulacją wzdłużną bez regulacji wysokości")
            add_value(config,"driver_seat_height_adjustment","false",source,3,"fotel kierowcy z regulacją wzdłużną bez regulacji wysokości")
        if "oparcie tylnej kanapy składane w całości" in st: add_value(config,"rear_seat_folding","one-piece",source,3,"oparcie tylnej kanapy składane w całości")
        if "tylne oparcie kanapy nieskładane" in st: add_value(config,"rear_seat_folding","fixed",source,3,"tylne oparcie kanapy nieskładane")
        # Multimedia component facts retained independently of marketing system name.
        if "radio dab" in st: add_standard(config,"dab_radio",source,"radio DAB")
        if "bluetooth" in st: add_standard(config,"bluetooth_connectivity",source,"Bluetooth")
        if "bezprzewodowa replikacja smartfona" in st: add_standard(config,"wireless_smartphone_replication",source,"bezprzewodowa replikacja smartfona")
        nums=[int(x) for x in re.findall(r"(\d+)\s*głośnik",st)]
        if nums: add_value(config,"speaker_count",str(max(nums)),source,3,"source-stated multimedia speaker count")

    # Deferred source statements that are explicit non-applicability are not missing numeric observations.
    for doc in ledger["documents"]:
        config=doc["configuration_code"]
        for p in doc["pages_ledger"]:
            if "technical" not in p.get("sections",[]): continue
            for raw in stitched_lines(p["text"]):
                if re.match(r"Maksymalna masa (?:całkowita zespołu pojazdów|przyczepy bez hamulca|przyczepy z hamulcem) \(kg\)\s+nd$",norm(raw),re.I):
                    counters["explicit_not_applicable_numeric_statements"]+=1

    out={"kind":"dacia_current_configurator_pdf_completion_import","observed_date":DATE,"mode":"apply" if apply else "dry-run","summary":dict(counters)|{"documents":len(ledger["documents"]),"pages":ledger["summary"]["pages"],"deferred_total":sum(deferred.values())},"deferred_by_reason":dict(sorted(deferred.items())),"deferred_examples":dict(sorted(examples.items()))}
    REPORT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if apply:
        write_csv("attributes.csv",attrs_fields,attrs)
        write_csv("configuration_attribute_values.csv",val_fields,values)
        write_csv("configuration_attribute_value_ranges.csv",range_fields,ranges)
        write_csv("configuration_attribute_availability.csv",av_fields,availability)
        write_csv("configuration_cargo_volume_contexts.csv",ctx_fields,contexts)
    print(json.dumps(out["summary"],ensure_ascii=False,indent=2))
    return out


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--apply",action="store_true"); args=ap.parse_args(); build(args.apply)

if __name__=="__main__": main()
