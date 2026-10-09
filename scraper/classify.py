"""Keyword-based classification.

Three independent questions are answered for every posting:

1. kind        - what sort of position is it?  internship | graduate | phd | research | junior
                 (None means "not an early-career position" and the posting is dropped)
2. topics      - devops / cloud / telco / green / ml / research (or "other")
3. eligibility - can somebody who has ALREADY GRADUATED apply?  (extra-curricular internship)
                 "graduates" | "students" (enrolment required) | "unknown"

Philosophy kept from the original tracker: recall over precision for kinds and topics
(better a false positive than a missed posting). Eligibility is a hint with the matched
phrase stored next to it, so it can always be checked by hand.
"""
import re

CLASSIFIER_VERSION = 4   # bump to force re-classification of cached postings


def _rx(patterns):
    return re.compile("|".join(f"(?:{p})" for p in patterns), re.I)


# ---------------------------------------------------------------------------
# 1. Kind of position
# ---------------------------------------------------------------------------

# Never early career / not reachable with a master's degree.
EXCLUDE = _rx([
    r"\bpost-?doc", r"post-?doctoral", r"\bprofessor", r"\blecturer\b", r"\bsenior\b", r"\bsr\.?\s",
    r"\bstaff\b", r"\bprincipal\b", r"\bdirector\b", r"\bhead of\b", r"\bvp\b", r"\bchief\b",
    r"\bmanager\b(?!.*\b(intern|trainee|graduate)\b)", r"\blead\b(?!.*\b(intern|trainee)\b)",
    r"\bassistant professor", r"\btenure", r"\bfaculty\b", r"\bhabilitation",
])

KIND_PATTERNS = [
    # order matters: first match wins
    ("phd", [
        r"\bph\.?\s?d\.?\s*(position|student|candidate|studentship|scholarship|fellowship|thesis|project|"
        r"opportunit|researcher|vacanc|offer|programme|program|grant|in\b|on\b)",
        r"\bfully[- ]funded ph\.?d", r"\bph\.?d\b\s*[-:–]", r"^ph\.?d\b",
        r"\bdoctoral (student|candidate|researcher|position|fellow|programme|program|network|school|thesis|scholarship)",
        r"\bdoctorant", r"\bdoctorat\b", r"\bth[eè]se\b(?!.*\bstage\b)", r"\bcifre\b",
        r"\bdottorat", r"\bdottorando", r"\bpromovend", r"\bpromotieplaats", r"\bdoktorand", r"\bpromotionsstelle",
        r"\bdoctorado\b", r"\bdoutoramento\b", r"\bearly[- ]stage researcher", r"\b(esr|dc)\s?\d+\b",
        r"\bmsca\b", r"\bmarie (sk[lł]odowska-)?curie", r"\bdoctoral network",
    ]),
    ("internship", [
        r"\bintern(ship|ships|s)?\b", r"\bco-?op\b", r"\bplacement\b", r"\bsummer (student|analyst|associate|engineer|research)",
        r"(?<!ph\.d )(?<!phd )(?<!doctoral )\bstudent\b", r"\bworking student\b", r"\bwerkstudent", r"\bpraktik", r"\bpraktyk", r"\bstagiaire\b",
        r"\bstage\b", r"\bstages\b", r"\btirocin", r"\bstagista\b", r"\bstagi(air|o)", r"\bpr[aá]cticas\b", r"\bbecari",
        r"\best[aá]gio\b", r"\bstageplaats\b", r"\bafstudeer", r"\bthesis\b", r"\bmaster'?s? (thesis|project)",
        r"\bapprenti", r"\balternan(ce|t)\b", r"\bresidency\b", r"\bfellowship\b", r"\bsummer of code\b",
        r"\bmentee\b", r"\bmentorship\b",
    ]),
    ("graduate", [
        r"\bgraduate (programme|program|scheme|trainee|engineer|developer|role|position|opportunit)",
        r"\bnew grad", r"\brecent grad", r"\byoung graduate", r"\bgraduate trainee",
        r"\btrainee(ship)?s?\b", r"\bearly[- ]careers?\b", r"(?-i:\bV\.?\s?I\.?\s?E\b)", r"\bvolontariat international",
        r"\bjeunes? dipl[oô]m", r"\bneo-?laureat", r"\babsolvent", r"\bberufseinsteiger", r"\bdirect[- ]einstieg",
        r"\btalent (programme|program)", r"\brotational (programme|program)", r"\bstarter\b",
        r"\bgraduate\b",
    ]),
    ("research", [
        r"\bresearch (engineer|assistant|associate|software engineer|developer|scientist i\b)",
        r"\bjunior (researcher|research)", r"\bpre-?doc", r"\bing[ée]nieur(e)? (de recherche|d'[ée]tudes|r&d|recherche)",
        r"\bwissenschaftlich", r"\bassegn[oi] di ricerca", r"\bborsa di (studio|ricerca)", r"\bborsist",
        r"\bresearch fellow\b", r"\bscientific (assistant|trainee)", r"\br1\b", r"\bfirst stage researcher",
    ]),
    ("junior", [
        r"\bjunior\b", r"\bentry[- ]level\b", r"\bjr\.?\b", r"\bassociate (software|cloud|devops|network|site|platform|systems|data)",
        r"\b(engineer|developer) i\b",
    ]),
]
_KINDS = [(k, _rx(p)) for k, p in KIND_PATTERNS]


