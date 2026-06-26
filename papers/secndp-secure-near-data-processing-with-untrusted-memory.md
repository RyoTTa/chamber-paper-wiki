---
tags: [paper, 2022, 2022HPCA, topic/dram, topic/near-data-processing, topic/pim, topic/security, topic/storage]
venue: "IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2022"
year: 2022
summary_path: "../paper-summaries/2022HPCA-summarize/secndp-secure-near-data-processing-with-untrusted-memory.md"
---

# SecNDP: Secure Near-Data Processing with Untrusted Memory

**Venue:** IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2022
**저자:** Wenjie Xiong, Liu Ke, Dimitrije Jankov, Michael Kounavis, Xiaochen Wang, Eric Northup, Jie Amy Yang, Bilge Acun, Carole-Jean Wu, Ping Tak Peter Tang, G. Edward Suh, Xuan Zhang, Hsien-Hsin S. Lee (Meta; Washington University in St. Louis; Rice University; Cornell University)

## 개요

- Data-intensive 애플리케이션에서 classical von Neumann 아키텍처의 memory bandwidth 병목이 핵심 성능 제약 → memory wall 문제 심화
- Near-Data Processing(NDP)는 DRAM이나 storage 근처에서 연산을 수행하여 데이터 이동을 줄이고 성능/에너지 효율을 개선하는 기술로 주목받음 (Samsung Aquabolt-XL HBM2-PIM 등)
- 민감한 데이터(개인 의료 기록, 추천 시스템 사용자 정보, IP 보호가 필요한 ML 모델 등)를 다루는 애플리케이션이 증가하면서 보안/프라이버시 보장이 일류 설계 관심사로 부상
- 기존 hardware TEE(Intel SGX, AMD SEV, ARM TrustZone 등)는 off-chip component를 untrusted로 간주하여 메모리 데이터를 암호화(CBC/CTR mode)하고 MAC으로 무결성 검증
- **문제점**: 기존 counter-mode 암호화는 암호화된 데이터 위에서의 연산을 지원하지 않음 → NDP PU가 ciphertext에 접근해야 하지만 기존 암호화 방식으로는 NDP 수행 불가
- **대안의 한계**:
  - Homomorphic Encryption(HE): 최소 4자릿수 이상의 성능 저하 (10,000× slowdown) → NDP가 TEE without NDP보다 성능 우위를 가질 수 없음
  - NDP PU를 TEE에 포함: 다중 하드웨어 벤더 신뢰 필요, 추가 key exchange 프로토콜, TCB 공격 표면 대폭 증가
- 현재까지 untrusted memory에서의 안전한 NDP를 위한 실용적 솔루션 부재

## 방법론

### 3.1. Arithmetic Encryption Scheme

