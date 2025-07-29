#!/usr/bin/env python3
"""
ملف اختبار بوت التليجرام العربي
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch

# إضافة مسار المشروع
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestBotComponents(unittest.TestCase):
    """اختبارات مكونات البوت"""
    
    def test_config_import(self):
        """اختبار استيراد ملف الإعدادات"""
        try:
            from config import Config
            self.assertIsNotNone(Config)
            print("✅ تم استيراد ملف الإعدادات بنجاح")
        except ImportError as e:
            self.fail(f"❌ فشل استيراد ملف الإعدادات: {e}")
    
    def test_database_import(self):
        """اختبار استيراد قاعدة البيانات"""
        try:
            from database import DatabaseManager, User, Transaction
            self.assertIsNotNone(DatabaseManager)
            self.assertIsNotNone(User)
            self.assertIsNotNone(Transaction)
            print("✅ تم استيراد قاعدة البيانات بنجاح")
        except ImportError as e:
            self.fail(f"❌ فشل استيراد قاعدة البيانات: {e}")
    
    def test_keyboards_import(self):
        """اختبار استيراد لوحات المفاتيح"""
        try:
            from keyboards import Keyboards
            self.assertIsNotNone(Keyboards)
            print("✅ تم استيراد لوحات المفاتيح بنجاح")
        except ImportError as e:
            self.fail(f"❌ فشل استيراد لوحات المفاتيح: {e}")
    
    def test_handlers_import(self):
        """اختبار استيراد المعالجات"""
        try:
            from handlers import start_handler, main_menu_handler
            self.assertIsNotNone(start_handler)
            self.assertIsNotNone(main_menu_handler)
            print("✅ تم استيراد المعالجات بنجاح")
        except ImportError as e:
            self.fail(f"❌ فشل استيراد المعالجات: {e}")
    
    def test_payment_handler_import(self):
        """اختبار استيراد معالج المدفوعات"""
        try:
            from payment_handler import PaymentHandler
            self.assertIsNotNone(PaymentHandler)
            print("✅ تم استيراد معالج المدفوعات بنجاح")
        except ImportError as e:
            self.fail(f"❌ فشل استيراد معالج المدفوعات: {e}")
    
    def test_referral_handler_import(self):
        """اختبار استيراد معالج الإحالات"""
        try:
            from referral_handler import ReferralHandler
            self.assertIsNotNone(ReferralHandler)
            print("✅ تم استيراد معالج الإحالات بنجاح")
        except ImportError as e:
            self.fail(f"❌ فشل استيراد معالج الإحالات: {e}")
    
    def test_admin_handler_import(self):
        """اختبار استيراد معالج الإدمن"""
        try:
            from admin_handler import AdminHandler
            self.assertIsNotNone(AdminHandler)
            print("✅ تم استيراد معالج الإدمن بنجاح")
        except ImportError as e:
            self.fail(f"❌ فشل استيراد معالج الإدمن: {e}")
    
    def test_contact_handler_import(self):
        """اختبار استيراد معالج التواصل"""
        try:
            from contact_handler import ContactHandler
            self.assertIsNotNone(ContactHandler)
            print("✅ تم استيراد معالج التواصل بنجاح")
        except ImportError as e:
            self.fail(f"❌ فشل استيراد معالج التواصل: {e}")
    
    def test_utils_import(self):
        """اختبار استيراد الأدوات المساعدة"""
        try:
            from utils import format_currency, validate_amount
            self.assertIsNotNone(format_currency)
            self.assertIsNotNone(validate_amount)
            print("✅ تم استيراد الأدوات المساعدة بنجاح")
        except ImportError as e:
            self.fail(f"❌ فشل استيراد الأدوات المساعدة: {e}")

class TestUtilityFunctions(unittest.TestCase):
    """اختبارات الدوال المساعدة"""
    
    def test_format_currency(self):
        """اختبار تنسيق العملة"""
        from utils import format_currency
        
        self.assertEqual(format_currency(100), "100.00")
        self.assertEqual(format_currency(100.5), "100.50")
        self.assertEqual(format_currency(0), "0.00")
        print("✅ دالة تنسيق العملة تعمل بشكل صحيح")
    
    def test_validate_amount(self):
        """اختبار التحقق من صحة المبلغ"""
        from utils import validate_amount
        
        self.assertTrue(validate_amount("100"))
        self.assertTrue(validate_amount("100.50"))
        self.assertFalse(validate_amount("abc"))
        self.assertFalse(validate_amount("-100"))
        print("✅ دالة التحقق من المبلغ تعمل بشكل صحيح")

def run_tests():
    """تشغيل جميع الاختبارات"""
    print("🧪 بدء اختبارات بوت التليجرام العربي...\n")
    
    # تشغيل الاختبارات
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # إضافة اختبارات المكونات
    suite.addTests(loader.loadTestsFromTestCase(TestBotComponents))
    suite.addTests(loader.loadTestsFromTestCase(TestUtilityFunctions))
    
    # تشغيل الاختبارات
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # النتائج
    print(f"\n📊 نتائج الاختبارات:")
    print(f"✅ نجح: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ فشل: {len(result.failures)}")
    print(f"⚠️ أخطاء: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ الاختبارات الفاشلة:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n⚠️ أخطاء الاختبارات:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

