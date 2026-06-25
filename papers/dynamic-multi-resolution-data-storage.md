---
tags: [paper, 2019, 2019MICRO, topic/gpu, topic/nvm, topic/storage]
venue: "52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO-52), 2019"
year: 2019
summary_path: "../paper-summaries/2019MICRO-summarize/dynamic-multi-resolution-data-storage.md"
---

# Dynamic Multi-Resolution Data Storage

**Venue:** 52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO-52), 2019
**저자:** Yu-Ching Hu (University of California, Riverside), Murtuza Taher Lokhandwala (North Carolina State University), Te I (Google Inc.), Hung-Wei Tseng (University of California, Riverside)

## 개요

- 근사 컴퓨팅(Approximate Computing)은 덜 정밀한 데이터로 작업하여 상당한 성능 향상과 에너지 비용 절감을 달성할 수 있으나, **현대 컴퓨터 아키텍처는 전체 스택 설계를 활용하지 못하여 근사 컴퓨팅의 잠재력을 저하시킨다**.
- 기존 근사 컴퓨팅 연구는 **연산 커널의 가속화에만 집중**하여 프로그래밍 프레임워크, 알고리즘, 아키텍처 구성 요소의 설계를 개선하는 데 초점을 맞추었다. 그러나 현대 컴퓨터 시스템은 **정확한 컴퓨팅을 위해 설계된 기존 스토리지 시스템 스택**을 여전히 사용하고 있다.
- 최신 세대의 GPGPU를 활용하여 근사 연산 커널을 실행할 때, **입력 데이터셋 준비 오버헤드**(스토리지 장치에서 데이터 수신, 데이터 해상도 조정 등)가 **데이터 처리 파이프라인에서 가장 중요한 단계**가 되었다.
- 최신 근사 하드웨어 가속기(TPU, NGPU, NPU, 혼합 정밀도 지원 GPGPU)의 발전으로 **연산 커널의 실행 시간이 더욱 단축**되어, 근사 애플리케이션에서 **데이터 준비와 연산 간 격차가 심화**되고 있다.
- 데이터 해상도 조정은 데이터 전송 지연시간을 줄이지만, **출력 품질 저하**를 초래할 수 있어 애플리케이션이 **재계산이나 더 높은 해상도의 데이터 재전송**을 요구하게 되어 **최종 대기 시간이 증가**한다.

## 방법론

### 3.1. 스토리지 인터페이스 확장

- **연산자/operator 도입:** 애플리케이션이 데이터 해상도 조정에 적용할 수 있는 연산자 집합을 스토리지 인터페이스에 추가
- **동작 원리:**
  - 스토리지 장치 내부에서 원시 데이터에 대해 연산을 수행
  - 연산 결과로 낮은 해상도의 데이터셋을 동적으로 생성
  - 호스트 컴퓨터의 연산 커널이 직접 저해상도 입력을 사용하여 불필요한 데이터 변환 회피

### 3.2. Autofocus 품질 제어 메커니즘

- **자동 해상도 선택:** 
  - 모든 제어 변수를 만족하는 최저 해상도를 자동으로 선택
  - 연산 커널이 데이터를 처리하기 전에 스토리지 장치 내부에서 해상도 결정
- **품질 보장:**
  - 저품질 결과를 초래하는 데이터의 처리를 방지
  - 재계산이나 더 높은 해상도의 데이터 재전송으로 인한 성능 손실 감소
  - 더 넓은 범위의 데이터셋을 애플리케이션이 수용할 수 있게 함

### 3.3. iFilter 메커니즘

- **근사 연산자와 필터링 규칙 통합:**
  - 근사 연산자와 데이터 필터링 규칙을 함께 지정
  - 프로그래머의 부담을 줄이면서 해상도 조정의 잠재력을 실현
- **유연한 데이터셋 지원:**
  - 다양한 애플리케이션 요구 사항에 맞는 다양한 해상도의 데이터셋 제공
  - 정확한 컴퓨팅과 근사 컴퓨팅 모두를 위한 유연하고 효율적인 지원

### 3.4. 비용 효율성 확보 전략

- **원시 데이터셋 저장:** 스토리지 장치에 원시 데이터셋만 저장하여 추가 스토리지 공간 오버헤드 없음
- **기존 SSD 컨트롤러 활용:** 기존 SSD 컨트롤러의 컴퓨팅 능력을 보완하는 연산자를 대상으로 하여, 기존 스토리지 시스템의 비용을 초과하지 않으면서 동적으로 낮은 해상도의 데이터셋 생성

## 핵심 기여

- **핵심 기여:** 근사 컴퓨팅의 병목 현상을 해결하는 동적 다중 해상도 스토리지 시스템 Varifocal Storage 제시
- **성능 향상:** 데이터 해상도 조정 2.02배 가속화, 전체 실행 시간 1.52배 가속화 달성
- **실용성:** 추가 하드웨어 비용 없이 기존 스토리지 시스템과 통합 가능한 실용적 설계
- **기술적 의의:** 스토리지 장치 수준에서의 데이터 해상도 관리를 통해 근사 컴퓨팅의 성능-품질 트레이드오프를 효과적으로 관리하는 새로운 패러다임 제시

## 주요 결과

- **프로토타입:** 이종 컴퓨터 시스템에서 Varifocal Storage를 지원하는 프로토타입 SSD 구현
- **하드웨어 플랫폼:** 현대 스토리지 장치의 NVM 컴퓨팅 리소스 활용
- **소프트웨어 프레임워크:** 데이터 해상도 조정을 위한 연산자 라이브러리 및 Autofocus/iFilter 메커니즘 구현
- **시스템 구성:** 호스트 컴퓨터와 프로토타입 SSD 간의 통신 인터페이스 확장

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2019MICRO-summarize/dynamic-multi-resolution-data-storage.md|전체 요약 보기]]