- Plaintext P를 wc비트 chunk로 분할 → 블록 암호(AES)로 OTP 블록(e_0, e_1, ...) 생성
- 입력: chunk 시작 physical address + version number v → E(K, 00||Addr||v)
- 각 we비트 요소에 대해: ciphertext c_j = p_j - e_j mod 2^we (Fig. 3)
- **보안 원리**: ciphertext c_j와 OTP e_j가 arithmetic share 역할 → c_j + e_j = p_j (secret sharing)
- **보안 증명 (Theorem 1)**: Adversary의 CPA advantage ≤ 1/2^{w_K} + Adv_{E00}^{|Q'|} (AES 기반 블록 암호의 의사난수성에 기반)

### 3.2. Ciphertext 위의 연산

- **Non-private vector × private matrix 연산** (Fig. 4(a)):
  - 초기화(T0): 행렬 P를 Arithmetic-E로 암호화 → C = P - E (OTP) 저장
  - 연산(T1): NDP는 a×C 수행 (same as unprotected NDP), 프로세서는 a×E 수행
  - 결과 결합: res = a×C + a×E = a×(C+E) = a×P
- NDP 연산은 unprotected NDP와 동일 → NDP 하드웨어 수정 불필요
- 프로세서의 OTP share 연산은 on-chip에서 수행 → off-chip 추가 데이터 이동 없음

### 3.3. Verification Scheme

- Linear Modular Hashing (h_K(P_i))을 MAC으로 활용:
  - s = first w_t bits of E(K, 01||paddr(P)||v)
  - T_i = Σ_{j=0}^{m-1} P_{i,j} × s^{m-j} mod q (q = 거대 소수, 예: 2^{127}-1)
- Encrypted MAC (el-MAC): CT_i = T_i - E_T_i mod q (Fig. 3)
- **검증 과정**:
  - NDP는 암호화된 checksum에 대한 벡터 곱셈 수행 → CT_res = a×CT
  - 프로세서는 OTP에 대한 곱셈 수행 → ET_res = a×ET
  - CT_res + ET_res = h_K(res) = a×h_K(P) → 선형성 보장
- **보안 증명 (Theorem 2)**: Forgery probability ≤ m×|Q_v|/q + |Q_v|×(AES 보안 항들 + n)
  - q = 2^{127}-1 사용 시, 1024차원 행렬에 대해 2^{53} 쿼리까지 64비트 이상 보안 수준 유지

### 3.4. SecNDP vs TEE vs Unprotected NDP 비교 (Fig. 4)

- **TEE**: 모든 데이터를 매번 processor ↔ memory로 이동 → memory bandwidth 최대 소비
- **Unprotected NDP**: 데이터가 memory에 머무르며 NDP PU가 직접 연산 → bandwidth 절약 최대
- **SecNDP**: NDP 연산은 동일, 프로세서는 on-chip에서 OTP share만 처리 → unprotected NDP와 동일한 bandwidth 절약 + 보안 보장
- NDP 연산의 결과만 processor로 전송 → 최소한의 데이터 이동
- SecNDP engine의 복호화/검증은 NDP 연산과 병렬 수행 가능 → critical path에 adder 1개만 추가

## 핵심 기여

- **핵심 Contribution**: Untrusted NDP에서 ciphertext 위의 연산을 안전하게 수행할 수 있는 최초의 실용적 암호화/검증 방식 제시
- **성능**: 충분한 AES 엔진 사용 시 unprotected NDP와 근접한 성능(2.3×~7.46× speedup), Intel SGX 대비 수십 배~수백 배 성능 우위
- **보안**: Arithmetic secret sharing 기반 formal 보안 증명, counter-mode encryption의 낮은 복호화 지연 특성 활용
- **実用性**: NDP 프로토콜/하드웨어 변경 불필요, 기존 NDP 시스템에 경량 추가(OTP PU + final adder)로 통합 가능
- **의의**: TEE + NDP 결합의 실용성을 최초로 입증 →未来的 data-intensive 보안 애플리케이션의 NDP 채택 촉진
- **한계점**: NDP가 untrusted이므로 verification 실패 시 재시도/보상 메커니즘 필요, floating-point 연산 미지원 (정수/고정소수점 고정), NDP PU register 수가 intermediate results에 bottleneck 가능

## 주요 결과

- **ISA Extensions**:
  - `ArithEnc`: 초기 암호화 + verification tag 생성 (address, plaintext, key → ciphertext + tag)
  - `SecNDPInst`: NDP 연산 지시 (NDPInst와 동일 형식 + version number v + verification 비트 추가)
  - `SecNDPLd`: NDP 결과 로드 + 복호화 + 검증
- **SecNDP Engine 구성요소** (Fig. 5, 녹색 박스):
  - **Encryption Engine**: AES 기반 OTP 생성, NDP memory throughput에 맞는 수의 엔진 필요
  - **OTP PU**: 프로세서 측 share 연산 (NDP PU와 동일한 registers/logic, lightweight integer ALU)
  - **Verification Engine**: Linear checksum 계산
- **Verification Tag 저장 옵션** (Section V-D):
  - Ver-coloc: 데이터와 인접에 tag 배치 → 같은 DRAM row 활성화로 접근 시간/에너지 절약
  - Ver-sep: 별도 영역에 tag 배치 → 소프트웨어 레이아웃 변경 불필요 but 성능 저하
  - Ver-ECC: ECC chip에 tag 저장 → 대역폭 활용도 높지만 고정 용량 제약
- **Version number 관리**: TEE 내부 소프트웨어가 관리 → replay attack 방지, 메모리 영역별 version 공유 가능

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/security.md|Security]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2022HPCA-summarize/secndp-secure-near-data-processing-with-untrusted-memory.md|전체 요약 보기]]
