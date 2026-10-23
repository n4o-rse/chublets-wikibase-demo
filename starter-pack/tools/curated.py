"""Hand-curated tables for the chublets Wikibase starter pack.

Everything here is a *decision or a transcription*, not a measurement. Each row
carries a provenance code so a reader can tell what is checked and what is not.

Provenance codes (see data/sources.csv):
  S1  sources/codemeta-wikidata-crosswalk.xlsx           (CodeMeta <-> Wikidata crosswalk workbook)
  S2  sources/wikidata-software-properties.csv           (hand-transcribed from the WikiProject Informatics/Software/Properties PDF)
  S3  open-archaeo py/wikidata/model.py + docs/MAPPING.md (n4o-rse/open-archaeo, HEAD 51d23b1)
  S4  Wikidata:WikiProject chublets-software             (search snippet, 2026-10-21; page itself not fetchable)
  S5  codemeta.github.io/crosswalk/wikidata              (fetched 2026-10-21, 30 rows)
  S6  Wikidata pages seen as search snippets             (2026-10-21)
  S7  earlier chats with Flo (summaries / excerpts)
  R   recalled by the assistant, NOT checked against Wikidata in this session

Confidence: checked = appears verbatim in a source above; source-claimed = a source
asserts it but this session could not re-check it; recalled = assistant memory only.
"""

