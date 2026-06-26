---
tags: [paper, 2025, 2025HPCA, topic/dram, topic/llm-inference, topic/nvm, topic/storage]
venue: "2025 IEEE International Symposium on High Performance Computer Architecture (HPCA 2025)"
year: 2025
summary_path: "../paper-summaries/2025HPCA-summarize/lincoln-real-time-llm-on-consumer-devices-with-compute-enabled-flash.md"
---

# Lincoln: Real-Time 50∼100B LLM Inference on Consumer Devices with LPDDR-Interfaced, Compute-Enabled Flash Memory

**Venue:** 2025 IEEE International Symposium on High Performance Computer Architecture (HPCA 2025)
**저자:** Weiyi Sun, Mingyu Gao, Zhaoshi Li, Aoyang Zhang, Iris Ying Chou, Jianfeng Zhu, Shaojun Wei, Leibo Liu (Tsinghua University, Shanghai Qi Zhi Institute, MetaX Technology)

## 개요

- 소비자 디바이스(노트북, 모바일)에서 LLM 추론을 로컬로 실행하려는 수요가 증가하고 있으나, 기존 시스템은 13B 미만의 소형 LLM만 실시간 추론 지원
  - Apple, OPPO, Intel, Qualcomm 등이 소비자 디바이스로 LLM 추론 이동을 추진 중
  - Llama-3.1 8B vs 70B의 MMLU-Pro 점수: 48.3 vs 66.4 → 모델 크기가 품질에 핵심적 역할
  - Quantization, pruning은 품질 저하를 유발하므로 정확도 손실 없는 50∼100B 모델 실시간 추론이 목표
- 소비자 디바이스는 폼 팩터 제한으로 ≤64GB DRAM을 보유 → 50B 모델(>100GB), 100B 모델(>200GB)의 대부분 가중치가 Flash에 저장
- Flash 기반 가중치 로딩이 추론 시간의 대부분을 차지:
  - 기존 NVMe SSD 기반 시스템(Base-2)에서 디코딩 단계 토큰당 최대 **41.8초** 소요
  - 그 중 Flash→DRAM 가중치 로딩이 **94.0%** 차지
  - 프리필링 단계에서도 가중치 로딩이 **91.4%** 차지
- Flash의 성능 병목 요인 2가지:
  1. **전송 인터페이스 대역폭 부족:** SoC의 대부분 고속 오프칩 대역폭이 LPDDR에 할당 (128+ 핀), NAND Flash는 4~8 레인만 할당 → 외부 I/O 대역폭 ~10GB/s
  2. **Flash 내부 대역폭 부족:** 밀도 중심 설계 → 큰 배열, 높은 지연시간(>50μs), 낮은 병렬성 → 32 die, 4 plane에서도 최대 41GB/s에 불과

## 방법론

### 3.1. LPDDR 기반 패키징 및 인터커넥트

- **물리적 구조 (Figure 4(a)):**
  - LPDDR 스타일 패키지에 Lincoln Flash die 4개 + DRAM die 4개 수직 적층
  - 2개의 수직 스택을 하나의 패키지에 배치, 모든 die는 bonding wire로 패키지 핀에 연결
  - Flash die가 기존 LPDDR 채널의 추가 rank로 동작 → 별도 채널 추가 없이 기존 채널 핀 공유
  - DRAM과 Flash rank는 flat 메모리 공간으로 소프트웨어에서 직접 접근 가능
- **논리적 구조 (Figure 4(b)):**
  - SoC의 메모리 컨트롤러(MC)가 4개 채널에 연결
  - 각 채널: Flash rank 1개 + DRAM rank 1개
  - 각 rank: 2개 die, 각 die는 16비트 채널의 8 DQ 핀에 연결
- **장점:** 기존 LPDDR 인터페이스/패키지를 재사용하므로 비용과 폼 팩터 오버헤드 최소화

### 3.2. Lincoln Flash 레이어 설계

- **XL-Flash 기반 확장:** 기존 4μs 지연, 16 plane을 개선
  - 플레인 크기를 비트라인 방향으로 약 절반 축소 → 읽기 지연시간 **3.426μs**, plane 수 **32개**로 증가
  - die당 내부 읽기 대역폭 **~34GB/s**, 16 die에서 **~500GB/s**