def kind_of(title: str, extra: str = "", hint: str | None = None) -> str | None:
    """Return the kind of early-career position, or None if it is not one."""
    text = f"{title} {extra}"
    if EXCLUDE.search(title or ""):
        # an excluded word in the title only loses if nothing early-career is in the title itself
        if not re.search(r"\b(intern|trainee|graduate|stage|ph\.?d|doctora|tirocin|praktik)", title or "", re.I):
            return None
    if re.search(r"\bintern(ship)?s?\b", title or "", re.I):
        return "internship"   # "PhD Intern", "Graduate Intern": internships for students, not PhD/graduate posts
    for kind, rx in _KINDS:
        if rx.search(text):
            return kind
    return hint


# ---------------------------------------------------------------------------
# 2. Topics
# ---------------------------------------------------------------------------

TOPIC_PATTERNS = {
    "devops": [
        r"devops", r"dev ops", r"\bsre\b", r"site reliability", r"\bci ?/ ?cd\b", r"\bci-cd\b",
        r"continuous (integration|delivery|deployment)", r"platform engineer", r"infrastructure as code", r"\biac\b",
        r"terraform", r"ansible", r"gitops", r"argo ?cd", r"release engineer", r"build (engineer|system)",
        r"observability", r"\bmlops\b", r"\bpipeline", r"automation engineer", r"reliability engineer",
        r"production engineer", r"\bjenkins\b", r"github actions", r"gitlab ci",
    ],
    "cloud": [
        r"\bcloud", r"kubernetes", r"\bk8s\b", r"container", r"docker", r"serverless", r"\bfaas\b",
        r"\baws\b", r"azure", r"\bgcp\b", r"openstack", r"infrastructure", r"\binfra\b", r"data ?cent(er|re)",
        r"virtuali[sz]", r"\bhpc\b", r"high[- ]performance computing", r"\bstorage\b", r"distributed (system|computing)",
        r"edge (computing|cloud|ai|devices?|nodes?)", r"\bfog computing", r"microservice", r"orchestrat", r"\blinux\b", r"systems engineer",
        r"\bwasm\b", r"webassembly", r"compute (platform|infrastructure)",
    ],
    "telco": [
        r"telco", r"telecom", r"t[ée]l[ée]com", r"telecomunicazion", r"\b[2-6]g\b", r"\blte\b", r"(?-i:\bRAN\b)", r"o-?ran\b",
        r"open ran", r"wireless", r"\bradio", r"(?<!neural )(?<!social )(?<!graph )\bnetworks?\b", r"networking",
        r"r[ée]seaux?\b", r"\bsdn\b", r"\bnfv\b", r"\bmec\b", r"core network", r"mobile network", r"spectrum",
        r"antenna", r"satellite", r"\biot\b", r"internet of things", r"backscatter", r"mm-?wave", r"\b3gpp\b",
        r"signal processing", r"optical", r"\bfib(er|re)\b", r"\bwi-?fi\b", r"\bbaseband", r"\brf\b", r"\bnetzwerk",
        r"\bmobilfunk", r"\breti\b",
    ],
    "green": [
        r"sustainab", r"\bgreen\b", r"energy", r"[ée]nergi", r"carbon", r"climat", r"emission", r"low[- ]power",
        r"power[- ]efficien", r"power consumption", r"renewable", r"environment(al)?\b", r"net[- ]zero",
        r"decarboni", r"durabilit", r"d[ée]veloppement durable", r"sostenib", r"risparmio energetico", r"\beco[- ](design|friendly|conception|responsible)", r"\becolog",
        r"frugal", r"smart grid", r"\bgrid\b", r"\bwatt", r"nachhaltig", r"duurzaam", r"\blca\b", r"life[- ]cycle assessment",
    ],
    "ml": [
        r"\bai\b", r"\bml\b", r"machine learning", r"deep learning", r"\bllms?\b", r"language model", r"data scien",
        r"neural", r"computer vision", r"\bnlp\b", r"reinforcement learning", r"generative", r"\bgenai\b",
        r"intelligence artificielle", r"intelligenza artificiale", r"k[üu]nstliche intelligenz", r"federated learning",
        r"\bia\b", r"artificial intelligence",
    ],
    "research": [
        r"research", r"scientist", r"ph\.?d", r"doctora", r"\blabs?\b", r"r&d", r"thesis", r"th[eè]se", r"recherche",
        r"ricerca", r"forschung", r"investigaci", r"academic",
    ],
}
_TOPICS = {k: _rx(v) for k, v in TOPIC_PATTERNS.items()}
_TOPIC_ORDER = ["devops", "cloud", "telco", "green", "ml", "research"]
# Sources with require_topic=True keep only postings matching one of these.
# Add "ml" here to also keep pure machine-learning postings from big boards (Inria, Bosch, portals...).
CORE_TOPICS = {"devops", "cloud", "telco", "green"}


