'''
【AI課題診断】
産業分類、事業内容、課題の入力をもとに、LLMを用いて課題を深堀するエンドポイントです。
*従量課金のため注意
'''
from fastapi import APIRouter

# スキーマのインポート
from schemas import Project

# AI課題診断用のモジュールインポート
from components.digging_issue import digging_issue

router = APIRouter(prefix="/ai-diagnosis", tags=["ai-diagnosis"])

'''
'''
@router.post("")
def ai_diagnosis(
    project_info: Project, # 本当はこれ用にスキーマを定義した方がよさそう(フロント側の開発に一旦合わせる。)
    ):
    # Projectモデルから必要な情報のみを抽出
    description = project_info.project_content
    industry = project_info.industry #業種情報
    business_description = project_info.business_description #事業内容

    response = digging_issue(industry=industry, business=business_description, challenge=description)

    return response
