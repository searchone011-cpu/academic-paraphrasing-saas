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

// ── JS Style Bank (5 categories) ─────────────────────────────────────
const JS_OPENERS = [
  [
    "It has been established that","It has been demonstrated that",
    "It has been empirically verified that","It has been rigorously substantiated that",
    "It has been widely acknowledged that","It has been independently corroborated that",
    "It has been analytically confirmed that","It has been formally established that",
    "It has been persuasively argued that","It has been consistently maintained that",
    "It is widely recognised that","It is generally acknowledged that",
    "It is broadly accepted within the literature that",
    "It is evident from the available evidence that",
    "It is demonstrably the case that","It is worth emphasising that",
    "It is critical to acknowledge that","It is important to recognise that",
    "It is axiomatic within this field that","It is analytically significant that",
  ],
  [
    "The weight of evidence suggests that",
    "The preponderance of scholarly evidence confirms that",
    "Converging lines of empirical evidence indicate that",
    "A robust body of literature demonstrates that",
    "Accumulated evidence from multiple sources establishes that",
    "The cumulative scholarly record affirms that",
    "Systematic review of the literature reveals that",
    "An analysis of the extant evidence base confirms that",
    "The balance of evidence strongly supports the view that",
    "Empirical investigation consistently demonstrates that",
    "Cross-disciplinary evidence converges on the finding that",
    "Meta-analytical findings consistently affirm that",
    "The totality of available research evidence confirms that",
    "Rigorous evidence-based analysis confirms that",
    "A comprehensive survey of the evidence establishes that",
    "The scholarly evidence base overwhelmingly supports the view that",
    "Empirical corroboration across multiple studies confirms that",
    "The aggregate of available empirical evidence affirms that",
    "Sustained empirical investigation has confirmed that",
    "Critical evaluation of the evidence base confirms that",
  ],
  [
    "From a theoretical standpoint,",
    "Situated within the relevant theoretical framework,",
    "Within the conceptual parameters of this field,",
    "Through the prism of contemporary scholarly discourse,",
    "Against the backdrop of established theoretical principles,",
    "Grounded in the foundational tenets of the discipline,",
    "A rigorous analytical examination reveals that",
    "Careful interrogation of the available evidence discloses that",
    "Critical analysis of the relevant data establishes that",
    "Systematic analytical scrutiny of the evidence confirms that",
    "An in-depth examination of the pertinent material reveals that",
    "A forensic examination of the available evidence demonstrates that",
    "A methodologically robust analysis reveals that",
    "Under sustained analytical scrutiny,",
    "Examining the evidence with appropriate critical rigour,",
    "Informed by prevailing theoretical perspectives,",
    "Drawing on the conceptual apparatus of the field,",
    "Anchored in the epistemological foundations of the discipline,",
    "Viewed through a rigorous scholarly lens,",
    "Proceeding from established theoretical premises,",
  ],
  [
    "The scholarly literature converges on the view that",
    "An extensive corpus of academic scholarship confirms that",
    "Peer-reviewed scholarship consistently affirms that",
    "The existing body of literature provides strong support that",
    "Extant research establishes with considerable rigour that",
    "The academic consensus, as reflected in the literature, holds that",
    "A substantial and growing literature demonstrates that",
    "The interdisciplinary literature converges on the view that",
    "Foundational works in this field have established that",
    "Of particular scholarly significance is the finding that",
    "The canon of relevant scholarship makes clear that",
    "Authoritative contributions to the literature confirm that",
    "A comprehensive review of the literature reveals that",
    "The relevant disciplinary literature unequivocally establishes that",
    "An overwhelming scholarly majority affirms that",
    "Seminal contributions to this area have confirmed that",
    "The emergent scholarly consensus affirms that",
    "Successive generations of scholars have affirmed that",
    "A broad survey of the academic literature confirms that",
    "The accumulated wisdom of the field affirms that",
  ],
  [
    "Over the past several decades, scholarly inquiry has confirmed that",
    "In the contemporary context of intensifying global pressures,",
    "As the twenty-first century unfolds, it is increasingly evident that",
    "Against a backdrop of rapid and sustained change,",
    "In the wake of decades of sustained empirical inquiry,",
    "It is essential to recognise that",
    "It is imperative to acknowledge that",
    "Intellectual honesty demands acknowledgement of the fact that",
    "Rigorous analysis requires the recognition that",
    "While diverse scholarly perspectives exist on this matter,",
    "Despite ongoing scholarly debate,",
    "In contradistinction to simplistic narratives,",
    "Contrary to conventional wisdom,",
    "Building on the existing literature, this analysis confirms that",
    "This analysis contributes to the growing body of evidence confirming that",
    "Even granting the complexity of this issue,",
    "While acknowledging alternative interpretations,",
    "In contrast to prior theoretical positions,",
    "Resisting the temptation of reductionist interpretation,",
    "As knowledge in this domain has advanced,",
  ]
];

