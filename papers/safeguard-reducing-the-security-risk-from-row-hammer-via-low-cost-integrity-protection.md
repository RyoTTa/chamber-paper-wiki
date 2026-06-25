---
tags: [paper, 2022, 2022HPCA, topic/cache, topic/dram, topic/rowhammer, topic/security, topic/storage]
venue: "IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2022"
year: 2022
summary_path: "../paper-summaries/2022HPCA-summarize/safeguard-reducing-the-security-risk-from-row-hammer-via-low-cost-integrity-protection.md"
---

# SafeGuard: Reducing the Security Risk from Row-Hammer via Low-Cost Integrity Protection

**Venue:** IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2022
**저자:** Ali Fakhrzadehgan (UT Austin), Yale N. Patt (UT Austin), Prashant J. Nair (UBC), Moinuddin K. Qureshi (Georgia Tech)

## 개요

- **RowHammer (RH) 위협 심화**: DRAM 공정 미세화로 셀 간 간격 축소 → RH 임계값이 2014년 139K(DDR3)에서 2020년 **4.8K(LPDDR4)**로 **약 30배 감소**
- 기존 RH 완화 기술은 특정 임계값과 공격 패턴을 가정 → 새로운 공격 패턴이 지속적으로 기존 방어를 우회
  - **Half-Double** (Google): 인접 행이 아닌 거리-2의 victim 행까지 disturbance 전파 → 정확한 mitigation 무력화
  - **TRRespass**: TRR의 추적 용량 제한을 이용한 capacity-based eviction 공격 → DDR4/DDR5의 TRR 우회
  - **ECCploit**: ECC correction 시간차를 이용한 timing channel 공격 → ECC 칩에서도 multi-bit failure 유발 가능
- RH 문제는 단순한 **reliability 문제가 아닌 심각한 security 위협**: 공격자가 임의 비트를 플리핑하여 privilege escalation 및 기밀 데이터 유출 가능
- 현재 RH에 대한 **보장된 해결책이 없음** → 완화 기술이 우회되더라도 시스템이 안전해야 함

## 방법론

### 3.1. SafeGuard with SECDED

- **기존 SECDED**: 64비트 데이터 + 8비트 ECC → word 단위(8바이트) 보호
- **SafeGuard**: 64비트 ECC를 cache-line 단위(64바이트)로 재구성
  - **10비트**: ECC-1 (단일 오류 교정 — 64-byte 라인 전체)
  - **8비트**: Column parity (핀 실패 대응)
  - **46비트**: MAC (강력한 무결성 탐지)
- MAC 계산: 컨트롤러가 라인 주소 + 16바이트 키를 연결 → QARMA 암호화(2.2ns 지연)로 8개 64비트 워드를 암호화 → XOR로 64비트 MAC 생성
- **읽기 시 동작**: ECC-1 교정 → MAC 계산 → 저장된 MAC과 비교 → 불일치 시 DUE(Detected Unrecoverable Error) 보고
- **신뢰성**: 두 독립 단일 비트 오류가 동일 cache-line의 다른 워드에 동시에 발생할 확률은 **3.51×10⁻⁵**로 극히 낮음 → SECDED 대비 동등한 교정 능력 유지

### 3.2. SafeGuard with Chipkill

- **기존 Chipkill**: x4 디바이스 18개(데이터 16개 + 메타데이터 2개) 사용, 심벌 기반 코드로 심벌 교정/탐지
- **SafeGuard re-design**: 데이터를 평문으로 저장, 두 메타데이터 칩을 각각 **32비트 MAC**과 **32비트 칩별 패리티**로 사용
- **Eager Correction**:
  - 기존 iterative correction: 최대 16회 반복 → MAC-32의 탐지 회피 위험 (평균 10억 번의 메모리 접근으로 1분 내 탐지 실패 가능)
  - **해결**: 마지막 실패 칩 ID를 추적 → 첫 번째 MAC 검증 건너뛰고 해당 칩을 긴급 복구 → MAC 검증
  - 영구 칩 실패 시 iterative correction의 지연 오버헤드 제거
  - 다중 칩 실패 시 iterative correction으로 fallback → 탐지 후 DUE 보고

### 3.3. Column Failure 대응

- Column failure: 핀 실패로 동일 위치의 여러 워드에서 비트 오류 발생 → SafeGuard만으로는 교정 불가
- **Column Parity**: 8비트 수직 패리티 저장 (64개 심볼의 XOR)
- **Iterative correction**: 각 열 위치를 순회하며 패리티로 복구 → MAC 검증으로 올바른 위치 확인
- Column failure 발생 빈도: 평균 **100년에 1회 이상** (16GB DIMM 기준) → 드문 이벤트

## 핵심 기여

- **핵심 기여**: RowHammer mitigation이 우회되더라도 시스템을 안전하게 유지하는 저비용 무결성 보호 방식 제시
- **패러다임 전환**: "RH 완화가 실패하면 security 위협" → "RH 비트 플리핑을 탐지하여 reliability 문제로 전환"
- **Zero-overhead 설계**: DRAM 저장 오버헤드 **제로**, 성능 오버헤드 **0.7%** — 기존 ECC 인프라 완전 재사용
- **실용성**: SECDED/Chipkill 모두에서 구현 가능, 기존 ECC DIMM 변경 없이 메모리 컨트롤러 수정만으로 구현
- **보안 관점**: RH 기반 비트 플리핑이 tamper detection으로 보호됨 → privilege escalation 방지, 데이터 무결성 보장
- **한계점**: DoS 취약성(지속적 실패 시 프로세스 재시작 필요), Replay attack 미보호, MAC 충돌 이론적 가능성
- **미래 지향성**: 메모리 신뢰성 감소와 복잡한 보안 공격 시대에 SafeGuard와 같은 무결성 보호가 점점 더 필요

## 주요 결과

- **MAC 계산**: QARMA 저지연 암호화 회로 (2.2ns) 사용 가능
- **SECDED SafeGuard**: 3K XOR 게이트 (ECC 로직) + MAC 계산 유닛 + 16바이트 키 저장
- **Chipkill SafeGuard**: 칩별 패리티 계산 로직 + MAC 유닛 + 실패 칩 추적 레지스터 + 카운터
- **총 SRAM 오버헤드**: **32바이트 미만**
- **DRAM 오버헤드**: **제로** — ECC 비트 재사용
- **시뮬레이터**: execution-driven cycle-accurate 시뮬레이터 + Ramulator (메모리 모델링)
- **신뢰성 평가**: FaultSim 사용, 1000만 디바이스 Monte Carlo 시뮬레이션 (7년 기간)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]
- [[paper-wiki/concepts/security.md|Security]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2022HPCA-summarize/safeguard-reducing-the-security-risk-from-row-hammer-via-low-cost-integrity-protection.md|전체 요약 보기]]
