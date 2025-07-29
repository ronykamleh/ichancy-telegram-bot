# دليل API للمطورين 👨‍💻

هذا الدليل يوضح كيفية دمج APIs خارجية مع بوت التليجرام لأتمتة عمليات الدفع والسحب.

## 🔌 نظرة عامة على APIs

البوت يدعم ثلاثة أنواع من APIs للمدفوعات:
1. **Syriatel Cash API** - للدفع عبر سيريتل كاش
2. **Bank API** - للتحويلات البنكية
3. **USDT API** - للعملات المشفرة

## 🏗️ هيكل API العام

### طلب الإيداع (Deposit Request)
```json
{
  "user_id": "123456789",
  "amount": 100.00,
  "payment_method": "syriatel_cash",
  "phone_number": "+963912345678",
  "transaction_id": "TXN_20240101_001"
}
```

### طلب السحب (Withdrawal Request)
```json
{
  "user_id": "123456789",
  "amount": 50.00,
  "payment_method": "syriatel_cash",
  "phone_number": "+963912345678",
  "transaction_id": "TXN_20240101_002"
}
```

### استجابة API
```json
{
  "success": true,
  "transaction_id": "TXN_20240101_001",
  "status": "completed",
  "message": "تمت العملية بنجاح",
  "balance": 150.00,
  "fee": 2.00
}
```

## 📱 Syriatel Cash API

### إعداد API
```python
# في ملف config.py
SYRIATEL_CASH_CONFIG = {
    'api_key': os.getenv('SYRIATEL_CASH_API_KEY'),
    'base_url': 'https://api.syriatelcash.sy/v1',
    'merchant_id': os.getenv('SYRIATEL_MERCHANT_ID'),
    'secret_key': os.getenv('SYRIATEL_SECRET_KEY')
}
```

### تنفيذ API
```python
import requests
import hashlib
import time
from config import SYRIATEL_CASH_CONFIG

class SyriatelCashAPI:
    def __init__(self):
        self.config = SYRIATEL_CASH_CONFIG
        self.base_url = self.config['base_url']
        self.api_key = self.config['api_key']
        self.merchant_id = self.config['merchant_id']
        self.secret_key = self.config['secret_key']
    
    def _generate_signature(self, data):
        """توليد التوقيع الرقمي للطلب"""
        sorted_data = sorted(data.items())
        query_string = '&'.join([f"{k}={v}" for k, v in sorted_data])
        signature_string = f"{query_string}&secret={self.secret_key}"
        return hashlib.sha256(signature_string.encode()).hexdigest()
    
    def _make_request(self, endpoint, data):
        """إرسال طلب إلى API"""
        data['merchant_id'] = self.merchant_id
        data['timestamp'] = int(time.time())
        data['signature'] = self._generate_signature(data)
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f"{self.base_url}/{endpoint}",
            json=data,
            headers=headers,
            timeout=30
        )
        
        return response.json()
    
    async def process_deposit(self, user_id, amount, phone_number):
        """معالجة طلب الإيداع"""
        data = {
            'user_id': str(user_id),
            'amount': float(amount),
            'phone_number': phone_number,
            'transaction_type': 'deposit',
            'currency': 'SYP'
        }
        
        try:
            result = self._make_request('deposit', data)
            return {
                'success': result.get('success', False),
                'transaction_id': result.get('transaction_id'),
                'status': result.get('status'),
                'message': result.get('message', 'خطأ غير معروف')
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في الاتصال: {str(e)}'
            }
    
    async def process_withdrawal(self, user_id, amount, phone_number):
        """معالجة طلب السحب"""
        data = {
            'user_id': str(user_id),
            'amount': float(amount),
            'phone_number': phone_number,
            'transaction_type': 'withdrawal',
            'currency': 'SYP'
        }
        
        try:
            result = self._make_request('withdrawal', data)
            return {
                'success': result.get('success', False),
                'transaction_id': result.get('transaction_id'),
                'status': result.get('status'),
                'message': result.get('message', 'خطأ غير معروف')
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في الاتصال: {str(e)}'
            }
    
    async def check_transaction_status(self, transaction_id):
        """التحقق من حالة المعاملة"""
        data = {'transaction_id': transaction_id}
        
        try:
            result = self._make_request('status', data)
            return {
                'success': result.get('success', False),
                'status': result.get('status'),
                'message': result.get('message')
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في الاتصال: {str(e)}'
            }
```

