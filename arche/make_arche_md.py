import csv
import glob
import os
import shutil

from acdh_tei_pyutils.tei import TeiReader
from rdflib import RDF, Graph, Literal, Namespace, URIRef
from slugify import slugify

entities = os.path.join("arche", "entities.csv")
to_ingest = "to_ingest"
out_file = os.path.join(to_ingest, "arche.ttl")
shutil.rmtree(to_ingest, ignore_errors=True)
os.makedirs(to_ingest, exist_ok=True)
g = Graph().parse("arche/arche_top_col.ttl")
arche_constants = Graph().parse("arche/arche_constants.ttl")
TOP_COL = os.environ.get("TOPCOLID", "https://id.acdh.oeaw.ac.at/dboe-tei-xml")
TOP_COL_URI = URIRef(TOP_COL)
ACDH = Namespace("https://vocabs.acdh.oeaw.ac.at/schema#")
LIMIT = os.environ.get("LIMIT", False)
SCHEMA_NAME = "WBOE-ODD.rnc"

print("process Vollartikel")
files = sorted(glob.glob("./102_derived_tei/Artikel_Redaktionstool/*.xml"))

print("generate persons")
person_lookup = {}
with open(entities, "r", encoding="utf-8", newline="") as csvfile:
    reader = csv.DictReader(csvfile, delimiter=",")

    for row in reader:
        if row["uri"]:
            person_lookup[row["name"]] = row["uri"]
            subj = URIRef(row["uri"])
            g.add((subj, RDF.type, ACDH["Person"]))
            g.add((subj, ACDH["hasFirstName"], Literal(row["first_name"], lang="de")))
            g.add((subj, ACDH["hasLastName"], Literal(row["last_name"], lang="de")))

if LIMIT:
    files = files[:3]

for x in files:
    try:
        doc = TeiReader(x)
    except Exception as e:
        print(x, e)
        continue
    f_name = f"{slugify(os.path.basename(x.replace('.xml', '')))}.xml"
    title = doc.any_xpath(".//tei:titleStmt/tei:title")[0].text
    subj = URIRef(f"{TOP_COL_URI}/{f_name}")
    g.add((subj, RDF.type, ACDH["Resource"]))
    if title:
        g.add((subj, ACDH["hasTitle"], Literal(title, lang="de")))
    else:
        g.add((subj, ACDH["hasTitle"], Literal(f"TITLE-ISSUE with {x}", lang="de")))
    for p, o in arche_constants.predicate_objects():
        g.add((subj, p, o))
    g.add(
        (
            subj,
            ACDH["hasCategory"],
            URIRef("https://vocabs.acdh.oeaw.ac.at/archecategory/text/tei"),
        )
    )
    g.add(
        (
            subj,
            ACDH["isPartOf"],
            URIRef(f"{TOP_COL_URI}/articles"),
        )
    )
    shutil.copy2(x, os.path.join(to_ingest, f_name))


print("process Retro Artikel")
files = sorted(glob.glob("./102_derived_tei/retro/*.xml"))
if LIMIT:
    files = files[:3]

for x in files:
    try:
        doc = TeiReader(x)
    except Exception as e:
        print(x, e)
        continue
    f_name = f"{slugify(os.path.basename(x.replace('.xml', '')))}.xml"
    subj = URIRef(f"{TOP_COL_URI}/{f_name}")
    g.add((subj, RDF.type, ACDH["Resource"]))
    for p, o in arche_constants.predicate_objects():
        g.add((subj, p, o))
    g.add(
        (
            subj,
            ACDH["isPartOf"],
            URIRef(f"{TOP_COL_URI}/retro-articles"),
        )
    )
    g.add(
        (
            subj,
            ACDH["hasCategory"],
            URIRef("https://vocabs.acdh.oeaw.ac.at/archecategory/text/tei"),
        )
    )
    entries = doc.any_xpath(".//tei:orth[@norm]/@norm")
    file_title = doc.any_xpath(".//tei:title")[0].text
    title = f"{file_title}: {entries[0]} - {entries[-1]}"
    g.add((subj, ACDH["hasTitle"], Literal(title, lang="de")))
    shutil.copy2(x, os.path.join(to_ingest, f_name))

shutil.copy2(
    os.path.join("803_RNG-schematron", SCHEMA_NAME),
    os.path.join(to_ingest, SCHEMA_NAME),
)

print("replace schema location")

for path in glob.glob(f"{to_ingest}/*.xml"):
    with open(path, "r", encoding="utf-8") as fp:
        x = fp.read().replace(
            "../../803_RNG-schematron/WBOE-ODD.rnc",
            "https://id.acdh.oeaw.ac.at/wboe-tei/WBOE-ODD.rnc",
        )
        x = x.replace(
            '<?xml-stylesheet href="wboe-view.xsl" type="text/xsl"?><!DOCTYPE TEI SYSTEM "tei_all.dtd">',
            "",
        )
        if "lieferung" in path:
            x = x.replace(
                '<?xml version="1.0" encoding="UTF-8"?>',
                """<?xml version="1.0" encoding="UTF-8"?>
<?xml-model href="http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>
<?xml-model href="http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng" type="application/xml"
	schematypens="http://purl.oclc.org/dsdl/schematron"?>
""",
            )
    with open(path, "w", encoding="utf-8") as fp:
        fp.write(x)


g.serialize(out_file)
print(person_lookup)
