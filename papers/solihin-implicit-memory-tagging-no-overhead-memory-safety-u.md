---
tags: [paper, 2023, 2023ISCA, topic/cache, topic/compression, topic/dram, topic/gpu, topic/rowhammer, topic/security, topic/storage]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023ISCA-summarize/implicit-memory-tagging-no-overhead-memory-safety-using-alias-free-tagged-ecc.md"
---

# Implicit Memory Tagging: No-Overhead Memory Safety Using Alias-Free Tagged ECC

**Venue:** 
**저자:** 

## 개요

### 1.1 Memory Safety는 여전히 가장 큰 보안 위협

C/C++ 및 CUDA/OpenACC 등 unsafe 언어에서 Memory Safety 버그는 **전체 CVE의 ~70%**를 차지하며 (Figure 1), 특히 **non-adjacent buffer overflow**의 비중이 최근 증가 추세. Memory tagging은 이러한 취약점을 하드웨어 가속으로 탐지하는 효과적 기법이나, 두 가지 주요 장벽이 존재:

1. **Meta-data storage & traffic overhead**: tag 저장을 위한 별도 storage, on-chip cache, memory bandwidth 소비
2. **Weak probabilistic guarantees**: 제한된 tag size(ARM MTE, SPARC ADI 모두 4-bit tag)로 인해 non-adjacent overflow 탐지 확률이 낮음

### 1.2 Industry Baseline의 한계

| 기법 | Tag Size | Tag Granule | 문제점 |
|---|---|---|---|
| **SPARC ADI** | 4-bit | 64B | ECC storage를 stealing → reliability 저하 (15.8x SDC risk 증가) |
| **ARM MTE** | 4-bit | 16B | Tag carve-out → 3.125% DRAM overhead + 1-4% 성능 저하 |
| **ECC Stealing (large tag)** | 9-15 bit | 32B | Single-bit error correction 불가, SDC risk 1.9x~120x 증가 |

### 1.3 GPU에서의 중요성

GPU가 HMM을 통해 application memory를 직접 접근하고, CUDA dynamic memory allocation이 보편화됨에 따라 GPU-side memory safety가 critical해짐. GPU는 DRAM 용량이 제한적이고 대역폭이 scarce하므로 tag storage overhead가 더 치명적.

---

## 방법론

### 3.1 Prior Art: Tagged ECC의 원리와 한계

**Tagged ECC**(Gumpertz 1981)는 ECC encoding 시 data와 tag를 함께 encode하지만, **tag를 memory에 명시적으로 저장하지 않는다**. Decoding 시 reference tag를 제공하여 equivalence check. 기존 Tagged ECC는 두 가지 문제:
- Small tag만 지원하거나
- Probabilistic tag mismatch detection (tag aliasing 존재)

### 3.2 AFT-ECC의 세 가지 속성

AFT-ECC는 다음을 동시에 만족하는 **새로운 class의 ECC code**:

1. **Alias-Free**: 모든 tag mismatch가 undetected로 남지 않음 (`0 ∉ T`, 즉 tag submatrix의 column space에 zero vector 없음)
2. **Single-Bit Error Correction 유지**: Tag submatrix의 column space `T`가 data/check-bit submatrix의 어떤 column과도 intersect하지 않음
3. **Maximal Tag Size**: 위 두 조건 하에서 가능한 최대 tag size

### 3.3 Parity Check Matrix Construction

Systematic AFT-ECC의 parity check matrix: `H = [Tᵀₛ | Dₖ | Iᵣ]`

- `Tᵀₛ`: R×TS tag submatrix (왼쪽에 추가)
- `Dₖ`: R×K data submatrix  
- `Iᵣ`: R×R identity submatrix (check-bit 위치)

**Encoding**: `check-bits = Dₖ × data ⊕ Tᵀₛ × tag`

**Decoding**: `syndrome = H × [tag | data | check-bits]ᵀ`

### 3.4 Alias-Free Tag Size Bound

AFT-ECC의 최대 tag size는 다음 bound를 따름 (Equation 5b):