## 🏦 Bank API

### إعداد API
```python
# في ملف config.py
BANK_API_CONFIG = {
    'api_key': os.getenv('BANK_API_KEY'),
    'base_url': 'https://api.bank.sy/v1',
    'bank_code': os.getenv('BANK_CODE'),
    'account_number': os.getenv('BANK_ACCOUNT_NUMBER')
}
```

### تنفيذ API
```python
import requests
import base64
from config import BANK_API_CONFIG

class BankAPI:
    def __init__(self):
        self.config = BANK_API_CONFIG
        self.base_url = self.config['base_url']
        self.api_key = self.config['api_key']
        self.bank_code = self.config['bank_code']
        self.account_number = self.config['account_number']
    
    def _get_headers(self):
        """إعداد headers للطلبات"""
        auth_string = base64.b64encode(f"{self.api_key}:".encode()).decode()
        return {
            'Authorization': f'Basic {auth_string}',
            'Content-Type': 'application/json',
            'X-Bank-Code': self.bank_code
        }
    
    async def process_deposit(self, user_id, amount, account_info):
        """معالجة طلب الإيداع البنكي"""
        data = {
            'from_account': account_info['account_number'],
            'to_account': self.account_number,
            'amount': float(amount),
            'currency': 'SYP',
            'reference': f"DEPOSIT_{user_id}_{int(time.time())}",
            'description': f'إيداع رصيد للمستخدم {user_id}'
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/transfer",
                json=data,
                headers=self._get_headers(),
                timeout=30
            )
            
            result = response.json()
            return {
                'success': result.get('success', False),
                'transaction_id': result.get('transaction_id'),
                'status': result.get('status'),
                'message': result.get('message', 'خطأ غير معروف')
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في الاتصال: {str(e)}'
            }
    
    async def process_withdrawal(self, user_id, amount, account_info):
        """معالجة طلب السحب البنكي"""
        data = {
            'from_account': self.account_number,
            'to_account': account_info['account_number'],
            'amount': float(amount),
            'currency': 'SYP',
            'reference': f"WITHDRAWAL_{user_id}_{int(time.time())}",
            'description': f'سحب رصيد للمستخدم {user_id}'
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/transfer",
                json=data,
                headers=self._get_headers(),
                timeout=30
            )
            
            result = response.json()
            return {
                'success': result.get('success', False),
                'transaction_id': result.get('transaction_id'),
                'status': result.get('status'),
                'message': result.get('message', 'خطأ غير معروف')
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في الاتصال: {str(e)}'
            }
```

## ₿ USDT API

### إعداد API
```python
# في ملف config.py
USDT_API_CONFIG = {
    'api_key': os.getenv('USDT_API_KEY'),
    'api_secret': os.getenv('USDT_API_SECRET'),
    'base_url': 'https://api.binance.com/api/v3',
    'wallet_address': os.getenv('USDT_WALLET_ADDRESS'),
    'network': 'TRC20'  # أو BEP20
}
```

