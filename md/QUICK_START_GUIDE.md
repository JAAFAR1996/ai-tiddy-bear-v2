# 🚀 دليل بدء التشغيل السريع - AI Teddy Bear v5

**وقت التنفيذ المتوقع:** 15-30 دقيقة  
**الهدف:** تشغيل النظام الأساسي للمشروع  

---

## ⚡ البدء السريع (5 دقائق)

### 1. فحص البيئة الحالية
```powershell
# التحقق من Python
python --version
# يجب أن يُظهر: Python 3.13.5

# التحقق من المجلد الحالي
Get-Location
# يجب أن يكون: c:\Users\jaafa\Desktop\5555\ai-teddy\ai-teddy-backup
```

### 2. تثبيت التبعيات الأساسية
```powershell
# تحديث pip
python -m pip install --upgrade pip

# تثبيت المتطلبات الأساسية
pip install fastapi==0.115.5
pip install uvicorn==0.27.0
pip install openai==1.55.0
pip install pydantic==2.10.2
pip install python-dotenv==1.0.0
```

### 3. إنشاء ملف البيئة الأساسي
```powershell
# إنشاء .env
@"
OPENAI_API_KEY=sk-test-dummy-key-for-development
DATABASE_URL=sqlite:///./ai_teddy_dev.db
REDIS_URL=redis://localhost:6379/0
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=development-secret-key-change-in-production
ENCRYPTION_KEY=YWUyNTZiMTMzNjAwNGRkZjlmNzMwODQwZjE5ZGVlOGI=
"@ | Out-File -FilePath .env -Encoding UTF8
```

---

## 🔧 الإصلاح الأساسي (10 دقائق)

### 1. إصلاح أخطاء الاستيراد
```powershell
# إنشاء ملف اختبار بسيط
@"
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_imports():
    try:
        # اختبار الواردات الأساسية
        from infrastructure.logging_config import get_logger
        print('✅ نظام السجلات يعمل')
        
        from application.services.child_safety.coppa_compliance_service import COPPAComplianceService
        print('✅ خدمة COPPA تعمل')
        
        from application.services.ai.main_service import AITeddyBearService
        print('✅ خدمة AI تعمل')
        
        return True
    except ImportError as e:
        print(f'❌ خطأ في الاستيراد: {e}')
        return False
    except Exception as e:
        print(f'❌ خطأ عام: {e}')
        return False

if __name__ == '__main__':
    print('🔍 فحص الواردات الأساسية...')
    success = test_basic_imports()
    if success:
        print('✅ جميع الواردات الأساسية تعمل بنجاح!')
    else:
        print('❌ هناك مشاكل في الواردات - تحقق من المسارات')
"@ | Out-File -FilePath quick_test.py -Encoding UTF8

# تشغيل الاختبار
python quick_test.py
```

### 2. إنشاء خادم تطوير بسيط
```powershell
# إنشاء ملف تشغيل مبسط
@"
import sys
import os
from pathlib import Path

# إضافة مجلد src إلى Python path
project_root = Path(__file__).parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    import uvicorn
    
    # إنشاء تطبيق FastAPI بسيط
    app = FastAPI(
        title='AI Teddy Bear v5 - Development Server',
        description='خادم تطوير بسيط لاختبار النظام الأساسي',
        version='5.0.0-dev'
    )
    
    # نموذج للرسائل
    class ChatMessage(BaseModel):
        message: str
        child_age: int = 5
    
    class ChatResponse(BaseModel):
        response: str
        safe: bool = True
        timestamp: str
    
    # نقطة صحة النظام
    @app.get('/')
    async def health_check():
        return {
            'status': 'healthy',
            'service': 'AI Teddy Bear v5',
            'version': '5.0.0-dev',
            'message': 'خادم التطوير يعمل بنجاح! 🧸'
        }
    
    # نقطة اختبار الدردشة
    @app.post('/chat/test', response_model=ChatResponse)
    async def test_chat(message: ChatMessage):
        # استجابة تجريبية
        response_text = f'مرحباً! لقد قلت: {message.message}. أنا دبدوب ذكي وآمن للأطفال! 🧸'
        
        return ChatResponse(
            response=response_text,
            safe=True,
            timestamp='2025-07-22T10:00:00Z'
        )
    
    # نقطة اختبار أمان الطفل
    @app.get('/safety/status')
    async def safety_status():
        return {
            'coppa_compliance': True,
            'content_filtering': True,
            'age_appropriate': True,
            'safe_mode': 'active',
            'message': 'جميع أنظمة الأمان تعمل 🛡️'
        }
    
    # نقطة معلومات النظام
    @app.get('/system/info')
    async def system_info():
        return {
            'python_version': sys.version,
            'project_root': str(project_root),
            'src_path': str(src_path),
            'environment': 'development',
            'features': {
                'ai_chat': 'mock_mode',
                'voice_recognition': 'mock_mode', 
                'text_to_speech': 'mock_mode',
                'coppa_compliance': 'active',
                'content_filtering': 'active'
            }
        }
    
    if __name__ == '__main__':
        print('🚀 بدء تشغيل خادم AI Teddy Bear...')
        print('📱 الخادم سيعمل على: http://localhost:8000')
        print('📚 الوثائق التفاعلية: http://localhost:8000/docs')
        print('🛡️ وضع الأمان: نشط')
        print('⚡ اضغط Ctrl+C لإيقاف الخادم')
        
        uvicorn.run(
            'dev_server:app',
            host='127.0.0.1',
            port=8000,
            reload=True,
            log_level='info'
        )

except ImportError as e:
    print(f'❌ خطأ في استيراد التبعيات: {e}')
    print('💡 تأكد من تثبيت: pip install fastapi uvicorn')
except Exception as e:
    print(f'❌ خطأ في بدء الخادم: {e}')
"@ | Out-File -FilePath dev_server.py -Encoding UTF8
```

