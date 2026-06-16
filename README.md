# AI Smart Air Traffic Control Dashboard

실시간 항공기 데이터를 수집하고 통계적 분석을 통해 이상 징후를 탐지하는 웹 기반 항공 관제 대시보드입니다.

OpenSky Network API를 활용하여 대한민국 영공 내 항공기 정보를 실시간으로 수집하고, Z-Score 기반 이상치 탐지 알고리즘을 적용하여 급격한 강하와 같은 비정상적인 비행 상태를 식별합니다.

---

## Overview

항공 관제 환경에서는 수많은 항공기의 상태를 동시에 모니터링해야 합니다.

본 프로젝트는 실시간 비행 데이터 중 수직 속도(Vertical Rate)를 분석하여 통계적으로 비정상적인 움직임을 보이는 항공기를 자동으로 탐지하고, 관제사가 빠르게 상황을 파악할 수 있도록 지원하는 것을 목표로 합니다.

단순 임계값 방식이 아닌 Z-Score 기반 분석을 적용하여 전체 비행 상황 대비 상대적으로 위험한 항공기를 탐지하도록 설계하였습니다.

---

## Features

### Real-Time Flight Monitoring

* OpenSky Network API 연동
* 대한민국 영공 내 항공기 데이터 수집
* 위치, 고도, 속도, 수직 속도 등 주요 정보 제공

### Statistical Anomaly Detection

* 실시간 수직 속도 데이터 분석
* 평균 및 표준편차 계산
* Z-Score 기반 이상치 탐지
* 위험 항공기 자동 분류

### Interactive Dashboard

* Streamlit 기반 웹 대시보드
* 위험 기체와 정상 기체 시각적 구분
* 선택한 항공기의 상세 정보 조회

### Map Visualization

* Pydeck 기반 인터랙티브 지도
* 실시간 항공기 위치 시각화
* 위험 항공기 강조 표시

---

## System Architecture

```text
OpenSky Network API
          │
          ▼
  Flight Data Collection
          │
          ▼
    Data Processing
          │
          ▼
   Z-Score Analysis
          │
          ▼
  Risk Aircraft Detection
          │
          ▼
     Visualization
          │
          ▼
 Streamlit Dashboard
```

---

## Tech Stack

### Backend

* Python 3

### Data Analysis

* Pandas

### Visualization

* Pydeck

### Web Framework

* Streamlit

### API

* OpenSky Network API

---

## Challenges & Solutions

### Streamlit Runtime Environment

초기 개발 과정에서 일반 Python 실행 환경에서 Streamlit 애플리케이션을 실행하여 ScriptRunContext 관련 경고가 발생하였습니다.

이를 해결하기 위해 Streamlit 전용 실행 환경을 구성하고 run.bat 파일을 제작하여 안정적으로 실행할 수 있도록 개선하였습니다.

### Map Rendering Issue

Mapbox 인증 문제로 인해 지도 배경이 정상적으로 표시되지 않는 문제가 발생하였습니다.

별도 인증 없이 사용 가능한 CARTO 기반 지도 스타일로 변경하여 안정적인 지도 렌더링 환경을 구축하였습니다.

### Visualization Optimization

수도권과 같은 항공 교통 밀집 지역에서 마커가 겹쳐 보이는 문제를 해결하기 위해 마커 크기와 렌더링 옵션을 조정하여 가독성을 향상시켰습니다.

---

## Installation

```bash
pip install streamlit pandas pydeck
```

---

## Run

```bash
streamlit run app.py
```

또는

```bash
run.bat
```

을 실행하여 프로그램을 시작할 수 있습니다.

---

## My Contributions

* 시스템 구조 설계
* OpenSky Network API 연동
* 실시간 데이터 수집 및 처리
* Z-Score 기반 이상 탐지 알고리즘 구현
* Streamlit 대시보드 개발
* Pydeck 지도 시각화 구현
* UI 개선 및 디버깅
* 실행 환경 구성 및 최적화

---

## Future Improvements

* 비행 경로 예측 기능
* 머신러닝 기반 위험 탐지
* 위험도 등급 세분화
* 알림 시스템 구축
* 다중 국가 영공 지원

---

## Screenshots

프로젝트 실행 화면을 추가하면 시스템의 기능과 UI를 더욱 직관적으로 확인할 수 있습니다.

```text
docs/dashboard.png
```