// Academic synonyms
const SYNONYMS = [
  [/\bimportant\b/gi,'significant'],[/\bimportance\b/gi,'significance'],
  [/\buse\b/gi,'utilise'],[/\buses\b/gi,'utilises'],[/\bused\b/gi,'utilised'],
  [/\bshows\b/gi,'demonstrates'],[/\bshow\b/gi,'demonstrate'],
  [/\bmany\b/gi,'numerous'],[/\bnew\b/gi,'novel'],
  [/\bproblem\b/gi,'challenge'],[/\bproblems\b/gi,'challenges'],
  [/\bneed\b/gi,'necessitate'],[/\bneeds\b/gi,'necessitates'],
  [/\bhelp\b/gi,'facilitate'],[/\bhelps\b/gi,'facilitates'],
  [/\bbig\b/gi,'substantial'],[/\blarge\b/gi,'considerable'],
  [/\bstart\b/gi,'commence'],[/\bget\b/gi,'obtain'],[/\bgot\b/gi,'obtained'],
  [/\balso\b/gi,'furthermore'],[/\bbasically\b/gi,'fundamentally'],
  [/\bobviously\b/gi,'evidently'],[/\ba lot of\b/gi,'a substantial number of'],
  [/\bdon't\b/gi,'do not'],[/\bdoesn't\b/gi,'does not'],
  [/\bwon't\b/gi,'will not'],[/\bcan't\b/gi,'cannot'],
  [/\bisn't\b/gi,'is not'],[/\baren't\b/gi,'are not'],
  [/\bIt's\b/g,'It is'],[/\bThat's\b/g,'That is'],
  [/\bThere's\b/g,'There is'],
];

// Protect citations and numbers
function protectAndStrip(text) {
  const store = {};
  let idx = 0;
  const key = () => `\x00P${String(idx++).padStart(4,'0')}\x00`;

  // quoted text
  text = text.replace(/"[^"]{1,200}"/g, m => { const k=key(); store[k]=m; return k; });
  // According to Author (Year)
  text = text.replace(/According\s+to\s+[A-Z][a-zA-Z\-']+(?:\s+et\s+al\.?)?\s*\(\s*\d{4}[a-z]?\s*\)/g,
    m => { const k=key(); store[k]=m; return k; });
  // (Author, Year)
  text = text.replace(/\(\s*[A-Z][a-zA-Z\-']+(?:\s+et\s+al\.?)?\s*,\s*\d{4}[a-z]?(?:\s*;\s*[A-Z][a-zA-Z\-']+(?:\s+et\s+al\.?)?\s*,\s*\d{4}[a-z]?)*\s*\)/g,
    m => { const k=key(); store[k]=m; return k; });
  // numbers
  text = text.replace(/\b\d+(?:\.\d+)?(?:\s*%|\s*percent|\s*million|\s*billion|\s*kg|\s*km)?\b/g,
    m => { const k=key(); store[k]=m; return k; });

  return { clean: text.replace(/  +/g,' ').trim(), store };
}

function restore(text, store) {
  for (const [k,v] of Object.entries(store)) text = text.split(k).join(v);
  return text.replace(/\x00P\d+\x00/g,'').replace(/  +/g,' ').trim();
}

function applySynonyms(text) {
  let r = text;
  for (const [pat, rep] of SYNONYMS) r = r.replace(pat, rep);
  return r;
}

function capitalise(s) {
  if (!s) return s;
  return s[0].toUpperCase() + s.slice(1);
}

function jsParaphrase(text, runId) {
  const cat = JS_OPENERS[runId % 5];
  // split into sentences
  const sentences = text.match(/[^.!?؟]+[.!?؟]+/g) || [text];

  const processed = sentences.map((sent, i) => {
    const trimmed = sent.trim();

    // protect citations + numbers
    const { clean, store } = protectAndStrip(trimmed);

    // pick opener deterministically: runId + sentence position
    const openerIdx = (runId * 7 + i * 3) % cat.length;
    const opener    = cat[openerIdx];

    // strip trailing punctuation from content
    let content = clean.replace(/[.!?؟]+$/, '').trim();
    content = applySynonyms(content);

    // lowercase first letter of content (opener provides the start)
    if (content.length > 0) content = content[0].toLowerCase() + content.slice(1);

    // build sentence
    let result;
    if (opener.endsWith(',')) {
      // "From a theoretical standpoint, ..." — no "that"
      result = opener + ' ' + content + '.';
    } else {
      result = opener + ' ' + content + '.';
    }

    result = capitalise(result.trim());
    result = result.replace(/  +/g,' ').replace(/\s+([.,;:!?])/g,'$1');

    // restore protected content
    result = restore(result, store);
    return result;
  });

  return processed.join(' ');
}

// ── Paraphrase API ───────────────────────────────────────────────────
app.post('/api/paraphrase', (req, res) => {
  try {
    const { text, level = 'أقصى درجة', run_id = 0 } = req.body;

    if (!text || !text.trim()) {
      return res.status(400).json({ success: false, error: 'No text provided' });
    }

    const rid    = parseInt(run_id) || 0;
    const result = jsParaphrase(text.trim(), rid);

    res.json({
      success: true,
      paraphrased_text: result,
      word_count: result.split(/\s+/).filter(Boolean).length
    });
  } catch (error) {
    console.error('Paraphrase error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// ── 404 ──────────────────────────────────────────────────────────────
app.use((req, res) => {
  res.status(404).json({ error: 'Not found' });
});

// ── Start ─────────────────────────────────────────────────────────────
const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log('='.repeat(50));
  console.log('Academic Paraphraser — 5 Models');
  console.log('Port: ' + PORT);
  console.log('='.repeat(50));
});