- **밀도 문제 해결 (하이브리드 본딩):**
  - 주볔回路(page buffer, PHY 등)를 별도의 로직 레이어로 3D 적층
  - Flash 배열 레이어와 로직 레이어를 하이브리드 본딩으로 연결
  - 면적 효율성: XL-Flash ~55% → Lincoln **74.6%** 향상
  - 하이브리드 본딩의 지연시간 영향: **<0.1%** (기생 효과 <1fF, ~1Ω)
- **전원 공급 문제 해결:**
  - 병렬 플래인 동작 시 전원 노이즈 발생 가능
  - 기존 전원 도메인을 복제하여 각 복제본이 제한된 수의 플래인에 전원 공급
  - 핀 수 증가는 최신 8채널 LPDDR 설계보다 적고, BGA 지원 한도(700+) 내

### 3.3. 논리 레이어: LPDDR 인터페이스

- **기본 설계:**
  1. NPU MC가 Flash 컨트롤러의 커맨드 버퍼에 프리페치 명령 기록
  2. Flash 플레인에서 데이터 읽기 → 글로벌 버퍼로 이동 (각 플래인별 전용 공간)
  3. NPU가 상태 레지스터를 폴링하여 읽기 완료 확인 후 LPDDR 접근
  4. 전체 파티션에 대한 ECC 수행 후 NPU 계산 시작
- **최적화 (더블 버퍼링 + 근처 Flash ECC):**
  - **더블 버퍼링 기반 프리페치:** 현재 파티션 계산 중 다음 파티션 프리페치 명령 발행 → Flash 읽기 지연 완전 숨김
    - LPDDR 대역폭이 Flash 내부 대역폭의 1/4 이하이므로 계산 시간이 프리페치 지연의 4배 이상 → 프리페치 완전 겹침 가능
  - **근처 Flash ECC 모듈:** 각 플래인 아래에 ECC 모듈 배치 → Flash 읽기 후 ECC 수행 → 중복 LPDDR 접근 제거
    - ECC 레이턴시도 더블 버퍼링으로 완전 숨김

### 3.4. 근처 Flash 로직: Near-Flash Computing

- **FP-Dot 유닛 (Figure 4(c)):**
  - 각 Flash 플래인 아래의 Logic Block(LB)에 2요소 내적(dot product) 로직 배치
  - 400MHz 보수적 클럭에서도 플래인당 1.06GB/s 대역폭 충분히 처리
  - 로컬 레지스터 파일로 중간 결과 저장
- **ECC 설계:** SLC 기반으로 상대적으로 강건 → 간단한 BCH 코드 사용 (최대 64비트 오류 정정)
- **스페큘레이티브 디코딩 (>100B 모델 지원):**
  - 소형 드래프트 모델(~1B)로 다음 ~7개 토큰 예측 → 대형 모델로 일괄 검증
  - 드래프트 모델이 대형 모델보다 ~100배 작으므로 토큰당 레이턴시, 메모리 트래픽, 에너지 절감
  - FP-Dot 유닛 복제 및 레지스터 파일 확장으로 지원 (면적 오버헤드 미미)

### 3.5. 데이터 레이아웃 및 워크플로우

- **데이터 레이아웃 (Figure 6):**
  - 행렬을 글로벌 버퍼 크기에 맞는 큰 파티션으로 분할
  - 파티션 내 행을 die에 round-robin 분배 → 근처 Flash 연산과 NPU LPDDR 채널 병렬성 동시 활용
  - die 내에서 plane에도 round-robin 분배, 동일 페이지 주소 할당 (멀티 플래인操作 호환)
- **근처 Flash 컴퓨팅 워크플로우:**
  1. NPU가 입력 벡터를 모든 Flash die의 글로벌 버퍼에 브로드캐스트
  2. 각 플래인에서 파티션 행에 해당하는 Flash 페이지 읽기 + ECC
  3. 컨트롤러가 입력 벡터를 각 플래인에 순차 브로드캐스트 → 각 근처 Flash 유닛이 내적 수행
  4. 최종 결과를 글로벌 버퍼로 이동 후 NPU가 읽기
  - Flash 페이지 읽기와 계산을 파이프라인화, 파티션 간 입/출력 겹침