def topics_of(text: str) -> list[str]:
    tags = [t for t in _TOPIC_ORDER if _TOPICS[t].search(text or "")]
    return tags or ["other"]


# Descriptions are full of boilerplate ("our cloud platform", "sustainable future", "global network"...),
# so description-only topics use specific technical terms and need >= 2 different ones.
DESC_PATTERNS = {
    "devops": [r"devops", r"\bsre\b", r"site reliability", r"\bci ?/ ?cd\b", r"terraform", r"ansible", r"gitops",
               r"argo ?cd", r"\bjenkins\b", r"github actions", r"gitlab ci", r"infrastructure as code", r"\bhelm\b",
               r"prometheus", r"observability", r"\bpuppet\b", r"\bchef\b"],
    "cloud": [r"kubernetes", r"\bk8s\b", r"\bdocker\b", r"containeri[sz]", r"container (orchestration|runtime|platform)",
              r"serverless", r"openstack", r"\baws\b", r"\bazure\b", r"\bgcp\b", r"microservices?", r"distributed systems?",
              r"edge computing", r"virtuali[sz]ation", r"\bhpc\b", r"cloud[- ]native", r"\bcncf\b"],
    "telco": [r"\b5g\b", r"\b6g\b", r"\blte\b", r"o-?ran\b", r"open ran", r"\b3gpp\b", r"(?-i:\bRAN\b)", r"\bsdn\b",
              r"\bnfv\b", r"core network", r"mm-?wave", r"baseband", r"telecommunications?", r"wireless communication",
              r"radio access", r"\bmec\b"],
    "green": [r"energy[- ]efficien", r"energy consumption", r"power consumption", r"carbon footprint", r"carbon emission",
              r"green (computing|software|it|ai)", r"sustainable (computing|software|it)", r"energy[- ]aware", r"low[- ]power",
              r"decarboni", r"life[- ]cycle assessment", r"\blca\b", r"renewable energ"],
    "ml": [r"machine learning", r"deep learning", r"pytorch", r"tensorflow", r"\bllms?\b", r"neural networks?",
           r"computer vision", r"\bnlp\b", r"reinforcement learning", r"large language model"],
}
_DESC = {k: [re.compile(p, re.I) for p in v] for k, v in DESC_PATTERNS.items()}


def desc_topics(desc: str, already: list[str]) -> list[str]:
    """Topics found only in the description (>= 2 different specific terms)."""
    out = []
    for t in _TOPIC_ORDER:
        if t in already or t not in _DESC:
            continue
        if sum(1 for rx in _DESC[t] if rx.search(desc or "")) >= 2:
            out.append(t)
    return out


# ---------------------------------------------------------------------------
# 3. Eligibility for people who already graduated (extra-curricular)
# ---------------------------------------------------------------------------

