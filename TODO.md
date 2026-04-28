# AAMS Restructuring TODO

## Phase 1 — Directory & Foundation
- [x] 1. Create folder tree structure
- [x] 2. Create `.env` with environment variables
- [x] 3. Create `run.py` entry point
- [x] 4. Create `app/__init__.py` (Application Factory)
- [x] 5. Create `app/config.py` (Config classes)
- [x] 6. Create `app/extensions.py` (Extension placeholders)

## Phase 2 — Database & Models
- [x] 7. Create `app/database/db.py`
- [x] 8. Create `app/models/student.py`
- [x] 9. Create `app/models/attendance.py`
- [x] 10. Create `app/models/user.py`

## Phase 3 — Services (Business Logic Layer)
- [x] 11. Create `app/services/face_recognition_service.py`
- [x] 12. Create `app/services/attendance_service.py`
- [x] 13. Create `app/services/report_service.py`

## Phase 4 — Routes (Blueprints)
- [x] 14. Create `app/routes/dashboard_routes.py`
- [x] 15. Create `app/routes/student_routes.py`
- [x] 16. Create `app/routes/attendance_routes.py`
- [x] 17. Create `app/routes/auth_routes.py`

## Phase 5 — Frontend Restructure
- [x] 18. Move & rename templates with Jinja2 url_for fixes
- [x] 19. Move static assets to proper folders
- [x] 20. Split JS into modular files

## Phase 6 — Utilities & Image Data
- [x] 21. Create `app/utils/constants.py`
- [x] 22. Create `app/utils/helpers.py`
- [x] 23. Setup `app/image_data/` structure

## Phase 7 — Documentation & Cleanup
- [x] 24. Update `requirements.txt`
- [x] 25. Rewrite `README.md`
- [x] 26. Update `API_DOCUMENTATION.md`
- [x] 27. Create `instance/config.py`
- [x] 28. Create `app/database/migrations/`
- [ ] 29. Clean up old flat files in APP/

## Phase 8 — Verification
- [x] 30. Test `python run.py` startup
- [x] 31. Verify all pages render
- [x] 32. Verify video feed and face recognition

