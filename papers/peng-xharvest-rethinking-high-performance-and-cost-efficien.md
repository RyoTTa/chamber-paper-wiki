---
tags: [paper, 2025, 2025ISCA, topic/cache, topic/disaggregation, topic/dram, topic/nvm, topic/security, topic/storage, topic/virtual-memory]
venue: "ISCA 2025 | **Authors:** Li Peng (PKU), Wenbo Wu (HUST), Shushu Yi (PKU), et al. (multiple Chinese institutions)"
year: 2025
summary_path: "../paper-summaries/2025ISCA-summarize/xharvest-rethinking-high-performance-and-cost-efficient-ssd-architecture-with-cxl-driven-harvesting.md"
---

# XHarvest: Rethinking High-Performance and Cost-Efficient SSD Architecture with CXL-Driven Harvesting

**Venue:** ISCA 2025 | **Authors:** Li Peng (PKU), Wenbo Wu (HUST), Shushu Yi (PKU), et al. (multiple Chinese institutions)
**저자:** Li Peng (PKU), Wenbo Wu (HUST), Shushu Yi (PKU), et al. (multiple Chinese institutions)

## 개요

현대 SSD는 고성능 I/O 대역폭 충족을 위해 방대한 내부 자원(computing power, DRAM)을 집적하나, production cluster에서 I/O burst의 occasional한 특성으로 인해 자원이 상시 underutilization 상태에 놓임. Alibaba 4,000대 서버 8일 모니터링 결과 [2, 21]:

- **96.64%의 runtime에서 I/O bandwidth utilization 25% 미만**
- 80%+ utilization은 **0.28%의 runtime**에 불과

비용 측면: 1TB SSD 기준 computing 자원 **30%**, DRAM **10%** 비용 [25, 65, 70, 87, 108, 117]. PCIe 5.0 SSD는 PCIe 3.0 대비 **4.43×** computing power 필요 [22, 109, 110, 112]. 또한 7.5TB SSD는 FTL mapping table용으로 **10GB DRAM** 필요 [17].

Open-Channel SSD (OCSSD) [8]는 SSD 내부 자원을 완전히 제거하고 host-side CPU/DRAM을 활용하나, 심각한 문제 존재:
1. **Resource contention:** application memory 사용률이 90%+인 환경에서 [2, 21] OCSSD의 static memory reservation이 application과 직접 경쟁
2. **Hampered host-SSD collaboration:** PCIe가 host와 SSD를 별도 cache-coherency domain으로 분리 → metadata access 시 복잡한 OS stack 필요 (10us vs. 200ns [120, 57])
3. **Firmware leakage risk:** host-side unprotected firmware 실행 → vendor가 proprietary algorithm 통합에 저항. 결국 Linux kernel 5.15에서 LightNVM/pblk deprecated [63]

## 방법론

### 1. XHarvest 개요 (Section 4)

XHarvest는 moderate 내부 자원 유지 + dynamic host resource harvesting 전략:
- 내부: ConvSSD computing power의 **25%**, FTL mapping table의 **10%** 용량 DRAM
- Host harvesting: CXL + Intel SGX (TEE) 기반

**Host resource harvesting insights:**
- I/O burst는 소수 SSD에 sporadic하게 발생 → 동시 active SSD 수 제한적 (Alibaba: active VM >5개가 동시 발생하는 시간 2.20%)
- CPU utilization: high I/O load(85-100%) 시에도 Low utilization(0-40%)이 45.69% → idle host CPU harvesting 가능

### 2. Secure CPU Harvesting (Section 5.1)

**Enclave launch flow:**
1. SSD load detector가 high I/O load 감지 → host daemon thread에 signal
2. Daemon이 enclave 생성 → SSD가 attestation service(IAS) 통해 enclave 무결성 검증
3. Enclave가 SSD로부터 encrypted firmware binary + decryption key 수신 → decrypt 및 실행
4. Enclave는 단일 host CPU core에 pinning

**Decoupled dynamic launch:** Host startup 시 미리 enclave 생성 및 firmware load 후 exit (EPC 미할당). High load 감지 시 ecall로 재진입 + EPC 할당 → instantiation latency 회피.

**I/O path (Figure 8):**
1. Enclave가 SSD 내 request queue polling (NVMe controller가 parsing한 명령)
2. FTL cache lookup → LPN→PPN 변환
3. PPN을 flash backbone에 dispatch → flash operation → response queue에 완료 posting

### 3. CXL-Driven Efficient Communication (Section 5.2)

**TEE Security Protocol (TSP) 기반 보안 통신:**
- CXL 3.1의 TSP feature [16, 33, 66, 106] 활용
- Enclave-SSD 간 mutual authentication (TSP CMA: certificate exchange + identity verification)
- AES-GCM symmetric encryption으로 CXL traffic 보호 (encryption + MAC for integrity)
- Overhead: CPU cycle/byte 수준 → access latency의 **~5%** 증가에 불과 [26, 43, 98]

**Message-passing mechanism:**
- SSD internal DRAM의 일부를 ring buffer로 사용 (message size: 64B)
- Host/SSD 각각 tail/head pointer 유지
- Cache coherence로 인해 enclave의 message write가 SSD에게 즉시 observable (ready bit polling)
- Traditional ecall/ocall (20K+ cycles overhead [121]) 완전 회피

## 핵심 기여

1. **핵심 기여:** CXL + TEE(SGX)를 결합하여 SSD architecture의 cost-utilization dilemma를 해결하는 최초의 dynamic resource harvesting 설계. Moderate 내부 자원 + on-demand host resource로 **비용 31.50% 절감 + 성능 5.02% 향상** 동시 달성.

2. **기술적 breakthroughs:**
   - CXL.mem의 cache-coherent fine-grained access로 DMA/OS stack bottleneck 제거 (metadata traffic 33.89% 감소)
   - TSP 기반 secure CXL traffic으로 enclave-SSD direct communication → ecall/ocall 회피 (6.85× faster)
   - Scrubbing overhead-aware dynamic launch (< 5ms, tail latency 무영향)

3. **Scalability:** 24-SSD 서버당 8 core(6.25% of 128-core)만으로 saturation. CXL.mem/cache latency가 CXL spec target과 일치 → mature CXL hardware에서 expected performance.

4. **Broader significance:** CXL+PCIe 통합 interconnect가 SSD뿐 아니라 다양한 peripheral의 host-collaborative architecture를 가능하게 하는 paradigm shift.

## 주요 결과

**Enclave-based FTL cache:**
- CXL.mem으로 host memory(EPC) + SSD internal DRAM을 unified cache-coherent memory space로 통합
- Translation page (4KB, 인접 LPN의 mapping entries 다수 포함) 단위 caching
- LRU replacement policy + hash table index로 translation page 관리
- Cache hit 시 load/store instruction으로 즉시 mapping entry 접근 (EPC에 있든 SSD DRAM에 있든)

**SSD firmware-based harvesting (fallback):**
- Host CPU resource 부족으로 enclave 기동 불가 시 사용
- Regular host memory 사용 → 자체 encryption (AES) + integrity verification (CRC/ECC) 필요

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/security.md|Security]]
- [[paper-wiki/concepts/storage.md|Storage]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2025ISCA-summarize/xharvest-rethinking-high-performance-and-cost-efficient-ssd-architecture-with-cxl-driven-harvesting.md|전체 요약 보기]]
