const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../public')));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../public/index.html'));
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'Server running', timestamp: new Date().toISOString() });
});

app.post('/api/paraphrase', (req, res) => {
  try {
    const { text } = req.body;
    if (!text) return res.status(400).json({ success: false, error: 'No text' });
    
    res.json({
      success: true,
      original_text: text,
      paraphrased_text: text.toUpperCase(),
      word_count: text.split(/\s+/).length
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.use((req, res) => res.status(404).json({ error: 'Not found' }));

// CRITICAL: Use Railway's PORT
const PORT = process.env.PORT || 3000;
const HOST = '0.0.0.0';

app.listen(PORT, HOST, () => {
  console.log('='.repeat(60));
  console.log('Academic Paraphraser Server STARTED');
  console.log('='.repeat(60));
  console.log('PORT from ENV:', process.env.PORT || 'NOT SET - using 3000');
  console.log('Listening on:', HOST + ':' + PORT);
  console.log('='.repeat(60));
});
