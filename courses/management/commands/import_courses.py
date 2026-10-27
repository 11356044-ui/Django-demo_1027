from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from courses.models import Course


class Command(BaseCommand):
    help = '匯入常用課程（國文、英文、數學、程式設計、網頁設計等）'

    def handle(self, *args, **options):
        # 取得或建立預設教師
        teacher, created = User.objects.get_or_create(
            username='teacher_default',
            defaults={'email': 'teacher@ntub.edu.tw', 'is_staff': False}
        )
        if created:
            teacher.set_password('teacher123')
            teacher.save()
            self.stdout.write(self.style.SUCCESS('已建立預設教師帳號: teacher_default / teacher123'))
        
        courses_data = [
            {
                'course_code': 'CH001',
                'name': '國文（一）',
                'credits': 2,
                'course_type': 'required',
                'grade': 1,
                'description': '培養學生閱讀、寫作與思辨能力，增進國文基本素養。',
                'objectives': '1. 熟悉應用文體\n2. 提升閱讀理解能力\n3. 強化寫作表達能力',
                'syllabus': '第一週：緒論\n第二週：記敘文寫作\n第三週：說明文寫作\n第四週：議論文寫作\n...'
            },
            {
                'course_code': 'EN001',
                'name': '英文（一）',
                'credits': 2,
                'course_type': 'required',
                'grade': 1,
                'description': '強化大一新生英文聽說讀寫能力，奠定日後專業英文基礎。',
                'objectives': '1. 提升基本會話能力\n2. 增強閱讀理解\n3. 建立單字與文法概念',
                'syllabus': 'Unit 1: Introduction\nUnit 2: Daily Life\nUnit 3: Family and Friends\n...'
            },
            {
                'course_code': 'MATH001',
                'name': '微積分（一）',
                'credits': 3,
                'course_type': 'required',
                'grade': 1,
                'description': '介紹微積分基本概念，為日後商管及資訊相關課程打基礎。',
                'objectives': '1. 理解極限與連續\n2. 掌握微分法則\n3. 應用微分於實際問題',
                'syllabus': '第一章：函數與極限\n第二章：導數與微分\n第三章：微分應用\n...'
            },
            {
                'course_code': 'CS101',
                'name': '程式設計',
                'credits': 3,
                'course_type': 'required',
                'grade': 1,
                'description': '學習程式設計基本概念與邏輯思考，使用 Python 語言入門。',
                'objectives': '1. 認識程式語言與演算法思維\n2. 學習基本程式結構\n3. 培養問題解決能力',
                'syllabus': '第1週：程式設計概論\n第2週：變數與資料型態\n第3週：條件判斷\n第4週：迴圈結構\n第5週：函式\n第6週：串列與字典\n...'
            },
            {
                'course_code': 'WD101',
                'name': '網頁設計',
                'credits': 3,
                'course_type': 'required',
                'grade': 2,
                'description': '學習 HTML、CSS、JavaScript 基礎，設計與製作靜態網站。',
                'objectives': '1. 掌握 HTML 結構與標籤\n2. 學習 CSS 樣式設計\n3. 初步應用 JavaScript 互動效果',
                'syllabus': '第1週：網頁設計概論與 HTML 基礎\n第2週：HTML 表格與表單\n第3週：CSS 基礎與選擇器\n第4週：CSS 版面配置\n第5週：響應式設計\n第6週：JavaScript 入門\n...'
            },
            {
                'course_code': 'DB101',
                'name': '資料庫概論',
                'credits': 3,
                'course_type': 'required',
                'grade': 2,
                'description': '介紹資料庫系統基本概念、關聯式資料庫設計與 SQL 語言。',
                'objectives': '1. 認識資料庫基本概念\n2. 學習關聯式資料庫設計\n3. 熟練 SQL 查詢語言',
                'syllabus': '第1週：資料庫系統簡介\n第2週：資料模型\n第3週：關聯式資料庫\n第4週：正規化\n第5週：SQL 語言基礎\n...'
            },
            {
                'course_code': 'MIS201',
                'name': '系統分析與設計',
                'credits': 3,
                'course_type': 'required',
                'grade': 3,
                'description': '學習資訊系統開發生命週期，從需求分析到系統設計的完整流程。',
                'objectives': '1. 了解系統開發流程\n2. 學習需求分析技巧\n3. 掌握系統設計方法',
                'syllabus': '第1週：系統分析與設計概論\n第2週：系統規劃與可行性分析\n第3週：需求分析\n第4週：資料流程圖與ER圖\n...'
            },
            {
                'course_code': 'IM301',
                'name': '網路與企業應用',
                'credits': 3,
                'course_type': 'required',
                'grade': 3,
                'description': '介紹電腦網路基礎概念及其在企業經營中的應用。',
                'objectives': '1. 認識網路架構與協定\n2. 了解企業網路應用\n3. 學習網路安全基礎',
                'syllabus': '第1週：網路概論\n第2週：網路通訊協定\n第3週：區域網路與廣域網路\n...'
            },
        ]
        
        created_count = 0
        for data in courses_data:
            course, created = Course.objects.get_or_create(
                course_code=data['course_code'],
                defaults={
                    'name': data['name'],
                    'teacher': teacher,
                    'credits': data['credits'],
                    'course_type': data['course_type'],
                    'grade': data['grade'],
                    'capacity': 30,
                    'description': data['description'],
                    'objectives': data['objectives'],
                    'syllabus': data['syllabus'],
                    'enrolled_count': 0,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'已新增: {course.course_code} - {course.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'已存在: {course.course_code} - {course.name}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n完成！共新增 {created_count} 門課程'))
        self.stdout.write(self.style.SUCCESS('預設教師: teacher_default / teacher123'))
