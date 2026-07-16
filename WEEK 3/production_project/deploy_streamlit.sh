#!/bin/bash
# Streamlit deployment script

echo "🚀 Deploying RAG Evaluation Benchmark"

# Install dependencies
pip install -r requirements_production.txt

# Create .streamlit directory
mkdir -p .streamlit

# Create Streamlit config
cat > .streamlit/config.toml << EOF
[theme]
primaryColor = "#2E86AB"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 200
enableXsrfProtection = true
enableCORS = false
EOF

# Run Streamlit
streamlit run project3_p_c_rag_benchmark.py -- --streamlit
