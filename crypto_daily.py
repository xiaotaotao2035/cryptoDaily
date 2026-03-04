#!/usr/bin/env python3
# crypto_briefing.py — 每日 Crypto 简报自动邮件
# 安装依赖: pip install anthropic

import anthropic, smtplib, json, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_KEY = os.environ["ANTHROPIC_KEY"]
EMAIL_FROM    = os.environ["EMAIL_FROM"]
EMAIL_PASS    = os.environ["EMAIL_PASS"]
EMAIL_TO      = os.environ["EMAIL_TO"]

SYSTEM = """你是专业Crypto分析师,输出纯JSON简报,包含字段:
headline, sentiment, market(summary,outlook), layer2(summary),
defi(summary), policy(summary,risk_level), investment(thesis,portfolio_bias)"""

def generate():
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    msg = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=2000,
        system=SYSTEM,
        messages=[{"role":"user","content":"生成今日Crypto深度简报"}]
    )
    text = msg.content[0].text
    return json.loads(text.replace("```json","").replace("```","").strip())

def to_html(r):
    date = datetime.now().strftime("%Y年%m月%d日")
    bias = r.get("investment",{}).get("portfolio_bias","观望")
    bias_color = {"进攻":"#00d4aa","防守":"#ffd166","观望":"#7b61ff"}.get(bias,"#7b61ff")
    return f"""<!DOCTYPE html>
<html><body style="font-family:'PingFang SC',sans-serif;background:#080d14;
color:#e0ecf8;padding:36px;max-width:680px;margin:0 auto">
<div style="color:#00d4aa;font-size:11px;letter-spacing:4px;margin-bottom:8px">
  ⚡ MORNING INTELLIGENCE · CRYPTO</div>
<h1 style="font-size:24px;margin:0 0 4px;color:#fff">每日深度简报</h1>
<p style="color:#3a5060;font-size:12px;margin:0 0 24px">{date}</p>
<div style="border-left:3px solid #00d4aa;padding:12px 16px;
background:rgba(0,212,170,.06);border-radius:0 10px 10px 0;margin-bottom:24px">
  <p style="font-size:16px;margin:0;font-weight:500">{r.get("headline","")}</p>
</div>
<h2 style="color:#00d4aa;font-size:14px">📊 行情走势</h2>
<p style="font-size:13px;line-height:1.8;color:#b0c4d4">
  {r.get("market",{}).get("summary","")}</p>
<p style="font-size:12px;color:#4a6070">展望：{r.get("market",{}).get("outlook","")}</p>
<h2 style="color:#7b61ff;font-size:14px">⚡ Layer2 & 新链</h2>
<p style="font-size:13px;line-height:1.8;color:#b0c4d4">
  {r.get("layer2",{}).get("summary","")}</p>
<h2 style="color:#0099ff;font-size:14px">🔗 DeFi 动态</h2>
<p style="font-size:13px;line-height:1.8;color:#b0c4d4">
  {r.get("defi",{}).get("summary","")}</p>
<h2 style="color:#ffd166;font-size:14px">🏛 监管政策</h2>
<p style="font-size:13px;line-height:1.8;color:#b0c4d4">
  {r.get("policy",{}).get("summary","")}</p>
<h2 style="color:#ef476f;font-size:14px">🎯 投资方向</h2>
<p style="font-size:13px;line-height:1.8;color:#b0c4d4">
  {r.get("investment",{}).get("thesis","")}</p>
<div style="display:inline-block;background:{bias_color}22;border:1px solid {bias_color}44;
border-radius:8px;padding:8px 16px;margin-top:8px">
  <span style="color:{bias_color};font-weight:700;font-size:13px">仓位方向：{bias}</span>
</div>
<hr style="border-color:#1a2a3a;margin:28px 0">
<p style="font-size:10px;color:#233040">
  本报告由 AI 生成，仅供参考，不构成投资建议 · DYOR · NFA</p>
</body></html>"""

def send(html):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"⚡ Crypto 简报 · {datetime.now().strftime('%m/%d')}"
    msg["From"] = EMAIL_FROM
    msg["To"]   = EMAIL_TO
    msg.attach(MIMEText(html, "html", "utf-8"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(EMAIL_FROM, EMAIL_PASS)
        s.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
    print("✅ 简报已发送！")

if __name__ == "__main__":
    print(f"🔮 {datetime.now().strftime('%H:%M')} 正在生成简报…")
    report = generate()
    send(to_html(report))