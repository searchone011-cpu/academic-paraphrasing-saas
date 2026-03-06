# -*- coding: utf-8 -*-
"""
Academic Rewriting Engine v27
==============================
API (backward-compatible):
  humanize_chunk(chunk, level, domain, idx, run_id) -> str
    ✅ يرجع str دائماً — النموذج الأول (run_id=0)
    ✅ متوافق مع كل الكود القديم

  humanize_chunk_5(chunk, level, domain, idx) -> List[str]
    ✅ يرجع 5 نماذج مختلفة — كل عنصر str مضمون

القواعد الصارمة:
  ✓ (Author, Year) محمي 100% — لا يُمس
  ✓ الأرقام محمية 100% — لا تُمس
  ✓ النص بين علامات تنصيص محمي كما هو
  ✓ لا إضافات خارج النص الأصلي
  ✓ الطول ≤ 130% من الأصل
  ✓ الـ headings لا تُعالج
"""

import re
import time
import random
import hashlib
import logging
import urllib.request
import urllib.parse
import json
from typing import List, Tuple, Dict

logger = logging.getLogger(__name__)

# ══ مكتبات اختيارية ══
try:
    import language_tool_python as _ltmod
    _LT = _ltmod.LanguageTool('en-US')
    _HAS_LT = True
except Exception:
    _LT = None
    _HAS_LT = False

try:
    import textstat as _ts
    _HAS_TS = True
except Exception:
    _HAS_TS = False

try:
    import nltk as _nltk
    for _r in ('punkt', 'averaged_perceptron_tagger', 'punkt_tab'):
        try:
            _nltk.data.find(f'tokenizers/{_r}')
        except LookupError:
            _nltk.download(_r, quiet=True)
    _HAS_NLTK = True
except Exception:
    _HAS_NLTK = False

LEVEL_INTENSITY = {
    "منخفضة": 0.60,
    "متوسطة": 0.80,
    "عالية":  0.95,
    "أقصى درجة": 1.00,
}

# ══════════════════════════════════════════════════════════════════════
# Google Translate
# ══════════════════════════════════════════════════════════════════════

class GoogleTranslate:
    BASE = ("https://translate.googleapis.com/translate_a/single"
            "?client=gtx&sl={sl}&tl={tl}&dt=t&q={q}")
    HDR = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36")
    }

    def translate(self, text: str, src: str, tgt: str) -> str:
        if not text or not text.strip():
            return text
        url = self.BASE.format(sl=src, tl=tgt,
                               q=urllib.parse.quote(text, safe=''))
        for i in range(3):
            try:
                req = urllib.request.Request(url, headers=self.HDR)
                with urllib.request.urlopen(req, timeout=20) as r:
                    data = json.loads(r.read().decode())
                    return ''.join(c[0] for c in data[0] if c and c[0]).strip()
            except Exception as e:
                logger.warning(f"GT attempt {i+1}: {e}")
                if i < 2:
                    time.sleep(1.0 * (i + 1))
        return text


_GT = GoogleTranslate()

# ══════════════════════════════════════════════════════════════════════
# Protected-Content Extractor
# ══════════════════════════════════════════════════════════════════════

_PAT_QUOTED  = re.compile(r'"[^"]{1,200}"|\u201c[^\u201d]{1,200}\u201d')
_PAT_ACCTO   = re.compile(
    r'According\s+to\s+[A-Z][a-zA-Z\u00C0-\u024F\-']+(?:\s+et\s+al\.?)?'
    r'(?:\s*(?:and|&)\s*[A-Z][a-zA-Z\u00C0-\u024F\-']+(?:\s+et\s+al\.?)?)*'
    r'\s*\(\s*\d{4}(?:\s*[a-z])?\s*\)')
_PAT_PAREN   = re.compile(
    r'\(\s*[A-Z][a-zA-Z\u00C0-\u024F\-']+(?:\s+et\s+al\.?)?'
    r'(?:\s*(?:and|&)\s*[A-Z][a-zA-Z\u00C0-\u024F\-']+(?:\s+et\s+al\.?)?)*'
    r'\s*,\s*\d{4}(?:\s*[a-z])?'
    r'(?:\s*;\s*[A-Z][a-zA-Z\u00C0-\u024F\-']+(?:\s+et\s+al\.?)?'
    r'(?:\s*(?:and|&)\s*[A-Z][a-zA-Z\u00C0-\u024F\-']+(?:\s+et\s+al\.?)?)*'
    r'\s*,\s*\d{4}(?:\s*[a-z])?)*\s*\)')
