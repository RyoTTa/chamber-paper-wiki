---
tags: [paper, 2018, 2018ASPLOS, topic/dram, topic/gpu]
venue: "ASPLOS 2018 (Architectural Support for Programming Languages and Operating Systems)"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/sugar-secure-gpu-acceleration-in-web-browsers.md"
---

# Sugar: Secure GPU Acceleration in Web Browsers

**Venue:** ASPLOS 2018 (Architectural Support for Programming Languages and Operating Systems)
**저자:** Zhihao Yao, Zongheng Ma, Yingtong Liu, Ardalan Amiri Sani, Aparna Chandramowlishwaran (University of California, Irvine)

## 개요

- 현대 웹 브라우저에서 GPU 기반 그래픽 가속이 인기 급증: WebGL이 현재 상위 100개 웹사이트의 53%에서 사용
- WebGL은 OpenGL과 유사한 그래픽 API를 웹 앱에 제공하지만, 심각한 보안 문제 초래
- 기존 브라우저의 보안 대응은 사후적이며, 발견된 취약점만 패치하고 런타임 보안 검사를 추가하는 방식
- graphics plane의 신뢰 컴퓨팅 기반(TCB: Trusted Computing Base)이 크고 복잡하여 제로데이 취약점에 취약
- 웹 앱은 신뢰할 수 없으나 graphics plane에 대한 접근이 가능하여 보안 위협 발생

## 방법론

### 3.1. 가상 그래픽 폴레인 아키텍처

- 각 웹 앱에 대해 독립된 가상 그래픽 폴레인 할당
- 가상 그래픽 폴레인 구성 요소:
  - 전용 가상 GPU(vGPU)
  - 그래픽 드라이버
  - OpenGL/WebGL 구현체
  - 모든 그래픽 관련 소프트웨어 스택
- 물리적 GPU 리소스를 가상화하여 여러 웹 앱에 안전하게 분배

### 3.2. GPU 가상화 기반 격리

- 최신 GPU 가상화 솔루션(NVIDIA GRID, AMD MxGPU 등) 활용
- vGPU 간 하드웨어 수준 격리 제공
- 웹 앱의 그래픽 작업이 다른 웹 앱이나 시스템에 영향을 미치지 않도록 보장
- 보안 격리와 성능 격리 동시 달성

### 3.3. 이중 GPU 동시 렌더링

- 두 개의 물리적 GPU가 있는 시스템에서:
  - GPU 1: 웹 앱용 가상 그래픽 폴레인 제공
  - GPU 2: 시스템 나머지용 기본 그래픽 폴레인 제공
- 웹 앱과 시스템 간 그래픽 리소스 경쟁 제거
- 강화된 성능 격리 제공

## 핵심 기여

- Sugar는 GPU 가상화를 활용하여 웹 브라우저에서의 GPU 가속을 안전하게 제공하는 최초의 OS 솔루션
- 기존 접근법(사후 보안 패치)과 달리 설계 기반 보안(secure by design) 달성
- 완전한 격리와 높은 성능을 동시에 제공
- 웹 앱의 보안과 성능을 위한 실용적인 솔루션 제시

## 주요 결과

- 리눅스 커널 기반 구현
- KVM(Kernel-based Virtual Machine) 가상화 프레임워크 활용
- virtio-gpu 가상 디바이스 사용
- WebGL API 지원을 위한 그래픽 스택 통합

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]


## 전체 요약

[[../paper-summaries/2018ASPLOS-summarize/sugar-secure-gpu-acceleration-in-web-browsers.md|전체 요약 보기]]
