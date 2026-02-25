import os
import requests
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from werkzeug.middleware.proxy_fix import ProxyFix

TRANSLATIONS = {
    'en': {
        'dir': 'ltr',
        'lang_code': 'en',
        'welcome': 'Welcome',
        'login': 'Log In',
        'logout': 'Log Out',
        'signup': 'Sign Up',
        'signup_title': 'Create Account',
        'login_title': 'Welcome back',
        'start_journey': 'Start your journey to German fluency today.',
        'first_name': 'First Name',
        'first_name_placeholder': 'Hans',
        'last_name': 'Last Name',
        'last_name_placeholder': 'Müller',
        'email': 'Email',
        'password': 'Password',
        'confirm_password': 'Confirm Password',
        'email_placeholder': 'name@example.com',
        'password_placeholder': 'Create a strong password',
        'repeat_password_placeholder': 'Repeat your password',
        'enter_password_placeholder': 'Enter your password',
        'current_german_level': 'Current Level',
        'select_cefr_level': 'Select your CEFR level',
        'target_language': 'Language to Learn',
        'learn_english': 'English',
        'learn_german': 'German',
        'select_target_language': 'Select the language you want to learn',
        'native_language': 'Native Language',
        'select_native_language': 'Select your native language',
        'correction_instructions': 'Grammar corrections will be provided in your native language.',
        'vocab_translation': 'Vocabulary translations will be shown in your native language.',
        'dashboard': 'Dashboard',
        'chat': 'Chat',
        'practice': 'Practice',
        'vocabulary': 'Vocabulary',
        'profile': 'Profile',
        'settings': 'Settings',
        'account': 'Account',
        'save_changes': 'Save Changes',
        'cancel': 'Cancel',
        'learning_preferences': 'Learning Preferences',
        'target_cefr_level': 'Target CEFR Level',
        'profile_information': 'Profile Information',
        'update_photo': 'Update your photo and personal details.',
        'change_photo': 'Change photo',
        'remove': 'Remove',
        'supported_formats': 'Supported formats: JPG, PNG. Max size: 5MB.',
        'email_address': 'Email address',
        'my_vocabulary': 'My Vocabulary',
        'vocabulary_subtitle': "Words you've improved during your writing practice sessions.",
        'search_words': 'Search words...',
        'vocabulary_empty': 'Your vocabulary list is empty',
        'vocabulary_empty_desc': 'Words that you\'ve made mistakes with will appear here automatically after your writing practice sessions.',
        'start_practicing': 'Start Practicing',
        'detailed_analysis': 'Detailed Analysis',
        'overview': 'Overview',
        'grammar': 'Grammar',
        'vocabulary_level': 'Vocabulary',
        'summary': 'Summary',
        'write_something': 'Write something to get analysis!',
        'check_grammar': 'Check Grammar',
        'checking': 'Checking...',
        'ready': 'Ready',
        'words': 'words',
        'ai_chat': 'AI Chat',
        'type_message_de': 'Type your message in German...',
        'type_message_en': 'Type your message in English...',
        'send': 'Send',
        'speaking_practice': 'Speaking Practice',
        'call_hans': 'Call Hans',
        'end_call': 'End Call',
        'beginner': 'Beginner',
        'elementary': 'Elementary',
        'intermediate': 'Intermediate',
        'upper_intermediate': 'Upper Int.',
        'advanced': 'Advanced',
        'mastery': 'Mastery',
        'level': 'Level',
        'enter_details': 'Enter your details to access your lessons.',
        'forgot_password': 'Forgot password?',
        'signin': 'Sign In',
        'fluency_away': 'Fluency is just a conversation away.',
        'ai_learning': 'AI-Assisted Learning',
        'next_gen': 'Experience the next generation of language learning. Our AI adapts to your CEFR level in real-time, correcting your pronunciation and grammar instantly.',
        'structured_path': 'Structured Path',
        'a1_to_c2': 'From A1 beginner to C2 mastery',
        'voice_analysis': 'Voice Analysis',
        'realtime_feedback': 'Real-time pronunciation feedback',
        'features': 'Features',
        'methodology': 'Methodology',
        'pricing': 'Pricing',
        'get_started': 'Get Started',
        'speak_lang_de': 'Speak German',
        'speak_lang_en': 'Speak English',
        'fluently_ai': 'Fluently with AI',
        'personalized': 'Personalized lessons based on CEFR standards (A1–C2). Learn smarter with an adaptive AI tutor that corrects your pronunciation and grammar in real-time.',
        'why_deutschai': 'Why DeutschAI?',
        'master_lang_de': 'Master German with Intelligent Tools',
        'master_lang_en': 'Master English with Intelligent Tools',
        'platform_adapts': 'Our platform adapts to your pace, ensuring you master every aspect of the language efficiently—from complex grammar to natural pronunciation.',
        'realtime_correction': 'Real-time Correction',
        'instant_feedback': 'Instant feedback on your writing, grammar mistakes, and style nuances as you type.',
        'ai_chat_partner': 'AI Chat Partner',
        'practice_247': 'Practice conversations 24/7 with a responsive AI that speaks naturally and adapts to your level.',
        'adaptive_drills': 'Adaptive Drills',
        'smart_exercises': 'Smart exercises that evolve based on your strengths and weaknesses to optimize memory retention.',
        'cefr_progress': 'CEFR Progress',
        'visualize': 'Visualize your detailed journey from A1 beginner to C2 fluency with analytics.',
        'path_fluency': 'Your Path to Fluency',
        'break_down_de': 'We break down the complexity of German grammar into manageable, logical steps aligned with the CEFR framework.',
        'break_down_en': 'We break down the complexity of English grammar into manageable, logical steps aligned with the CEFR framework.',
        'build_habit': 'Build a Daily Habit',
        'consistency': 'Consistency beats intensity. Committing to short, focused practice sessions every day is the most effective way to achieve fluency.',
        'personalized_plan': 'Personalized Plan',
        'daily_routine': 'Get a daily routine tailored to your goals, whether it\'s travel, business, or exam prep.',
        'active_practice': 'Active Practice',
        'engage': 'Engage in speaking, writing, and listening exercises that adapt to your performance.',
        'structured_learning': 'STRUCTURED LEARNING',
        'complete_journey': 'Your complete journey mapped out clearly.',
        'help_center': 'Help Center',
        'new_gpt4': 'New: GPT-4 Integration',
        'quick_practice': 'Quick Practice',
        'vocab_lab': 'Vocab Lab',
        'vocab_lab_desc': 'Review and master words you\'ve learned.',
        'chat_with_ahmad': 'Chat with Ahmad',
        'chat_desc_de': 'Practice ordering a coffee in Berlin.',
        'chat_desc_en': 'Practice ordering a coffee in London.',
        'grammar_drill': 'Grammar Drill',
        'grammar_drill_desc': 'Write a text and let AI check it.',
        'voice_call': 'Voice Call',
        'voice_call_desc': 'Speak directly with Ahmad by voice.',
        'recent_activity': 'Recent Activity',
        'view_all': 'View all',
        'choose_topic': 'Choose a Conversation Topic',
        'at_restaurant': 'At the Restaurant',
        'hotel_checkin': 'Hotel Check-in',
        'at_doctor': 'At the Doctor',
        'job_interview': 'Job Interview',
        'living_berlin': 'Living in Berlin',
        'living_london': 'Living in London',
        'start_chatting': 'Start Chatting',
        'writing_practice': 'Writing Practice',
        'goal': 'Goal: 5–15 min',
        'topic': 'Topic',
        'grammar_focus': 'Grammar Focus',
        'instructions_de': 'Write a text in German. DeutschAI will analyze your grammar, suggest improvements, and evaluate your vocabulary level.',
        'instructions_en': 'Write a text in English. DeutschAI will analyze your grammar, suggest improvements, and evaluate your vocabulary level.',
        'write_text_placeholder_de': 'Write your German text here...',
        'write_text_placeholder_en': 'Write your English text here...',
        'words': 'words',
        'ready': 'Ready',
        'my_vocabulary': 'My Vocabulary',
        'search_words': 'Search words...',
        'start_now': 'Start now →',
        'no_activity': 'No activity yet. Your journey starts today!',
        'ready_improve': 'Ready to improve? Let\'s keep going!',
        'current_level': 'Current Level',
        'learning_level_label': 'Level',
        'completed': 'Completed',
        'next_level': 'XP to next level',
        'beginner': 'Beginner',
        'advanced': 'Advanced',
        'start_conversation': 'Start a conversation with Ahmad',
        'practice_lang_de': 'Practice your German naturally. Ahmad is ready to chat about any topic.',
        'practice_lang_en': 'Practice your English naturally. Ahmad is ready to chat about any topic.',
        'say_hello': 'Say hello 👋',
        'great_choice': 'Great choice! Let\'s talk about',
        'ahmad_preparing': 'Ahmad is preparing...',
        'ahmad_thinking': 'Ahmad is thinking...',
        'ahmad_speaking': 'Ahmad is speaking...',
        'ahmad_listening': 'Just speak — Ahmad is always listening',
        'ahmad_greeting_de': 'Hallo! Ich bin Ahmad, dein KI-Deutschlehrer. Sprich einfach mit mir — ich höre immer zu!',
        'ahmad_greeting_en': 'Hello! I am Ahmad, your AI language tutor. Just speak to me — I am always listening!',
        'ahmad_tech': 'Ahmad – DeutschAI',
    },
    'ar': {
        'dir': 'rtl',
        'lang_code': 'ar',
        'welcome': 'مرحباً',
        'login': 'تسجيل الدخول',
        'logout': 'تسجيل الخروج',
        'signup': 'إنشاء حساب',
        'signup_title': 'إنشاء حساب',
        'login_title': 'مرحباً بعودتك',
        'start_journey': 'ابدأ رحلتك لإتقان اللغة الألمانية اليوم.',
        'first_name': 'الاسم الأول',
        'first_name_placeholder': 'أحمد',
        'last_name': 'اسم العائلة',
        'last_name_placeholder': 'كريطة',
        'email': 'البريد الإلكتروني',
        'password': 'كلمة المرور',
        'confirm_password': 'تأكيد كلمة المرور',
        'email_placeholder': 'name@example.com',
        'password_placeholder': 'أنشئ كلمة مرور قوية',
        'repeat_password_placeholder': 'كرر كلمة المرور',
        'enter_password_placeholder': 'أدخل كلمة المرور',
        'current_german_level': 'المستوى الحالي',
        'select_cefr_level': 'اختر مستوى CECRL',
        'target_language': 'اللغة المراد تعلمها',
        'learn_english': 'الإنجليزية',
        'learn_german': 'الألمانية',
        'select_target_language': 'اختر اللغة التي تريد تعلمها',
        'native_language': 'اللغة الأم',
        'select_native_language': 'اختر لغتك الأم',
        'correction_instructions': 'سيتم تقديم تصحيحات القواعد بلغتك الأم.',
        'vocab_translation': 'سيتم عرض ترجمة المفردات بلغتك الأم.',
        'dashboard': 'لوحة التحكم',
        'chat': 'الدردشة',
        'practice': 'التدريب',
        'vocabulary': 'المفردات',
        'profile': 'الملف الشخصي',
        'settings': 'الإعدادات',
        'account': 'الحساب',
        'save_changes': 'حفظ التغييرات',
        'cancel': 'إلغاء',
        'learning_preferences': 'تفضيلات التعلم',
        'target_cefr_level': 'مستوى CECRL المستهدف',
        'profile_information': 'معلومات الملف الشخصي',
        'update_photo': 'قم بتحديث صورتك الشخصية والتفاصيل.',
        'change_photo': 'تغيير الصورة',
        'remove': 'إزالة',
        'supported_formats': 'الصيغ المدعومة: JPG، PNG. الحد الأقصى: 5 ميجابايت.',
        'email_address': 'البريد الإلكتروني',
        'my_vocabulary': 'مفرداتي',
        'vocabulary_subtitle': 'الكلمات التي تحسنت فيها خلال جلسات التدريب على الكتابة.',
        'search_words': 'البحث عن كلمات...',
        'vocabulary_empty': 'قائمة مفرداتك فارغة',
        'vocabulary_empty_desc': 'الكلمات التي ارتكبت فيها أخطاء ستظهر هنا تلقائياً بعد جلسات التدريب على الكتابة.',
        'start_practicing': 'ابدأ التدريب',
        'detailed_analysis': 'التحليل التفصيلي',
        'overview': 'نظرة عامة',
        'grammar': 'القواعد',
        'vocabulary_level': 'المفردات',
        'summary': 'ملخص',
        'write_something': 'اكتب شيئاً للحصول على التحليل!',
        'check_grammar': 'فحص القواعد',
        'checking': 'جاري الفحص...',
        'ready': 'جاهز',
        'words': 'كلمات',
        'ai_chat': 'الدردشة الذكية',
        'type_message_de': 'اكتب رسالتك بالألمانية...',
        'type_message_en': 'اكتب رسالتك بالإنجليزية...',
        'send': 'إرسال',
        'speaking_practice': 'تدريب النطق',
        'call_hans': 'الاتصال بهانس',
        'end_call': 'إنهاء الاتصال',
        'beginner': 'مبتدئ',
        'elementary': 'ابتدائي',
        'intermediate': 'متوسط',
        'upper_intermediate': 'متوسط أعلى',
        'advanced': 'متقدم',
        'mastery': 'إتقان',
        'level': 'مستوى',
        'enter_details': 'أدخل بياناتك للوصول إلى دروسك.',
        'forgot_password': 'نسيت كلمة المرور؟',
        'signin': 'تسجيل الدخول',
        'fluency_away': 'الإتقان مجرد محادثة بعيدة.',
        'ai_learning': 'تعلم بمساعدة الذكاء الاصطناعي',
        'next_gen': 'استمتع بجيل جديد من تعلم اللغات. يتكيف الذكاء الاصطناعي مع مستوى CECRL الخاص بك في الوقت الفعلي، ويصحح نطقك وقواعدك على الفور.',
        'structured_path': 'مسار منظم',
        'a1_to_c2': 'من المبتدئ A1 إلى الإتقان C2',
        'voice_analysis': 'تحليل النطق',
        'realtime_feedback': 'تعليقات فورية على النطق',
        'features': 'المميزات',
        'methodology': 'المنهجية',
        'pricing': 'الأسعار',
        'get_started': 'ابدأ الآن',
        'speak_lang_de': 'تحدث الألمانية',
        'speak_lang_en': 'تحدث الإنجليزية',
        'fluently_ai': 'بإتقان مع الذكاء الاصطناعي',
        'personalized': 'دروس مخصصة基于CEFR标准（A1-C2）。通过自 adaptiveAI导师学习更聪明，实时纠正您的发音和语法。',
        'why_deutschai': 'لماذا دوتش آي؟',
        'master_lang_de': 'أتقن الألمانية بأدوات ذكية',
        'master_lang_en': 'أتقن الإنجليزية بأدوات ذكية',
        'platform_adapts': 'تتكيف منصتنا مع وتيرتك، مما يضمن إتقان كل جانب من جوانب اللغة بكفاءة—من القواعد المعقدة إلى النطق الطبيعي.',
        'realtime_correction': 'تصحيح فوري',
        'instant_feedback': 'تعليقات فورية على كتابتك وأخطاء القواعد والتفاصيل النحوية أثناء الكتابة.',
        'ai_chat_partner': 'شريك الدردشة بالذكاء الاصطناعي',
        'practice_247': 'تدرب على المحادثات على مدار الساعة مع ذكاء اصطناعي يستجيب ويتحدث بشكل طبيعي ويتكيف مع مستواك.',
        'adaptive_drills': 'تمارين تكيفية',
        'smart_exercises': 'تمارين ذكية تتطور بناءً على نقاط قوتك وضعفك لتحسين الاحتفاظ بالذاكرة.',
        'cefr_progress': 'تقدم CECFR',
        'visualize': 'تصور رحلتك التفصيلية من المبتدئ A1 إلى الإتقان C2.',
        'path_fluency': 'مسارك للإتقان',
        'break_down_de': 'نقسم تعقيدات القواعد الألمانية إلى خطوات منطقية وقابلة للإدارة مصممة وفقاً للإطار الأوروبي المرجعي اللغوي.',
        'break_down_en': 'نقسم تعقيدات القواعد الإنجليزية إلى خطوات منطقية وقابلة للإدارة مصممة وفقاً للإطار الأوروبي المرجعي اللغوي.',
        'build_habit': 'بناء عادة يومية',
        'consistency': 'الاتساق يتفوق على الشدة. الالتزام بجلسات تدريب قصيرة ومركزة كل يوم هو الطريقة الأكثر فعالية لتحقيق الإتقان.',
        'personalized_plan': 'خطة مخصصة',
        'daily_routine': 'احصل على روتين يومي مصمم لأهدافك، سواء كان للسفر أو العمل أو التحضير للامتحانات.',
        'active_practice': 'تدريب نشط',
        'engage': 'شارك في تمارين التحدث والكتابة والاستماع التي تتكيف مع أدائك.',
        'structured_learning': 'تعلم منظم',
        'complete_journey': 'رحلتك الكاملة مصورة بوضوح.',
        'help_center': 'مركز المساعدة',
        'new_gpt4': 'جديد: تكامل GPT-4',
        'quick_practice': 'تدريب سريع',
        'vocab_lab': 'مختبر المفردات',
        'vocab_lab_desc': 'راجع وأتقن الكلمات التي تعلمتها.',
        'chat_with_ahmad': 'دردشة مع أحمد',
        'chat_desc_de': 'تدرب على طلب قهوة في برلين.',
        'chat_desc_en': 'تدرب على طلب قهوة في لندن.',
        'grammar_drill': 'تمارين القواعد',
        'grammar_drill_desc': 'اكتب نصاً ودع الذكاء الاصطناعي يفحصه.',
        'voice_call': 'مكالمة صوتية',
        'voice_call_desc': 'تحدث مباشرة مع أحمد بالصوت.',
        'recent_activity': 'النشاط الأخير',
        'view_all': 'عرض الكل',
        'choose_topic': 'اختر موضوع المحادثة',
        'at_restaurant': 'في المطعم',
        'hotel_checkin': 'تسجيل الدخول للفندق',
        'at_doctor': 'عند الطبيب',
        'job_interview': 'مقابلة عمل',
        'living_berlin': 'العيش في برلين',
        'living_london': 'العيش في لندن',
        'start_chatting': 'ابدأ الدردشة',
        'writing_practice': 'تدريب الكتابة',
        'goal': 'الهدف: 5-15 دقيقة',
        'topic': 'الموضوع',
        'grammar_focus': 'تركيز القواعد',
        'instructions_de': 'اكتب نصاً بالألمانية. سيقوم DeutschAI بتحليل القواعد واقتراح التحسينات وتقييم مستوى مفرداتك.',
        'instructions_en': 'اكتب نصاً بالإنجليزية. سيقوم DeutschAI بتحليل القواعد واقتراح التحسينات وتقييم مستوى مفرداتك.',
        'write_text_placeholder_de': 'اكتب نصك الألماني هنا...',
        'write_text_placeholder_en': 'اكتب نصك الإنجليزي هنا...',
        'words': 'كلمات',
        'ready': 'جاهز',
        'my_vocabulary': 'مفرداتي',
        'search_words': 'البحث عن كلمات...',
        'start_now': 'ابدأ الآن ←',
        'no_activity': 'لا يوجد نشاط بعد. رحلتك تبدأ اليوم!',
        'ready_improve': 'مستعد للتحسين؟ هيا نستمر!',
        'current_level': 'المستوى الحالي',
        'learning_level_label': 'مستوى',
        'completed': 'مكتمل',
        'next_level': 'XP للمستوى التالي',
        'beginner': 'مبتدئ',
        'advanced': 'متقدم',
        'start_conversation': 'ابدأ محادثة مع أحمد',
        'practice_lang_de': 'تدرب على الألمانية بشكل طبيعي. أحمد مستعد للدردشة حول أي موضوع.',
        'practice_lang_en': 'تدرب على الإنجليزية بشكل طبيعي. أحمد مستعد للدردشة حول أي موضوع.',
        'say_hello': 'قل مرحباً 👋',
        'great_choice': 'اختيار رائع! دعنا نتحدث عن',
        'ahmad_preparing': 'أحمد يستعد...',
        'ahmad_thinking': 'أحمد يفكر...',
        'ahmad_speaking': 'أحمد يتحدث...',
        'ahmad_listening': 'تحدث فقط — أحمد دائماً يستمع',
        'ahmad_greeting_de': 'Hallo! Ich bin Ahmad, dein KI-Deutschlehrer. Sprich einfach mit mir — ich هو دائماً يستمع!',
        'ahmad_greeting_en': 'Hello! I am Ahmad, your AI language tutor. Just speak to me — I am always listening!',
        'ahmad_tech': 'أحمد - DeutschAI',
    }
}