```
TS ≤ ⌊log₂(2ᴿ - K - R)⌋
```

- `TS ≤ R-1` (R = check-bit 수). `TS=R`이면 모든 syndrome을 tag가 소비하여 error correction 불가
- Common SEC-DED codeword(power-of-2 data size)에서 **TS = R-1**
- **IMT-10 (R=10)**: TS ≤ 9-bit tag @ K=256 (32B)
- **IMT-16 (R=16)**: TS ≤ 15-bit tag @ K=256 (32B)

### 3.5 Recommended Construction

**Tag submatrix**: 모든 열이 even-weight인 left-invertible matrix. 권장: **all-weight-2 columns**

```
Equation 6: R≤16, TS≤15 tag submatrix
Column format (16 rows × 15 cols): all weight-2, forming a chain
→ 각 열은 2개의 1을 가진 unique pattern
```

**Data submatrix**: 모든 열이 odd-weight (Hsiao code → SEC-DED). Genetic algorithm으로 3-bit error detection maximization + row당 max 1's minimization.

### 3.6 AFT-ECC Constraints

1. **Fatal TMM**: Tag mismatch는 반드시 fatal error로 처리되어야 함 (multi-bit data error가 TMM으로 misattribution될 수 있으므로, recovery action은 두 경우 모두에 유효해야 함)
2. **No Tag Value Extraction**: AFT-ECC codeword에서 stored tag value를 안전하게 추출할 수 없음 (multi-bit error 존재 시 corrupted tag 추출 위험)

---

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1 Design: ECC에 Tag를 Implicit하게 Embed

IMT는 AFT-ECC를 GPU memory hierarchy에 적용:

- **Lock tag**: ECC check-bits에 embed → memory에 별도 저장 X
- **Key tag**: Pointer의 upper virtual address bits에 저장
- **Decoding 시**: 각 memory access마다 key tag를 ECC decoder에 전달하여 tag match 검증

### 4.2 GPU Memory Hierarchy 적용 (Figure 6)

```
Upper VA Bits (Key Tag) → ECC Encoder → {Data, ECC Check-Bits} → DRAM
DRAM → {Data, ECC Check-Bits} → ECC Decoder ← Key Tag → Tag Match Check
```

**변경 사항**:
- On-chip address bus widening (key tag 전달)
- ECC encoder/decoder에 TS개 column 추가
- L1 MSHR에 key tag 저장 필드 추가
- L2 cache atomic datapath의 ECC encode/decode에도 key tag 전달
- End-to-end ECC: L2 write-back cache 아래부터는 ECC가 유지되어야 함 (dirty writeback 시 tag extract 불가)

### 4.3 Software Interface & Precise Diagnosis (Figure 7)

**Hardware → Driver reporting**:
- Faulting address, key tag, ECC syndrome 전송

**Lock Tag Extraction**:
- 각 tag error는 unique syndrome에 mapping → syndrome lookup table (2ᴿ-1 entry)로 lock tag 추정
- `lock_tag_estimate = key_tag ⊕ error_pattern[syndrome]`

**Precise Diagnosis (optional, Equation 7)**:
```
if (Ref ≠ Key && Ref = Lock) → TMM (Tag Mismatch)
if (Ref = Key && Ref ≠ Lock) → DUE (Data Error)
if (Ref ≠ Key && Ref ≠ Lock) → BOTH
```
- Driver가 memory allocation 정보를 tree structure로 관리 → fault address의 reference tag lookup
- Fatal error 시에만 수행되므로 performance-critical하지 않음

### 4.4 Debug Mode

Privileged mode (nvidia-smi 등)에서 TMM을 non-fatal로 설정 → asynchronous DUE raise + TMM passive logging (CUDA context 파괴 없이 디버깅 가능). 단, synchronous error containment는 위반.

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]
- [[paper-wiki/concepts/security.md|Security]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2023ISCA-summarize/implicit-memory-tagging-no-overhead-memory-safety-using-alias-free-tagged-ecc.md|전체 요약 보기]]
