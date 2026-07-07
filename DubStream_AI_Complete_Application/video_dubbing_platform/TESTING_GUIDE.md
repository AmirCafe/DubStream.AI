# DubStream AI - Testing Guide

**Status:** Implementation Complete - Ready for Testing  
**Configuration:** Free & Open-Source Stack  
**Estimated Runtime:** 5-15 minutes per video (CPU), 1-3 minutes (GPU)

---

## 🎯 PRE-TESTING CHECKLIST

### System Requirements

```
Minimum (CPU):
- 8GB RAM
- 20GB disk space (for models)
- FFmpeg installed
- Python 3.11+

Recommended (GPU):
- NVIDIA GPU (RTX 3060+)
- CUDA 11.8+
- 16GB VRAM
- 30GB disk space
```

### Check System Setup

```bash
# Check Python version
python --version  # Should be 3.11+

# Check FFmpeg
ffmpeg -version

# Check Docker
docker --version
docker-compose --version

# Check GPU availability
python -c "import torch; print(torch.cuda.is_available())"
```

---

## 🐳 DOCKER SETUP

### Start Services

```bash
cd /home/claude/video_dubbing_platform

# Start all services (development)
docker-compose up

# In another terminal, verify services are running
docker-compose ps

# View logs
docker-compose logs -f api
docker-compose logs -f redis
docker-compose logs -f postgres
```

### Services Running

```
✅ PostgreSQL:  localhost:5432
✅ Redis:       localhost:6379
✅ FastAPI:     http://localhost:8000
✅ Swagger:     http://localhost:8000/docs
✅ Frontend:    http://localhost:3000
```

---

## 📋 TEST SCENARIO 1: English → Arabic

### Step 1: Prepare Test Video

Create a simple test video with English speech:

```bash
# Using FFmpeg to create a test video
ffmpeg -f lavfi -i testsrc=s=1280x720:d=10 -f lavfi -i sine=f=1000:d=10 \
  -pix_fmt yuv420p -vf scale=1280:720 \
  test_english.mp4

# OR use an existing English video
# Just ensure it's < 500MB
```

### Step 2: Upload via API

```bash
curl -X POST http://localhost:8000/api/jobs/upload \
  -F "file=@test_english.mp4" \
  -F "target_language=ar"

# Response:
# {
#   "job_id": "abc123...",
#   "status": "pending",
#   "progress": 0
# }
```

Save the `job_id` for next steps.

### Step 3: Monitor Progress

```bash
# Check status every 10 seconds
curl http://localhost:8000/api/jobs/{job_id}

# Expected progression:
# Step 1: 10% - Ingesting
# Step 2: 20% - Extracting audio
# Step 3: 30% - Transcribing
# Step 4: 40% - Translating
# Step 5: 50% - Aligning timestamps
# Step 6: 60% - Synthesizing voice
# Step 7: 70% - Cloning voice
# Step 8: 80% - Lip-sync (optional)
# Step 9: 90% - Rendering
# Step 10: 100% - Uploading
```

### Step 4: Download Result

```bash
# When status = "completed"
curl http://localhost:8000/api/jobs/{job_id}/download \
  -o dubbed_arabic.mp4

# Play the video
ffplay dubbed_arabic.mp4
```

### Verification Checklist

- [ ] Video uploads successfully
- [ ] Job ID returned
- [ ] Progress increases over time
- [ ] All 10 steps complete
- [ ] Output video created
- [ ] Audio is in Arabic
- [ ] Video quality acceptable
- [ ] Subtitles present (optional)
- [ ] Lip-sync matches (if available)

---

## 📋 TEST SCENARIO 2: Hindi → English

### Repeat Steps 1-4

```bash
# Create or upload Hindi video
curl -X POST http://localhost:8000/api/jobs/upload \
  -F "file=@test_hindi.mp4" \
  -F "target_language=en"

# Monitor and download
```

### Verification Checklist

- [ ] Hindi detected correctly
- [ ] Transcription accurate
- [ ] Translation to English correct
- [ ] Voice synthesis natural
- [ ] Audio clear and audible
- [ ] No loss of meaning in translation