# --------------------------------------------------------------------------
# Wikidata properties
# columns: pid | label_en | datatype | group | role | provenance | confidence
# datatype is blank when not known with confidence.
# --------------------------------------------------------------------------
PROPERTIES = """
P31|instance of|wikibase-item|identity|statement|S3|checked
P279|subclass of|wikibase-item|identity|statement|R|recalled
P6104|maintained by WikiProject|wikibase-item|identity|statement|S3;S4|checked
P361|part of|wikibase-item|identity|statement|S1;S2;S3;S4|checked
P527|has part(s)|wikibase-item|relations|statement|S1;S5|source-claimed
P195|collection|wikibase-item|identity|statement|S3|checked
P217|inventory number|string|identity|statement|S3|checked
P2888|exact match|url|identity|statement|S1;S3;S4|checked
P2561|name|monolingualtext|identity|statement|S1;S3|checked
P1476|title|monolingualtext|identity|statement|S7;S6|source-claimed
P1448|official name|monolingualtext|identity|statement|S6|source-claimed
P1705|native label|monolingualtext|identity|statement|S1|recalled
P10|video|commonsMedia|media|statement|S1|recalled
P973|described at URL|url|links|statement|S1;S3|checked
P921|main subject|wikibase-item|classification|statement|S1;S3|checked
P1269|facet of|wikibase-item|relations|statement|S2|source-claimed
P1545|series ordinal|string|people|qualifier|S3|source-claimed
P178|developer|wikibase-item|people|statement|S1;S2;S3|source-claimed
P170|creator|wikibase-item|people|statement|S2|source-claimed
P50|author|wikibase-item|people|statement|S1;S5|source-claimed
P2093|author name string|string|people|statement|S1|source-claimed
P767|contributor to the creative work or subject|wikibase-item|people|statement|S1;S5|source-claimed
P98|editor|wikibase-item|people|statement|S1;S5|source-claimed
P126|maintained by|wikibase-item|people|statement|S1|source-claimed
P162|producer|wikibase-item|people|statement|S1;S5|source-claimed
P123|publisher|wikibase-item|people|statement|S1;S5|source-claimed
P859|sponsor|wikibase-item|people|statement|S1;S5|source-claimed
P8324|funder|wikibase-item|people|statement|S1|source-claimed
P2037|GitHub username|external-id|people|statement|S2;S3|source-claimed
P735|given name|wikibase-item|people|statement|S1;S5|source-claimed
P734|family name|wikibase-item|people|statement|S1;S5|source-claimed
P968|email address|url|people|statement|S1;S5|source-claimed
P101|field of work|wikibase-item|people|statement|S1|source-claimed
P463|member of|wikibase-item|people|statement|S1|source-claimed
P800|notable work|wikibase-item|people|statement|S1|source-claimed
P166|award received|wikibase-item|people|statement|S1|source-claimed
P856|official website|url|links|statement|S1;S2;S3|checked
P1324|source code repository URL|url|links|statement|S1;S2;S3;S4|checked
P8423|version control system|wikibase-item|links|qualifier|S3;S4|checked
P10627|web interface software|wikibase-item|links|qualifier|S3;S6|source-claimed
P1401|issue tracker URL|url|links|statement|S1;S2;S5|source-claimed
P2078|user manual URL|url|links|statement|S1;S2|source-claimed
P1581|official blog URL|url|links|statement|S2|source-claimed
P1613|IRC channel URL|url|links|statement|S2|source-claimed
P11201|official demo URL|url|links|statement|S1|source-claimed
P1065|archive URL|url|links|qualifier|S3;S4|checked
P2960|archive date|time|links|qualifier|S3;S4|checked
P4945|download link|url|versioning|qualifier|S1;S2;S4;S5|source-claimed
P154|logo image|commonsMedia|media|statement|S1|source-claimed
P18|image|commonsMedia|media|statement|S1|source-claimed
P485|archives at|wikibase-item|media|statement|S1|source-claimed
P277|programmed in|wikibase-item|technical|statement|S1;S2;S3;S4|checked
P400|platform|wikibase-item|technical|statement|S1;S2|source-claimed
P306|operating system|wikibase-item|technical|statement|S1;S2|source-claimed
P1547|depends on software|wikibase-item|technical|statement|S1;S2;S3|checked
P1372|binding of software library|wikibase-item|technical|statement|S2|source-claimed
P408|software engine|wikibase-item|technical|statement|S2|source-claimed
P1414|GUI toolkit or framework|wikibase-item|technical|statement|S2|source-claimed
P1641|port|wikibase-item|technical|statement|S2|source-claimed
P479|input device|wikibase-item|technical|statement|S2|source-claimed
P5196|output device|wikibase-item|technical|statement|S2|source-claimed
P1072|readable file format|wikibase-item|technical|statement|S1;S2|source-claimed
P1073|writable file format|wikibase-item|technical|statement|S1;S2|source-claimed
P1163|media type|string|technical|statement|S2|source-claimed
P3033|package management system|wikibase-item|technical|statement|S2|source-claimed
P2701|file format|wikibase-item|technical|statement|S1;S5|source-claimed
P3575|data size|quantity|technical|statement|S1;S5|source-claimed
P144|based on|wikibase-item|relations|statement|S1;S2|source-claimed
P629|edition or translation of|wikibase-item|relations|statement|S2|source-claimed
P155|follows|wikibase-item|relations|statement|S2|source-claimed
P156|followed by|wikibase-item|relations|statement|S2|source-claimed
P179|part of the series|wikibase-item|relations|statement|S2|source-claimed
P737|influenced by|wikibase-item|relations|statement|S2|source-claimed
P348|software version identifier|string|versioning|statement|S1;S2;S4;S6|checked
P548|version type|wikibase-item|versioning|qualifier|S4;S7|source-claimed
P577|publication date|time|versioning|qualifier|S1;S2;S4|source-claimed
P571|inception|time|versioning|statement|S1;S2|source-claimed
P5017|last update|time|versioning|statement|S1;S6|source-claimed
P580|start time|time|versioning|qualifier|S7|source-claimed
P582|end time|time|versioning|qualifier|S2;S7|source-claimed
P585|point in time|time|versioning|qualifier|S7|source-claimed
P813|retrieved|time|versioning|reference|S7|source-claimed
P1552|has characteristic|wikibase-item|versioning|qualifier|S7|source-claimed
P356|DOI|external-id|rights|statement|S1;S2;S3|checked
P275|copyright license|wikibase-item|rights|statement|S1;S2;S3|source-claimed
P2284|price|quantity|rights|statement|S2|source-claimed
P2992|software quality assurance|wikibase-item|rights|statement|S2|source-claimed
P6138|SoftWare Hash IDentifier (SWHID)|external-id|registries|statement|S4;S3|source-claimed
P5565|CRAN project|external-id|registries|statement|S3|checked
P5568|PyPI project|external-id|registries|statement|S3|checked
P1972|Open Hub ID|external-id|registries|statement|S2|source-claimed
P2209|SourceForge project|external-id|registries|statement|S2|source-claimed
P2537|Free Software Directory entry|external-id|registries|statement|S2|source-claimed
P6830|swMATH work ID|external-id|registries|statement|S2;S3|source-claimed
P1343|described by source|wikibase-item|publication|statement|S1;S3|checked
P2860|cites work|wikibase-item|publication|statement|S1;S5|source-claimed
P2159|computes solution to|wikibase-item|relations|statement|S7|source-claimed
P437|distribution format|wikibase-item|technical|statement|S7|source-claimed
P4107|Framalibre ID|external-id|registries|statement|S7|source-claimed
P3454|distribution package ID P3454 (label to be filled)|external-id|registries|statement|S7|pid-only
P3442|distribution package ID P3442 (label to be filled)|external-id|registries|statement|S7|pid-only
P3463|distribution package ID P3463 (label to be filled)|external-id|registries|statement|S7|pid-only
P3499|distribution package ID P3499 (label to be filled)|external-id|registries|statement|S7|pid-only
P3473|distribution package ID P3473 (label to be filled)|external-id|registries|statement|S7|pid-only
P3597|distribution package ID P3597 (label to be filled)|external-id|registries|statement|S7|pid-only
P3418|distribution package ID P3418 (label to be filled)|external-id|registries|statement|S7|pid-only
P3112|distribution package ID P3112 (label to be filled)|external-id|registries|statement|S7|pid-only
P1416|affiliation|wikibase-item|people|statement|R|recalled
P496|ORCID iD|external-id|people|statement|R|recalled
""".strip()

