# DubStream AI - AI Pipeline Completion Change Plan

**Date:** January 2025  
**Scope:** Complete actual AI pipeline implementations  
**Risk Level:** MEDIUM (Core business logic, requires careful testing)

---

## PHASE 1: CURRENT STATE AUDIT

### File Status Analysis

#### Backend Services (app/services/)

| File | Current State | Status | Risk |
|------|---------------|--------|------|
| `asr_service.py` | MISSING | ❌ NEEDS CREATION | HIGH |
| `translation_service.py` | MISSING | ❌ NEEDS CREATION | HIGH |
| `tts_service.py` | MISSING | ❌ NEEDS CREATION | HIGH |
| `voice_clone_service.py` | MISSING | ❌ NEEDS CREATION | HIGH |
| `lipsync_service.py` | MISSING | ❌ NEEDS CREATION | HIGH |
| `render_service.py` | MISSING | ❌ NEEDS CREATION | HIGH |
| `storage_service.py` | EXISTS | ⚠️ PARTIALLY WORKING | MEDIUM |

#### Celery Tasks (app/tasks/pipeline_tasks.py)

| Task | Current State | Status | Risk |
|------|---------------|--------|------|
| `step1_ingest_video` | STUB | ⚠️ NEEDS IMPLEMENTATION | MEDIUM |
| `step2_extract_audio` | STUB | ⚠️ NEEDS IMPLEMENTATION | MEDIUM |
| `step3_transcribe` | STUB | ⚠️ NEEDS IMPLEMENTATION | HIGH |
| `step4_translate` | STUB | ⚠️ NEEDS IMPLEMENTATION | HIGH |
| `step5_align_timestamps` | STUB | ⚠️ NEEDS IMPLEMENTATION | MEDIUM |
| `step6_synthesize_voice` | STUB | ⚠️ NEEDS IMPLEMENTATION | HIGH |
| `step7_clone_voice` | STUB | ⚠️ NEEDS IMPLEMENTATION | HIGH |
| `step8_lipsync` | STUB | ⚠️ NEEDS IMPLEMENTATION | HIGH |
| `step9_render_video` | STUB | ⚠️ NEEDS IMPLEMENTATION | MEDIUM |
| `step10_upload_storage` | STUB | ⚠️ NEEDS IMPLEMENTATION | MEDIUM |

#### API Routes (app/api/routes/)

| File | Current State | Status | Risk |
|------|---------------|--------|------|
| `health.py` | WORKING | ✅ KEEP AS-IS | SAFE |
| `auth.py` | PARTIALLY WORKING | ✅ KEEP AS-IS | SAFE |
| `jobs.py` | STUB | ⚠️ NEEDS COMPLETION | MEDIUM |

#### Core Infrastructure

| File | Current State | Status | Risk |
|------|---------------|--------|------|
| `app/main.py` | WORKING | ✅ KEEP AS-IS | SAFE |
| `app/core/config.py` | WORKING | ✅ KEEP AS-IS | SAFE |
| `app/core/celery_app.py` | WORKING | ✅ KEEP AS-IS | SAFE |
| `app/db/session.py` | WORKING | ✅ KEEP AS-IS | SAFE |
| `app/models/__init__.py` | WORKING | ✅ KEEP AS-IS | SAFE |
| `docker-compose.yml` | WORKING | ✅ KEEP AS-IS | SAFE |
| `Dockerfile` | WORKING | ✅ KEEP AS-IS | SAFE |
| `requirements.txt` | OUTDATED | ⚠️ NEEDS UPDATES | MEDIUM |

---

## PHASE 2: IMPLEMENTATION PLAN

### Step 1: Create Missing Service Files

**Files to CREATE:**

1. `app/services/asr_service.py`
   - Faster-Whisper integration
   - Audio transcription
   - Language detection
   - Confidence scoring

2. `app/services/translation_service.py`
   - Google Translate integration
   - DeepL integration
   - Segment translation
   - Timestamp preservation

3. `app/services/tts_service.py`
   - Coqui XTTS-v2 integration
   - Voice synthesis
   - Speaker reference handling
   - Quality optimization

4. `app/services/voice_clone_service.py`
   - OpenVoice integration
   - ElevenLabs fallback
   - Audio normalization
   - Speaker embedding

5. `app/services/lipsync_service.py`
   - Wav2Lip integration
   - Face detection
   - Audio-visual sync
   - Quality preservation

6. `app/services/render_service.py`
   - FFmpeg video composition
   - Audio mixing
   - Subtitle burning
   - Quality settings

7. `app/services/speaker_diarization_service.py`
   - pyannote.audio integration
   - Speaker detection
   - Timeline mapping
   - Multi-speaker support

### Step 2: Update Celery Tasks

**File to MODIFY:**
`app/tasks/pipeline_tasks.py`

**Changes:**
- Replace stub implementations with real service calls
- Add proper error handling
- Add logging at each step
- Implement task orchestration
- Add progress tracking
- Implement retry logic

**Risk:** HIGH - Core business logic

### Step 3: Update Storage Service

**File to MODIFY:**
`app/services/storage_service.py`

**Changes:**
- Complete AWS S3 operations
- Complete Cloudflare R2 operations
- Add file verification
- Add metadata tracking
- Improve error handling

**Risk:** MEDIUM - External API integration

### Step 4: Complete API Routes

**File to MODIFY:**
`app/api/routes/jobs.py`