### تنفيذ API
```python
import requests
import hmac
import hashlib
import time
from config import USDT_API_CONFIG

class USDTAPI:
    def __init__(self):
        self.config = USDT_API_CONFIG
        self.base_url = self.config['base_url']
        self.api_key = self.config['api_key']
        self.api_secret = self.config['api_secret']
        self.wallet_address = self.config['wallet_address']
        self.network = self.config['network']
    
    def _generate_signature(self, query_string):
        """توليد التوقيع للطلب"""
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _get_headers(self):
        """إعداد headers للطلبات"""
        return {
            'X-MBX-APIKEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    async def get_usdt_rate(self):
        """الحصول على سعر USDT مقابل الليرة السورية"""
        try:
            # يمكن استخدام API خارجي للحصول على السعر
            response = requests.get(
                'https://api.exchangerate-api.com/v4/latest/USD',
                timeout=10
            )
            data = response.json()
            # تحويل تقريبي - يجب استخدام API حقيقي
            syp_rate = data['rates'].get('SYP', 2500)
            return syp_rate
        except:
            return 2500  # سعر افتراضي
    
    async def process_deposit(self, user_id, amount_syp, wallet_address):
        """معالجة طلب الإيداع بـ USDT"""
        try:
            # تحويل المبلغ إلى USDT
            usdt_rate = await self.get_usdt_rate()
            usdt_amount = amount_syp / usdt_rate
            
            # في التطبيق الحقيقي، يجب التحقق من المعاملة على البلوك تشين
            # هذا مثال مبسط
            
            # محاكاة التحقق من المعاملة
            transaction_verified = await self._verify_usdt_transaction(
                wallet_address, usdt_amount
            )
            
            if transaction_verified:
                return {
                    'success': True,
                    'transaction_id': f"USDT_{int(time.time())}",
                    'status': 'completed',
                    'message': 'تم تأكيد الإيداع بنجاح',
                    'usdt_amount': usdt_amount,
                    'syp_amount': amount_syp
                }
            else:
                return {
                    'success': False,
                    'message': 'لم يتم العثور على المعاملة أو المبلغ غير صحيح'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في معالجة USDT: {str(e)}'
            }
    
    async def process_withdrawal(self, user_id, amount_syp, wallet_address):
        """معالجة طلب السحب بـ USDT"""
        try:
            # تحويل المبلغ إلى USDT
            usdt_rate = await self.get_usdt_rate()
            usdt_amount = amount_syp / usdt_rate
            
            # في التطبيق الحقيقي، يجب إرسال USDT إلى المحفظة
            # هذا مثال مبسط
            
            transaction_sent = await self._send_usdt_transaction(
                wallet_address, usdt_amount
            )
            
            if transaction_sent:
                return {
                    'success': True,
                    'transaction_id': f"USDT_OUT_{int(time.time())}",
                    'status': 'completed',
                    'message': 'تم إرسال USDT بنجاح',
                    'usdt_amount': usdt_amount,
                    'syp_amount': amount_syp
                }
            else:
                return {
                    'success': False,
                    'message': 'فشل في إرسال USDT'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في معالجة USDT: {str(e)}'
            }
    
    async def _verify_usdt_transaction(self, from_address, amount):
        """التحقق من معاملة USDT (مثال مبسط)"""
        # في التطبيق الحقيقي، يجب استخدام API البلوك تشين
        # مثل Tron API أو BSC API للتحقق من المعاملات
        return True  # محاكاة
    
    async def _send_usdt_transaction(self, to_address, amount):
        """إرسال معاملة USDT (مثال مبسط)"""
        # في التطبيق الحقيقي، يجب استخدام محفظة حقيقية
        # وإرسال المعاملة إلى البلوك تشين
        return True  # محاكاة
```

## 🔧 دمج APIs في البوت

### تحديث PaymentHandler
```python
# في ملف payment_handler.py
from syriatel_api import SyriatelCashAPI
from bank_api import BankAPI
from usdt_api import USDTAPI

class PaymentHandler:
    def __init__(self):
        self.syriatel_api = SyriatelCashAPI()
        self.bank_api = BankAPI()
        self.usdt_api = USDTAPI()
    
    async def process_automatic_deposit(self, user_id, amount, method, details):
        """معالجة الإيداع التلقائي"""
        if method == 'syriatel_cash':
            return await self.syriatel_api.process_deposit(
                user_id, amount, details['phone_number']
            )
        elif method == 'bank':
            return await self.bank_api.process_deposit(
                user_id, amount, details
            )
        elif method == 'usdt':
            return await self.usdt_api.process_deposit(
                user_id, amount, details['wallet_address']
            )
        else:
            return {
                'success': False,
                'message': 'طريقة دفع غير مدعومة'
            }
    
    async def process_automatic_withdrawal(self, user_id, amount, method, details):
        """معالجة السحب التلقائي"""
        if method == 'syriatel_cash':
            return await self.syriatel_api.process_withdrawal(
                user_id, amount, details['phone_number']
            )
        elif method == 'bank':
            return await self.bank_api.process_withdrawal(
                user_id, amount, details
            )
        elif method == 'usdt':
            return await self.usdt_api.process_withdrawal(
                user_id, amount, details['wallet_address']
            )
        else:
            return {
                'success': False,
                'message': 'طريقة سحب غير مدعومة'
            }
```

