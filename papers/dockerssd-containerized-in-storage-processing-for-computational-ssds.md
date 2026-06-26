---
tags: [paper, 2024, 2024HPCA, topic/nvm, topic/storage, topic/virtual-memory]
venue: "IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2024"
year: 2024
summary_path: "../paper-summaries/2024HPCA-summarize/dockerssd-containerized-in-storage-processing-for-computational-ssds.md"
---

# DockerSSD: Containerized In-Storage Processing and Hardware Acceleration for Computational SSDs

**Venue:** IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2024
**저자:** Donghyun Gouk, Miryeong Kwon, Hanyeoreum Bae, Myoungsoo Jung (KAIST, Computer Architecture and Memory Systems Laboratory; Panmnesia, Inc.)

## 개요

- In-Storage Processing(ISP)은 호스트와 스토리지 간 데이터 전송 오버헤드를 최소화하여 대규모 데이터셋 탐색을 가능케 하는 스토리지 모델이나, 실제 시스템에서의 구현은 성능 부족과 실용적 문제로 인해 성공적이지 못함
- 기존 ISP 모델의 다섯 가지 핵심 과제:
  1. **수동 ISP 구현**: 사용자가 애플리케이션의 오프로딩 가능한 코드 세그먼트를 수동으로 식별하고 정적 커널 라이브러리로 교체해야 함
  2. **파일 레이아웃 무시**: 펌웨어는 파일 시스템의 레이아웃을 알지 못하므로, 호스트가 LBA 세트를 ISP 커널에 전달해야 하는 번거로움 존재
  3. **커널 컨텍스트 스위치**: 호스트와 SSD 간 빈번한 컨텍스트 전환으로 인한 통신 오버헤드 발생 (P.ISP에서 Communicate 비용이 전체 실행 시간의 43% 차지)
  4. **장치 의존성**: SSD 벤더가 제공하는 특정 도체인을 사용해야 하며, 이식성과 호환성 문제 발생
  5. **데이터 취약성**: 호스트와 스토리지의 동시 실행으로 인해 블록 디바이스의 동일 플래시 위치에 대한 무단 접근 가능
- 기존 ISP 모델(P.ISP)은 스토리지에서 데이터를 처리하여 데이터 이동 오버헤드를 줄이나(Storage 50% 감소), Communicate 비용(43%)으로 인해 전체 지연 시간이 1.4배 증가
- 시스템 호출이나 파일 접근이 많은 워크로드는 ISP의 잠재적 이점을 누릴 수 있으나, 기존 오프로딩 패러다임의 한계로 인해 성능이 크게 저하됨

## 방법론

### 3.1. Ether-oN (Ethernet over NVMe)

- NVMe 프로토콜을 확장하여 PCIe를 통한 소켓 기반 이더넷 통신 지원
- 드라이버가 네트워크-스토리지 패킷 변환과 비동기적 업콜 메커니즘을 지원
- 각 NVMe 엔드포인트에 개별 IP 주소 할당 가능
- 사용자가 `docker-cli`를 통해 ISP 관련 요청을 Virtual-FW에 언제든지 전송 가능
- 기존 NVMe 인터페이스를 수정하지 않으므로 네트워크와 블록 I/O 서비스를 병렬화 가능

### 3.2. Virtual-FW (가상 펌웨어)

- Linux 4.19 커널의 핵심 컴포넌트를 분석하여 베어메탈 SSD 하드웨어에서 시스템 호출 인터페이스를 에뮬레이션
- **mini-docker**: Docker 스택의 핵심 기능을 구현하여 펌웨어 레벨 ISP 컨테이너화 지원
- 시스템 호출 비용을 함수 관리 비용 수준으로 유지하여 경량화 달성
- 기존 Docker 이미지에서 ISP-container를 생성하고 종속성 없이 독립적으로 실행 가능
- **NVMe 네임스페이스 격리**: private-NS(호스트에서 숨김)와 sharable-NS(호스트와 ISP-container가 공유)로 미디어 분할
- Lambda 파일 시스템(ΛFS)을 통해 호스트의 EXT4 파일 구조를 통합하여 파일 동시성과 보호 구현

### 3.3. 하드웨어 가속화

- **네트워크 가속기**: Virtual-FW의 네트워크 기능을 처리하여 호스트와 ISP-container 간 통신 오버헤드 감소
- **파일 I/O 가속기**: per--file 경로 탐색(path walking)을 독립적으로 수행하여 루트 파일 시스템 디렉토리 전체를 순회하는 연산 부하 경감
- 이 가속기들은 Virtual-FW의 I/O와 네트워크 기능을 활용하는 컨테이너 관련 요청의 빈번한 서비스 루틴을 가속화

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1. 방법론

| 항목 | 내용 |
|------|------|
| **프로토타입** | 16nm FinFET FPGA 기반 고성능 PCIe SSD (NVMe 컨트롤러, 멀티코어 프로세서, 하드웨어 가속기) |
| **시뮬레이터** | 전체 시스템 시뮬레이션 프레임워크 |
| **기반 소프트웨어** | Linux 4.19 커널 분석 기반 |
| **벤치마크** | 시스템 호출/파일 접근이 많은 워크로드 (rocksdb, pattern 등) |
| **지표** | 처리량, 지연 시간, 전력 소비, 에너지 효율성 |
| **Baselines** | Host 중심 시스템, Programmable-ISP(P.ISP), 기타 기존 ISP 모델 |

### 4.2. 주요 결과

- **DockerSSD vs Host 시스템**: 평균 **1.5배 성능 향상**
- **DockerSSD vs 기존 ISP 모델(P.ISP)**: 평균 **2.0배 성능 향상**
- **전력 소비**: 기존 모델 대비 **1.6배 감소**
- **에너지 효율성**: 기존 모델 대비 **2.3배 향상**
- **Communicate 비용 제거**: Virtual-FW의 시스템 호출 에뮬레이션과 Ether-oN의 통신 최적화로 호스트-SSD 간 통신 오버헤드 대폭 감소
- **스토리지 백엔드 지연**: 기존 Host 시스템 대비 Storage 비율 38% 감소 (데이터 전송 오버헤드 제거 효과)
- **컨테이너 실행 오버헤드**: 가상화된 ISP 환경에서 기존 애플리케이션을 소스 수정 없이 자율적으로 실행 가능

### 4.3. Design Choices / Ablation Study

- **NVMe 네임스페이스 격리**: private-NS와 sharable-NS 분리를 통한 보안과 동시성 확보 — ISP-container가 호스트 데이터에 무단 접근 차단
- **Ether-oN vs 기존 NVMe**: Ether-oN은 네트워크와 블록 I/O를 병렬화 가능하여 기존 NVMe 대비 통신 효율성 향상
- **하드웨어 가속화 효과**: 네트워크 패킷 처리와 파일 경로 탐색을 하드웨어로 오프로딩하여 Virtual-FW의 처리 부하 감소
- **Docker 이미지 재사용**: 기존 컨테이너 이미지를 SSD로 다운로드하여 실행하므로 소스 수준 수정 불필요 — 이식성과 호환성 확보

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2024HPCA-summarize/dockerssd-containerized-in-storage-processing-for-computational-ssds.md|전체 요약 보기]]
