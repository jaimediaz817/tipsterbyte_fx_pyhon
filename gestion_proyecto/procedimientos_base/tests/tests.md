# Todos los tests
cd backend
pytest apps/leagues_manager/tests/ -v

# Solo tests unitarios (sin BD)
pytest apps/leagues_manager/tests/test_process_run_flow.py -v

# Solo tests de integración (con BD real)
pytest apps/leagues_manager/tests/test_process_run_integration.py -v

- ESTANDO DESDE LA RAIZ:
pytest backend/apps/leagues_manager/tests/test_process_run_integration.py -v

# Con output detallado de logs
pytest apps/leagues_manager/tests/test_process_run_flow.py -v -s

- ESTANDO DESDE LA RAIZ:
pytest backend/apps/leagues_manager/tests/test_process_run_flow.py -v -s

pip install pytest-asynciow


- Correr manualmente el test como script:
cd cd "backend\apps\leagues_manager\tests"
python run_robot_logs_test.py