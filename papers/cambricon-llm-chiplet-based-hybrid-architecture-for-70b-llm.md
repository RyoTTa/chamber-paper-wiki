---
tags: [paper, 2024, 2024MICRO, topic/cache, topic/dram, topic/llm-inference, topic/storage]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO) 2024"
year: 2024
summary_path: "../paper-summaries/2024MICRO-summarize/cambricon-llm-chiplet-based-hybrid-architecture-for-on-device-inference-of-70b-llm.md"
---

# Cambricon-LLM: A Chiplet-Based Hybrid Architecture for On-Device Inference of 70B LLM

**Venue:** IEEE/ACM International Symposium on Microarchitecture (MICRO) 2024
**저자:** Zhongkai Yu, Shengwen Liang, Tianyun Ma, Yunke Cai, Ziyuan Nan, Di Huang, Xinkai Song, Yifan Hao, Jie Zhang, Tian Zhi, Yongwei Zhao, Zidong Du, Xing Hu, Qi Guo, Tianshi Chen (Institute of Computing Technology, CAS; University of Chinese Academy of Sciences; University of Science and Technology of China; Peking University; Shanghai Innovation Center for Processor Technologies; Cambricon Technologies Co., Ltd.)

## 개요

- 최신 대규모 언어 모델(LLM)을 스마트폰, 로봇 등 엣지 디바이스에서 구동하려는 수요가 지속적으로 증가하고 있으나, 기존 하드웨어로는 70B 파라미터 LLM을 엣지에서 단일 배치 추론하는 것이 거의 불가능하다
- Llama-70B 모델을 INT8 양자화 시 최소 70GB 메모리가 필요하며, 이는 일반 스마트폰 DRAM 용량(12~16GB)을 크게 초과한다
- 데이터 이동 비용은 연산 비용 대비 100~500배 높으며, 단일 배치 LLM 추론의 산술 강도(arithmetic intensity)는 INT8 기준 2에 불과하여 다른 AI 알고리즘(DLRM, BERT, VGG) 대비 30~100배 낮다(Fig.1)
- 기존 Flash offloading 방식(FlexGen, DeepSpeed)은 UFS 4.0 플래시의 4GB/s 대역폭 제한으로 최대 0.06 token/s 수준의 극도로 느린 추론 속도를 보이며, 실시간 인터랙티브 응용(최소 3~10 token/s 필요)에 부적합하다
- In-Storage Computing(ISC) 기반 최신 연구(OptimStore, BeaconGNN)도 LLM 단일 배치 추론의 높은 reduction ratio(100배 이상)로 인해 플래시 채널 활용률이 10% 미만으로 떨어지며, on-die 오류 정정 메커니즘이 없어 오류 발생 시 정확도가 70% 이상 떨어진다

## 방법론

### 3.1. 전체 구조 개요

- NPU와 온-die 처리 기능을 갖춘 플래시가 high-speed D2D chiplet 링크로 연결됨(Fig.4)
- NPU는 Flash Controller를 통합하여 플래시 데이터에 직접 접근 가능 (기존 NPU 설계와 차별화)
- 가중치는 플래시에, KV cache(700MB 미만)는 DRAM에 할당하여 메모리 활용 극대화
- LLM 추론 연산을 세 그룹으로 분류: (1) 가중치 기반 GeMV → NPU+플래시 공동 처리, (2) KV cache 행렬 연산 → NPU 전용, (3) KV cache 로딩 → NPU+DRAM 공동 처리

### 3.2. Flash Die 설계

- 각 플래시 다이에 Compute Core(PE, 버퍼, ECC 모듈), Compute Control, Slice Control 로직 추가(Fig.4(b))
- Compute Core는 planes 간 공유 구조로 면적 소비와 발열 문제를 완화 (독립 할당 시 면적 부담 및 온도 상승으로 오류율 증가)
- Read-compute 요청 명령어 도입: 입력 벡터 → 플래시 채널로 전송 → 가중치 메트릭스를 NAND array에서 data register로 로드 → cache register로 전달 → PEs에서 GeMV 수행 → 결과 벡터를 NPU로 반환
- 예: 20μs(tR) 동안 16KB 페이지 크기의 가중치에 대해 32K 연산(INT8) 수행 → 약 1.6 GOPS, 2개 MAC 유닛으로 충분

### 3.3. Slice Control 메커니즘

- 단일 read-compute 요청의 결과 벡터 전송 시간은 페이지 읽기 시간(tR) 대비 극히 짧아 채널 활용률이 ≤6%로 매우 낮음(Fig.6(a))
- Solution: 유휴 플레인이 read-compute 처리 동안 일반 read 요청으로 NPU에 가중치 전송 → 채널 대역폭 활용 극대화
- Read request slice 메커니즘 도입: 페이지 단위 read 요청을 작은 slice로 분할하여 read-compute 요청 간 채널 유휴 구간에 삽입(Fig.6(c))
- 비교: read-compute만 사용 대비 slice 기반 혼합 사용 시 실행 시간이 동일 수준으로 감소, 채널 사용률 대폭 향상

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1. 최적 타일 형태 결정

- 가중치 행렬(H_weight × W_weight)을 작은 타일(H_req × W_req)로 분할
- 각 타일은 모든 Compute Core에 분배되어 단일 read-compute 요청으로 처리
- 채널 수(channel_num)와 코어 수(ccore_num) 기반 AM-GM 부등식으로 최소 데이터 전송량 도출:

```
min{Trans} = 2 × channel_num × √(ccore_num × page_size)
최적 타일: H_req* = √(ccore_num × page_size), W_req* = channel_num × √(ccore_num × page_size)
```

- 동일 채널의 코어들이 입력 벡터를 broadcast로 공유하여 데이터 전송량 대폭 절감

### 4.2. 최적 워크로드 분배 비율 결정

- α 비율의 가중치를 플래시(on-die 처리), 나머지를 NPU에서 처리
- read-compute 요청과 read 요청의 실행 시간이 균형을 이루도록 최적 α 결정:

```
t_rc = t_R + W_req / (channel_num × bw_channel)
rate_rc = (H_req + W_req / channel_num) / (t_R × bw_channel)
t_r = page_size / ((1 - rate_rc) × bw_channel)
α = t_r / (t_r + t_rc)
```

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2024MICRO-summarize/cambricon-llm-chiplet-based-hybrid-architecture-for-on-device-inference-of-70b-llm.md|전체 요약 보기]]
