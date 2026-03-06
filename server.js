'use strict';

const express = require('express');
const cors    = require('cors');
const path    = require('path');

const app = express();
app.use(cors());
app.use(express.json({ limit: '2mb' }));
app.use(express.static(path.join(__dirname, 'public')));

// ── Health ──────────────────────────────────────────────────────────
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'Server running', ts: new Date().toISOString() });
});

// ── Main page ────────────────────────────────────────────────────────
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// ── Style Banks (5 styles × ≥20 openers each) ────────────────────────
// Guillemet tokens «P0», «P1» … are used as placeholders because «»
// never appear in academic text and cannot be confused with sentence content.

const STYLE_BANKS = [
  {
    name: 'Passive Evidence',
    openers: [
      'It has been established that',
      'It has been demonstrated that',
      'It has been empirically verified that',
      'It has been rigorously substantiated that',
      'It has been widely acknowledged that',
      'It has been independently corroborated that',
      'It has been analytically confirmed that',
      'It has been formally established that',
      'It has been persuasively argued that',
      'It has been consistently maintained that',
      'It is widely recognised that',
      'It is generally acknowledged that',
      'It is broadly accepted within the literature that',
      'It is evident from the available evidence that',
      'It is demonstrably the case that',
      'It is worth emphasising that',
      'It is critical to acknowledge that',
      'It is important to recognise that',
      'It is axiomatic within this field that',
      'It is analytically significant that',
      'It has been repeatedly observed that',
      'It has been thoroughly documented that',
      'It is increasingly recognised that',
      'It is now well established that',
    ],
  },
  {
    name: 'Evidence-Led',
    openers: [
      'The weight of evidence suggests that',
      'The preponderance of scholarly evidence confirms that',
      'Converging lines of empirical evidence indicate that',
      'A robust body of literature demonstrates that',
      'Accumulated evidence from multiple sources establishes that',
      'The cumulative scholarly record affirms that',
      'Systematic review of the literature reveals that',
      'An analysis of the extant evidence base confirms that',
      'The balance of evidence strongly supports the view that',
      'Empirical investigation consistently demonstrates that',
      'Cross-disciplinary evidence converges on the finding that',
      'Meta-analytical findings consistently affirm that',
      'The totality of available research evidence confirms that',
      'Rigorous evidence-based analysis confirms that',
      'A comprehensive survey of the evidence establishes that',
      'The scholarly evidence base overwhelmingly supports the view that',
      'Empirical corroboration across multiple studies confirms that',
      'The aggregate of available empirical evidence affirms that',
      'Sustained empirical investigation has confirmed that',
      'Critical evaluation of the evidence base confirms that',
      'A convergence of empirical findings suggests that',
      'The preponderance of available data indicates that',
      'Evidence drawn from systematic inquiry confirms that',
      'The available empirical record strongly suggests that',
    ],
  },
  {
    name: 'Theoretical / Analytical',
    openers: [
      'From a theoretical standpoint,',
      'Situated within the relevant theoretical framework,',
      'Within the conceptual parameters of this field,',
      'Through the prism of contemporary scholarly discourse,',
      'Against the backdrop of established theoretical principles,',
      'Grounded in the foundational tenets of the discipline,',
      'A rigorous analytical examination reveals that',
      'Careful interrogation of the available evidence discloses that',
      'Critical analysis of the relevant data establishes that',
      'Systematic analytical scrutiny of the evidence confirms that',
      'An in-depth examination of the pertinent material reveals that',
      'A forensic examination of the available evidence demonstrates that',
      'A methodologically robust analysis reveals that',
      'Under sustained analytical scrutiny,',
      'Examining the evidence with appropriate critical rigour,',
      'Informed by prevailing theoretical perspectives,',
      'Drawing on the conceptual apparatus of the field,',
      'Anchored in the epistemological foundations of the discipline,',
      'Viewed through a rigorous scholarly lens,',
      'Proceeding from established theoretical premises,',
      'A careful theoretical appraisal reveals that',
      'An analytically grounded reading of the evidence suggests that',
      'Applying established conceptual frameworks,',
      'Deploying the theoretical tools of the discipline,',
    ],
  },
  {
    name: 'Literature Attribution',
    openers: [
      'The scholarly literature converges on the view that',
      'An extensive corpus of academic scholarship confirms that',
      'Peer-reviewed scholarship consistently affirms that',
      'The existing body of literature provides strong support for the view that',
      'Extant research establishes with considerable rigour that',
      'The academic consensus, as reflected in the literature, holds that',
      'A substantial and growing literature demonstrates that',
      'The interdisciplinary literature converges on the view that',
      'Foundational works in this field have established that',
      'Of particular scholarly significance is the finding that',
      'The canon of relevant scholarship makes clear that',
      'Authoritative contributions to the literature confirm that',
      'A comprehensive review of the literature reveals that',
      'The relevant disciplinary literature unequivocally establishes that',
      'An overwhelming scholarly majority affirms that',
      'Seminal contributions to this area have confirmed that',
      'The emergent scholarly consensus affirms that',
      'Successive generations of scholars have affirmed that',
      'A broad survey of the academic literature confirms that',
      'The accumulated wisdom of the field affirms that',
      'As demonstrated by prior scholarship,',
      'Building on the existing literature,',
      'Consistent with the prevailing scholarly view,',
      'Prior academic inquiry has firmly established that',
    ],
  },
  {
    name: 'Temporal & Critical',
    openers: [
      'Over the past several decades, scholarly inquiry has confirmed that',
      'In the contemporary context of intensifying global pressures,',
      'As the twenty-first century unfolds, it is increasingly evident that',
      'Against a backdrop of rapid and sustained change,',
      'In the wake of decades of sustained empirical inquiry,',
      'It is essential to recognise that',
      'It is imperative to acknowledge that',
      'Intellectual honesty demands acknowledgement of the fact that',
      'Rigorous analysis requires the recognition that',
      'While diverse scholarly perspectives exist on this matter,',
      'Despite ongoing scholarly debate,',
      'In contradistinction to simplistic narratives,',
      'Contrary to conventional wisdom,',
      'Building on the existing literature, this analysis confirms that',
      'This analysis contributes to the growing body of evidence confirming that',
      'Even granting the complexity of this issue,',
      'While acknowledging alternative interpretations,',
      'In contrast to prior theoretical positions,',
      'Resisting the temptation of reductionist interpretation,',
      'As knowledge in this domain has advanced,',
      'In the contemporary scholarly context,',
      'Under sustained critical scrutiny,',
      'As recent developments in the field have made plain,',
      'Given the escalating urgency of these concerns,',
    ],
  },
];