---

## 📋 TEST SCENARIO 3: Urdu → French

```bash
# Upload Urdu video
curl -X POST http://localhost:8000/api/jobs/upload \
  -F "file=@test_urdu.mp4" \
  -F "target_language=fr"

# Monitor and download
```

### Verification Checklist

- [ ] Urdu detected and transcribed
- [ ] Translation to French accurate
- [ ] French pronunciation natural
- [ ] Speaker characteristics preserved
- [ ] Output quality acceptable

---

## 🔍 DETAILED TESTING

### Test Transcription

```bash
# Test Whisper directly
python -c "
from app.services.asr_service import ASRService
asr = ASRService(device='auto')
result = asr.transcribe('test_audio.wav')
print(f'Language: {result[\"language\"]}')
print(f'Text: {result[\"text\"]}')
print(f'Confidence: {result[\"language_probability\"]}')
"
```

### Test Translation

```bash
# Test Google Translate
python -c "
from app.services.translation_service import TranslationService
translator = TranslationService()
text = 'Hello, how are you?'
translated = translator.translate_text(text, 'en', 'ar')
print(f'English: {text}')
print(f'Arabic: {translated}')
"
```

### Test TTS

```bash
# Test Coqui XTTS-v2
python -c "
from app.services.tts_service import TTSService
tts = TTSService(device='auto')
audio = tts.synthesize('مرحبا', 'ar')
print(f'Generated {len(audio)} audio samples')
"
```

### Test Voice Cloning

```bash
# Test voice cloning
python -c "
from app.services.voice_clone_service import VoiceCloneService
cloner = VoiceCloneService()
# Requires synthesized audio and speaker reference
# See pipeline_tasks.py for usage
"
```

### Test Rendering

```bash
# Test FFmpeg operations
python -c "
from app.services.render_service import RenderService
render = RenderService()
info = render.get_video_info('test_video.mp4')
print(f'Duration: {info[\"duration\"]}s')
print(f'Bitrate: {info[\"bitrate\"]} bps')
"
```

### Test Storage

```bash
# Test file storage
python -c "
from app.services.storage_service import StorageService
storage = StorageService(backend='local', path='/data/videos')
result = storage.upload_file('test.mp4', 'jobs/test/output.mp4')
print(f'Upload success: {result[\"success\"]}')
print(f'URL: {result[\"url\"]}')
"
```

---

## 📊 PERFORMANCE METRICS

### Expected Processing Times

**CPU Only (Intel i7/Ryzen 7):**
```
Transcription:    2-5 minutes
Translation:      1-2 seconds
TTS Synthesis:    3-8 minutes
Voice Cloning:    2-3 minutes
Lip-Sync:         SKIP (needs GPU)
Rendering:        2-3 minutes
─────────────────────────────
Total:            ~12-22 minutes per video
```

**GPU (NVIDIA RTX 3060+):**
```
Transcription:    30-60 seconds
Translation:      1-2 seconds
TTS Synthesis:    1-2 minutes
Voice Cloning:    30-60 seconds
Lip-Sync:         2-5 minutes
Rendering:        1-2 minutes
─────────────────────────────
Total:            ~5-10 minutes per video
```

### Memory Usage

```
Idle:             ~500MB
With Whisper:     +2GB
With XTTS-v2:     +4GB
With Wav2Lip:     +6GB
─────────────────────────────
Peak (all):       ~12GB
```

### Disk Usage

```
Models:           ~8GB
Test videos:      ~200MB
Outputs:          ~100-500MB per video
─────────────────────────────
Total:            ~8-9GB
```

---

## 🐛 TROUBLESHOOTING

### Issue: "Whisper model download fails"

**Solution:**
```bash
# Download manually
python -c "
from faster_whisper import WhisperModel
model = WhisperModel('medium', download_root='/models/whisper')
"
```

### Issue: "XTTS-v2 out of memory"

**Solution:**
```bash
# Use smaller model or CPU only
TTS(
    model_name='tts_models/multilingual/multi-dataset/xtts_v2',
    device='cpu',
    gpu_memory=0
)
```

