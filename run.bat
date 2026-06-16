@echo off
title AI Smart Aviation Control Tower Dashboard Launcher
chcp 64001 >nul
cls

echo =========================================================================
echo       [AI 스마트 항공 관제탑 대시보드 원클릭 자동 실행 스크립트]
echo =========================================================================
echo.
echo [*] 사용자 시스템 환경의 파이썬 핵심 웹 라이브러리 구성을 검사합니다...

:: 1. 필수 라이브러리(streamlit, pydeck, pandas) 로드 검사 및 미설치 시 강제 셋업
python -c "import streamlit" 2>nul
if %errorlevel% neq 0 (
    echo [!] 'streamlit' 라이브러리가 누락되었습니다. 즉시 인스톨러를 가동합니다.
    pip install streamlit
) else (
    echo [OK] 'streamlit' 엔진 감지 완료.
)

python -c "import pydeck" 2>nul
if %errorlevel% neq 0 (
    echo [!] 'pydeck' 공간 맵핑 라이브러리가 누락되었습니다. 즉시 인스톨러를 가동합니다.
    pip install pydeck
) else (
    echo [OK] 'pydeck' 공간 맵핑 라이브러리 감지 완료.
)

python -c "import pandas" 2>nul
if %errorlevel% neq 0 (
    echo [!] 'pandas' 매트릭스 연산 프레임워크가 누락되었습니다. 즉시 인스톨러를 가동합니다.
    pip install pandas
) else (
    echo [OK] 'pandas' 매트릭스 연산 프레임워크 감지 완료.
)

echo.
echo =========================================================================
echo [*] 모든 필수 라이브러리 적합성 검증 완료. Streamlit 서버를 부팅합니다.
echo [안내] 잠시 후 기본 웹 브라우저를 통해 실시간 대시보드 웹 UI 창이 자동 활성화됩니다.
echo =========================================================================
echo.

:: 2. Streamlit 대시보드 런처 즉각 구동
python -m streamlit run app.py

pause