def get_translations(lang):
    return TRANSLATIONS.get(lang, TRANSLATIONS['en'])

def get_lang_dir(lang):
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get('dir', 'ltr')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'deutschai-secret-key-x7k2p9m4q1r8v5w3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///deutschai.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Trust proxy headers for HTTPS detection
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Session configuration - production uses HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['REMEMBER_COOKIE_SAMESITE'] = 'None'
app.config['REMEMBER_COOKIE_SECURE'] = True

app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    target_language = db.Column(db.String(10), nullable=False, default='de')
    german_level = db.Column(db.String(20), nullable=False)
    native_language = db.Column(db.String(10), nullable=False, default='en')
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    progress = db.Column(db.Integer, default=0)
    xp = db.Column(db.Integer, default=0)
    vocabularies = db.relationship('Vocabulary', backref='owner', lazy=True)
    activities = db.relationship('Activity', backref='owner', lazy=True)

class Vocabulary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    word = db.Column(db.String(100), nullable=False)
    correction = db.Column(db.String(100), nullable=False)
    explanation = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False) # 'chat', 'practice', 'vocab'
    description = db.Column(db.String(200), nullable=False)
    points = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

def log_activity(user, type, description, points):
    activity = Activity(user_id=user.id, type=type, description=description, points=points)
    user.xp += points
    # Simple logic: 1000 XP per level, progress is % of current 1000
    user.progress = (user.xp % 1000) // 10
    if user.progress > 100: user.progress = 100
    db.session.add(activity)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error logging activity: {e}")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def handle_options():
    """Handle OPTIONS requests for CORS preflight"""
    if request.method == 'OPTIONS':
        response = app.make_response('')
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