**Changes:**
- Implement POST /api/jobs/upload (real file handling)
- Implement GET /api/jobs/{job_id} (real job status)
- Implement GET /api/jobs/{job_id}/download (real file download)
- Add progress tracking
- Implement error responses

**Risk:** MEDIUM - API contracts

### Step 5: Update Requirements

**File to MODIFY:**
`requirements.txt`

**Changes:**
- Add: faster-whisper==1.0.2
- Add: pyannote.audio==3.0.0
- Add: deep-translator==1.11.4
- Add: deepl==1.18.0
- Add: TTS==0.24.1
- Add: openvoice (if available)
- Add: elevenlabs==0.2.1
- Update: FFmpeg-python==0.2.1
- Update: pydub==0.25.1

**Risk:** MEDIUM - Dependency management

---

## PHASE 3: BACKUP STRATEGY

**Action:** Create `backup_original/` directory

Files to backup:
```
backup_original/
├── app/services/storage_service.py (if modified)
├── app/tasks/pipeline_tasks.py (will be heavily modified)
├── app/api/routes/jobs.py (will be modified)
├── requirements.txt (will be modified)
```

**Purpose:** Allow rollback if issues occur

---

## PHASE 4: IMPLEMENTATION SEQUENCE

### Order of Implementation (Dependencies)

1. **First:** Create service layer files
   - asr_service.py
   - translation_service.py
   - speaker_diarization_service.py
   - tts_service.py
   - voice_clone_service.py
   - render_service.py
   - lipsync_service.py

2. **Second:** Update requirements.txt
   - Add all AI/ML dependencies

3. **Third:** Complete Celery pipeline tasks
   - Implement step1-step10 with real service calls
   - Add error handling and logging

4. **Fourth:** Update storage service
   - Complete S3/R2 operations

5. **Fifth:** Complete API routes
   - Implement job upload, status, download

6. **Sixth:** End-to-end testing
   - Test English → Arabic
   - Test Hindi → English
   - Test Urdu → French

---

## PHASE 5: TESTING PLAN

### Unit Tests
- Each service works independently
- Error handling works
- Service initialization works

### Integration Tests
- Services work together
- Celery tasks execute
- Job status updates work
- File operations work

### End-to-End Tests
- Upload video → Get job ID
- Job processes through all 10 steps
- Video renders successfully
- Download works
- Three language pairs verified

### Success Criteria

User journey:
```
1. Upload English video → Job created
2. Select "Dub to Arabic"
3. System processes:
   - Transcribes English
   - Translates to Arabic
   - Generates Arabic voice
   - Clones voice
   - Syncs lips
   - Renders video
   - Uploads to storage
4. Download dubbed video
5. Verify Arabic audio + English video
```

---

## PHASE 6: ROLLBACK PLAN

If critical issues occur:

1. Stop Celery workers
2. Restore from backup_original/
3. Restart system
4. Investigate issues
5. Retry with safer approach

---

## RISK ASSESSMENT

| Component | Risk | Mitigation |
|-----------|------|-----------|
| Whisper model loading | HIGH | Test on startup, handle gracefully |
| Memory usage (models) | HIGH | Monitor RAM, implement cleanup |
| GPU availability | HIGH | Fallback to CPU, document requirements |
| Translation quality | MEDIUM | Use proven services (Google/DeepL) |
| Voice cloning quality | HIGH | Test with multiple speakers |
| Lip sync accuracy | MEDIUM | Optional, skip on error |
| File upload size | MEDIUM | Implement size limits |
| Storage operations | MEDIUM | Implement retry logic |
| Task failures | MEDIUM | Implement queue retry |

---

## DEPENDENCIES & REQUIREMENTS

### Python Libraries
- faster-whisper
- pyannote.audio
- deep-translator / deepl
- TTS (Coqui)
- openvoice (optional)
- elevenlabs
- ffmpeg-python
- pydub
- librosa
- soundfile
- numpy

### System Requirements
- FFmpeg binary
- libsndfile1
- CUDA (optional, for GPU acceleration)

### External APIs
- Google Translate (free tier available)
- DeepL (free tier available)
- ElevenLabs (free tier available)
- AWS S3 (credentials needed)
- Cloudflare R2 (credentials needed)

---

## TIMELINE

| Phase | Tasks | Estimated Time |
|-------|-------|-----------------|
| Setup | Create services, backup | 1 hour |
| Implementation | Code all services | 8-12 hours |
| Integration | Connect tasks, test | 4-6 hours |
| Testing | E2E testing, fixes | 4-8 hours |
| **Total** | | **17-27 hours** |

---

## SUCCESS DEFINITION

✅ Task complete when:

1. User uploads video → Job starts
2. Transcription works (Whisper)
3. Translation works (Google/DeepL)
4. Voice synthesis works (XTTS)
5. Voice cloning works (OpenVoice or ElevenLabs)
6. Lip sync works (Wav2Lip)
7. Video renders (FFmpeg)
8. Download works (S3/R2)
9. Three language pairs verified
10. No broken existing features

---

## DO NOT CHANGE

✅ PRESERVE AS-IS:
- Frontend code
- UI/design
- Database schema
- Authentication
- Monitoring
- Kubernetes configs
- CI/CD pipelines
- Documentation
- Styling
- API contracts (only fill in stubs)

---

**Status:** READY FOR IMPLEMENTATION  
**Approval Needed:** YES - Confirm before starting Phase 1