const STYLE_NAMES = STYLE_BANKS.map(b => b.name);

// ── Academic synonyms ─────────────────────────────────────────────────
const SYNONYMS = [
  [/\bimportant\b/gi, 'significant'],
  [/\bimportance\b/gi, 'significance'],
  [/\bused\b/gi, 'utilised'],
  [/\buses\b/gi, 'utilises'],
  [/\buse\b/gi, 'utilise'],
  [/\bshows\b/gi, 'demonstrates'],
  [/\bshow\b/gi, 'demonstrate'],
  [/\bmany\b/gi, 'numerous'],
  [/\bnew\b/gi, 'novel'],
  [/\bproblems\b/gi, 'challenges'],
  [/\bproblem\b/gi, 'challenge'],
  [/\bneeds\b/gi, 'necessitates'],
  [/\bneed\b/gi, 'necessitate'],
  [/\bhelps\b/gi, 'facilitates'],
  [/\bhelp\b/gi, 'facilitate'],
  [/\bbig\b/gi, 'substantial'],
  [/\blarge\b/gi, 'considerable'],
  [/\bstart\b/gi, 'commence'],
  [/\bget\b/gi, 'obtain'],
  [/\bgot\b/gi, 'obtained'],
  [/\balso\b/gi, 'furthermore'],
  [/\bbasically\b/gi, 'fundamentally'],
  [/\bobviously\b/gi, 'evidently'],
  [/\ba lot of\b/gi, 'a substantial number of'],
  [/\bdon't\b/gi, 'do not'],
  [/\bdoesn't\b/gi, 'does not'],
  [/\bwon't\b/gi, 'will not'],
  [/\bcan't\b/gi, 'cannot'],
  [/\bisn't\b/gi, 'is not'],
  [/\baren't\b/gi, 'are not'],
  [/\bIt's\b/g, 'It is'],
  [/\bThat's\b/g, 'That is'],
  [/\bThere's\b/g, 'There is'],
  [/\bkey\b/gi, 'critical'],
  [/\bmain\b/gi, 'principal'],
  [/\bgoal\b/gi, 'objective'],
  [/\bgoals\b/gi, 'objectives'],
  [/\bfindings\b/gi, 'results'],
  [/\blink\b/gi, 'relationship'],
];

// ── Placeholder pipeline (CRITICAL) ──────────────────────────────────
// Guillemet tokens «P0», «P1» … are used because «» never appear in
// academic text and survive all synonym/opener transformations unchanged.

function protect(text) {
  const map = new Map();
  let counter = 0;
  const makeToken = () => `«P${counter++}»`;

  // 1. Protect quoted strings "..." (up to 300 chars)
  text = text.replace(/"[^"\n]{1,300}"/g, m => {
    const t = makeToken(); map.set(t, m); return t;
  });
  // 2. Protect single-quoted strings '...' (up to 300 chars)
  text = text.replace(/'[^'\n]{1,300}'/g, m => {
    const t = makeToken(); map.set(t, m); return t;
  });
  // 3. Protect "According to Author (Year)" constructs
  text = text.replace(
    /According\s+to\s+[A-Z][a-zA-Z\u00C0-\u024F\-']+(?:\s+et\s+al\.?)?\s*\(\s*\d{4}[a-z]?\s*\)/g,
    m => { const t = makeToken(); map.set(t, m); return t; }
  );
  // 4. Protect (Author et al., Year) / (Author, Year) / (A, Y; B, Y) citations
  text = text.replace(
    /\(\s*[A-Z][a-zA-Z\u00C0-\u024F\-']+(?:\s+et\s+al\.?)?\s*,\s*\d{4}[a-z]?(?:\s*(?:,\s*p\.?\s*\d+)?)(?:\s*;\s*[A-Z][a-zA-Z\u00C0-\u024F\-']+(?:\s+et\s+al\.?)?\s*,\s*\d{4}[a-z]?(?:\s*(?:,\s*p\.?\s*\d+)?))*\s*\)/g,
    m => { const t = makeToken(); map.set(t, m); return t; }
  );
  // 5. Protect numbered citations [1] / [1,2] / [1-3]
  text = text.replace(/\[\s*\d+(?:\s*[,\-]\s*\d+)*\s*\]/g, m => {
    const t = makeToken(); map.set(t, m); return t;
  });
  // 6. Protect standalone numbers, decimals, percentages, years, units
  text = text.replace(
    /\b\d+(?:[.,]\d+)*(?:\s*%|\s*percent|\s*million|\s*billion|\s*trillion|\s*thousand|\s*kg|\s*km|\s*cm|\s*mm|\s*mg|\s*g\b|\s*L\b|\s*ml|\s*GHz|\s*MHz|\s*GB|\s*MB|\s*TB|\s*kB)?\b/g,
    m => { const t = makeToken(); map.set(t, m); return t; }
  );

  return { protected: text, map };
}

function restore(text, map) {
  for (const [token, original] of map) {
    text = text.split(token).join(original);
  }
  // VERIFY: if any «P\d+» token still present, the pipeline failed
  const leaked = text.match(/«P\d+»/g);
  if (leaked) {
    throw new Error('RestoreError: placeholders not restored: ' + leaked.join(', '));
  }
  return text;
}

// ── Constants ────────────────────────────────────────────────────────
const MIN_SENTENCE_LENGTH = 12;
const SEED_ATTEMPT_MULTIPLIER = 100;

// ── Sentence utilities ────────────────────────────────────────────────

function applySynonyms(text) {
  let r = text;
  for (const [pat, rep] of SYNONYMS) r = r.replace(pat, rep);
  return r;
}

function capitalise(s) {
  if (!s) return s;
  return s[0].toUpperCase() + s.slice(1);
}

// Strip common academic opener patterns so the sentence core is extracted cleanly
const OPENER_PATTERNS = [
  /^It\s+(?:has\s+been|is|was)\s+(?:established|demonstrated|empirically\s+verified|rigorously\s+substantiated|widely\s+acknowledged|independently\s+corroborated|analytically\s+confirmed|formally\s+established|persuasively\s+argued|consistently\s+maintained|repeatedly\s+observed|thoroughly\s+documented|well\s+established)\s+that\s+/i,
  /^It\s+is\s+(?:widely|generally|broadly|commonly|increasingly|now\s+well)\s+(?:recognised|acknowledged|accepted|understood|apparent|evident)\s+(?:within\s+the\s+literature\s+)?that\s+/i,
  /^It\s+is\s+(?:demonstrably\s+the\s+case|worth\s+emphasising|critical\s+to\s+acknowledge|important\s+to\s+recognise|axiomatic\s+within\s+this\s+field|analytically\s+significant|essential\s+to\s+recognise|imperative\s+to\s+acknowledge)\s+that\s+/i,
  /^(?:The\s+weight\s+of\s+evidence|The\s+preponderance\s+of\s+scholarly\s+evidence|The\s+cumulative\s+scholarly\s+record|The\s+balance\s+of\s+evidence|The\s+totality\s+of\s+available\s+research\s+evidence|The\s+scholarly\s+evidence\s+base|The\s+aggregate\s+of\s+available\s+empirical\s+evidence|The\s+preponderance\s+of\s+available\s+data)\s+(?:suggests?|confirms?|affirms?|supports?\s+the\s+view|indicates?)\s+that\s+/i,
  /^(?:Converging\s+lines\s+of\s+empirical\s+evidence|Accumulated\s+evidence\s+from\s+multiple\s+sources|Systematic\s+review\s+of\s+the\s+literature|An\s+analysis\s+of\s+the\s+extant\s+evidence\s+base|Empirical\s+investigation|Cross-disciplinary\s+evidence|Meta-analytical\s+findings|Rigorous\s+evidence-based\s+analysis|A\s+comprehensive\s+survey\s+of\s+the\s+evidence|Empirical\s+corroboration\s+across\s+multiple\s+studies|Sustained\s+empirical\s+investigation|Critical\s+evaluation\s+of\s+the\s+evidence\s+base|A\s+convergence\s+of\s+empirical\s+findings|Evidence\s+drawn\s+from\s+systematic\s+inquiry)\s+(?:suggests?|confirms?|affirms?|reveals?|indicates?|establishes?|has\s+confirmed)\s+that\s+/i,
  /^(?:The\s+scholarly\s+literature|An\s+extensive\s+corpus\s+of\s+academic\s+scholarship|Peer-reviewed\s+scholarship|The\s+existing\s+body\s+of\s+literature|Extant\s+research|The\s+academic\s+consensus[^,]*|A\s+substantial\s+and\s+growing\s+literature|The\s+interdisciplinary\s+literature|Foundational\s+works\s+in\s+this\s+field|The\s+canon\s+of\s+relevant\s+scholarship|Authoritative\s+contributions\s+to\s+the\s+literature|A\s+comprehensive\s+review\s+of\s+the\s+literature|The\s+relevant\s+disciplinary\s+literature|An\s+overwhelming\s+scholarly\s+majority|Seminal\s+contributions\s+to\s+this\s+area|The\s+emergent\s+scholarly\s+consensus|Successive\s+generations\s+of\s+scholars|A\s+broad\s+survey\s+of\s+the\s+academic\s+literature|The\s+accumulated\s+wisdom\s+of\s+the\s+field|Prior\s+academic\s+inquiry)\s+(?:converges?\s+on\s+the\s+view|confirms?|affirms?|provides?\s+strong\s+support|establishes?|holds?|demonstrates?|reveals?|makes?\s+clear|has\s+(?:established|confirmed|affirmed))\s+that\s+/i,
  /^(?:Over\s+the\s+past\s+several\s+decades[^,]*,|In\s+the\s+contemporary\s+context[^,]*,|As\s+the\s+twenty-first\s+century[^,]*,|Against\s+a\s+backdrop[^,]*,|In\s+the\s+wake\s+of[^,]*,|Building\s+on\s+the\s+existing\s+literature[^,]*,|This\s+analysis\s+contributes[^.]+?\s+that\s+|Even\s+granting[^,]*,|While\s+acknowledging[^,]*,|In\s+contrast\s+to[^,]*,|Resisting\s+the\s+temptation[^,]*,|As\s+knowledge\s+in\s+this\s+domain\s+has\s+advanced[^,]*,|In\s+the\s+contemporary\s+scholarly\s+context[^,]*,|Under\s+sustained\s+critical\s+scrutiny[^,]*,|As\s+recent\s+developments[^,]*,|Given\s+the\s+escalating\s+urgency[^,]*,)/i,
  /^(?:From\s+a\s+theoretical\s+standpoint[^,]*,|Situated\s+within[^,]*,|Within\s+the\s+conceptual\s+parameters[^,]*,|Through\s+the\s+prism[^,]*,|Against\s+the\s+backdrop[^,]*,|Grounded\s+in[^,]*,|Under\s+sustained\s+analytical\s+scrutiny[^,]*,|Examining\s+the\s+evidence[^,]*,|Informed\s+by[^,]*,|Drawing\s+on[^,]*,|Anchored\s+in[^,]*,|Viewed\s+through[^,]*,|Proceeding\s+from[^,]*,|Applying\s+established[^,]*,|Deploying\s+the\s+theoretical[^,]*,|A\s+careful\s+theoretical\s+appraisal\s+reveals\s+that\s+|An\s+analytically\s+grounded\s+reading[^.]+?\s+that\s+)/i,
  /^(?:A\s+rigorous\s+analytical\s+examination\s+reveals\s+that|Careful\s+interrogation\s+of\s+the\s+available\s+evidence\s+discloses\s+that|Critical\s+analysis\s+of\s+the\s+relevant\s+data\s+establishes\s+that|Systematic\s+analytical\s+scrutiny\s+of\s+the\s+evidence\s+confirms\s+that|An\s+in-depth\s+examination\s+of\s+the\s+pertinent\s+material\s+reveals\s+that|A\s+forensic\s+examination\s+of\s+the\s+available\s+evidence\s+demonstrates\s+that|A\s+methodologically\s+robust\s+analysis\s+reveals\s+that)\s+/i,
  /^(?:As\s+demonstrated\s+by\s+prior\s+scholarship[^,]*,|Building\s+on\s+the\s+existing\s+literature[^,]*,|Consistent\s+with\s+the\s+prevailing\s+scholarly\s+view[^,]*,|Of\s+particular\s+scholarly\s+significance\s+is\s+the\s+finding\s+that\s+)/i,
  /^(?:Intellectual\s+honesty\s+demands[^.]+?\s+that\s+|Rigorous\s+analysis\s+requires\s+the\s+recognition\s+that\s+|While\s+diverse\s+scholarly\s+perspectives[^,]*,|Despite\s+ongoing\s+scholarly\s+debate[^,]*,|In\s+contradistinction\s+to[^,]*,|Contrary\s+to\s+conventional\s+wisdom[^,]*,)/i,
];

function stripCommonOpeners(text) {
  for (const pat of OPENER_PATTERNS) {
    const m = text.match(pat);
    if (m && m[0].length < text.length - 5) {
      const stripped = text.slice(m[0].length).trim();
      if (stripped.length > 5) return stripped;
    }
  }
  return text;
}

// Split text into sentences, respecting end-of-sentence punctuation.
// Avoids splitting on periods inside guillemet tokens (they have none).
function splitSentences(text) {
  const results = [];
  // Match: non-punctuation chars + end punctuation + optional trailing whitespace
  const re = /[^.!?؟]*[.!?؟]+(?:\s+|$)|[^.!?؟\s][^.!?؟]*$/g;
  let m;
  while ((m = re.exec(text)) !== null) {
    const s = m[0].trim();
    if (s) results.push(s);
  }
  return results.length ? results : [text];
}

// Determine if a line is a heading (skip rewriting)
function isHeading(line) {
  const t = line.trim();
  if (!t) return false;
  if (t.endsWith(':')) return true;
  // All-caps short line (title-like)
  if (t.length < 80 && t === t.toUpperCase() && /[A-Z]/.test(t)) return true;
  return false;
}

// ── Core rewriter ─────────────────────────────────────────────────────

function rewriteSentences(text, styleIndex, seed) {
  const bank = STYLE_BANKS[styleIndex];
  const openers = bank.openers;
  const lines = text.split(/\r?\n/);

  const processedLines = lines.map((line, lineIdx) => {
    if (!line.trim()) return line;             // preserve blank lines
    if (isHeading(line)) return line;          // preserve headings

    const sentences = splitSentences(line.trim());

    const processedSents = sentences.map((sent, sentIdx) => {
      const s = sent.trim();
      // Skip very short fragments or those that are only tokens
      if (s.length < MIN_SENTENCE_LENGTH || /^«P\d+»\.?$/.test(s)) return s;

      // Deterministic but varied selection: avoids repeating the same opener
      const openerIdx = (seed * 7 + lineIdx * 11 + sentIdx * 3) % openers.length;
      const opener = openers[openerIdx];

      // Extract trailing punctuation
      const punctMatch = s.match(/[.!?؟]+$/);
      const punct = punctMatch ? punctMatch[0] : '.';

      // Remove trailing punctuation from content
      let content = s.replace(/[.!?؟]+$/, '').trim();

      // Apply academic synonym substitution
      content = applySynonyms(content);

      // Strip any pre-existing opener so we don't double-up
      content = stripCommonOpeners(content);

      // Lowercase the first character so the opener flows naturally
      // (Safe even when content starts with «P0»: «  stays as-is)
      if (content.length > 0 && /[A-Z]/.test(content[0])) {
        content = content[0].toLowerCase() + content.slice(1);
      }

      // Reconstruct
      let result = opener + ' ' + content + '.';
      result = capitalise(result.trim())
        .replace(/  +/g, ' ')
        .replace(/\s+([.,;:!?؟])/g, '$1');

      return result;
    });

    return processedSents.join(' ');
  });

  return processedLines.join('\n');
}

// ── Paraphrase pipeline per model ─────────────────────────────────────

function paraphraseModel(text, styleIndex, callSeed) {
  const { protected: pText, map } = protect(text);
  const rewritten = rewriteSentences(pText, styleIndex, callSeed);
  return restore(rewritten, map);
}

// ── Global call counter (ensures each invocation gets a unique seed) ──
let callCounter = 0;

// ── POST /api/paraphrase — returns 5 models in one response ───────────
app.post('/api/paraphrase', (req, res) => {
  const { text } = req.body;
  if (!text || !text.trim()) {
    return res.status(400).json({ success: false, error: 'No text provided' });
  }

  callCounter++;
  const models = [];

  for (let i = 0; i < 5; i++) {
    let result = text.trim();
    let attempts = 0;
    while (attempts < 3) {
      try {
        result = paraphraseModel(text.trim(), i, callCounter + attempts * SEED_ATTEMPT_MULTIPLIER);
        break;
      } catch (e) {
        attempts++;
        if (attempts === 3) {
          // Final fallback: return original text unchanged
          result = text.trim();
        }
      }
    }
    models.push({ style: STYLE_NAMES[i], text: result });
  }

  res.json({ success: true, models });
});

// ── 404 ──────────────────────────────────────────────────────────────
app.use((req, res) => {
  res.status(404).json({ error: 'Not found' });
});

// ── Start ─────────────────────────────────────────────────────────────
const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log('='.repeat(50));
  console.log('Academic Paraphraser v2 — 5 Models per Request');
  console.log('Port: ' + PORT);
  console.log('='.repeat(50));
});