@app.after_request
def after_request(response):
    """Add CORS headers to all responses"""
    origin = request.headers.get('Origin')
    if origin:
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.context_processor
def inject_user():
    lang = current_user.native_language if current_user.is_authenticated else 'en'
    return dict(user=current_user, translations=get_translations(lang), native_lang=lang, lang_dir=get_lang_dir(lang))

@app.route('/')
def index():
    lang = request.args.get('lang', 'en')
    if lang not in ['en', 'ar']:
        lang = 'en'
    return render_template('index.html', translations=get_translations(lang), native_lang=lang, lang_dir=get_lang_dir(lang))

@app.route('/debug/session')
def debug_session():
    """Debug endpoint to check session status"""
    from flask import session
    return jsonify({
        'authenticated': current_user.is_authenticated,
        'user_id': current_user.id if current_user.is_authenticated else None,
        'session_permanent': session.permanent if hasattr(session, 'permanent') else None,
        'config': {
            'SESSION_COOKIE_SECURE': app.config.get('SESSION_COOKIE_SECURE'),
            'SESSION_COOKIE_SAMESITE': app.config.get('SESSION_COOKIE_SAMESITE'),
            'SESSION_COOKIE_HTTPONLY': app.config.get('SESSION_COOKIE_HTTPONLY'),
        }
    })

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    lang = request.args.get('lang', 'en')
    if lang not in ['en', 'ar']:
        lang = 'en'
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        target_language = request.form.get('target_language', 'de')
        german_level = request.form.get('german_level')
        native_language = request.form.get('native_language', 'en')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('signup'))

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Email already registered!', 'danger')
            return redirect(url_for('signup'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(first_name=first_name, last_name=last_name, target_language=target_language, german_level=german_level, native_language=native_language, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', translations=get_translations(lang), native_lang=lang, lang_dir=get_lang_dir(lang))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    lang = request.args.get('lang', 'en')
    if lang not in ['en', 'ar']:
        lang = 'en'
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=True)
            # Make session permanent so it persists longer
            from flask import session
            session.permanent = True
            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', translations=get_translations(lang), native_lang=lang, lang_dir=get_lang_dir(lang))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    activities = Activity.query.filter_by(user_id=current_user.id).order_by(Activity.timestamp.desc()).limit(5).all()
    return render_template('dashboard.html', activities=activities)

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')

@app.route('/chat/api', methods=['POST', 'OPTIONS'])
def chat_api():
    if request.method == 'OPTIONS':
        response = make_response('', 200)
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    # Debug: Print session info to console
    print(f"\n=== /chat/api called ===")
    print(f"Cookies: {list(request.cookies.keys())}")
    print(f"Session cookie: {request.cookies.get('session', 'NOT SET')[:50] if request.cookies.get('session') else 'NOT SET'}")
    print(f"User authenticated: {current_user.is_authenticated}")
    print(f"Request method: {request.method}")
    print(f"Is secure: {request.is_secure}")
    print(f"========================\n")
    
    # Debug: Check session
    if not current_user.is_authenticated:
        print("DEBUG: User not authenticated, returning 401")
        return jsonify({
            "error": "Unauthorized",
            "debug": {
                "cookies": list(request.cookies.keys()),
                "session_cookie": request.cookies.get('session', 'NOT SET'),
                "user_agent": request.headers.get('User-Agent', 'Unknown')[:50]
            }
        }), 401
    
    print("DEBUG: User IS authenticated, continuing...")
    
    try:
        data = request.json
        user_message = data.get('message')
        
        if not user_message:
            print("DEBUG: No message provided")
            return jsonify({"error": "No message provided"}), 400

        print(f"DEBUG: Calling AI with message: {user_message[:50]}...")
        
        api_key = "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"
        
        target_lang = current_user.target_language
        target_lang_name = "German" if target_lang == "de" else "English"
        
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://deutchai.tayba.blog",
                "X-Title": "DeutschAI",
            },
            data=json.dumps({
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": f"You are Ahmad, a helpful {target_lang_name} language tutor. The user's {target_lang_name} level is {current_user.german_level}. Please speak primarily in {target_lang_name} and encourage the user. Keep your responses concise and engaging."
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            })
        )
        
        if response.status_code == 200:
            log_activity(current_user, 'chat', f'Konversation mit Ahmad geführt ({target_lang_name})', 10)
            return jsonify(response.json())
        else:
            return jsonify({"error": "Failed to get response from AI"}), response.status_code
    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/practice')
