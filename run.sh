#!/bin/bash
docker build -t web-app .
docker run -p 5000:5000 web-app
