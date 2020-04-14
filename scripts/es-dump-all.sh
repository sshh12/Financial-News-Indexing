#!/bin/bash
elasticdump \
  --input=http://localhost:9200/index-news \
  --output=./data/news.data \
  --noRefresh \
  --sourceOnly \
  --limit 1000 \
  --type=data
elasticdump \
  --input=http://localhost:9200/index-ticks \
  --output=./data/ticks.data \
  --noRefresh \
  --sourceOnly \
  --limit 1000 \
  --type=data