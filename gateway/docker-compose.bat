@echo off
setlocal enabledelayedexpansion

REM MSA Gateway Docker Compose 실행 스크립트 (Windows)

if "%1"=="" goto help

if "%1"=="start" goto start
if "%1"=="stop" goto stop
if "%1"=="restart" goto restart
if "%1"=="status" goto status
if "%1"=="logs" goto logs
if "%1"=="health" goto health
if "%1"=="test" goto test
if "%1"=="help" goto help

goto help

:start
echo [INFO] MSA 서비스들을 시작합니다...
docker-compose up -d
echo [INFO] 서비스 시작 대기 중...
timeout /t 10 /nobreak > nul
goto status

:stop
echo [INFO] MSA 서비스들을 중지합니다...
docker-compose down
echo [SUCCESS] 모든 서비스가 중지되었습니다.
goto end

:restart
echo [INFO] MSA 서비스들을 재시작합니다...
docker-compose restart
echo [SUCCESS] 모든 서비스가 재시작되었습니다.
goto end

:status
echo [INFO] 컨테이너 상태 확인 중...
docker-compose ps
goto end

:logs
if "%2"=="" (
    echo [INFO] 모든 서비스의 로그를 확인합니다...
    docker-compose logs -f
) else (
    echo [INFO] %2 서비스의 로그를 확인합니다...
    docker-compose logs -f %2
)
goto end

:health
echo [INFO] 서비스 헬스 체크를 수행합니다...
echo.
echo 게이트웨이 헬스 체크:
curl -f http://localhost:8000/health 2>nul && echo [SUCCESS] 게이트웨이가 정상 작동 중입니다. || echo [ERROR] 게이트웨이에 연결할 수 없습니다.
echo.
echo 사용자 서비스 헬스 체크:
curl -f http://localhost:8001/health 2>nul && echo [SUCCESS] 사용자 서비스가 정상 작동 중입니다. || echo [ERROR] 사용자 서비스에 연결할 수 없습니다.
echo.
echo 주문 서비스 헬스 체크:
curl -f http://localhost:8002/health 2>nul && echo [SUCCESS] 주문 서비스가 정상 작동 중입니다. || echo [ERROR] 주문 서비스에 연결할 수 없습니다.
echo.
echo 상품 서비스 헬스 체크:
curl -f http://localhost:8003/health 2>nul && echo [SUCCESS] 상품 서비스가 정상 작동 중입니다. || echo [ERROR] 상품 서비스에 연결할 수 없습니다.
goto end

:test
echo [INFO] API 테스트를 실행합니다...
echo.
echo === 게이트웨이 테스트 ===
curl -s http://localhost:8000/health 2>nul
echo.
echo === 사용자 서비스 테스트 ===
curl -s http://localhost:8000/api/users 2>nul
echo.
echo === 주문 서비스 테스트 ===
curl -s http://localhost:8000/api/orders 2>nul
echo.
echo === 상품 서비스 테스트 ===
curl -s http://localhost:8000/api/products 2>nul
echo.
echo [SUCCESS] 테스트가 완료되었습니다.
goto end

:help
echo MSA Gateway Docker Compose 관리 스크립트 (Windows)
echo.
echo 사용법: %0 [명령어]
echo.
echo 명령어:
echo   start     - 모든 서비스 시작
echo   stop      - 모든 서비스 중지
echo   restart   - 모든 서비스 재시작
echo   status    - 서비스 상태 확인
echo   logs      - 모든 서비스 로그 확인
echo   logs [서비스명] - 특정 서비스 로그 확인
echo   health    - 서비스 헬스 체크
echo   test      - API 테스트 실행
echo   help      - 이 도움말 표시
echo.
echo 예시:
echo   %0 start
echo   %0 logs gateway
echo   %0 health
goto end

:end
endlocal 