# --------------------------------------------------------------------------
# Wikidata items
# columns: qid | label_en | kind | used_for | provenance | confidence
# --------------------------------------------------------------------------
ENTITIES = """
Q7397|software|class|root class for software; its "properties for this type" list drives the WikiProject property set|S6|source-claimed
Q40056|computer program|class|narrower than software; programme as executable|R|recalled
Q166142|application software|class|vocabulary.json item_class for "Standalone software"|S3|checked
Q188860|software library|class|vocabulary.json item_class for "Packages and libraries"|S3|checked
Q1070421|script file|class|vocabulary.json item_class for "Scripts"|S3|checked
Q95001953|research software|class|vocabulary.json superclass; also parent of the chublet class|S3|checked
Q506883|free and open-source software|class|used as P31 value in a ShEx schema for research software|S6|source-claimed
Q128751|source code|class|schema:SoftwareSourceCode equivalent class|S6|source-claimed
Q20826013|software version|class|"defined and identifiable development stage of a software product"|S6|source-claimed
Q9143|programming language|class|programming-language items; value domain of P277|S6|source-claimed
Q4027615|informatics|topic|scope of WikiProject Informatics|S6|source-claimed
Q281039|abandonware|class|P31 value for software that is no longer maintained (with P582/P585)|S7|source-claimed
Q151885|concept|version-type|value of P548 version type (publiccode.yml mapping)|S6|source-claimed
Q2804309|stable version|version-type|value of P548 version type|S6|source-claimed
Q3295609|beta version|version-type|value of P548 version type|S6|source-claimed
Q21683863|obsolete version|version-type|value of P548 version type|S6|source-claimed
Q186055|Git|vcs|vocabulary.json version_control_system; value of P8423|S3|checked
Q364|GitHub|forge|example value of P10627 web interface software|S6|source-claimed
Q141115627|chublet|class|THE chublet class; subclass of Q73899440, belonging to Q141115774|S3;S4|checked
Q73899440|Little Minion|class|parent class of chublet (CAA Little Minions working group)|S4|source-claimed
Q141115774|chublets.software|platform|the platform item; value of P361 on every chublet|S3;S4|checked
Q141169143|WikiProject chublets.software|wikiproject|value of P6104 on every chublet|S3;S4|checked
Q141190255|open-archaeo (Repository)|collection|value of P361 and P195 on open-archaeo chublets|S3;S4|checked
Q66606154|Florian Thiery|person|developer of Alligator and AMT; Zenodo record 6976176 cites this QID|S6|source-claimed
Q88865971|Allard W. Mees|person|co-developer of Alligator and AMT; same Zenodo record|S6|source-claimed
Q73901110|CAA SIG Data-Dragon|organisation|CAA special interest group; same Zenodo record|S6|source-claimed
Q1765672|Akregator|software-example|worked example of a software item cited in a Wikidata tutorial|S6|source-claimed
Q8045810|YAGO|software-example|worked example with P1324 + P8423 + P10627 + P348 qualifiers|S6|source-claimed
""".strip()