@login_required
def practice():
    return render_template('practice.html')

@app.route('/practice/api', methods=['POST', 'OPTIONS'])
def practice_api():
    if request.method == 'OPTIONS':
        return '', 200
    
    # Debug: Check session
    if not current_user.is_authenticated:
        return jsonify({
            "error": "Unauthorized",
            "debug": {
                "cookies": list(request.cookies.keys()),
                "session_cookie": request.cookies.get('session', 'NOT SET'),
                "user_agent": request.headers.get('User-Agent', 'Unknown')[:50]
            }
        }), 401
    
    data = request.json
    user_text = data.get('text')
    
    if not user_text:
        return jsonify({"error": "No text provided"}), 400

    api_key = "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"
    
    target_lang = current_user.target_language
    target_lang_name = "German" if target_lang == "de" else "English"
    native_lang = current_user.native_language
    lang_instruction = "in English" if native_lang == "en" else "in Arabic"
    
    system_prompt = f"""
    You are an expert {target_lang_name} grammar checker. The user's level is {current_user.german_level}.
    The user's native language is: {"English" if native_lang == "en" else "Arabic"}.
    
    Analyze the following {target_lang_name} text for:
    1. Grammar errors
    2. Spelling mistakes
    3. Suggested improvements for better fluency
    4. CEFR level of the vocabulary used
    5. An overall grammar score (0-100%)

    IMPORTANT: Your response MUST be in JSON format with the following structure. All text fields must be {lang_instruction}:
    {{
        "score": number,
        "vocab_level": "string (A1-C2)",
        "analysis_summary": "string {lang_instruction}",
        "corrections": [
            {{
                "original": "string",
                "correction": "string",
                "explanation": "string {lang_instruction}",
                "type": "grammar" | "spelling" | "style"
            }}
        ]
    }}
    """
    
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://deutchai.tayba.blog",
            "X-Title": "DeutschAI",
        },
        data=json.dumps({
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            "response_format": { "type": "json_object" }
        })
    )
    
    if response.status_code == 200:
        result_data = response.json()
        try:
            content = json.loads(result_data['choices'][0]['message']['content'])
            score = content.get('score', 0)
            log_activity(current_user, 'practice', f'Grammatik-Übung abgeschlossen ({score}%)', score // 5)
        except:
            pass
        return jsonify(result_data)
    else:
        return jsonify({"error": "Failed to get response from AI"}), response.status_code

@app.route('/call')
@login_required
def call():
    return render_template('call.html')

@app.route('/call/api', methods=['POST', 'OPTIONS'])
def call_api():
    if request.method == 'OPTIONS':
        return '', 200
    
    # Debug: Print session info to console
    print(f"\n=== /call/api called ===")
    print(f"Cookies: {list(request.cookies.keys())}")
    print(f"Session cookie: {request.cookies.get('session', 'NOT SET')[:50] if request.cookies.get('session') else 'NOT SET'}")
    print(f"User authenticated: {current_user.is_authenticated}")
    print(f"========================\n")
    
    # Debug: Check session
    if not current_user.is_authenticated:
        from flask import session
        return jsonify({
            "error": "Unauthorized",
            "debug": {
                "cookies": list(request.cookies.keys()),
                "session_cookie": request.cookies.get('session', 'NOT SET'),
                "session_data": dict(session),
                "user_agent": request.headers.get('User-Agent', 'Unknown')[:50]
            }
        }), 401
    
    data = request.json
    messages = data.get('messages', [])

    if not messages:
        return jsonify({"error": "No messages provided"}), 400

    api_key = "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"

    target_lang = current_user.target_language
    target_lang_name = "German" if target_lang == "de" else "English"

    system_message = {
        "role": "system",
        "content": f"You are Ahmad, a friendly and encouraging {target_lang_name} language teacher. The user's level is {current_user.german_level}. The user is practicing speaking {target_lang_name}. Always respond in {target_lang_name}, keep responses short and natural like a real conversation. If the message seems unclear or broken, try your best to understand the intent and respond helpfully. Gently correct any grammar mistakes."
    }

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "DeutschAI",
        },
        data=json.dumps({
            "model": "openai/gpt-3.5-turbo",
            "messages": [system_message] + messages
        })
    )

    if response.status_code == 200:
        target_lang_name = "German" if current_user.target_language == "de" else "English"
        log_activity(current_user, 'chat', f'Sprachanruf mit Ahmad geführt ({target_lang_name})', 15)
        return jsonify(response.json())
    else:
        return jsonify({"error": "AI response failed"}), response.status_code

