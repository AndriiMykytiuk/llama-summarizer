#!/bin/bash
# Test script for DistilBART Summarizer API

API_URL="https://distilbart-summarizer.onrender.com"

echo "Testing DistilBART Summarizer API..."
echo "======================================"
echo

echo "1. Testing root endpoint:"
curl -s -X GET "$API_URL/" | jq
echo
echo

echo "2. Testing health endpoint:"
curl -s -X GET "$API_URL/health" | jq
echo
echo

echo "3. Testing summarization:"
curl -s -X POST "$API_URL/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of intelligent agents: any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals. Colloquially, the term artificial intelligence is often used to describe machines that mimic cognitive functions that humans associate with the human mind, such as learning and problem solving.",
    "max_length": 100,
    "min_length": 30
  }' | jq

echo
echo "======================================"
echo "Test complete!"