# --------------------------------------------------------------------------
# What chublets.software needs, per CodeMeta term
# columns: codemeta_property | chublets_property | datatype | tier | strategy | source_field | note
# tier: T1 identity/mandatory · T2 core discovery · T3 extended · T4 later/optional · T5 not planned
# strategy: reuse-wikidata | reuse-wikidata-corrected | wikibase-native | new-property | not-planned
# ALL ROWS ARE PROPOSALS (decision_status = proposed) unless stated in the note.
# --------------------------------------------------------------------------
CODEMETA_DECISIONS = """
codeRepository|source code repository URL|url|T2|reuse-wikidata|open-archaeo: repository (390/416)|Qualifier P8423 is a required-qualifier constraint on Wikidata; add P1065+P2960 from internetarchive.
codeSampleType|-|-|T5|not-planned||Not in CodeMeta proper; no chublets use case.
programmingLanguage|programmed in|item|T2|reuse-wikidata|open-archaeo: platform where platform_role=language (301)|Needs a language item per value; vocabulary.json has them unresolved (null).
runtimePlatform|platform|item|T3|reuse-wikidata||Reviewers: partial match; P400 broader than runtime platform.
targetProduct|target product|item|T3|new-property|open-archaeo: platform where platform_role=host application (34)|OPEN DECISION: open-archaeo maps host application (QGIS, Blender) to P1547 depends on software. CodeMeta targetProduct describes exactly this plugin-to-host relation. Pick one.
applicationCategory|instance of (second class)|item|T2|reuse-wikidata-corrected|open-archaeo: category (416)|Not mapped in the crosswalk; MAPPING.md models it as a further P31 value (software library / application software / script file).
applicationSubCategory|main subject|item|T3|reuse-wikidata-corrected|open-archaeo: tags (416)|Not mapped in the crosswalk; tags are subject terms, see keywords.
applicationSuite|part of|item|T3|reuse-wikidata||Reviewers: P361 covers it and more (partial).
availableOnDevice|-|-|T5|not-planned||Reviewers suggested P400; no use case.
countriesNotSupported|-|-|T5|not-planned||
countriesSupported|-|-|T5|not-planned||
downloadUrl|download link|url|T3|reuse-wikidata||Qualifier on software version identifier (P348), not an item-level statement.
featureList|feature list|text|T4|new-property||CodeMeta-only.
fileSize|data size|quantity|T4|reuse-wikidata||Version-specific; low value for discovery.
installUrl|install URL|url|T4|new-property||CodeMeta-only.
memoryRequirements|-|-|T5|not-planned||
operatingSystem|operating system|item|T3|reuse-wikidata||
permissions|-|-|T5|not-planned||
processorRequirements|-|-|T5|not-planned||
screenshot|image|commonsMedia|T4|reuse-wikidata-corrected||Corrected to P18 in the crosswalk review.
softwareAddOn|-|-|T5|not-planned||Inverse of targetProduct; derive instead.
softwareHelp|user manual URL|url|T3|reuse-wikidata-corrected||Corrected to P2078 in the crosswalk review (range differs).
softwareRequirements|depends on software|item|T2|reuse-wikidata||The dependency relation named in the paper draft as a discovery term.
softwareVersion|software version identifier|string|T3|reuse-wikidata||Version pattern: qualifiers P577, P4945, P356, P548; newest version gets preferred rank (S7).
storageRequirements|-|-|T5|not-planned||
supportingData|supporting data|item|T3|new-property||Relevant for archaeology (tool-to-dataset link); no Wikidata equivalent in the crosswalk.
author|developer|item|T2|reuse-wikidata-corrected|open-archaeo: authors (416)|Crosswalk review corrected P50 author to P178 developer. 187 author strings need person/organisation items (S3).
citation|cites work|item|T4|reuse-wikidata||Direction differs: CodeMeta citation = what the software cites.
contributor|contributor to the creative work or subject|item|T3|reuse-wikidata||
copyrightHolder|copyright holder|item|T4|new-property||CodeMeta-only.
copyrightYear|-|-|T5|not-planned||
dateCreated|inception|time|T3|reuse-wikidata||open-archaeo has none; the archive date bounds it from above.
dateModified|last update|time|T3|reuse-wikidata||
datePublished|publication date|time|T3|reuse-wikidata||Use as qualifier on software version identifier.
editor|-|-|T5|not-planned||Crosswalk review: corrected to no mapping (P98 is for editorial work).
encoding|-|-|T5|not-planned||
encodingFormat|file format|item|T4|reuse-wikidata||For tools prefer readable/writable file format (P1072/P1073).
funder|funder|item|T3|reuse-wikidata-corrected||Corrected to P8324 funder.
hasPart|has part(s)|item|T3|reuse-wikidata||
isAccessibleForFree|-|-|T5|not-planned||Open source is implied by scope.
isPartOf|part of|item|T1|reuse-wikidata|identity block|Used for chublets.software and open-archaeo membership.
keywords|main subject|item|T2|reuse-wikidata|open-archaeo: tags (416)|56 tags need reconciliation; 6 of them are not subjects (docs/ENRICHMENT.md in open-archaeo).
license|copyright license|item|T2|reuse-wikidata|none - open-archaeo records no licence|Largest data gap; must come from repositories (GitHub SPDX).
producer|-|-|T5|not-planned||
provider|-|-|T5|not-planned||
publisher|publisher|item|T4|reuse-wikidata||
review|-|-|T5|not-planned||
sponsor|sponsor|item|T4|reuse-wikidata-corrected||
description|(item description)|monolingualtext|T1|wikibase-native|open-archaeo: description (416)|Native Wikibase field, not a property. Wikidata style: short, lower case, no full stop; open-archaeo values are sentences and need rewriting.
identifier|DOI|external-id|T2|reuse-wikidata-corrected|open-archaeo: doi (34)|Corrected to P356. Zenodo (10.5281) DOIs are release DOIs: qualifier on software version identifier.
name|name|monolingualtext|T1|reuse-wikidata-corrected|open-archaeo: name (416)|Label AND P2561 name statement (tracks renamed tools with dated qualifiers).
sameAs|exact match|url|T1|reuse-wikidata|open-archaeo: url (416)|Entry URL as P2888; in a new Wikibase also the link to the Wikidata item.
url|official website|url|T2|reuse-wikidata|open-archaeo: website (121)|Crosswalk cell reads "wd:856", a typo for P856.
relatedLink|described at URL|url|T3|reuse-wikidata-corrected|open-archaeo: blogpost, youtube (4)|Two rows in the source: P973 and official demo URL (P11201).
buildInstructions|build instructions URL|url|T4|new-property||CodeMeta-only.
continuousIntegration|continuous integration URL|url|T4|new-property||CodeMeta-only.
developmentStatus|development status|item|T3|new-property||Candidate values: active, inactive, abandonware (Q281039). Could be derived from GitHub archived flag.
embargoDate|-|-|T5|not-planned||
embargoEndDate|-|-|T5|not-planned||
funding|-|-|T4|not-planned||Text field; prefer funder statements.
hasSourceCode|has source code|item|T4|new-property||Only if source code and application are modelled as separate items.
isSourceCodeOf|source code of|item|T4|new-property||Inverse of hasSourceCode.
issueTracker|issue tracker URL|url|T3|reuse-wikidata||
maintainer|maintained by|item|T3|reuse-wikidata-corrected||Corrected to P126.
readme|readme URL|url|T4|new-property||CodeMeta-only.
referencePublication|described by source|item|T2|reuse-wikidata|open-archaeo: publication (25)|Reviewers disagree (P2860 vs P1343); MAPPING.md chose P1343 so the article becomes an item keyed by DOI.
softwareSuggestions|-|-|T5|not-planned||
""".strip()