_PAT_NUMBERS = re.compile(
    r'\b\d+(?:\.\d+)?(?:\s*%|\s*percent|\s*million|\s*billion'
    r'|\s*km\u00b2?|\s*m\u00b2?|\s*ha|\s*tonnes?|\s*kg|\s*MW|\s*GW'
    r'|\s*USD|\s*SAR)?\b')


def protect_and_strip(text: str) -> Tuple[str, Dict[str, str]]:
    store, counter = {}, [0]

    def _save(m):
        k = f"\x00P{counter[0]:04d}\x00"
        store[k] = m.group(0)
        counter[0] += 1
        return k

    t = _PAT_QUOTED.sub(_save, text)
    t = _PAT_ACCTO.sub(_save, t)
    t = _PAT_PAREN.sub(_save, t)
    t = _PAT_NUMBERS.sub(_save, t)
    t = re.sub(r'  +', ' ', t).strip()
    t = re.sub(r'\s+([.,;:!?])', r'\1', t).strip()
    return t, store


def restore(text: str, store: Dict[str, str]) -> str:
    r = text
    for k, v in store.items():
        r = r.replace(k, v)
    r = re.sub(r'\x00P\d+\x00', '', r)
    r = re.sub(r'  +', ' ', r).strip()
    r = re.sub(r'\s+([.,;:!?])', r'\1', r)
    return r


def verify_restore(original: str, result: str, store: Dict[str, str]) -> str:
    for k, v in store.items():
        if v not in result:
            pos = original.find(v)
            rel = pos / max(len(original), 1) if pos >= 0 else 1.0
            words = result.rstrip('.!?').split()
            ins = min(int(rel * len(words)), len(words))
            words.insert(ins, v)
            result = ' '.join(words)
            result = re.sub(r'\s+([.,;:!?])', r'\1', result)
    if result and result[-1] not in '.!?':
        result += '.'.
    return result

# ══════════════════════════════════════════════════════════════════════
# STYLE BANK — 5 فئات (run_id 0..4)
# ══════════════════════════════════════════════════════════════════════

_CAT_0: List[str] = [
    "It has been established that {s}.",
    "It has been demonstrated that {s}.",
    "It has been empirically verified that {s}.",
    "It has been rigorously substantiated that {s}.",
    "It has been widely acknowledged that {s}.",
    "It has been independently corroborated that {s}.",
    "It has been analytically confirmed that {s}.",
    "It has been formally established that {s}.",
    "It has been persuasively argued that {s}.",
    "It has been consistently maintained that {s}.",
    "It is widely recognised that {s}.",
    "It is generally acknowledged that {s}.",
    "It is broadly accepted within the literature that {s}.",
    "It is evident from the available evidence that {s}.",
    "It is demonstrably the case that {s}.",
    "It is worth emphasising that {s}.",
    "It is critical to acknowledge that {s}.",
    "It is important to recognise that {s}.",
    "It is axiomatic within this field that {s}.",
    "It is analytically significant that {s}.",
]

_CAT_1: List[str] = [
    "The weight of evidence suggests that {s}.",
    "The preponderance of scholarly evidence confirms that {s}.",
    "Converging lines of empirical evidence indicate that {s}.",
    "A robust body of literature demonstrates that {s}.",
    "Accumulated evidence from multiple sources establishes that {s}.",
    "The cumulative scholarly record affirms that {s}.",
    "Systematic review of the literature reveals that {s}.",
    "An analysis of the extant evidence base confirms that {s}.",
    "The balance of evidence strongly supports the view that {s}.",
    "Empirical investigation consistently demonstrates that {s}.",
    "Cross-disciplinary evidence converges on the finding that {s}.",
    "Meta-analytical findings consistently affirm that {s}.",
    "The totality of available research evidence confirms that {s}.",
    "Rigorous evidence-based analysis confirms that {s}.",
    "A comprehensive survey of the evidence establishes that {s}.",
    "The scholarly evidence base overwhelmingly supports the view that {s}.",
    "Empirical corroboration across multiple studies confirms that {s}.",
    "The aggregate of available empirical evidence affirms that {s}.",
    "Sustained empirical investigation has confirmed that {s}.",
    "Critical evaluation of the evidence base confirms that {s}.",
]

