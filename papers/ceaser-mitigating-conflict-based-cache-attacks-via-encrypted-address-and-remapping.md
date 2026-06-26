---
tags: [paper, 2018, 2018MICRO, topic/cache, topic/dram]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/ceaser-mitigating-conflict-based-cache-attacks-via-encrypted-address-and-remapping.md"
---

# CEASER: Mitigating Conflict-Based Cache Attacks via Encrypted-Address and Remapping

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Moinuddin K. Qureshi (Georgia Institute of Technology)

## 개요

- 모던 프로세서는 모든 코어가 Last-Level Cache(LLC)를 공유하지만, 이러한 공유는 캐시 기반 사이드 채널 공격에 취약
- **Confllict-based cache attacks:** 공격자가 캐시 충돌을 정교하게 조작하여 공동 실행 중인 애플리케이션의 접근 패턴을 추론 → AES 키 등 비밀 정보 탈취 가능 (Spectre/Meltdown 등)
- 기존 완화 기법의 한계:
  - **보존 기반(Preservation-based):** 특정 코어에 캐시 부분을 전용 → 캐시 공간 비효율적 사용
  - **랜덤화 기반(Randomization-based):** 매핑 테이블 사용 → 테이블 크기가 LLC에서는 비현실적으로 크고, OS가 애플리케이션을 보호/비보호로 분류해야 함
- Eviction Set(동일 세트에 매핑되는 라인 그룹)을 구성하면 공격 가능 → 정적 해시 함수로 인해 한 번 학습한 매핑이 모든 머신에 동일하게 적용

## 방법론

### 3.1. CEASE: 암호화된 주소 기반 캐시

- **LLBC (Low-Latency Block-Cipher):**
  - b비트 PLA를 b비트 ELA로 변환
  - 암호화/복호화가 **2사이클** 내에 수행 가능하도록 최적화
  - 암호화의 avalanche effect로空间적 상관관계가 있는 PLA 라인들이 EAS에서 무작위로 분산
- **캐시 접근:**
  - LLC 접근 시 PLA를 ELA로 변환 후 캐시 인덱싱
  - 태그 매칭은 암호화된 라인 주소로 수행
- **Eviction Set 학습 방지:** 랜덤 키에 의해 매핑이 결정되므로 한 머신에서 학습한 eviction set이 다른 머신이나 다른 키에서는 유효하지 않음

### 3.2. CEASER: 동적 리매핑

- **에포크 기반 키 변경:**
  - 시간을 에포크로 분할, 각 에포크마다 고유 키 사용
  - 에포크 종료 시 현재 키(CurrKey)를 NextKey로 변경하고 새로운 무작위 키를 NextKey에 설정
- **점진적 리매핑 (Gradual-Remapping):**
  - **Bulk-Remap:** 에포크 종료 시 모든 캐시 라인을 한 번에 리매핑 → 비현실적 (동시 리매핑 필요)
  - **Gradual-Remap (기본 설계):** 에포크 기간 동안 캐시 라인을 점진적으로 리매핑
- **점진적 리매핑 메커니즘:**
  - **SPtr (Set-Relocation Pointer):** 다음에 리매핑할 세트를 추적
  - **ACtr (Access-Counter):** 캐시 접근 횟수 추적, 리매핑 트리거 결정
  - **APLR (Accesses-Per-Line-Remap):** 리매핑 속도 조절 파라미터 (기본값: 100)
  - APLR=K 설정 시, W-way 캐시에서 W×K 접근마다 한 세트 리매핑 → 전체 캐시 리매핑에 K×N 접근 필요
- **EpochID (EID):** 현재/다음 에포크의 라인을 구분하기 위한 1비트 식별자
  - 두 에포크의 라인이 동시에 캐시에 공존할 수 있으므로 EID로 암호화된 주소 구분

### 3.3. CEASER 캐시 접근 흐름

- LLC 접근 시 CurrKey와 NextKey로 각각 암호화 수행
- 셋 인덱스가 SPtr 이상이면 NextKey 매핑 사용, 미만이면 CurrKey 매핑 사용
- EID(에포크 ID)와 함께 태그 매칭 수행 → 정상적인 캐시 접근/설치 진행

### 3.4. 은행 기반 공유 캐시 고려

- 일부 프로세서 설계에서는 LLC가 은행(bank)으로 분할되고, 은행 간 접근 레이턴시 차이 존재
- CEASER는 은행 간 레이턴시 차이가 없다고 가정하지만, 은행 기반 캐시에서도 확장 가능

## 핵심 기여

- **핵심 기여:** 암호화된 주소 공간과 동적 리매핑을 결합하여 LLC의 conflict-based 캐시 공격을 효과적으로 완화하는 CEASER 제시
- **보안:** 100년 이상의 연속 공격 견딤으로 실질적인 보안 보장
- **효율성:** 1% 성능 오버헤드, 24바이트 미만 스토리지로 높은 실용성
- **독립성:** OS 지원 불필요로 기존 시스템과의 통합 용이
- **의의:** Spectre/Meltdown 등 캐시 기반 사이드 채널 공격에 대한 실용적인 하드웨어 완화 방안 제시

## 주요 결과

- **하드웨어 오버헤드:**
  - LLBC 암호화/복호화 유닛: 2사이클 지연
  - SPtr, ACtr 레지스터: 리매핑 관리
  - EpochID(EID): 1비트 per 캐시 라인
  - 추가 스토리지: **24바이트 미만** (새로 추가된 구조체)
- **성능 오버헤드:** 평균 **1% 느림**
- **OS 지원:** 불필요 (완전히 하드웨어 기반)
- **보안:** 100년 이상의 연속적인 공격을 견딜 수 있는 강건성

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/ceaser-mitigating-conflict-based-cache-attacks-via-encrypted-address-and-remapping.md|전체 요약 보기]]
