import glob
import os
import shutil

from acdh_tei_pyutils.tei import TeiReader
from rdflib import RDF, Graph, Literal, Namespace, URIRef
from slugify import slugify

to_ingest = "to_ingest"
out_file = os.path.join(to_ingest, "arche.ttl")
shutil.rmtree(to_ingest, ignore_errors=True)
os.makedirs(to_ingest, exist_ok=True)
g = Graph().parse("arche/arche_top_col.ttl")
arche_constants = Graph().parse("arche/arche_constants.ttl")
TOP_COL = os.environ.get("TOPCOLID", "https://id.acdh.oeaw.ac.at/dboe-tei-xml")
TOP_COL_URI = URIRef(TOP_COL)
ACDH = Namespace("https://vocabs.acdh.oeaw.ac.at/schema#")

print("process Vollartikel")
files = sorted(glob.glob("./102_derived_tei/Artikel_Redaktionstool/*.xml"))

for x in files:
    try:
        doc = TeiReader(x)
    except Exception as e:
        print(x, e)
        continue
    f_name = os.path.basename(x)
    title = slugify(doc.any_xpath(".//tei:titleStmt/tei:title")[0].text)
    subj = URIRef(f"{TOP_COL_URI}/{f_name}")
    g.add((subj, RDF.type, ACDH["Resource"]))
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
            TOP_COL_URI,
        )
    )
    try:
        g.add((subj, ACDH["hasTitle"], Literal(slugify(title), lang="de")))
    except Exception as e:
        print(f"TITLE-ISSUE in {x}: {e}")
        continue
g.serialize(out_file)
