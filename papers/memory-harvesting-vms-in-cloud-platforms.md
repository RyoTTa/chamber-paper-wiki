---
tags: [paper, 2022, 2022ASPLOS, topic/cache, topic/security]
venue: ""
year: 2022
summary_path: "../paper-summaries/2022ASPLOS-summarize/memory-harvesting-vms-in-cloud-platforms.md"
---

# Memory-Harvesting VMs in Cloud Platforms

**Venue:** 
**저자:** Alexander Fuerst (Indiana University / Microsoft Research), Stanko Novaković (Microsoft Research), Íñigo Goiri (Microsoft Research), Gohar Irfan Chaudhry (Microsoft Research), Prateek Sharma (Indiana University), Kapil Arya (Microsoft Research), Kevin Broas (Microsoft Azure), Eugene Bak (Microsoft Azure), Mehmet Iyigun (Microsoft Azure), Ricardo Bianchini (Microsoft Research)

## 개요

- 클라우드 플랫폼은 미사용 자원을 "Spot VM"으로 판매하지만, 고정된 리소스 할당으로 인해 eviction 발생 시 리소스 낭비
- 기존 Harvest VM은 CPU core harvesting에 초점을 맞췄으나, **메모리는 서버 비용의 약 50%를 차지**하므로 미사용 메모리의 수익화 기회 상실
- 메모리 harvesting은 고유한 과제를 가짐: (1) 정규 VM 도착 시 대규모 페이지 deallocation으로 인해 VM 생성 시간 증가, (2) NUMA spanning 유발 가능, (3) large page 파편화로 인한 성능 저하
- Azure 분석 결과: 서버당 평균 40% 미사용 메모리 존재하나 기존에는 이를 활용하지 못함

## 방법론

### 3.1. 메모리 버퍼링 및 배치

- 서버당 미사용 메모리에서 일정량(기본 192GB)을 버퍼로 유지
- 정규 VM 도착 시 버퍼에서 즉시 할당하고, 동시에 MHVM으로부터 나머지를 회수
- 버퍼 크기와 MHVM 최소 크기의 트레이드오프: 큰 버퍼 = 적은 메모리 수확, 작은 버퍼 = VM 생성 지연

### 3.2. 메모리 리사이징 최적화

- **Pre-reclamation:** 호스트가 메모리 요청 시 게스트 OS가 백그라운드에서 추가 청크(128MB)를 사전 회수
- **Batch size 증가:** 단일 small 청크 대신 multi-GB 청크로 요청하여 회수 처리량 향상
- **Application notification (proactive):** 파라가상화 인터페이스를 통해 MHVM에 목표 메모리 크기를 사전 알림
  - Reactive 대비 idle VM 수준의 리사이징 처리량 달성 (4.4 GB/s)
- **Hot-remove 최적화:** 1GB batch + pre-reclamation 적용 시 최대 6.2 GB/s 처리량

### 3.3. NUMA 인식

- MHVM에 virtual NUMA 토폴로지 노출
- NUMA-aware 리사이징으로 정규 VM의 NUMA spanning 방지
- 128GB 버퍼 설정 시 NUMA spanning이 baseline(수확 없음) 수준으로 감소

### 3.4. Large Page 파편화 대응

- 2MB contiguous 청크 단위로 메모리 회수하여 large page 파편화 방지
- Large page 할당 시 4KB 할당 대비 회수 후 22.9GB 연속 청크 확보 (19GB가 1GB aligned)
- 4KB 할당 시 17.8GB 연속 청크 중 1GB aligned 없음

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1. MH-Hadoop

- 기존 Harvest Hadoop에 메모리 harvesting 지원 추가
- 리소스 매니저가 서버별 메모리 크기 변경에 따라 컨테이너 수 동적 조정
- 메모리 감소 시 새 컨테이너 할당 중지, 기존 컨테이너 drain → 완료 후 새 컨테이너 할당
- 예상치 못한 eviction은 서버 실패와 동일하게 처리 (컨테이너 자동 재시작)

### 4.2. MH-FaaS

- Azure Functions 기반 메모리 수확 FaaS 플랫폼
- 각 MHVM에서 invoker가 함수 실행, 컨트롤러가 메모리 변경에 따라 함수 호출 분배 조정
- 메모리 harvesting로 Larger function instance cache 유지 → cold start 감소

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/security.md|Security]]


## 전체 요약

[[../paper-summaries/2022ASPLOS-summarize/memory-harvesting-vms-in-cloud-platforms.md|전체 요약 보기]]