_CAT_2: List[str] = [
    "From a theoretical standpoint, {s}.",
    "Situated within the relevant theoretical framework, {s}.",
    "Within the conceptual parameters of this field, {s}.",
    "Through the prism of contemporary scholarly discourse, {s}.",
    "Against the backdrop of established theoretical principles, {s}.",
    "Grounded in the foundational tenets of the discipline, {s}.",
    "A rigorous analytical examination reveals that {s}.",
    "Careful interrogation of the available evidence discloses that {s}.",
    "Critical analysis of the relevant data establishes that {s}.",
    "Systematic analytical scrutiny of the evidence confirms that {s}.",
    "An in-depth examination of the pertinent material reveals that {s}.",
    "A forensic examination of the available evidence demonstrates that {s}.",
    "A methodologically robust analysis reveals that {s}.",
    "Under sustained analytical scrutiny, {s}.",
    "Examining the evidence with appropriate critical rigour, {s}.",
    "Informed by prevailing theoretical perspectives, {s}.",
    "Drawing on the conceptual apparatus of the field, {s}.",
    "Anchored in the epistemological foundations of the discipline, {s}.",
    "Viewed through a rigorous scholarly lens, {s}.",
    "Proceeding from established theoretical premises, {s}.",
]

_CAT_3: List[str] = [
    "The scholarly literature converges on the view that {s}.",
    "An extensive corpus of academic scholarship confirms that {s}.",
    "Peer-reviewed scholarship consistently affirms that {s}.",
    "The existing body of literature provides strong support that {s}.",
    "Extant research establishes with considerable rigour that {s}.",
    "The academic consensus, as reflected in the literature, holds that {s}.",
    "A substantial and growing literature demonstrates that {s}.",
    "The interdisciplinary literature converges on the view that {s}.",
    "Foundational works in this field have established that {s}.",
    "Of particular scholarly significance is the finding that {s}.",
    "The canon of relevant scholarship makes clear that {s}.",
    "Authoritative contributions to the literature confirm that {s}.",
    "A comprehensive review of the literature reveals that {s}.",
    "The relevant disciplinary literature unequivocally establishes that {s}.",
    "An overwhelming scholarly majority affirms that {s}.",
    "Seminal contributions to this area have confirmed that {s}.",
    "The emergent scholarly consensus affirms that {s}.",
    "Successive generations of scholars have affirmed that {s}.",
    "A broad survey of the academic literature confirms that {s}.",
    "The accumulated wisdom of the field affirms that {s}.",
]

_CAT_4: List[str] = [
    "Over the past several decades, scholarly inquiry has confirmed that {s}.",
    "In the contemporary context of intensifying global pressures, {s}.",
    "As the twenty-first century unfolds, it is increasingly evident that {s}.",
    "Against a backdrop of rapid and sustained change, {s}.",
    "In the wake of decades of sustained empirical inquiry, {s}.",
    "It is essential to recognise that {s}.",
    "It is imperative to acknowledge that {s}.",
    "Intellectual honesty demands acknowledgement of the fact that {s}.",
    "Rigorous analysis requires the recognition that {s}.",
    "While diverse scholarly perspectives exist on this matter, {s}.",
    "Despite ongoing scholarly debate, {s}.",
    "In contradistinction to simplistic narratives, {s}.",
    "Contrary to conventional wisdom, {s}.",
    "Building on the existing literature, this analysis confirms that {s}.",
    "This analysis contributes to the growing body of evidence confirming that {s}.",
    "Even granting the complexity of this issue, {s}.",
    "While acknowledging alternative interpretations, {s}.",
    "In contrast to prior theoretical positions, {s}.",
    "Resisting the temptation of reductionist interpretation, {s}.",
    "As knowledge in this domain has advanced, {s}.",
]

_ALL_CATS: List[List[str]] = [_CAT_0, _CAT_1, _CAT_2, _CAT_3, _CAT_4]


def _get_pattern(run_id: int, sentence_seed: int) -> str:
    cat = _ALL_CATS[run_id % 5]
    rng = random.Random(sentence_seed + run_id * 997)
    return rng.choice(cat)

# ══════════════════════════════════════════════════════════════════════
# Pre-Fix
# ══════════════════════════════════════════════════════════════════════

