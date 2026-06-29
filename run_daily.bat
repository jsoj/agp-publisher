@echo off
:: Script para automação do AGP
cd /d "C:\Users\jose.junior\OneDrive - SEMENTES PRODUTIVA\dev\publisher"
python autonomous_publisher.py >> run_daily.log 2>&1