@app.route('/setting', methods=['GET', 'POST'])
@login_required
def setting():
    if request.method == 'POST':
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        current_user.email = request.form.get('email')
        current_user.german_level = request.form.get('cefr_level')
        current_user.native_language = request.form.get('native_language', 'en')
        current_user.target_language = request.form.get('target_language', 'de')
        
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile.', 'danger')
        
        return redirect(url_for('setting'))
    return render_template('setting.html')

@app.route('/vocabulary')
@login_required
def vocabulary():
    return render_template('vocabulary.html')

@app.route('/vocabulary/api/add', methods=['POST', 'OPTIONS'])
@login_required
def add_vocabulary():
    data = request.json
    word = data.get('word')
    correction = data.get('correction')
    explanation = data.get('explanation')

    if not word or not correction:
        return jsonify({"error": "Missing word or correction"}), 400

    # Avoid duplicates for the same user
    existing = Vocabulary.query.filter_by(user_id=current_user.id, word=word, correction=correction).first()
    if existing:
        return jsonify({"message": "Word already in vocabulary"}), 200

    new_vocab = Vocabulary(
        user_id=current_user.id,
        word=word,
        correction=correction,
        explanation=explanation
    )
    db.session.add(new_vocab)
    log_activity(current_user, 'vocab', f'Neues Wort gelernt: {correction}', 5)
    db.session.commit()
    return jsonify({"message": "Vocabulary added successfully"}), 201

@app.route('/vocabulary/api/list', methods=['GET', 'OPTIONS'])
@login_required
def list_vocabulary():
    vocabs = Vocabulary.query.filter_by(user_id=current_user.id).order_by(Vocabulary.timestamp.desc()).all()
    return jsonify([{
        "id": v.id,
        "word": v.word,
        "correction": v.correction,
        "explanation": v.explanation,
        "timestamp": v.timestamp.isoformat()
    } for v in vocabs])

@app.route('/vocabulary/api/delete/<int:vocab_id>', methods=['DELETE', 'OPTIONS'])
@login_required
def delete_vocabulary(vocab_id):
    vocab = Vocabulary.query.filter_by(id=vocab_id, user_id=current_user.id).first()
    if not vocab:
        return jsonify({"error": "Vocabulary item not found"}), 404
    
    db.session.delete(vocab)
    db.session.commit()
    return jsonify({"message": "Vocabulary item deleted"}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
