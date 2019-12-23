#!/bin/bash
elasticdump \
  --input=http://localhost:9200/index-news \
  --output=./dump/news.data \
  --type=data
elasticdump \
  --input=http://localhost:9200/index-ticks \
  --output=./dump/ticks.data \
  --type=data