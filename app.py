import os
import requests
import json
import traceback
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
CORS(app)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not found in environment variables!")
else:
    print(f"✅ API Key configured: {GEMINI_API_KEY[:15]}...")


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/analyze')
def analyze():
    return render_template('analyze.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/api/explain-code', methods=['POST'])
def explain_code():
    print("\n" + "="*50)
    print("🚀 EXPLAIN CODE REQUEST RECEIVED")
    print("="*50)
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        code = data.get('code', '').strip()
        language = data.get('language', 'python').strip()
        
        if not code:
            return jsonify({
                'success': False,
                'error': 'Please paste some code to analyze'
            }), 400
        
        if not GEMINI_API_KEY:
            return jsonify({
                'success': False,
                'error': 'API key not configured. Please check your .env file.'
            }), 500
        
        explanation = generate_explanation(code, language)
        
        return jsonify({
            'success': True,
            'explanation': explanation,
            'language': language
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500


def generate_explanation(code, language):
    prompt = f"""
You are an expert programming mentor. Explain the following {language} code in simple, 
easy-to-understand language for beginners. Structure your explanation in these sections:

1. **Overview**: What does this code do? (1-2 sentences)
2. **Key Components**: Explain the main parts (functions, classes, variables, etc.)
3. **Logic Flow**: How does the code execute step by step?
4. **Key Takeaways**: What are the most important things to learn from this code?

Code to explain:
{code}

Make it beginner-friendly and educational. Use simple terms and provide context.
"""
    
    try:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY
        }
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        print("🌐 Sending request to Gemini API...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            explanation_text = result['candidates'][0]['content']['parts'][0]['text']
            print("✅ API call successful!")
            return format_explanation(explanation_text)
            
        elif response.status_code == 429:
            print("❌ Quota exceeded (429)")
            return quota_exceeded_message(code, language)
            
        else:
            print(f"❌ API Error: {response.status_code}")
            return demo_explanation(code, language, f"API Error: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ API Timeout")
        return demo_explanation(code, language, "Request timeout")
    except Exception as e:
        print(f"❌ API call failed: {str(e)}")
        return demo_explanation(code, language, str(e))


def format_explanation(explanation_text):
    explanation_text = explanation_text.replace('**', '<strong>')
    explanation_text = explanation_text.replace('* ', '• ')
    explanation_text = explanation_text.replace('- ', '◦ ')
    explanation_text = explanation_text.replace('\n', '<br>')
    
    return f"""
    <div class="explanation-content">
        <div style="background: #d1fae5; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #10b981;">
            <p style="margin: 0;"><strong>✅ AI Generated Explanation</strong></p>
            <p style="margin: 5px 0 0 0; font-size: 0.8rem; color: #6b7280;">Powered by: Google Gemini AI</p>
        </div>
        {explanation_text}
    </div>
    """


def quota_exceeded_message(code, language):
    current_time = datetime.now()
    tomorrow = current_time + timedelta(days=1)
    reset_time = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    hours_left = int((reset_time - current_time).total_seconds() / 3600)
    
    return f"""
    <div class="explanation-content">
        <div style="background: #fef3c7; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #f59e0b;">
            <h3 style="color: #92400e; margin-top: 0;">
                <i class="fas fa-clock"></i> API Quota Exceeded
            </h3>
            <p style="color: #78350f;">
                You've reached the daily limit for the free Gemini API. 
                The quota resets in approximately <strong>{hours_left} hours</strong>.
            </p>
            <div style="background: #fffbeb; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <p style="margin: 0; color: #78350f;">
                    <strong>💡 Tips:</strong><br>
                    1. Wait {hours_left} hours for quota reset<br>
                    2. Create a new API key with a different Google account<br>
                    3. Enable billing for higher limits
                </p>
            </div>
            <p style="color: #78350f; margin-bottom: 0;">
                <strong>Your code has been analyzed in Demo Mode below:</strong>
            </p>
        </div>
        {demo_explanation(code, language, "Using Demo Mode (Quota exceeded)")}
    </div>
    """


def demo_explanation(code, language, error_msg=None):
    lines = code.strip().split('\n') if code else []
    line_count = len(lines)
    char_count = len(code) if code else 0
    
    has_function = any('def ' in line or 'function ' in line or 'void ' in line for line in lines)
    has_import = any('import ' in line or '#include' in line for line in lines)
    has_loop = any('for ' in line or 'while ' in line for line in lines)
    has_conditional = any('if ' in line or 'else ' in line or 'switch ' in line for line in lines)
    has_class = any('class ' in line for line in lines)
    
    code_preview = '\n'.join(lines[:8])
    if len(lines) > 8:
        code_preview += f"\n... and {len(lines) - 8} more lines"
    
    return f"""
    <div class="explanation-content">
        <div style="background: #fef3c7; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #f59e0b;">
            <p style="margin: 0;"><strong>ℹ️ Demo Mode</strong></p>
            <p style="margin: 5px 0 0 0; font-size: 0.9rem; color: #6b7280;">
                Code analysis and structure overview
            </p>
        </div>
        
        <h3>📝 Code Analysis</h3>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin: 15px 0;">
            <div style="background: #eef2ff; padding: 12px; border-radius: 8px; text-align: center;">
                <div style="font-size: 22px; font-weight: bold; color: #6366f1;">{line_count}</div>
                <div style="font-size: 0.8rem; color: #4b5563;">Lines</div>
            </div>
            <div style="background: #d1fae5; padding: 12px; border-radius: 8px; text-align: center;">
                <div style="font-size: 22px; font-weight: bold; color: #10b981;">{char_count}</div>
                <div style="font-size: 0.8rem; color: #4b5563;">Characters</div>
            </div>
            <div style="background: #fce4ec; padding: 12px; border-radius: 8px; text-align: center;">
                <div style="font-size: 22px; font-weight: bold; color: #ef4444;">{'✅' if has_function else '❌'}</div>
                <div style="font-size: 0.8rem; color: #4b5563;">Functions</div>
            </div>
            <div style="background: #ede9fe; padding: 12px; border-radius: 8px; text-align: center;">
                <div style="font-size: 22px; font-weight: bold; color: #8b5cf6;">{'✅' if has_class else '❌'}</div>
                <div style="font-size: 0.8rem; color: #4b5563;">Classes</div>
            </div>
        </div>
        
        <h3>🔍 Code Structure</h3>
        <ul>
            <li><strong>Language:</strong> {language}</li>
            <li><strong>Imports:</strong> {'✅ Found' if has_import else '❌ None'}</li>
            <li><strong>Loops:</strong> {'✅ Found' if has_loop else '❌ None'}</li>
            <li><strong>Conditionals:</strong> {'✅ Found' if has_conditional else '❌ None'}</li>
        </ul>
        
        <div style="background: #f1f5f9; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <h4 style="margin-top: 0; color: #0f172a;">📄 Code Preview</h4>
            <pre style="background: #0f172a; color: #e2e8f0; padding: 12px; border-radius: 6px; overflow-x: auto; font-size: 0.8rem; margin: 0; font-family: 'Courier New', monospace;">
{code_preview}
            </pre>
        </div>
        
        <div style="background: #eef2ff; padding: 15px; border-radius: 8px; margin-top: 15px; border-left: 4px solid #6366f1;">
            <h4 style="margin-top: 0; color: #4f46e5;">💡 Summary</h4>
            <p style="margin-bottom: 0;">
                This code contains <strong>{line_count} lines</strong> of {language} code 
                {'with ' if has_function else 'without '}functions, 
                {'including ' if has_import else 'no '}imports,
                {'and ' if has_loop else 'and no '}loops.
            </p>
        </div>
    </div>
    """


@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({
        'success': False,
        'error': 'Internal server error. Please try again later.'
    }), 500


if __name__ == '__main__':
    print("\n" + "="*50)
    print("AI Code Explainer - Flask Application")
    print("="*50)
    print(f"Access at: http://localhost:5000")
    print(f"Debug mode: {app.config['DEBUG']}")
    print(f"API Key: {'✅ Configured' if GEMINI_API_KEY else '❌ Not Configured'}")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)