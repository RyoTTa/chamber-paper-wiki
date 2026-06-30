---
tags: [paper, llm, inference, compression, gpu, tensor-core]
venue: ASPLOS
year: 2026
summary_path: paper-summaries/2026ASPLOS-summarize/zipserv-fast-and-memory-efficient-llm-inference-with-hardware-aware-lossless-compression.md
---

# ZipServ: Fast and Memory-Efficient LLM Inference with Hardware-Aware Lossless Compression

## 개요

ZipServ는 GPU 아키텍처와 공동 설계된 최초의 무손실 압축 LLM 추론 프레임워크입니다. 기존 무손실 압축 기술이 GPU의 SIMT 실행 모델과 불일치하여 추론 속도를 저하시키는 문제를 해결합니다.

## 방법론

- **Tensor-Core-Aware Triple Bitmap Encoding (TCA-TBE)**: 고정 길이 비트맵 기반 인코딩으로 상수 시간 병렬 디코딩 가능
- **Fused Decompression-GEMM (ZipGEMM)**: 압축된 가중치를 Tensor Core 레지스터로 직접 전달하는 융합 커널
- **"Load-compressed, compute-decompressed" 설계**: 중간 메모리 버퍼 제거

## 핵심 기여

- 기존 엔트로피 코덱과 GPU 아키텍처 간의 근본적 불일치 식별 및 해결
- TCA-TBE: SIMT 실행과 Tensor Core 타일링에 최적화된 고정 길이 인코딩
- ZipGEMM: 온더플라이 디코딩을 통한 중간 버퍼 제거

## 주요 결과

- 모델 크기 최대 30% 감소
- NVIDIA cuBLAS 대비 최대 2.21배 커널 수준 가속
- vLLM 대비 평균 1.22배 종단간 추론 가속
- 무손실 압축이 LLM 추론을 직접 가속할 수 있는 최초의 실용적 증거

## 한계점

- BFloat16 가중치의 지수 비트 분포에 의존
- 다양한 LLM 아키텍처에서의 일반화 필요
- GPU 메모리 대역폭 제한에 따른 잠재적 병목

## 관련 개념

- [[paper-wiki/concepts/llm-inference|LLM Inference]]
- [[paper-wiki/concepts/compression|Compression]]
- [[paper-wiki/concepts/gpu-architecture|GPU Architecture]]

## 관련 논문

- [vLLM](paper-summaries/2023SOSP-summarize/vllm-efficient-memory-management-for-large-language-model-serving.md)
- [DFloat11](paper-summaries/2024-arxiv-summarize/dfloat11-an-efficient-compression-format-for-llm-weights.md)