# Explicitly open to graduates.
GRAD_STRONG = _rx([
    r"recent(ly)?[- ]graduat", r"\bnew grad", r"graduated (with)?in the (last|past)", r"within \w+ (months|years?) (of|after|from) (your )?graduat",
    r"(or|and) (have )?(recently )?(graduated|completed (your|a|their) (degree|studies|master))",
    r"\bor (a )?recent graduate", r"post-?graduate internship", r"graduate (programme|program|scheme)",
    r"young graduate", r"graduate trainee", r"\btraineeship", r"tirocini[oi]? extra-?curricular", r"extra-?curricular",
    r"neo-?laureat", r"jeunes? dipl[oô]m", r"(?-i:\bV\.?\s?I\.?\s?E\b)", r"volontariat international",
    r"freiwillige[sn]? praktikum", r"\bnach (dem|deinem|ihrem|abgeschlossenem) (studium|abschluss)", r"\babsolvent",
    r"berufseinsteiger", r"net afgestudeerd", r"reci[eé]n (titulad|graduad|egresad)", r"rec[eé]m-?(licenciad|formad|graduad)",
    r"no longer (a )?(enrolled )?student", r"not (be )?(currently )?enrolled", r"do not need to be (enrolled|a student)",
    r"open to (students and )?(recent )?graduates", r"graduates (are )?(welcome|eligible)",
    r"\bfirst job\b", r"no more than (one|1|two|2) years? of (professional )?experience",
])

# Clearly requires being enrolled somewhere (curricular internship).
STUDENT_ONLY = _rx([
    r"currently (enrolled|pursuing|studying|attending|registered)", r"must be (a )?(current(ly)? )?(enrolled|pursuing|registered|student)",
    r"(be|are) enrolled (in|at)", r"enrolled (in|at) (a|an) (accredited )?(university|college|bachelor|master|degree|program|higher)",
    r"returning to (school|university|college|your (studies|degree|program))", r"return to (school|university|your studies)",
    r"(at least )?one (more )?(semester|term|quarter|year) (of (study|school) )?remaining", r"remaining (semester|term)s? (of|in)",
    r"(expected )?graduation (date )?(in|between|after|no earlier than|from)\b.{0,25}20(2[7-9]|3\d)",
    r"graduating (in|between|after)\b.{0,20}20(2[7-9]|3\d)", r"class of 20(2[7-9])",
    r"student status", r"enrolment certificate", r"proof of enrol?lment", r"current student",
    r"convention de stage", r"convention tripartite", r"stage de fin d'[ée]tudes", r"\bstage de (m1|m2|master|l3|bac)",
    r"en cours de (formation|cursus|scolarit|master|dipl[oô]me)", r"[ée]tudiant(e)?s? en (derni[eè]re ann[ée]e|master|[ée]cole|m1|m2|bac)",
    r"pflichtpraktikum", r"immatrikul", r"eingeschrieben", r"werkstudent", r"working student",
    r"\balternance\b", r"\bapprentissage\b", r"contrat d'apprentissage", r"\bapprenticeship",
    r"tirocinio curriculare", r"iscritt[oaie] (a|al|ad|presso|ad un)", r"stageovereenkomst", r"ingeschreven",
    r"convenio de pr[aá]cticas", r"matriculad[oa]", r"\bmaster'?s? thesis", r"\bthesis (student|work|project)",
    r"masterarbeit", r"abschlussarbeit", r"examensarbete", r"afstudeer", r"\btfm\b",
    r"ph\.?d\.? intern", r"(enrolled|registered) (in|as) a ph\.?d", r"currently a ph\.?d", r"current ph\.?d",
])

# Weak signal: asks for a degree that has already been obtained.
GRAD_WEAK = _rx([
    r"(hold|holding|have|completed|obtained|possess)(ing)? (a|an|your)? ?(master|msc|m\.sc|bachelor|degree|university degree)",
    r"master'?s? degree (is )?(required|in hand)", r"(master|msc|bachelor)'?s?( degree)? (completed|obtained)",
    r"titulaire d'un", r"dipl[oô]m[ée](e)? d'un", r"bac\s?\+\s?5 (obtenu|valid)", r"abgeschlossene[sn]? (studium|hochschulstudium|master)",
    r"laurea (magistrale )?(conseguita|in)", r"in possesso (di|della) laurea",
])

_FR_LOC = re.compile(r"\bfrance\b|paris|lyon|grenoble|sophia|rennes|lille|nantes|toulouse|marseille|nice|bordeaux|saclay|"
                     r"palaiseau|montpellier|strasbourg|\bfr\b", re.I)


def _snippet(m, text):
    a, b = max(0, m.start() - 50), min(len(text), m.end() + 50)
    return re.sub(r"\s+", " ", text[a:b]).strip()


