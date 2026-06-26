---
tags: [paper, 2025, 2025HPCA, topic/cache, topic/dram, topic/gpu, topic/llm-inference, topic/near-data-processing, topic/nvm, topic/storage]
venue: "IEEE International Symposium on High Performance Computer Architecture (HPCA) 2025"
year: 2025
summary_path: "../paper-summaries/2025HPCA-summarize/instattention-in-storage-attention-offloading-for-long-context-llm.md"
---

# InstAttention: In-Storage Attention Offloading for Cost-Effective Long-Context LLM Inference

**Venue:** IEEE International Symposium on High Performance Computer Architecture (HPCA) 2025
**저자:** Xiurui Pan, Endian Li, Qiao Li, Shengwen Liang, Yizhou Shan, Ke Zhou, Yingwei Luo, Xiaolin Wang, Jie Zhang (Peking University, University of Electronic Science and Technology of China, Institute of Computing Technology CAS, Huawei Cloud, Huazhong University of Science and Technology)

## 개요

- LLM 추론에서 컨텍스트 길이와 배치 크기가 증가하면서 KV 캐시의 메모리 요구사항이 급격히 증가하여 GPU VRAM에 큰 부담을 줌
- 13B 파라미터 모델, batch size 32, 4K tokens 기준 KV 캐시가 약 100GB 필요하며, 이는 모델 크기의 4.2배에 해당
- 기존 SSD 오프로딩 솔루션(DeepSpeed, FlexGen)은 PCIe 대역폭 병목(3~7 GB/s)으로 인해 심각한 성능 저하 발생
- FlexGen 디코딩 단계에서 KV Cache Access 오버헤드가 최대 98.94%에 달함
- GPU VRAM 대비 SSD 대역폭이 수십 배 낮아, KV 캐시 전송이 새로운 성능 병목으로 부상

## 방법론

### 3.1. 시스템 아키텍처

- **InstCSD**: 디코딩 단계 attention 연산 수행 및 대용량 KV 캐시 저장 (FPGA 기반 CSD)
- **InstGPU**: 프리필링 단계 및 기타 추론 연산 수행, KV 캐시 생성
- **InstHost**: 소프트웨어 스택, 추론 작업 스케줄링, GPU-CSD 간 데이터 전송 조율
- 피어 투 피어 DMA로 호스트 메모리 bypass → 데이터 복사 최소화

### 3.2. SparF Attention 알고리즘

- SparQ Attention 기반 flash-aware 희소 attention 알고리즘 제안
- query 벡터의 top-r 엔트리를 기반으로 attention score 근사 → top-k 토큰 선택
- **2단계 로딩 메커니즘**: flash 페이지 크기에 맞춘 그룹 단위 필터링 후, 토큰 단위 정밀 필터링
  - 1단계: 전체 그룹 단위로 약한 토큰이 포함된 페이지 무시 (page-level)
  - 2단계: 강한 토큰만 NFC 필터를 통과 (token-level)
- 압축 비율 1/8에서 정확도 거의 손실 없음 (vanilla SparQ와 동등 수준)
- 알고리즘 1: flash-aware sparse q-attention의 의사코드 상세 기술

### 3.3. 하드웨어 기반 attention 엔진 (FPGA)

- InstCSD의 FPGA에 SparF attention 엔진 구현
- **Attention Kernel**: GeMV 및 Softmax 유닛으로 구성된 attention 연산 하드웨어
- **argtopk 유닛**: top-r/top-k 인덱스 추출
- **NFC 필터**: flash 페이지에서 불필요한 엔트리 필터링
- flash 채널 간 파이프라인 병렬화로 flash 접근 지연 시간 숨김
- Zynq7045 FPGA에서 285MHz 클록으로 동작, LUT 80.27%, FF 58.92% 사용

### 3.4. KV 캐시 관리 및 주소 매핑

- **Token-Indexed Mapping**: K/V 캐시를 토큰 차원에서 16개 연속 토큰을 flash 페이지(4KB)에 통합
  - 각 그룹은 특정 attention head의 숨김 차원 하위 공간을 포함
- **Channel-Indexed Mapping**: K 캐시를 채널 차원에서 액세스 (SparF의 1단계 로딩용)
  - K 매트릭스를 두 번 별도 방향으로 저장하여 접근 효율성 확보
- 커스텀 FTL 설계: 논리 주소를 task/batch/layer/token/head/channel 필드로 분할
- 배치 쓰기: 프리필링 단계에서 생성된 KV 캐시를 DRAM 버퍼에 임시 저장 후 flash에 플러시

## 핵심 기여

- InstAttention은 CSD를 활용한 최초의 in-storage attention offloading 시스템으로, KV 캐시의 저장 비용과 대역폭 문제를 효과적으로 해결
- 디코딩 단계 attention만 CSD로 오프로딩하여 CSD의 낮은 연산 능력 문제를 회피
- 하드웨어-알고리즘 공동 설계(SparF + FPGA 엔진)로 GPU-CSD 대역폭 격차를 해소
- 최대 11.1배 throughput 향상으로 기존 SSD 기반 오프로딩 솔루션을 크게 능가
- 리소스 제약 시나리지(엣지, 개인 디바이스)에서 비용 효율적인 장문 LLM 추론에 적합
- 코드 공개: https://github.com/ChaseLab-PKU/InstAttention

## 주요 결과

- **하드웨어 플랫폼**: Daisyplus OpenSSD (Zynq7045 MPSoC, 4코어 ARM + FPGA)
- **소프트웨어**: FlexGen 기반 확장, TorchDisk 객체를 TorchDevice로 변환하여 CSD 통합
- **드라이버**: NVMe 기반 커스텀 드라이버, config()/attend()/reclaim() 커맨드 지원
- **가상화**: NVMeVirt 기반 소프트웨어 정의 가상 NVMe 디바이스로 실용적 CSD 솔루션 시뮬레이션
- GPU-CSD 간 PCIe Gen4x4 (최대 7GB/s), CSD 내부 8 플래시 채널 (채널당 1.4GB/s)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2025HPCA-summarize/instattention-in-storage-attention-offloading-for-long-context-llm.md|전체 요약 보기]]