# Wikidata properties that appear in the workbook's "Properties only in the other
# metadata schema" block (or are used by the open-archaeo pipeline) and have no CodeMeta term.
# columns: pid | chublets_property | datatype | tier | strategy | source_field | note
NON_CODEMETA_DECISIONS = """
P279|subclass of|item|T1|reuse-wikidata|class hierarchy|chublet is a subclass of Little Minion (Q73899440); needed to build the class tree in the new Wikibase.
P31|instance of|item|T1|reuse-wikidata|identity block|Value Q141115627 (chublet) on every item; further values from open-archaeo category.
P6104|maintained by WikiProject|item|T1|reuse-wikidata|identity block|Wikidata only. In a new Wikibase every item is a chublet by construction; keep the property only where items are mirrored into Wikidata.
P195|collection|item|T1|reuse-wikidata|identity block|Pairs with P217; open-archaeo (Q141190255). Pipeline model.py (S3).
P217|inventory number|string|T1|reuse-wikidata|open-archaeo: slug (416)|Holds the slug, qualified by P195. A dedicated "open-archaeo ID" (P6830 swMATH precedent) is preferred in a new Wikibase.
P2561|name|monolingualtext|T1|reuse-wikidata|open-archaeo: name|See codemeta name.
P1065|archive URL|url|T2|reuse-wikidata|open-archaeo: internetarchive (222)|Qualifier on P1324.
P2960|archive date|time|T2|reuse-wikidata|derived from internetarchive path (221/222)|Qualifier on P1324.
P8423|version control system|item|T2|reuse-wikidata|derived from repository_host (385 Git)|Required qualifier on P1324.
P10627|web interface software|item|T4|reuse-wikidata|repository_host|Optional qualifier naming the forge (GitHub Q364).
P5565|CRAN project|external-id|T2|reuse-wikidata|open-archaeo: registry where registry_name=CRAN (39)|Package name parsed from the CRAN URL.
P5568|PyPI project|external-id|T2|reuse-wikidata|open-archaeo: registry where registry_name=PyPI (1)|Package name parsed from the PyPI URL.
P3033|package management system|item|T4|reuse-wikidata||Alternative to registry-specific ID properties.
P6138|SoftWare Hash IDentifier (SWHID)|external-id|T3|reuse-wikidata||Upstream open-archaeo lists Software Heritage as planned.
P2037|GitHub username|external-id|T3|reuse-wikidata|derived from forge URL owner (239 owners)|Belongs on the developer item, not the software item.
P1545|series ordinal|string|T3|reuse-wikidata|open-archaeo: authors order|Qualifier on developer; author order is meaningful.
P1343|described by source|item|T2|reuse-wikidata|open-archaeo: publication (25)|See referencePublication.
P1072|readable file format|item|T3|reuse-wikidata||High value for archaeology tools; CodeMeta has no equivalent.
P1073|writable file format|item|T3|reuse-wikidata||As above.
P144|based on|item|T3|reuse-wikidata||Fork/derivation relation.
P973|described at URL|url|T3|reuse-wikidata|open-archaeo: blogpost, youtube|See relatedLink.
P548|version type|item|T3|reuse-wikidata||Qualifier on P348; values Q151885, Q2804309, Q3295609, Q21683863.
P813|retrieved|time|T2|reuse-wikidata||Reference qualifier for every harvested statement (provenance of the ingestion run).
P1552|has characteristic|item|T4|reuse-wikidata||Qualifier, e.g. mirror storage on repository statements.
P734|family name|item|T4|reuse-wikidata||Person items only.
P735|given name|item|T4|reuse-wikidata||Person items only.
P968|email address|url|T5|not-planned||Personal data; do not store in a public Wikibase.
P101|field of work|item|T4|reuse-wikidata||Person/organisation items.
P800|notable work|item|T5|not-planned||
P166|award received|item|T5|not-planned||
P463|member of|item|T4|reuse-wikidata||Person/organisation items.
P485|archives at|item|T5|not-planned||Archival holdings, not web archives.
P154|logo image|commonsMedia|T4|reuse-wikidata||chublets have a mascot and logo family.
P170|creator|item|T4|reuse-wikidata||Prefer developer (P178) for software.
P737|influenced by|item|T4|reuse-wikidata||
P1581|official blog URL|url|T4|reuse-wikidata||
P2078|user manual URL|url|T3|reuse-wikidata||See softwareHelp.
""".strip()