def eligibility(kind: str, title: str, desc: str, location: str = "") -> tuple[str, str]:
    """Return (eligibility, reason). eligibility in {"graduates", "students", "unknown"}."""
    title = title or ""
    text = f"{title}\n{desc or ''}"
    m = GRAD_STRONG.search(text)
    if m:
        return "graduates", _snippet(m, text)
    m = STUDENT_ONLY.search(text)
    if m:
        return "students", _snippet(m, text)
    if kind in ("phd", "graduate", "research", "junior"):
        # PhD / graduate programmes / research-engineer posts / junior jobs never require enrolment.
        return "graduates", f"{kind} position"
    m = GRAD_WEAK.search(text)
    if m:
        return "graduates", _snippet(m, text)
    if kind == "internship" and re.search(r"\bstage\b|stagiaire", text, re.I) and _FR_LOC.search(f"{location} {title}"):
        return "students", "France: a 'stage' needs a convention de stage from a school"
    if kind == "internship" and not desc:
        return "unknown", "description not available"
    return "unknown", ""


# ---------------------------------------------------------------------------
# 4. Region (for the location filter)
# ---------------------------------------------------------------------------

COUNTRIES = {
    "Italy": r"\bital(y|ia)\b|milan|milano|rome\b|roma\b|turin|torino|bologna|pisa|naples|napoli|genova|genoa|padova|"
             r"trento|florence|firenze|ispra|catania|bari\b|cagliari",
    "France": r"\bfrance\b|paris|lyon|grenoble|sophia|rennes|lille|nantes|toulouse|marseille|\bnice\b|bordeaux|saclay|"
              r"palaiseau|montpellier|strasbourg|biot|lannion|massy|v[ée]lizy|nancy|m[ée]aulte|saint[- ]nazaire|"
              r"[ée]lancourt|brest\b|blagnac|cannes|marignane|valence|limours|gennevilliers|sophia|\bfra\b",
    "Belgium": r"belgi|brussel|bruxelles|leuven|ghent|gent\b|antwerp|li[eè]ge|louvain|mechelen|geel",
    "Netherlands": r"netherlands|nederland|holland|amsterdam|eindhoven|delft|rotterdam|utrecht|the hague|den haag|"
                   r"leiden|groningen|enschede|petten|nijmegen|hengelo|veldhoven|\bnld\b",
    "Portugal": r"portugal|lisbon|lisboa|porto\b|braga|coimbra|aveiro",
    "Spain": r"spain|espa[ñn]a|madrid|barcelona|valencia|seville|sevilla|bilbao|malaga|m[aá]laga",
    "Germany": r"german|deutschland|berlin|munich|m[üu]nchen|hamburg|frankfurt|stuttgart|cologne|k[öo]ln|"
               r"darmstadt|karlsruhe|dresden|aachen|n[üu]rnberg|nuremberg|d[üu]sseldorf|bonn|hannover|gerlingen|"
               r"renningen|reutlingen|ludwigsburg|bremen|ottobrunn|manching|immenstaad|\bdeu\b",
    "Switzerland": r"switzerland|schweiz|suisse|zurich|z[üu]rich|geneva|gen[eè]ve|lausanne|basel|bern\b",
    "Austria": r"austria|[öo]sterreich|vienna|wien|graz|linz|innsbruck",
    "Ireland": r"ireland|dublin|cork|galway|limerick",
    "United Kingdom": r"united kingdom|\buk\b|england|scotland|wales|london|cambridge, uk|oxford|manchester|edinburgh|"
                      r"bristol|glasgow|reading|belfast|crawley|cheadle|broughton|templecombe|filton|stevenage|"
                      r"portsmouth|basingstoke|guildford|bracknell|newport|stockport|swindon|\bgbr\b",
    "Nordics": r"sweden|stockholm|gothenburg|g[öo]teborg|lund|link[öo]ping|kista|finland|helsinki|espoo|tampere|oulu|"
               r"denmark|copenhagen|aarhus|norway|oslo|trondheim|iceland",
    "Central/Eastern Europe": r"poland|warsaw|krak[oó]w|wroc[lł]aw|gda[nń]sk|czech|prague|praha|brno|slovakia|bratislava|"
                              r"hungary|budapest|romania|bucharest|cluj|bulgaria|sofia|greece|athens|croatia|zagreb|"
                              r"slovenia|ljubljana|serbia|belgrade|estonia|tallinn|latvia|riga|lithuania|vilnius|luxembourg|"
                              r"ukraine|kyiv|blaj|timi[sș]oara|ia[sș]i\b",
}
_COUNTRY_RX = [(c, re.compile(p, re.I)) for c, p in COUNTRIES.items()]
_CODES = {"IT": "Italy", "LU": "Central/Eastern Europe", "HU": "Central/Eastern Europe", "SK": "Central/Eastern Europe",
          "BG": "Central/Eastern Europe", "HR": "Central/Eastern Europe", "SI": "Central/Eastern Europe", "UA": "Central/Eastern Europe", "FR": "France", "BE": "Belgium", "NL": "Netherlands", "PT": "Portugal", "ES": "Spain",
          "DE": "Germany", "CH": "Switzerland", "AT": "Austria", "IE": "Ireland", "GB": "United Kingdom",
          "SE": "Nordics", "FI": "Nordics", "DK": "Nordics", "NO": "Nordics", "PL": "Central/Eastern Europe",
          "CZ": "Central/Eastern Europe", "RO": "Central/Eastern Europe", "GR": "Central/Eastern Europe"}
