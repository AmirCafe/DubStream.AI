# DubStream AI - Quick Start Guide

**Status:** ✅ AI Pipeline Complete & Ready to Test  
**Total Implementation:** 2900+ lines of code  
**Services:** 8 AI/ML services integrated  
**Pipeline:** 10-step end-to-end workflow  

---

## ⚡ 5-MINUTE SETUP

### 1. Check Prerequisites

```bash
python --version  # Must be 3.11+
ffmpeg -version   # Must be installed
docker --version
docker-compose --version
```

### 2. Start Services

```bash
cd /home/claude/video_dubbing_platform
docker-compose up
```

### 3. Verify Services

```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

---

## 🎬 FIRST TEST

### Upload & Dub to Arabic

```bash
# Create test video (30 seconds)
ffmpeg -f lavfi -i testsrc=s=1280x720:d=30 \
       -f lavfi -i sine=f=1000:d=30 \
       -pix_fmt yuv420p test.mp4

# Upload and queue
JOB_ID=$(curl -X POST http://localhost:8000/api/jobs/upload \
  -F "file=@test.mp4" \
  -F "target_language=ar" | jq -r '.job_id')

# Check progress
curl http://localhost:8000/api/jobs/$JOB_ID

# Download (when complete)
curl http://localhost:8000/api/jobs/$JOB_ID/download -o dubbed_ar.mp4

# Play result
ffplay dubbed_ar.mp4
```

---

## 📊 WHAT'S INCLUDED

**8 AI Services** (1800+ lines):
- Whisper ASR (99 languages)
- Google Translate (100+ languages)
- Coqui XTTS-v2 TTS
- Audio voice cloning
- Speaker diarization
- Wav2Lip lip-sync
- FFmpeg rendering
- Multi-backend storage

**10-Step Pipeline** (500+ lines):
1. Video ingestion
2. Audio extraction
3. Transcription
4. Translation
5. Timestamp alignment
6. Voice synthesis
7. Voice cloning
8. Lip-sync (optional)
9. Video rendering
10. Storage upload

**API Endpoints** (300+ lines):
- Upload, status, download, list, delete

---

## ⏱️ EXPECTED TIMES

**CPU Only:** 12-22 minutes per video  
**GPU:** 5-10 minutes per video  
**Models:** 5-10GB (first download)

---

## 🎯 TEST LANGUAGES

```bash
# English → Arabic
curl -X POST http://localhost:8000/api/jobs/upload \
  -F "file=@video_en.mp4" -F "target_language=ar"

# Hindi → English
curl -X POST http://localhost:8000/api/jobs/upload \
  -F "file=@video_hi.mp4" -F "target_language=en"

# Urdu → French
curl -X POST http://localhost:8000/api/jobs/upload \
  -F "file=@video_ur.mp4" -F "target_language=fr"
```

---

## 📈 MONITOR PROGRESS

```bash
# Watch real-time updates
JOB_ID="your_job_id"
while true; do
  curl -s http://localhost:8000/api/jobs/$JOB_ID | jq .progress
  sleep 10
done

# View detailed logs
docker-compose logs -f api
docker-compose logs -f celery
```

---

## 🎯 SUCCESS CRITERIA

✅ Video uploads successfully  
✅ Job ID returned  
✅ Progress updates (0-100%)  
✅ All 10 steps complete  
✅ Output video generated  
✅ Audio dubbed in target language  
✅ Subtitles added  
✅ Download works  

---

## 🛠️ CONFIG

**Default:** Local storage  
**Options:** S3, R2, or Local  
**Device:** Auto-detects GPU  
**Languages:** 99+ supported  

---

## ⚠️ TROUBLESHOOT

```bash
# Check services
docker-compose ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Health check
curl http://localhost:8000/health
```

---

**Ready to test! 🚀**

