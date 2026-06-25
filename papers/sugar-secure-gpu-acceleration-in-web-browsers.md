---
tags: [gpu, security, virtualization, web-browser, graphics]
venue: ASPLOS
year: 2018
summary_path: paper-summaries/2018ASPLOS-summarize/sugar-secure-gpu-acceleration-in-web-browsers.md
---

# Sugar: Secure GPU Acceleration in Web Browsers

## 개요

Sugar는 GPU 가상화를 활용하여 웹 브라우저에서의 GPU 가속을 안전하게 제공하는 OS 솔루션으로, 각 웹 앱에 전용 가상 그래픽 폴레인을 제공하여 완전한 격리를 달성합니다.

## 방법론

- **전용 가상 그래픽 폴레인**: 각 웹 앱에 전용 vGPU와 그래픽 스택 제공
- **GPU 가상화 기반 격리**: 하드웨어 수준 격리로 웹 앱 간 완전한 분리
- **이중 GPU 동시 렌더링**: 웹 앱과 시스템 간 그래픽 리소스 경쟁 제거

## 핵심 기여

- GPU 가상화를 활용한 웹 브라우저 GPU 가속의 최초의 OS 솔루션
- 설계 기반 보안(secure by design) 달성
- 완전한 격리와 높은 성능 동시 제공

## 주요 결과

- 완전한 웹 앱 격리 달성
- GPU 가상화 오버헤드에도 높은 성능 유지
- 이중 GPU 구성에서 동시 렌더링 성능 향상
- 웹 앱의 그래픽 작업이 시스템 성능에 미치는 영향 최소화

## 한계점

- 이중 GPU 구성이 필요한 고사양 시스템 요구
- GPU 가상화 기술에 대한 의존성

## 관련 개념

- [[paper-wiki/concepts/gpu|GPU]]
- [[paper-wiki/concepts/security|Security]]
- [[paper-wiki/concepts/virtualization|Virtualization]]