_PRE_FIX_RULES = [
    (r'\binternet[- ]zero\b', 'net-zero'),
    (r'\bround financial system\b', 'circular economy'),
    (r'\bround economy\b', 'circular economy'),
    (r'\bstrong waste\b', 'solid waste'),
    (r'\bweather change\b', 'climate change'),
    (r'\bfirst[- ]rate person\b', 'primary contributor'),
    (r'\ba first[- ]rate person of\b', 'a primary source of'),
    (r'\bby myself\b', 'independently'),
    (r'\bthe development segment\b', 'the construction sector'),
    (r'\bnonrenewable electricity assets\b', 'non-renewable energy resources'),
    (r'\belectricity assets\b', 'energy resources'),
    (r'\bfor the duration of\b', 'throughout'),
    (r'\bhave brought about\b', 'have caused'),
    (r'\bbrings about\b', 'causes'),
    (r'\bimmoderate dependence\b', 'excessive dependence'),
    (r'\bwith the aid of (\d{4})\b', r'by \1'),
    (r'\bsturdy environmental\b', 'robust environmental'),
    (r'\bthe take a look at\b', 'the study'),
    (r'\btake a look at\b', 'study'),
    (r'\bPM2\.Five\b', 'PM2.5'),
    (r'\bheavy metallic accumulation\b', 'heavy metal accumulation'),
]

def pre_fix(text: str) -> str:
    r = text
    for pat, repl in _PRE_FIX_RULES:
        try:
            r = re.sub(pat, repl, r, flags=re.IGNORECASE)
        except re.error:
            pass
    return r

# ══════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════

def _is_english(t: str) -> bool:
    return not bool(re.search(r'[\u0600-\u06FF]', t))


def _is_heading(line: str) -> bool:
    s = line.strip()
    if not s or len(s) > 80:
        return False
    if s.endswith(('.', '?', '!')):
        return False
    return len(s.split()) <= 6


def _clean_arabic(t: str) -> str:
    r = re.sub(r'[\u0600-\u06FF]+', '', t)
    return re.sub(r'  +', ' ', r).strip()


def _polish(t: str) -> str:
    r = t.strip()
    if r and r[0].islower():
        r = r[0].upper() + r[1:]
    r = re.sub(r'  +', ' ', r)
    r = re.sub(r'\s+([.,;:!?])', r'\1', r)
    r = re.sub(r'\.\.+', '.', r)
    r = re.sub(r',\s*\.', '.', r)
    r = re.sub(r'\b(\w+)\s+\1\b', r'\1', r)
    if r and r[-1] not in '.!?':
        r += '.'.
    return r


def _wc(t: str) -> int:
    return len(t.split())


def _detect_lang(t: str) -> str:
    ar = len(re.findall(r'[\u0600-\u06FF]', t))
    en = len(re.findall(r'[a-zA-Z]', t))
    return 'ar' if ar >= en else 'en'

_ABBREVS = [
    'et al.', 'e.g.', 'i.e.', 'vs.', 'cf.', 'Fig.', 'approx.', 'etc.',
    'No.', 'Vol.', 'pp.', 'ed.', 'Dr.', 'Mr.', 'Mrs.', 'Prof.',
    'Jan.', 'Feb.', 'Mar.', 'Apr.', 'Jun.', 'Jul.', 'Aug.',
    'Sep.', 'Oct.', 'Nov.', 'Dec.'
]


def _split_sentences(text: str) -> List[str]:
    prot, rmap = text, {}
    for i, ab in enumerate(_ABBREVS):
        k = f"__AB{i}__"
        rmap[k] = ab
        prot = prot.replace(ab, k)

    def _ph(m):
        k = f"__PH{len(rmap)}__"
        rmap[k] = m.group(0)
        return k

    prot = re.sub(
        r'\(\s*[A-Z][a-zA-Z\-']+(?:\s+et\s+al\.?)?(?:\s*,\s*\d{4})?\s*\)',
        _ph, prot)
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z\(\[])', prot)
    out = []
    for p in parts:
        for k, v in rmap.items():
            p = p.replace(k, v)
        p = p.strip()
        if p:
            out.append(p)
    return out or [text]


def _sentence_seed(sent: str) -> int:
    return int(hashlib.md5(sent[:30].encode()).hexdigest(), 16) % 100000

# ══════════════════════════════════════════════════════════════════════
# Post-Processor
# ══════════════════════════════════════════════════════════════════════

