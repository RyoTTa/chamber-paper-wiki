---
tags: [nvm, pcm, coset-coding, write-energy, compression]
venue: HPCA
year: 2018
summary_path: paper-summaries/2018HPCA-summarize/enabling-fine-grain-restricted-coset-coding-through-word-level-compression-for-pcm.md
---

# Enabling Fine-Grain Restricted Coset Coding Through Word-Level Compression for PCM

## 개요

MLC PCM의 높은 쓰기 에너지를 해결하기 위해 16비트 세밀화 인코딩과 Word-Level Compression (WLC)을 결합한 WLCRC 기법입니다. 세밀한 인코딩 세밀화에서 보조 비트 문제를 WLC로 해결하여 기존 기법 대비 39% 쓰기 에너지 절감을 달성합니다.

## 방법론

- **Restricted Coset Encoding**: 쓰기 에너지 + 빈도 분포를 동시 고려한 코드 매핑
- **Word-Level Compression (WLC)**: 91% 이상의 메모리 라인을 압축하는 가벼운 압축 기법
- **16비트 인코딩 세밀화**: 캐시 라인(512비트) 대신 16비트 서브블록 단위로 인코딩
- **보조 심볼 저장**: 압축된 라인 내에 인코딩 메타데이터 저장

## 핵심 기여

1. 세밀한 인코딩 세밀화에서 보조 비트 문제를 해결하는 WLC 기법
2. 빈도 + 에너지를 동시에 고려한 restricted coset encoding
3. 20% 내구성 향상 + 쓰기 왜strup 확률 감소

## 주요 결과

- 16비트 인코딩: 기존 선도적 인코딩 대비 평균 39% 쓰기 에너지 절감
- 내구성: 20% 향상
- 신뢰성: 기존 기법 대비 더 높은 신뢰성
- 하드웨어: 매우 작은 면적으로 온칩 구현 가능

## 한계점

- MLC PCM에 최적화 (SLC 또는 다른 NVM 기술에는 직접 적용 불가)
- WLC의 압축률이 낮지만 라인 수가 많아 보조 심볼 확보 가능
- 실제 워크로드에서의 비트 패턴 의존성

## 관련 concept

- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/compression.md|Compression]]
