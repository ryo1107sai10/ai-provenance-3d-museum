"""Hash pipeline: SHA-256 (exact) + pHash (perceptual, re-encode tolerant).

pHash strategy (pro spec):
- If `videohash` / ffmpeg is available in your environment, hash keyframes.
- Fallback used here: decode the first decodable frame with Pillow-compatible
  pipelines is not possible for raw video bytes, so we derive a stable
  perceptual-style fingerprint from sampled byte windows. Replace
  `compute_phash()` with imagehash.phash(Image.open(keyframe)) in production
  once keyframe extraction (ffmpeg) is wired in.
"""
import hashlib

def calculate_sha256(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()

def compute_phash(file_bytes: bytes) -> str:
    # Try real image pHash when the payload is an image/keyframe
    try:
        import io, imagehash
        from PIL import Image
        img = Image.open(io.BytesIO(file_bytes))
        return str(imagehash.phash(img))
    except Exception:
        pass
    # Deterministic fallback fingerprint (documented as placeholder, not a true pHash)
    h = hashlib.sha256()
    step = max(1, len(file_bytes) // 64)
    h.update(file_bytes[::step][:4096])
    return "sampled-" + h.hexdigest()[:16]

def build_metadata(file_bytes: bytes) -> dict:
    return {"sha256": calculate_sha256(file_bytes), "phash": compute_phash(file_bytes)}