- **NPU 실행:**
  - 파티션 데이터를 타일 단위로 접근, round-robin 분배로 LPDDR 채널 병렬성 완전 활용
  - 글로벌 SRAM 버퍼 덕분에 임의 순서로 타일 접근 가능 (성능 손실 없음)

### 3.6. 내구성 관리

- **Read Disturb 문제:** LLM 가중치는 자주 업데이트되지 않으나 빈번한 읽기 발생
  - SLC Flash는 10K 읽기 사이클까지 견딜 수 있으나, 2시간 내 초과 가능
- **해결책 (Read Reclaim):** P/E(Program/Erase) 사이클로 read disturb 오류 리셋
  - SLC는 최대 100K P/E 사이클, 보존 시간을 1년→3일로 줄이면 **4M P/E 사이클**까지 향상
  - 가중치는 거의 갱신되지 않으므로 마모 균등화(wear leveling) 용이
  - 5년 보증 기간, 5K 읽기 사이클 임계값 가정 시 최대 P/E 소비: **310K** (4M 대비 7.8%)
  - 읽기 리클레임을 매 실행 반복마다 분산 수행 → ~0.4% 실행 시간 오버헤드

### 3.7. 제어 시스템 (Figure 7)

- **Management Layer(ML):** 주소 변환, 마모 균등화, 읽기 리클레임 등 고수준 관리 → 트랜잭션 레벨 명령 발행
- **Operation Layer(OL):** Flash 컨트롤러(FC)에서 마이크로 연산으로 분해하여 실행
- **ML-OL 인터페이스:** LPDDR를 통해 Flash 컨트롤러의 커맨드 버퍼/상태 레지스터에 접근
- **NPU 접근 가속:** Lincoln Access Unit(LAU) 추가 →高效的 타일 접근 및 주소 변환 지원

## 핵심 기여

- **핵심 기여:** 소비자 디바이스에서 50∼100B LLM의 실시간 추론을 가능하게 하는 디바이스-아키텍처 공동 설계
- **성능:** 프리필 최대 **13.23×**, 디코딩 최대 **254.1×** 가속 (기존 SSD 기반 대비)
- **혁신성:**
  1. LPDDR 인터페이스를 Flash에 적용하여 전송 대역폭 병목 해결 (프리필)
  2. 하이브리드 본딩 기반 근처 Flash 컴퓨팅으로 Flash 내부 대역폭 완전 활용 (디코딩)
  3. 스페큘레이티브 디코딩 통합으로 실시간 레이턴시 목표 달성
  4. 디바이스 레벨 배열 축소 + 아키텍처 레벨 인터페이스 최적화의 공동 설계
- **비용 효율성:** 기존 LPDDR 인터페이스/패키지 재사용, 근처 Flash 로직은 기존 로직 레이어의 빈 공간 활용 → 추가 비용 최소화
- **실용성:** 하이브리드 본딩은 이미 상용 Flash 제품에서 채택된 기술, SLC Flash의 높은 내구성(100K P/E 사이클)으로 5년 이상 서비스 가능
- **의의:** Flash 스토리지의 내부/전송 대역폭 병목을 디바이스와 아키텍처 레벨에서 동시에 해결하여, 소비자 디바이스에서 대형 LLM의 실시간 추론이라는 기존의 난제를 해결

## 주요 결과

- **시뮬레이터:** ONNXim (NPU), Ramulator 2 (DRAM/LPDDR), NVSim 기반 3DFPIM (Flash 배열), MQSim (NVMe SSD), HotSpot (열 분산)
- **NPU:** 32 TOPS (BF16 Tensor Core), 4.60W
- **Lincoln Flash:** SLC, 96 워드라인 레이어, (4KB + 448B ECC)/페이지, 768 페이지/블록, 177 블록/플레인, 32 플레인
  - tR = 3.426μs, 페이지 읽기 에너지 = 98.0nJ
  - 면적: 72.99mm² (Flash 레이어), 71.0mm² (로직 레이어)
- **근처 Flash 로직:** 16 FMACs + 8KB 레지스터 파일/플레인, BCH ECC
- **스토리지 구성 비교:** TLC, 2TB, tR=56μs, 8채널×4die×4플레인, NVMe PCIe 4.0 (8GB/s)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2025HPCA-summarize/lincoln-real-time-llm-on-consumer-devices-with-compute-enabled-flash.md|전체 요약 보기]]
