#!/bin/bash
elasticdump \
  --input=http://localhost:9200/index-news \
  --output=news.data \
  --type=data
elasticdump \
  --input=http://localhost:9200/index-ticks \
  --output=ticks.data \
  --type=data