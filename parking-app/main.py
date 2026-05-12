from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.requests import Request
import anthropic
import base64
import os
import json
import re
from typing import Optional

app = FastAPI(title="コインパーキング営業支援ツール")
import os as _os
_base = _os.path.dirname(_os.path.abspath(__file__))
templates = Jinja2Templates(directory=_os.path.join(_base, "templates"))
app.mount("/static", StaticFiles(directory="static"), name="static")

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/analyze-floorplan")
async def analyze_floorplan(
    file: Optional[UploadFile] = File(None),
    demo: Optional[str] = Form(None),
    extra_instruction: Optional[str] = Form(None)
):
    prompt = build_analysis_prompt(extra_instruction)
    try:
        if file and file.filename:
            contents = await file.read()
            b64 = base64.standard_b64encode(contents).decode("utf-8")
            mime = file.content_type or "image/jpeg"
            message = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=1500,
                messages=[{"role": "user", "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": mime, "data": b64}},
                    {"type": "text", "text": prompt}
                ]}]
            )
        else:
            demo_prompt = "東京都内250㎡角地（長方形、接道2方向、幅員6m）の想定データとして" + prompt
            message = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=1500,
                messages=[{"role": "user", "content": demo_prompt}]
            )
        text = message.content[0].text
        clean = re.sub(r"```json|```", "", text).strip()
        match = re.search(r"\{[\s\S]+\}", clean)
        if not match:
            raise ValueError("JSONが見つかりません")
        data = json.loads(match.group(0))
        return JSONResponse(content={"success": True, "data": data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/market-research")
async def market_research(body: dict):
    address = body.get("address", "東京都内")
    area = body.get("area", 300)
    slots = body.get("slots", 10)
    prompt = f"""駐車場市場調査の専門家として、以下の場所の周辺コインパーキング相場を分析してください。
所在地: {address} / 面積: {area}㎡ / {slots}台規模

必ず以下のJSONのみ返してください（マークダウン不要）:
{{
  "weekday_day": {{"min": 数値, "max": 数値}},
  "weekday_night": {{"min": 数値, "max": 数値}},
  "holiday_day": {{"min": 数値, "max": 数値}},
  "recommended_rate": 数値,
  "competitors_500m": 数値,
  "demand_level": "高|中|低",
  "demand_reason": "需要の理由",
  "market_summary": "市場評価（2〜3文）",
  "max_daily": 数値
}}"""
    try:
        message = client.messages.create(
            model="claude-opus-4-5", max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        text = message.content[0].text
        match = re.search(r"\{[\s\S]+\}", re.sub(r"```json|```", "", text).strip())
        data = json.loads(match.group(0)) if match else {}
        return JSONResponse(content={"success": True, "data": data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/finance")
async def finance(body: dict):
    slots = body.get("slots", 10)
    rate = body.get("rate", 200)
    address = body.get("address", "東京都内")
    prompt = f"""コインパーキング収支試算。台数:{slots}台 料金:{rate}円/30分 所在地:{address} 稼働率:平日60%休日80%

必ず以下のJSONのみ返してください（マークダウン不要）:
{{
  "monthly_revenue": 数値,
  "monthly_mgmt": 数値,
  "monthly_lease": 数値,
  "monthly_electric": 数値,
  "monthly_tax": 数値,
  "monthly_total_cost": 数値,
  "monthly_profit": 数値,
  "annual_profit": 数値,
  "initial_investment": 数値,
  "payback_months": 数値,
  "yield_rate": 数値,
  "comment": "収支の特記事項（1〜2文）"
}}"""
    try:
        message = client.messages.create(
            model="claude-opus-4-5", max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        text = message.content[0].text
        match = re.search(r"\{[\s\S]+\}", re.sub(r"```json|```", "", text).strip())
        data = json.loads(match.group(0)) if match else {}
        return JSONResponse(content={"success": True, "data": data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/proposal")
async def proposal(body: dict):
    address = body.get("address", "東京都内")
    area = body.get("area", 300)
    slots = body.get("slots", 10)
    rate = body.get("rate", 200)
    monthly_profit = body.get("monthly_profit", 0)
    annual_profit = body.get("annual_profit", 0)
    yield_rate = body.get("yield_rate", 0)
    payback_months = body.get("payback_months", 0)

    prompt = f"""コインパーキング土地オーナー向け営業提案資料を作成してください。
所在地:{address} 面積:{area}㎡ {slots}台 {rate}円/30分
月間純利益:{monthly_profit:,}円 年間純利益:{annual_profit:,}円 利回り:{yield_rate}% 回収:{payback_months}ヶ月

7枚のスライド内容をJSONで返してください（マークダウン不要）:
{{
  "slides": [
    {{"num": 1, "title": "表紙", "headline": "見出し文", "body": "本文", "key_numbers": []}},
    {{"num": 2, "title": "現状分析", "headline": "", "body": "", "key_numbers": []}},
    {{"num": 3, "title": "提案概要", "headline": "", "body": "", "key_numbers": []}},
    {{"num": 4, "title": "レイアウト計画", "headline": "", "body": "", "key_numbers": []}},
    {{"num": 5, "title": "市場調査", "headline": "", "body": "", "key_numbers": []}},
    {{"num": 6, "title": "収支試算", "headline": "", "body": "", "key_numbers": ["{monthly_profit:,}円/月", "{annual_profit:,}円/年", "{yield_rate}%利回り"]}},
    {{"num": 7, "title": "まとめ・次のステップ", "headline": "", "body": "", "key_numbers": []}}
  ]
}}"""
    try:
        message = client.messages.create(
            model="claude-opus-4-5", max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        text = message.content[0].text
        match = re.search(r"\{[\s\S]+\}", re.sub(r"```json|```", "", text).strip())
        data = json.loads(match.group(0)) if match else {}
        return JSONResponse(content={"success": True, "data": data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def build_analysis_prompt(extra=None):
    return f"""コインパーキング設計の専門家として図面を解析し、以下のJSONのみ返してください（マークダウン不要）。
{f'追加指示: {extra}' if extra else ''}
{{
  "area_total": 数値,
  "area_effective": 数値,
  "shape": "rect|l|flag|triangle|irreg",
  "road_directions": 数値,
  "road_width": 数値,
  "slots_recommended": 数値,
  "slots_max": 数値,
  "sqm_per_slot": 数値,
  "layout_type": "parallel|vertical|angle|mixed",
  "obstacles": "障害物の説明",
  "confidence": {{
    "area": "high|mid|low", "road": "high|mid|low",
    "slots": "high|mid|low", "shape": "high|mid|low", "obstacles": "high|mid|low"
  }},
  "evidence": "解析根拠2〜3文",
  "warnings": "注意点（なければ空文字）",
  "checks": [
    {{"label": "接道幅員 3.5m以上", "status": "ok|warn|ng", "note": ""}},
    {{"label": "有効面積 20㎡/台 以上確保", "status": "ok|warn|ng", "note": ""}},
    {{"label": "入出庫動線の確保", "status": "ok|warn|ng", "note": ""}},
    {{"label": "精算機設置スペース（約2㎡）", "status": "ok|warn|ng", "note": ""}},
    {{"label": "照明・防犯カメラ設置余地", "status": "ok|warn|ng", "note": ""}},
    {{"label": "障害物・埋設物リスク", "status": "ok|warn|ng", "note": ""}},
    {{"label": "排水勾配確保見込み", "status": "ok|warn|ng", "note": ""}}
  ]
}}"""
