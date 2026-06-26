---
tags: [paper, 2018, 2018HPCA, topic/compression, topic/dram, topic/rowhammer]
venue: "24th IEEE International Symposium on High Performance Computer Architecture (HPCA '18)"
year: 2018
summary_path: "../paper-summaries/2018HPCA-summarize/enabling-fine-grain-restricted-coset-coding-through-word-level-compression-for-pcm.md"
---

# Enabling Fine-Grain Restricted Coset Coding Through Word-Level Compression for PCM

**Venue:** 24th IEEE International Symposium on High Performance Computer Architecture (HPCA '18)
**저자:** Seyed Mohammad Seyedzadeh (University of Pittsburgh), Alex K. Jones (University of Pittsburgh), Rami Melhem (University of Pittsburgh)

## 개요

- **Phase Change Memory (PCM)**: DRAM을 대체할 유망한 비휘발성 메모리 기술
  - 스케일링 가능, 낮은 접근 지연 시간, 무시할 수 있는 대기 전력
  - Multi-Level Cell (MLC) PCM: 높은 밀도, 낮은 바이트당 제조 비용
- **MLC PCM의 문제**: 중간 상태 프로그래밍 에너지가 SLC PCM 대비 **10배**
  - Program-and-Verify (P&V) 기법 사용 → 셀 리셋 후 반복적 SET 펄스
  - 셀 내구성 저하, 쓰기 에너지 증가, 쓰기 왜곡(write disturbance) 발생
- **인코딩 기반 쓰기 에너지 절감 기법의 한계**:
  - 기존: 캐시 라인 크기 (512비트) 단위로 인코딩 → 쓰기 에너지 절감
  - 세밀한 인코딩 (8~16비트) 시도 시: **보조 비트(auxiliary bits) 증가** → 쓰기 에너지 절감을 상쇄하거나 초과
- 핵심 문제: **세밀한 인코딩 세밀화(granularity)에서도 쓰기 에너지를 효과적으로 절감하는 방법 부재**

## 방법론

### 3.1. Coset Coding 배경
- MLC PCM의 2비트 심볼: 4가지 상태 (00, 01, 10, 11)
- 쓰기 에너지: 상태별로 다름 (HIGH 상태가 가장 높음)
- Coset coding: 데이터를 쓰기 에너지가 낮은 대체 코드워드로 매핑
- **제약 조건**: 같은 coset의 코드워드끼리만 매핑 (디코딩 불필요)

### 3.2. Restricted Coset Encoding
- 기존 coset coding의 확장: 코드 매핑 시 **쓰기 에너지 + 빈도 분포** 동시 고려
- 512비트 메모리 라인을 16비트 서브블록으로 분할
- 각 서브블록에 대해 제약된 코딩 적용:
  - 높은 빈도 + 높은 에너지 심볼 → 낮은 에너지 심볼로 매핑
  - 코드 매핑 선택 시 비트 패턴 빈도 고려
- 보조 심볼: 각 서브블록의 인코딩 정보를 저장 → 라인 내에 저장 가능

### 3.3. Word-Level Compression (WLC)
- **핵심 관찰**: 메모리 라인의 워드들은 유사한 특성 공유
  - 예: 메모리 라인의 대부분의 워드가 0으로 초기화된 경우가 많음
- **WLC 알고리즘**:
  1. 메모리 라인을 워드 단위로 분할
  2. 각 워드의 값을 비교하여 압축 가능한 워드 식별
  3. 동일한 값을 가진 워드를 단일 워드로 압축 + 마스크 저장
  4. 91% 이상의 라인에서 압축 가능 (기존 압축: ~50%)
- **장점**: 가벼운 압축 로직 (버튼 포인트 연산) + 높은 압축 가능 라인 비율

### 3.4. 통합 인코딩 파이프라인
- 메모리 쓰기 요청 → WLC 압축 → Restricted Coset Encoding → PCM 쓰기
- 디코딩: PCM 읽기 → Coset 디코딩 → WLC 디코딩 → 원본 데이터 복원
- **오버헤드**: 매우 낮음 (온칩 구현 가능, 면적 오버헤드 미미)

## 핵심 기여

- **핵심 기여**: MLC PCM의 쓰기 에너지 절감을 위한 세밀한 인코딩 세밀화와 WLC 기반 보조 심볼 저장 기법
- **성능**: 16비트 세밀화에서 기존 기법 대비 39% 쓰기 에너지 절감
- **내구성/신뢰성**: 20% 내구성 향상 + 쓰기 왜strup 확률 감소
- **실용성**: 매우 낮은 하드웨어 오버헤드로 온칩 구현 가능
- **의의**: PCM 기반 차세대 메모리 시스템의 에너지 효율성과 수명 향상에 기여

## 주요 결과

- **인코딩/디코딩 하드웨어**: Verilog RTL 구현
- **평가 플랫폼**: MLC PCM 모델 (4가지 상태)
- **파워 모델**: 기존 MLC PCM 쓰기 에너지 모델 기반
- **암호화**: 다양한 워크로드의 비트 패턴 분석

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]


## 전체 요약

[[../paper-summaries/2018HPCA-summarize/enabling-fine-grain-restricted-coset-coding-through-word-level-compression-for-pcm.md|전체 요약 보기]]
