import os, json, re, base64
from typing import Optional
import anthropic
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI()
_dir = os.path.dirname(os.path.abspath(__file__))

def get_client():
    return anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

@app.get("/", response_class=HTMLResponse)
async def index():
    with open(os.path.join(_dir, "templates", "index.html"), encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/api/analyze-floorplan")
async def analyze_floorplan(file: Optional[UploadFile] = File(None), demo: Optional[str] = Form(None), extra_instruction: Optional[str] = Form(None)):
    prompt = "コインパーキング設計の専門家として図面を解析しJSONのみ返してください。" + (extra_instruction or "")
    try:
        client = get_client()
        if file and file.filename:
            contents = await file.read()
            b64 = base64.standard_b64encode(contents).decode("utf-8")
            msg = client.messages.create(model="claude-opus-4-5", max_tokens=1500, messages=[{"role":"user","content":[{"type":"image","source":{"type":"base64","media_type":file.content_type or "image/jpeg","data":b64}},{"type":"text","text":prompt}]}])
        else:
            msg = client.messages.create(model="claude-opus-4-5", max_tokens=1500, messages=[{"role":"user","content":"東京都内250sqm角地の想定データとして "+prompt+' {"area_total":250,"area_effective":200,"shape":"rect","road_directions":2,"road_width":6,"slots_recommended":8,"slots_max":10,"sqm_per_slot":25,"layout_type":"parallel","obstacles":"なし","confidence":{"area":"high","road":"high","slots":"high","shape":"high","obstacles":"high"},"evidence":"東京都内角地250sqmの標準的な配置","warnings":"","checks":[{"label":"接道幅員3.5m以上","status":"ok","note":""},{"label":"有効面積20sqm/台","status":"ok","note":""},{"label":"入出庫動線確保","status":"ok","note":""},{"label":"精算機スペース","status":"ok","note":""},{"label":"照明設置余地","status":"ok","note":""},{"label":"障害物リスク","status":"ok","note":""},{"label":"排水勾配確保","status":"ok","note":""}]}'}])
        text = msg.content[0].text
        match = re.search(r"\{[\s\S]+\}", re.sub(r"```json|```", "", text).strip())
        return JSONResponse(content={"success": True, "data": json.loads(match.group(0)) if match else {}})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/market-research")
async def market_research(body: dict):
    try:
        client = get_client()
        msg = client.messages.create(model="claude-opus-4-5", max_tokens=800, messages=[{"role":"user","content":f'駐車場市場調査。所在地:{body.get("address","東京都内")} 面積:{body.get("area",300)}sqm {body.get("slots",10)}台。JSONのみ: {{"weekday_day":{{"min":200,"max":300}},"weekday_night":{{"min":100,"max":200}},"holiday_day":{{"min":300,"max":400}},"recommended_rate":200,"competitors_500m":5,"demand_level":"中","demand_reason":"周辺商業施設あり","market_summary":"需要安定","max_daily":2400}}'}])
        text = msg.content[0].text
        match = re.search(r"\{[\s\S]+\}", re.sub(r"```json|```", "", text).strip())
        return JSONResponse(content={"success": True, "data": json.loads(match.group(0)) if match else {}})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/finance")
async def finance(body: dict):
    try:
        client = get_client()
        msg = client.messages.create(model="claude-opus-4-5", max_tokens=800, messages=[{"role":"user","content":f'収支試算。台数:{body.get("slots",10)}台 料金:{body.get("rate",200)}円/30分 所在地:{body.get("address","東京都内")}。JSONのみ: {{"monthly_revenue":500000,"monthly_mgmt":15000,"monthly_lease":30000,"monthly_electric":8000,"monthly_tax":20000,"monthly_total_cost":73000,"monthly_profit":427000,"annual_profit":5124000,"initial_investment":3000000,"payback_months":7,"yield_rate":17.1,"comment":"良好な収益性"}}'}])
        text = msg.content[0].text
        match = re.search(r"\{[\s\S]+\}", re.sub(r"```json|```", "", text).strip())
        return JSONResponse(content={"success": True, "data": json.loads(match.group(0)) if match else {}})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/proposal")
async def proposal(body: dict):
    try:
        client = get_client()
        msg = client.messages.create(model="claude-opus-4-5", max_tokens=2000, messages=[{"role":"user","content":f'営業提案資料。{body.get("address","東京")} {body.get("area",300)}sqm {body.get("slots",10)}台。JSONのみ: {{"slides":[{{"num":1,"title":"表紙","headline":"コインパーキング設置のご提案","body":"この度は土地活用のご提案をさせていただきます","key_numbers":[]}},{{"num":2,"title":"現状分析","headline":"土地の現状と可能性","body":"対象地の特性を分析しました","key_numbers":[]}},{{"num":3,"title":"提案概要","headline":"コインパーキング設置が最適","body":"収益性と手軽さを兼ね備えた活用法です","key_numbers":[]}},{{"num":4,"title":"レイアウト計画","headline":"{body.get("slots",10)}台配置計画","body":"効率的なレイアウトを実現します","key_numbers":[]}},{{"num":5,"title":"市場調査","headline":"需要は旺盛","body":"周辺の需要と競合状況を調査しました","key_numbers":[]}},{{"num":6,"title":"収支試算","headline":"安定した収益が見込めます","body":"月間収益シミュレーション","key_numbers":["{body.get("monthly_profit",0)}円/月","{body.get("annual_profit",0)}円/年"]}},{{"num":7,"title":"まとめ","headline":"ぜひご検討ください","body":"次のステップをご案内します","key_numbers":[]}}]}}'}])
        text = msg.content[0].text
        match = re.search(r"\{[\s\S]+\}", re.sub(r"```json|```", "", text).strip())
        return JSONResponse(content={"success": True, "data": json.loads(match.group(0)) if match else {}})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))