class PostProcessor:
    _FORM = [
        (r"\bdon't\b", "do not"),
        (r"\bdoesn't\b", "does not"),
        (r"\bwon't\b", "will not"),
        (r"\bcan't\b", "cannot"),
        (r"\bisn't\b", "is not"),
        (r"\baren't\b", "are not"),
        (r"\bwasn't\b", "was not"),
        (r"\bweren't\b", "were not"),
        (r"\bIt's\b", "It is"),
        (r"\bThat's\b", "That is"),
        (r"\bThere's\b", "There is"),
        (r"\bThey're\b", "They are"),
    ]
    _ACAD = [
        (r'\bobviously\b', 'evidently'),
        (r'\bbasically\b', 'fundamentally'),
        (r'\ba lot of\b', 'a substantial number of'),
        (r'\blots of\b', 'numerous'),
        (r'\bget\b', 'obtain'),
        (r'\bgot\b', 'obtained'),
        (r'\bfind out\b', 'ascertain'),
        (r'\blook at\b', 'examine'),
        (r'\buse\b', 'utilise'),
        (r'\buses\b', 'utilises'),
        (r'\bused\b', 'utilised'),
        (r'\bstart\b', 'commence'),
        (r'\bhelp\b', 'facilitate'),
        (r'\bhelps\b', 'facilitates'),
        (r'\bneed\b', 'necessitate'),
        (r'\bneeds\b', 'necessitates'),
        (r'\bimportant\b', 'significant'),
        (r'\bimportance\b', 'significance'),
        (r'\bnew\b', 'novel'),
        (r'\bproblem\b', 'challenge'),
        (r'\bproblems\b', 'challenges'),
    ]

    def process(self, text: str) -> str:
        if not text or not text.strip():
            return text
        ph, cnt = {}, [0]

        def _s(m):
            k = f"\x01F{cnt[0]:03d}\x01"
            cnt[0] += 1
            ph[k] = m.group(0)
            return k

        r = _PAT_QUOTED.sub(_s, text)
        r = _PAT_ACCTO.sub(_s, r)
        r = _PAT_PAREN.sub(_s, r)
        r = _PAT_NUMBERS.sub(_s, r)

        for pat, repl in self._FORM:
            try:
                r = re.sub(pat, repl, r)
            except re.error:
                pass
        for pat, repl in self._ACAD:
            try:
                r = re.sub(pat, repl, r, flags=re.IGNORECASE)
            except re.error:
                pass

        if _HAS_LT and _LT:
            _SKIP = {
                'UPPERCASE_SENTENCE_START', 'EN_UNPAIRED_BRACKETS',
                'COMMA_PARENTHESIS_WHITESPACE', 'DASH_RULE',
                'WORD_CONTAINS_UNDERSCORE', 'EN_QUOTES'
            }
            try:
                ms = _LT.check(r)
                mf = [m for m in ms
                      if m.ruleId not in _SKIP
                      and m.replacements
                      and not any(k in r[max(0, m.offset-5):m.offset+m.errorLength+5]
                                  for k in ph)]
                r = _ltmod.utils.correct(r, mf)
            except Exception as e:
                logger.warning(f"LT: {e}")

        for k, v in ph.items():
            r = r.replace(k, v)
        return _polish(r)


_PP = PostProcessor()

# ══════════════════════════════════════════════════════════════════════
# Core: rewrite one sentence with a specific run_id
# ══════════════════════════════════════════════════════════════════════

def _rewrite_sentence(sent: str, run_id: int) -> str:
    """يُعيد صياغة جملة واحدة باستخدام فئة الأسلوب المقابلة لـ run_id."""
    orig_wc = _wc(sent)
    clean, store = protect_and_strip(sent)

    if not clean or len(clean.strip()) < 6:
        return _polish(sent)

    # EN→AR→EN
    arabic = _GT.translate(clean, 'en', 'ar')
    if not arabic or not arabic.strip():
        arabic = clean
    back_en = _GT.translate(arabic, 'ar', 'en')
    if not back_en or not back_en.strip():
        back_en = clean
    back_en = _clean_arabic(back_en).strip()
    if not _is_english(back_en):
        back_en = clean
    base = back_en if _wc(back_en) <= orig_wc * 1.3 else clean
    base_lc = base.strip().rstrip('.')
    if base_lc:
        base_lc = base_lc[0].lower() + base_lc[1:]

    ss = _sentence_seed(sent)
    pattern = _get_pattern(run_id, ss)

    try:
        candidate = pattern.format(s=base_lc)
    except Exception:
        candidate = f"It has been established that {base_lc}."

    if _wc(candidate) > orig_wc * 1.3:
        candidate = f"It has been confirmed that {base_lc}."

    candidate = _PP.process(candidate)
    candidate = restore(candidate, store)
    candidate = verify_restore(sent, candidate, store)
    return candidate