### Issue: "Wav2Lip not found"

**Solution:**
```bash
# Lip-sync is optional and will be skipped
# Check logs: "Lip-sync skipped, using original video"
# This is expected behavior on CPU-only systems
```

### Issue: "FFmpeg not found"

**Solution:**
```bash
# Install FFmpeg
# Ubuntu/Debian:
sudo apt-get install ffmpeg

# macOS:
brew install ffmpeg

# Windows:
choco install ffmpeg
```

### Issue: "PostgreSQL connection refused"

**Solution:**
```bash
# Verify Docker is running
docker ps

# Restart services
docker-compose restart postgres
docker-compose logs postgres

# Check connection
psql postgresql://postgres:postgres@localhost:5432/dubstream
```

### Issue: "Job stuck in 'processing' state"

**Solution:**
```bash
# Check Celery worker logs
docker-compose logs celery

# Restart worker
docker-compose restart celery

# Check Redis
redis-cli ping  # Should return PONG
```

---

## ✅ SUCCESS CRITERIA

### Transcription
✅ Text extracted from audio  
✅ Language detected correctly  
✅ Confidence score available  

### Translation
✅ Text translated to target language  
✅ Special characters preserved  
✅ Timing information maintained  

### Voice Synthesis
✅ Audio generated from text  
✅ Quality acceptable  
✅ Duration matches original  

### Voice Cloning
✅ Speaker characteristics detected  
✅ Audio normalized  
✅ Voice enhancement applied  

### Rendering
✅ Video + audio combined  
✅ Quality maintained  
✅ Subtitles added (optional)  

### Download
✅ File downloads successfully  
✅ Video playable  
✅ Audio is dubbed language  

---

## 📈 MONITORING

### Real-Time Logs

```bash
# API logs
docker-compose logs -f api

# Celery worker logs
docker-compose logs -f celery

# Database logs
docker-compose logs -f postgres

# All services
docker-compose logs -f
```

### Database Inspection

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d dubstream

# View jobs
SELECT id, status, progress, current_step, target_language 
FROM job 
ORDER BY created_at DESC 
LIMIT 10;

# View failed jobs
SELECT id, status, error_message 
FROM job 
WHERE status = 'failed' 
ORDER BY created_at DESC;
```

### Redis Inspection

```bash
# Connect to Redis
redis-cli

# View queue
LLEN celery

# View task info
KEYS celery*

# Monitor real-time
MONITOR
```

---

## 🔄 REGRESSION TESTING

After each change, verify:

```bash
# Test API health
curl http://localhost:8000/health

# Test each endpoint
curl http://localhost:8000/api/jobs

# Test database connection
curl http://localhost:8000/api/jobs -X GET

# Test full pipeline with small test video
```

---

## 📝 TEST REPORT TEMPLATE

```markdown
# Test Report - [Date]

## Test Case: [Language Pair]

### Input
- Video: [filename]
- Duration: [seconds]
- Language: [source language]
- Target: [target language]

### Execution
- Start time: [time]
- End time: [time]
- Duration: [minutes:seconds]
- GPU used: [Yes/No]

### Results
- Transcription: [✅/❌] - [quality]
- Translation: [✅/❌] - [accuracy]
- TTS: [✅/❌] - [naturalness]
- Voice clone: [✅/❌] - [similarity]
- Rendering: [✅/❌] - [quality]
- Download: [✅/❌]

### Notes
- [Any issues encountered]
- [Performance observations]
- [Quality assessment]

### Overall Status: [PASS/FAIL]
```

---

## 🎯 NEXT STEPS

1. ✅ Start Docker services
2. ✅ Verify all services running
3. ✅ Run Test Scenario 1 (English → Arabic)
4. ✅ Run Test Scenario 2 (Hindi → English)
5. ✅ Run Test Scenario 3 (Urdu → French)
6. ✅ Document results
7. ✅ Fix any issues
8. ✅ Production deployment

---

**Ready to test! 🚀**