# --------------------------------------------------------------------------
# Properties the earlier chat's page excerpt listed but sources/wikidata-software-properties.csv
# does not (the CSV is a hand transcription of a PDF; the excerpt came from the page itself).
# Both are the WikiProject Informatics/Software/Properties list.  Labels of the eight
# distribution-package IDs were not given; only the PIDs.
# --------------------------------------------------------------------------
WIKIPROJECT_LIST_S7_EXTRA = ["P2159", "P437", "P4107", "P3454", "P3442", "P3463", "P3499", "P3473",
                             "P3597", "P3418", "P3112", "P1476", "P548", "P580", "P585", "P813", "P1552"]

# --------------------------------------------------------------------------
# CodeMeta terms that the official terms page lists (https://codemeta.github.io/terms/,
# fetched 2026-10-21) but the reviewed workbook has no row for.
# columns: term | group | range | codemeta_org_pid (S5) | phase | open_archaeo_source | candidates | note
# --------------------------------------------------------------------------
EXTRA_CODEMETA = """
fileFormat|SoftwareSourceCode/SoftwareApplication (v2 term)|Text or URL|P2701|3||P1072;P1073|Superseded by encodingFormat in schema.org; codemeta.org crosswalk maps it to P2701, same as encodingFormat.
version|SoftwareSourceCode/SoftwareApplication|Number or Text||2||P348|schema.org term next to softwareVersion; candidate only, not in the crosswalk.
position|SoftwareSourceCode/SoftwareApplication|Integer or Text||3|open-archaeo: authors order|P1545|Position in a list, e.g. author order; Wikidata uses series ordinal (P1545) as qualifier.
releaseNotes|SoftwareSourceCode/SoftwareApplication|Text or URL||3||P973|No Wikidata property found in the sources.
contIntegration|CodeMeta (v2 only)|URL||3|||Replaced by continuousIntegration in v3; keep for v2 import.
address|Person|PostalAddress or Text||3|||Person items only.
affiliation|Person|Organization||3||P1416|Candidate recalled, not in any source.
email|Person|Text|P968|3|||Personal data: create the property, do not populate in a public Wikibase.
familyName|Person|Text|P734|3|||Person items only.
givenName|Person|Text|P735|3|||Person items only.
identifier (Person)|Person|URL||3|open-archaeo: derived from forge owner (P2037)|P496;P2037|Person identifier such as ORCID or GitHub username.
reviewAspect|Review (v3)|Text||3|||Only with the Review type.
reviewBody|Review (v3)|Text||3|||Only with the Review type.
roleName|Role (v3)|Text or URL||3|||Qualifier-like term for author/contributor roles.
startDate|Role (v3)|Date or Datetime||3||P580|Qualifier-like.
endDate|Role (v3)|Date or Datetime||3||P582|Qualifier-like.
""".strip()