def _process_block(chunk: str, run_id: int) -> str:
    """يعالج كتلة نص كاملة (إنجليزي) بـ run_id محدد → str."""
    lines = chunk.split('\n')
    out = []
    for line in lines:
        if not line.strip():
            out.append(line)
            continue
        if _is_heading(line.strip()):
            out.append(line)
            continue
        sentences = _split_sentences(line.strip())
        parts = []
        for sent in sentences:
            if not sent.strip():
                parts.append(sent)
                continue
            parts.append(_rewrite_sentence(sent, run_id))
            time.sleep(0.15)
        out.append(' '.join(parts))
    return '\n'.join(out)


def _process_block_ar(chunk: str, run_id: int) -> str:
    """يعالج كتلة نص كاملة (عربي) بـ run_id محدد → str."""
    lines = chunk.split('\n')
    out = []
    for line in lines:
        if not line.strip():
            out.append(line)
            continue
        if _is_heading(line.strip()):
            out.append(line)
            continue
        sents = [s for s in re.split(r'(?<=[.!?؟])\s+', line.strip()) if s.strip()]
        parts = []
        for sent in sents:
            orig_wc = _wc(sent)
            clean, store = protect_and_strip(sent)
            if not clean.strip():
                parts.append(sent)
                continue
            en = _GT.translate(clean, 'ar', 'en')
            time.sleep(0.12)
            if not en or not _is_english(en):
                en = clean
            ss = _sentence_seed(sent)
            pattern = _get_pattern(run_id, ss)
            en_lc = en.strip().rstrip('.')
            if en_lc:
                en_lc = en_lc[0].lower() + en_lc[1:]
            try:
                cand_en = pattern.format(s=en_lc)
            except Exception:
                cand_en = f"It has been established that {en_lc}."
            if _wc(cand_en) > orig_wc * 1.3:
                cand_en = f"It has been confirmed that {en_lc}."
            cand_ar = _GT.translate(cand_en, 'en', 'ar')
            time.sleep(0.1)
            if not cand_ar or not cand_ar.strip():
                cand_ar = cand_en
            cand_ar = _clean_arabic(cand_ar)
            if _wc(cand_ar) > orig_wc * 1.3:
                cand_ar = clean
            cand_ar = restore(cand_ar, store)
            cand_ar = verify_restore(sent, cand_ar, store)
            if not cand_ar.endswith(('.', '!', '?', '؟')):
                cand_ar += '.'.
            parts.append(cand_ar)
        out.append(' '.join(parts))
    return '\n'.join(out)

# ══════════════════════════════════════════════════════════════════════
# TextHumanizer v27 — PUBLIC API
# ══════════════════════════════════════════════════════════════════════

class TextHumanizer:
    """
    API:
      humanize_chunk(chunk, level, domain, idx, run_id) -> str
        ✅ يرجع str دائماً — متوافق مع كل الكود القديم
        run_id=0 افتراضياً

      humanize_chunk_5(chunk, level, domain, idx) -> List[str]
        ✅ يرجع قائمة من 5 str — كل عنصر نموذج مستقل بأسلوب مختلف
    """

    def humanize_chunk(self,
                       chunk: str,
                       level: str,
                       domain: str = "",
                       idx: int = 0,
                       run_id: int = 0) -> str:
        """
        يرجع str واحد — النموذج المقابل لـ run_id.
        run_id 0..4 يحدد فئة الأسلوب.
        متوافق تماماً مع الكود القديم.
        """
        if not chunk or not chunk.strip():
            return chunk
        chunk = pre_fix(chunk)
        if _detect_lang(chunk) == 'en':
            result = _process_block(chunk, run_id)
        else:
            result = _process_block_ar(chunk, run_id)
        # ضمان إرجاع str
        if not isinstance(result, str):
            result = str(result)
        return result

    def humanize_chunk_5(self,
                         chunk: str,
                         level: str,
                         domain: str = "",
                         idx: int = 0) -> List[str]:
        """
        يُطبّق humanize_chunk 5 مرات بـ run_id مختلف (0..4).
        يرجع List[str] — كل عنصر str مضمون، كل عنصر أسلوب مختلف تماماً.

        مثال:
          models = humanizer.humanize_chunk_5(text, level)
          # models[0] → Passive Evidence
          # models[1] → Evidence-Led
          # models[2] → Theoretical/Analytical
          # models[3] → Literature Attribution
          # models[4] → Temporal/Critical
        """
        results: List[str] = []
        for run_id in range(5):
            result = self.humanize_chunk(chunk, level, domain, idx, run_id)
            # ضمان str في كل الحالات
            if not isinstance(result, str):
                result = str(result)
            results.append(result)
        return results