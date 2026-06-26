---
tags: [paper, 2022, 2022HPCA, topic/cache, topic/disaggregation, topic/gpu, topic/storage]
venue: "IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2022"
year: 2022
summary_path: "../paper-summaries/2022HPCA-summarize/enabling-efficient-large-scale-dl-training-with-cache-coherent-disaggregated-memory-systems.md"
---

# Enabling Efficient Large-Scale Deep Learning Training with Cache Coherent Disaggregated Memory Systems

**Venue:** IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2022
**저자:** Zixuan Wang (University of California, San Diego), Joonseop Sim (University of California, San Diego), Euicheol Lim (System Architecture Division, SK hynix), Jishen Zhao (University of California, San Diego)

## 개요

- 딥러닝(DL) 학습은 모델 크기와 데이터셋의 지속적인 증가로 인해 단일 장치의 메모리 용량과 크로스 디바이스 통신 대역폭에 심각한 제약을 받음
- 기존 분산 학습 접근법(데이터 병렬화, 모델 병렬화, 파이프라인 병렬화)은 추가적인 코드 복잡성과 트레이드오프를 도입하며, 항상 학습 가속으로 이어지지 않음
- 교차 디바이스 통신 오버헤드가 전체 학습 시간의 **최대 76%**까지 차지하며, GPU 활용도와 학습 성능을 크게 저하시킴 (Figure 2)
- MPI AllReduce 기반 분산 통신은 동기화 시점에서 빠른 워커가 느린 워커를 기다리도록 강제하여 GPU 계산 활용도를 떨어뜨림
- 기존 파라미터 서버 중앙 집중식 설계에서는 CPU의 제한된 직렬 버스 라인이 GPU의 동시 메모리 접근을 병목으로 만들며, Ring AllReduce는 최저 디바이스 간 대역폭에 의해 성능이 제한됨 (NVIDIA DGX-1에서 대역폭 활용도 **34%** 수준)

## 방법론

### 3.1. 비중앙집중적 파라미터 동기화

- **파라미터 계층 구조**: parameter client (워커 GPU), parameter proxy (메모리 디바이스), parameter storage (메모리 디바이스)의 3단계 구조
- 각 워커 GPU는 전용 파라미터 클라이언트를 운영하며, 로컬 파라미터를 유지하고 전용 프록시와 통신
- 프록시는 클라이언트와 파라미터 스토리지 사이의 브리지 역할을 수행하며, 로컬 파라미터 캐시도 유지
- 로컬 클라이언트-프록시 및 프록시-스토리지 페어 간 통신을 로컬화하여 CCI 경로의 트래픽 부하를 줄임
- Figure 7에서 3단계 계층 구조를 통해 파라미터 동기화가 분산되는 것을 보여줌

### 3.2. 텐서 라우팅 및 파티셔닝

- **비균일 파라미터 크기 및 대역폭 분포 관찰**: AWS V100 인스턴스에서 로컬 PCIe 대역폭(9GB/s)이 원격 대역폭(16GB/s)보다 낮은 "안티 로컬리티" 현상 발견 (Figure 8)
- 작은 크기 파라미터(< 2MB)는 지연 시간에 민감하고, 큰 크기 파라미터는 대역폭에 민감함
- **텐서 라우팅**: 사전 프로파일링을 통해 각 클라이언트의 라우팅 테이블 구축 — 데이터 크기 임계값에 따라 LatProxy(저지연) 또는 BwProxy(고대역폭)로 라우팅
- **텐서 파티셔닝**: 큰 텐서를 동일 크기의 작은 샤드로 분할하여 파이프라인 방식으로 동기화 → 직렬 버스 양방향 대역폭 완전 활용 (Figure 9)
- **동적 파티셔닝**: 프로파일러가 학습 전 통신 대역폭을 측정하고, 최소 샤드 크기 S'를 결정하여 대역폭 포화 달성

### 3.3. 이중 파라미터 동기화

- **우선순위 기반 이중 동기화**: DL 모델의 backward pass에서 첫 번째 레이어들의 텐서는 역순으로 업데이트되지만 다음 반복의 forward pass에서 즉시 사용되므로 우선 동기화 필요
- 첫 번째 레이어들의 텐서는 워커 GPU에서 동기화하고, 나머지 레이어의 텐서는 프록시로 푸시하여 프록시가 동기화
- **최적 분할점 m 계산**: Ttrain = max{TFP + TBP + Tsync(GPU), TFP + Tsync(proxy)}를 최소화하는 m값 산출
- **데드락 방지**: 큐 기반 동기화 — 프록시는 각 클라이언트별 큐를 유지하고 모든 큐를 동시 동기화하여 단일 텐서 동기화에 차단되지 않음

### 3.4. Sync Core 및 하드웨어 설계

- **Sync Core**: 메모리 디바이스당 특수화된 근접 메모리 프로세싱 코어 세트 — ARM Cortex-A53 대비 높은 병렬성 제공
- 각 Sync Core는 RecvBuf, LocalBuf, SendBuf의 3개 버퍼를 유지하고 CCI 주소 공간에 매핑
- 그룹 기반 집단 통신: 메모리 디바이스별 Sync Core가 링 토폴로지로 연결, 인접 그룹은 반대 방향 링 사용하여 양방향 대역폭 활용 (Figure 11)
- **장애 터런스**: copy-on-write 메커니즘을 활용한 저오버헤드 스냅샷 — 각 에포크 종료 시 체크포인트 저장

## 핵심 기여

- **핵심 기여**: CCI 기반 분산 메모리 시스템을 활용한 최초의 분산 DL 학습 파라미터 동기화 가속화
- **성능**: AllReduce 대비 **최대 48.3%** 학습 가속, 다양한 시스템(T4, V100, P100)에서 일관된 성능 향상
- **설계 혁신**: 비중앙집중적 통신 + 텐서 라우팅/파티셔닝 + 이중 동기화의 3중 최적화
- **실용성**: TensorFlow와의 쉬운 통합(2줄 코드 변경), 상용 HW 없이 GPU 에뮬레이션으로 프로토타입 구현
- **의의**: CCI 프로토콜의 실용적 활용 사례 제시 — 분산 학습의 통신 병목을 하드웨어-소프트웨어 공동 설계로 해결
- **한계점**: 모든 플랫폼에서 균일한 성능 향상 미제공 (T4 플랫폼에서 AllReduce보다 약간 낮은 성능), CCI 지원 CPU/메인보드 부재로 인한 에뮬레이션 기반 평가

## 주요 결과

- **소프트웨어**: Python 3 + CUDA 11.4로 구현, TensorFlow 프레임워크 플러그인 제공
- **하드웨어 프로토타입**: Xilinx KCU1500 FPGA + BittWare 250-SoC FPGA를 CCI 프로토콜 기반으로 연결
- KCU1500이 공유 메모리 풀 역할, 250-SoC의 ARM 코어가 CCI 클라이언트 컨트롤러를 통해 접근
- QSFP 케이블로 두 FPGA 연결, PCIe P2P 통신 지원
- **시뮬레이션**: GPU를 CCI 메모리 디바이스로 에뮬레이션 (CCI 지원 CPU/메인보드 부재)
- **코드 변경**: COARSE 분산 전략 사용 시 기존 TensorFlow 코드에서 **약 2줄**만 변경

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2022HPCA-summarize/enabling-efficient-large-scale-dl-training-with-cache-coherent-disaggregated-memory-systems.md|전체 요약 보기]]
