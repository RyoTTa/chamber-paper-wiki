---
tags: [coherence, heterogeneous-systems, cpu-gpu, cache-coherence, memory-system]
venue: ISCA
year: 2018
summary_path: paper-summaries/2018ISCA-summarize/spandex-a-flexible-interface-for-efficient-heterogeneous-coherence.md
---

# Spandex: A Flexible Interface for Efficient Heterogeneous Coherence

**Venue:** 45th Annual International Symposium on Computer Architecture (ISCA '18)
**저자:** NOTA 논문 정보에서 확인 필요

---

## 개요

이기종 시스템(CPU, GPU, 가속기)을 위한 유연하고 단순한 코히어런스 인터페이스 Spandex를 제안. 기존 MESI 기반 계층적 캐시 구조의 한계를 해결하기 위해 플랫 LLC 구조와 단어 단위 소유권 추적을 도입.

## 방법론

- **플랫 LLC 구조:** 계층적 캐시 없이 CPU, GPU가 직접 LLC에 접근
- **단어 단위 소유권 추적:** 라인 전체가 아닌 단어 단위로 소유권 관리로 거짓 공유 최소화
- **유연한 요청 타입:** ReqV(셀프-무효화), ReqO(비블로킹 소유권), ReqWT(라이트스루), ReqS(라이터-무효화)
- **TU(Translation Unit):** 디바이스 고유 프로토콜과 Spandex LLC 간의 갭 해소

## 핵심 기여

- 이기종 디바이스의 다양한 코히어런스 요구사항을 하나의 프로토콜로 지원
- 계층적 캐시 구조의 인디렉션 오버헤드 제거
- 비블로킹 소유권 전송으로 높은 동시성 달성

## 주요 결과

- 기존 계층적 MESI 대비 실행 시간 평균 **16%** 절감 (최대 **29%**)
- 네트워크 트래픽 평균 **27%** 절감 (최대 **58%**)
- 합성 마이크로벤치마크에서 최대 **69%** 네트워크 트래픽 감소

## 한계점

- 단어 단위 소유권 추적을 위한 LLC 저장소 오버헤드
- 디바이스에 TU 추가 필요 (면적/전력 오버헤드)
- 기존 MESI 확장 프로토콜(MOESI, MESIF) 미지원

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/gpu.md|GPU]]

## 전체 요약

[paper-summaries/2018ISCA-summarize/spandex-a-flexible-interface-for-efficient-heterogeneous-coherence.md](paper-summaries/2018ISCA-summarize/spandex-a-flexible-interface-for-efficient-heterogeneous-coherence.md)