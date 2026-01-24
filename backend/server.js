const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.static(path.join(__dirname, '../public')));

// Configuration
const CONFIG = {
  "email": "search.one011@gmail.com",
  "bank_account": {
    "iban": "EG050003054450014190137000110",
    "account_number": "5445001419013700011",
    "account_holder": "Mostafa Mahmoud Mohamed elmahdi ewida",
    "bank_name": "البنك الاهلي",
    "branch": "الخارجة",
    "cif": "14190137",
    "swift": "NBEGEGCXXXX"
  },
  "github_repo": "searchone011-cpu/academic-paraphrasing-saas",
  "railway_url": "https://academic-paraphrasing-saas-production.up.railway.app"
};

// Serve index.html
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../public/index.html'));
});

// Health check
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    message: 'Server running',
    timestamp: new Date().toISOString()
  });
});

// Get config (without sensitive data)
app.get('/api/config', (req, res) => {
  res.json({
    email: CONFIG.email,
    github_repo: CONFIG.github_repo
  });
});

// Paraphrase endpoint
app.post('/api/paraphrase', (req, res) => {
  try {
    const { text } = req.body;
    
    if (!text || text.trim().length === 0) {
      return res.status(400).json({ 
        error: 'No text provided',
        success: false 
      });
    }
    
    // Simple paraphrasing (you can integrate AI later)
    const paraphrased = text.toUpperCase();
    const wordCount = text.trim().split(/\s+/).length;
    
    res.json({
      success: true,
      original_text: text,
      paraphrased_text: paraphrased,
      word_count: wordCount,
      char_count: paraphrased.length,
      processing_time: 0.1
    });
    
  } catch (error) {
    console.error('Paraphrase error:', error);
    res.status(500).json({ 
      error: error.message,
      success: false 
    });
  }
});

// Payment info endpoint
app.get('/api/payment-info', (req, res) => {
  res.json({
    supported_methods: ['stripe', 'paypal', 'bank_transfer'],
    bank_account: {
      holder: CONFIG.bank_account.account_holder,
      iban: CONFIG.bank_account.iban,
      bank: CONFIG.bank_account.bank_name,
      branch: CONFIG.bank_account.branch
    }
  });
});

// Subscription endpoint (placeholder)
app.post('/api/subscribe', (req, res) => {
  try {
    const { email, plan } = req.body;
    
    if (!email) {
      return res.status(400).json({ error: 'Email required' });
    }
    
    console.log('Subscription attempt:', { email, plan, timestamp: new Date() });
    
    res.json({
      success: true,
      message: 'Subscription created',
      email: email,
      plan: plan || 'free'
    });
    
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Error handlers
app.use((req, res) => {
  res.status(404).json({ error: 'Not found' });
});

app.use((err, req, res, next) => {
  console.error('Server error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
const PORT = process.env.PORT || 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log('\n' + '='.repeat(60));
  console.log('Academic Paraphraser Server');
  console.log('='.repeat(60));
  console.log('Server running on port ' + PORT);
  console.log('Environment: ' + (process.env.NODE_ENV || 'development'));
  console.log('Email: ' + CONFIG.email);
  console.log('='.repeat(60) + '\n');
});