## 🔒 أمان APIs

### التشفير والتوقيع
```python
import hmac
import hashlib
import base64
from cryptography.fernet import Fernet

class APISecurityManager:
    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.cipher = Fernet(base64.urlsafe_b64encode(secret_key[:32].encode()))
    
    def encrypt_sensitive_data(self, data):
        """تشفير البيانات الحساسة"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data):
        """فك تشفير البيانات الحساسة"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def generate_api_signature(self, data, secret):
        """توليد توقيع API"""
        message = '&'.join([f"{k}={v}" for k, v in sorted(data.items())])
        return hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def verify_webhook_signature(self, payload, signature, secret):
        """التحقق من توقيع webhook"""
        expected_signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected_signature)
```

## 📊 مراقبة APIs

### تسجيل العمليات
```python
import logging
from datetime import datetime

class APILogger:
    def __init__(self):
        self.logger = logging.getLogger('api_logger')
        handler = logging.FileHandler('logs/api_transactions.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_api_request(self, api_name, method, user_id, amount, status):
        """تسجيل طلب API"""
        self.logger.info(
            f"API: {api_name} | Method: {method} | User: {user_id} | "
            f"Amount: {amount} | Status: {status}"
        )
    
    def log_api_error(self, api_name, error_message, user_id=None):
        """تسجيل خطأ API"""
        self.logger.error(
            f"API Error: {api_name} | User: {user_id} | Error: {error_message}"
        )
```

## 🧪 اختبار APIs

### اختبارات الوحدة
```python
import unittest
from unittest.mock import patch, Mock
from syriatel_api import SyriatelCashAPI

class TestSyriatelCashAPI(unittest.TestCase):
    def setUp(self):
        self.api = SyriatelCashAPI()
    
    @patch('requests.post')
    def test_successful_deposit(self, mock_post):
        # محاكاة استجابة ناجحة
        mock_response = Mock()
        mock_response.json.return_value = {
            'success': True,
            'transaction_id': 'TXN123',
            'status': 'completed',
            'message': 'تمت العملية بنجاح'
        }
        mock_post.return_value = mock_response
        
        # اختبار الإيداع
        result = await self.api.process_deposit(123456, 100.0, '+963912345678')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['transaction_id'], 'TXN123')
    
    @patch('requests.post')
    def test_failed_deposit(self, mock_post):
        # محاكاة استجابة فاشلة
        mock_response = Mock()
        mock_response.json.return_value = {
            'success': False,
            'message': 'رصيد غير كافي'
        }
        mock_post.return_value = mock_response
        
        # اختبار الإيداع الفاشل
        result = await self.api.process_deposit(123456, 100.0, '+963912345678')
        
        self.assertFalse(result['success'])
        self.assertIn('رصيد غير كافي', result['message'])
```

## 📝 ملاحظات مهمة

1. **الأمان**: تأكد من تشفير جميع البيانات الحساسة
2. **المعالجة**: استخدم try-catch لمعالجة الأخطاء
3. **التسجيل**: سجل جميع العمليات للمراجعة
4. **الاختبار**: اختبر جميع APIs قبل النشر
5. **المراقبة**: راقب أداء APIs باستمرار

---

**هذا الدليل يوفر إطار عمل شامل لدمج APIs مع البوت** 🔌