_CODE_RX = re.compile(r"(?:^|[\s,(/-])(" + "|".join(_CODES) + r")(?=$|[\s,)/-])")
# lowercase ISO codes at the end ("Gerlingen, de" - SmartRecruiters) and other countries' codes
_TAIL_CODE = re.compile(r",\s*([a-z]{2})\s*$")
_NON_EU_CODES = re.compile(r"(?:^|[\s,(])(US|USA|CA|IN|CN|JP|SG|SGP|IL|BR|MX|AU|KR|TW|VN|PH|MY|ID|TH|AE|SA|ZA|AR|CL|CO|NZ|CR|PR|EG|MA|TN)(?=$|[\s,)])")
_REMOTE = re.compile(r"remote|anywhere|telework|work from home|distributed|home[- ]?based|t[ée]l[ée]travail", re.I)
_EUROPE_GENERIC = re.compile(r"europe|\bemea\b|\beu\b", re.I)
_NON_EU = re.compile(r"\b(usa|united states|canada|india|china|japan|singapore|israel|brazil|mexico|australia|korea|"
                     r"costa rica|puerto rico|ottawa|kanata|atlanta|chicago|redwood city|ashburn|englewood|santa clara|"
                     r"san jose|hillsboro|silicon valley|yorktown|research triangle|raleigh|tucson|baton rouge|"
                     r"poughkeepsie|maynard|denver|dallas|houston|phoenix|portland|san diego|los angeles|"
                     r"pittsburgh|minneapolis|detroit|ann arbor|madison|columbus|nashville|charlotte|miami|"
                     r"taiwan|vietnam|philippines|egypt|turkey|t[üu]rkiye|uae|dubai|saudi|south africa|argentina|chile|"
                     r"colombia|malaysia|indonesia|thailand|pakistan|nigeria|kenya|morocco|tunisia|new zealand)\b|"
                     r"san francisco|new york|seattle|austin|boston|bangalore|bengaluru|hyderabad|pune|chennai|beijing|"
                     r"shanghai|shenzhen|tokyo|tel aviv|toronto|montreal|vancouver|sydney|s[ãa]o paulo|"
                     r",\s?(AL|AK|AZ|CA|CO|CT|DC|FL|GA|IL|IN|MA|MD|MI|MN|MO|NC|NJ|NY|OH|OR|PA|TX|UT|VA|WA|WI)\b", re.I)


def region_of(location: str) -> tuple[str, str]:
    """Return (region, country). region in {"europe", "remote", "other", ""}."""
    loc = location or ""
    if not loc.strip():
        return "", ""
    for country, rx in _COUNTRY_RX:
        if rx.search(loc):
            return ("remote" if _REMOTE.search(loc) else "europe"), country
    if _NON_EU.search(loc) or _NON_EU_CODES.search(loc):
        return "other", ""
    m = _TAIL_CODE.search(loc)
    if m and m.group(1).upper() in _CODES:
        return ("remote" if _REMOTE.search(loc) else "europe"), _CODES[m.group(1).upper()]
    if m:
        return "other", ""
    m = _CODE_RX.search(loc)
    if m:
        return ("remote" if _REMOTE.search(loc) else "europe"), _CODES[m.group(1)]
    if _REMOTE.search(loc):
        return "remote", ""
    if _EUROPE_GENERIC.search(loc):
        return "europe", ""
    if _NON_EU.search(loc):
        return "other", ""
    return "", ""
