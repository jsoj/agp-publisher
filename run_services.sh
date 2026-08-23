#!/bin/bash
cd /root/agp-publisher
/root/agp-publisher/venv/bin/python3 -m uvicorn main_api:app --host 0.0.0.0 --port 8060