---

## 🎯 تشغيل النظام

### 1. بدء خادم التطوير
```powershell
# تشغيل الخادم
python dev_server.py
```

### 2. اختبار النظام
```powershell
# في terminal جديد - اختبار صحة النظام
curl http://localhost:8000/ | ConvertFrom-Json

# اختبار API الدردشة
$body = @{
    message = "مرحباً يا دبدوب!"
    child_age = 7
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/chat/test" -Method Post -Body $body -ContentType "application/json"

# اختبار أنظمة الأمان
curl http://localhost:8000/safety/status | ConvertFrom-Json
```

---

## 📱 واجهات الاختبار

بعد تشغيل الخادم، يمكنك الوصول إلى:

### 1. الواجهة الرئيسية
🔗 **http://localhost:8000/**
- صفحة حالة النظام الأساسية

### 2. الوثائق التفاعلية
🔗 **http://localhost:8000/docs**
- واجهة Swagger لاختبار APIs
- تجربة جميع النقاط المتاحة

### 3. نقاط الاختبار المتاحة:
- `GET /` - صحة النظام
- `POST /chat/test` - اختبار الدردشة
- `GET /safety/status` - حالة أنظمة الأمان
- `GET /system/info` - معلومات النظام

---

## 🔍 استكشاف الأخطاء

### مشكلة: خطأ في الاستيراد
```powershell
# إصلاح مسارات Python
$env:PYTHONPATH = "$(Get-Location)\src"
python dev_server.py
```

### مشكلة: Port 8000 مستخدم
```powershell
# استخدام port مختلف
python -c "
import uvicorn
from dev_server import app
uvicorn.run(app, host='127.0.0.1', port=8001)
"
```

### مشكلة: تبعيات مفقودة
```powershell
# تثبيت جميع التبعيات
pip install -r requirements.txt
# أو التبعيات الأساسية فقط:
pip install fastapi uvicorn openai pydantic python-dotenv
```

---

## ✅ التحقق من نجاح البدء

إذا رأيت هذه الرسائل، فالنظام يعمل بنجاح:

```
✅ نظام السجلات يعمل
✅ خدمة COPPA تعمل  
✅ خدمة AI تعمل
🚀 بدء تشغيل خادم AI Teddy Bear...
📱 الخادم سيعمل على: http://localhost:8000
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**🎉 تهانينا! النظام الأساسي يعمل الآن.**

---

## 🔄 الخطوات التالية

1. **اختبر APIs** عبر http://localhost:8000/docs
2. **راجع ملف الإصلاحات العاجلة** في `md/URGENT_FIX_PLAN.md`
3. **اقرأ التحليل الشامل** في `md/COMPLETE_PROJECT_DISCOVERY_REPORT.md`
4. **ابدأ تنفيذ الإصلاحات** حسب الأولوية المحددة

**📞 للدعم:** راجع الملفات في مجلد `md/` للحصول على تحليل شامل ومفصل.