# codemeta.github.io/crosswalk/wikidata/ (fetched 2026-10-21, 30 rows)
S5_CROSSWALK = {
    "codeRepository": "P1324", "programmingLanguage": "P277", "runtimePlatform": "P400",
    "downloadUrl": "P4945", "fileSize": "P3575", "operatingSystem": "P306",
    "softwareRequirements": "P1547", "softwareVersion": "P348", "author": "P50", "citation": "P2860",
    "contributor": "P767", "dateCreated": "P571", "dateModified": "P5017", "datePublished": "P577",
    "editor": "P98", "fileFormat": "P2701", "funder": "P859", "keywords": "P921", "license": "P275",
    "producer": "P162", "publisher": "P123", "isPartOf": "P361", "hasPart": "P527", "sameAs": "P2888",
    "url": "P856", "givenName": "P735", "familyName": "P734", "email": "P968", "issueTracker": "P1401",
    "referencePublication": "P1343",
}

# Curated close-match candidates for CodeMeta terms that have no Wikidata twin (term -> PIDs).
# These are suggestions to document next to the new property, not mappings.
CANDIDATES = {
    "applicationCategory": "P31", "applicationSubCategory": "P921", "applicationSuite": "P361",
    "targetProduct": "P1547", "developmentStatus": "P548", "hasSourceCode": "P527",
    "isSourceCodeOf": "P361", "funding": "P8324", "copyrightHolder": "P123",
    "description": "(native Wikibase description field)", "installUrl": "P4945", "readme": "P973",
}
