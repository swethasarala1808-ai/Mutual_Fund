import frappe
from frappe.utils import nowdate, add_days, flt
import datetime, random, urllib.parse

def _wa(mobile, msg):
    url = "https://wa.me/91{}?text={}".format(mobile, urllib.parse.quote(msg))
    frappe.log_error(url, "WA")
    return url

def _save(doctype, **kwargs):
    data = {k:v for k,v in kwargs.items() if not k.startswith("cmd")}
    name = data.pop("name", None)
    if name and frappe.db.exists(doctype, name):
        doc = frappe.get_doc(doctype, name); doc.update(data); doc.save(ignore_permissions=True)
    else:
        doc = frappe.new_doc(doctype); doc.update(data); doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return doc.name

# ── DASHBOARD ──────────────────────────────────────────────
@frappe.whitelist(allow_guest=True)
def get_dashboard_stats():
    try:
        total_aum = frappe.db.sql("SELECT COALESCE(SUM(current_value),0) FROM `tabPortfolio`")[0][0] or 0
        active_sips = frappe.db.count("SIP", {"status":"Active"})
        total_clients = frappe.db.count("MF Client", {"kyc_status":"Verified"})
        active_leads = frappe.db.count("Lead", {"status":["in",["New","Contacted","Qualified"]]})
        pending_kyc = frappe.db.count("MF Client", {"kyc_status":"Pending"})
        new_clients = frappe.db.sql("SELECT COUNT(*) FROM `tabMF Client` WHERE creation>=%s", [nowdate()[:8]+"01"])[0][0] or 0
        sip_due = frappe.db.count("SIP", {"status":"Active","next_sip_date":["between",[nowdate(), add_days(nowdate(),3)]]})
        monthly_commission = frappe.db.sql("SELECT COALESCE(SUM(received_amount),0) FROM `tabCommission Settlement` WHERE period=%s",[nowdate()[:7]])[0][0] or 0
        return {"total_aum":flt(total_aum,2),"active_sips":active_sips,"total_clients":total_clients,
                "active_leads":active_leads,"pending_kyc":pending_kyc,"new_clients_month":new_clients,
                "sip_due_today":sip_due,"monthly_commission":flt(monthly_commission,2)}
    except Exception as e:
        frappe.log_error(str(e),"DashStats")
        return {"total_aum":0,"active_sips":0,"total_clients":0,"active_leads":0,"pending_kyc":0,"new_clients_month":0,"sip_due_today":0,"monthly_commission":0}

# ── AMC / SCHEMES ───────────────────────────────────────────
@frappe.whitelist(allow_guest=True)
def get_amc_list():
    return frappe.db.get_all("AMC Master", fields=["name","amc_name","sebi_registration_no","rta_name","contact_email","is_active"], order_by="amc_name")

@frappe.whitelist(allow_guest=True)
def get_schemes(amc=None, category=None, search=None):
    f = {}
    if amc: f["amc"] = amc
    if category: f["category"] = category
    if search:
        return frappe.db.get_all("Scheme Master", filters=[["scheme_name","like",f"%{search}%"]],
            fields=["name","scheme_name","amc","isin","category","plan_type","expense_ratio","min_sip_amount","risk_level","aum_cr","is_active"])
    return frappe.db.get_all("Scheme Master", filters=f,
        fields=["name","scheme_name","amc","isin","category","plan_type","expense_ratio","min_sip_amount","risk_level","aum_cr","is_active"], order_by="scheme_name")

@frappe.whitelist(allow_guest=True)
def get_nav_history(scheme, days=30):
    cutoff = add_days(nowdate(), -int(days))
    return frappe.db.get_all("NAV History", filters={"scheme":scheme,"nav_date":[">=",cutoff]},
        fields=["nav_date","nav_value","source"], order_by="nav_date asc")

@frappe.whitelist(allow_guest=True)
def save_amc(**kwargs): return _save("AMC Master", **kwargs)
@frappe.whitelist(allow_guest=True)
def save_scheme(**kwargs): return _save("Scheme Master", **kwargs)

# ── DISTRIBUTOR ─────────────────────────────────────────────
@frappe.whitelist(allow_guest=True)
def get_distributors():
    return frappe.db.get_all("Distributor", fields=["name","company_name","arn_number","kyd_status","pan","contact_person","email","mobile","is_active"])

@frappe.whitelist(allow_guest=True)
def get_empanelments(distributor=None):
    f = {}
    if distributor: f["distributor"] = distributor
    return frappe.db.get_all("Empanelment", filters=f, fields=["name","distributor","amc","agreement_date","validity_date","status"])

@frappe.whitelist(allow_guest=True)
def get_commission_settlements(distributor=None, period=None):
    f = {}
    if distributor: f["distributor"] = distributor
    if period: f["period"] = period
    return frappe.db.get_all("Commission Settlement", filters=f,
        fields=["name","period","amc","distributor","calculated_amount","received_amount","variance","tds_deducted","status"], order_by="period desc")

@frappe.whitelist(allow_guest=True)
def get_payouts(agent=None, period=None):
    f = {}
    if agent: f["agent"] = agent
    if period: f["period"] = period
    return frappe.db.get_all("Payout", filters=f,
        fields=["name","agent","period","gross_amount","tds_amount","net_payout","payment_date","status"])

@frappe.whitelist(allow_guest=True)
def save_distributor_rec(**kwargs): return _save("Distributor", **kwargs)
@frappe.whitelist(allow_guest=True)
def save_empanelment(**kwargs): return _save("Empanelment", **kwargs)
@frappe.whitelist(allow_guest=True)
def save_commission_settlement(**kwargs): return _save("Commission Settlement", **kwargs)
@frappe.whitelist(allow_guest=True)
def save_payout(**kwargs): return _save("Payout", **kwargs)

# ── AGENT CRM ───────────────────────────────────────────────
@frappe.whitelist(allow_guest=True)
def get_agents(distributor=None):
    f = {}
    if distributor: f["distributor"] = distributor
    return frappe.db.get_all("MF Agent", filters=f,
        fields=["name","agent_name","euin","mobile","email","territory","aum_target","sip_count_target","status"])

@frappe.whitelist(allow_guest=True)
def get_leads(assigned_agent=None, status=None, search=None):
    f = {}
    if assigned_agent: f["assigned_agent"] = assigned_agent
    if status: f["status"] = status
    if search:
        return frappe.db.get_all("Lead", filters=[["full_name","like",f"%{search}%"]],
            fields=["name","full_name","mobile","email","source","assigned_agent","status","city","estimated_investment","follow_up_date"])
    return frappe.db.get_all("Lead", filters=f,
        fields=["name","full_name","mobile","email","source","assigned_agent","status","city","estimated_investment","follow_up_date"], order_by="creation desc")

@frappe.whitelist(allow_guest=True)
def get_meetings(agent=None, client=None, lead=None):
    f = {}
    if agent: f["agent"] = agent
    if client: f["client"] = client
    if lead: f["lead"] = lead
    return frappe.db.get_all("Meeting", filters=f,
        fields=["name","meeting_with","lead","client","agent","meeting_date","mode","outcome","follow_up_date"])

@frappe.whitelist(allow_guest=True)
def get_risk_profile(client):
    rows = frappe.db.get_all("Risk Profile", filters={"client":client},
        fields=["name","client","assessment_date","risk_profile_type","risk_score","investment_horizon"], order_by="assessment_date desc", limit=1)
    return rows[0] if rows else None

@frappe.whitelist(allow_guest=True)
def get_recommendations(client=None, agent=None):
    f = {}
    if client: f["client"] = client
    if agent: f["agent"] = agent
    return frappe.db.get_all("Recommendation", filters=f,
        fields=["name","client","agent","recommendation_date","investment_goal","total_sip_amount","status"])

@frappe.whitelist(allow_guest=True)
def save_lead(**kwargs): return _save("Lead", **kwargs)
@frappe.whitelist(allow_guest=True)
def save_meeting(**kwargs): return _save("Meeting", **kwargs)
@frappe.whitelist(allow_guest=True)
def save_mf_agent(**kwargs): return _save("MF Agent", **kwargs)

@frappe.whitelist(allow_guest=True)
def save_risk_profile(**kwargs):
    data = {k:v for k,v in kwargs.items() if not k.startswith("cmd")}
    horizon_map = {"Less than 1Y":1,"1-3Y":2,"3-5Y":3,"5Y+":4}
    income_map = {"Below 5L":1,"5-10L":2,"10-25L":3,"25-50L":4,"50L+":5}
    score = horizon_map.get(data.get("investment_horizon"),2)*3 + income_map.get(data.get("annual_income"),2)*2
    data["risk_score"] = score
    data["risk_profile_type"] = "Conservative" if score<=6 else "Moderate" if score<=10 else "Moderately Aggressive" if score<=14 else "Aggressive"
    name = data.pop("name", None)
    if name and frappe.db.exists("Risk Profile", name):
        doc = frappe.get_doc("Risk Profile", name); doc.update(data); doc.save(ignore_permissions=True)
    else:
        doc = frappe.new_doc("Risk Profile"); doc.update(data); doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return doc.as_dict()

@frappe.whitelist(allow_guest=True)
def save_recommendation(**kwargs): return _save("Recommendation", **kwargs)

# ── KYC ─────────────────────────────────────────────────────
@frappe.whitelist(allow_guest=True)
def get_kyc_doc(client):
    rows = frappe.db.get_all("KYC Doc", filters={"client":client},
        fields=["name","client","pan_number","aadhaar_last4","kyc_status","verified_date","verified_by"], limit=1)
    return rows[0] if rows else None

@frappe.whitelist(allow_guest=True)
def save_kyc_doc(**kwargs): return _save("KYC Doc", **kwargs)

@frappe.whitelist(allow_guest=True)
def verify_kyc_mock(client_name):
    ref = "NSDL{}".format(random.randint(100000,999999))
    kyc = frappe.db.get_value("KYC Doc", {"client":client_name}, "name")
    client = frappe.db.get_value("MF Client", client_name, ["full_name","mobile","pan"], as_dict=True)
    if kyc:
        doc = frappe.get_doc("KYC Doc", kyc); doc.kyc_status="Verified"; doc.verified_date=nowdate(); doc.verified_by="NSDL Mock"; doc.ekyc_reference=ref; doc.save(ignore_permissions=True)
    if client:
        frappe.db.set_value("MF Client", client_name, "kyc_status", "Verified")
        _wa(client.mobile, "✅ KYC Verified for {}. PAN: {}XXXXX. You can now invest. — Bizaxl MF".format(client.full_name, (client.pan or "")[:4]))
    frappe.db.commit()
    return {"status":"Verified","reference":ref}

# ── CLIENTS / PORTFOLIO ─────────────────────────────────────
@frappe.whitelist(allow_guest=True)
def get_clients(agent=None, distributor=None, kyc_status=None, search=None):
    f = {}
    if agent: f["agent"] = agent
    if distributor: f["distributor"] = distributor
    if kyc_status: f["kyc_status"] = kyc_status
    if search:
        return frappe.db.get_all("MF Client", filters=[["full_name","like",f"%{search}%"]],
            fields=["name","full_name","mobile","email","pan","kyc_status","agent","total_aum"])
    return frappe.db.get_all("MF Client", filters=f,
        fields=["name","full_name","mobile","email","pan","kyc_status","agent","total_aum"], order_by="creation desc")

@frappe.whitelist(allow_guest=True)
def get_client_detail(client_name):
    return frappe.db.get_value("MF Client", client_name,
        ["name","full_name","pan","date_of_birth","mobile","email","address","pincode","bank_name","ifsc","nominee_name","nominee_relation","kyc_status","agent","distributor","total_aum"], as_dict=True)

@frappe.whitelist(allow_guest=True)
def get_folios(client):
    return frappe.db.get_all("Folio", filters={"client":client},
        fields=["name","folio_number","scheme","units_held","average_nav","invested_amount","current_value","xirr","status"])

@frappe.whitelist(allow_guest=True)
def get_portfolio(client):
    rows = frappe.db.get_all("Portfolio", filters={"client":client},
        fields=["name","as_of_date","total_invested","current_value","absolute_gain","absolute_gain_pct","xirr"], order_by="as_of_date desc", limit=1)
    return rows[0] if rows else None

@frappe.whitelist(allow_guest=True)
def get_sips(client=None, scheme=None, status=None, agent=None):
    f = {}
    if client: f["client"] = client
    if scheme: f["scheme"] = scheme
    if status: f["status"] = status
    # if agent filter needed join via client
    return frappe.db.get_all("SIP", filters=f,
        fields=["name","client","scheme","folio","sip_amount","frequency","sip_date","next_sip_date","mandate_status","status","total_invested"])

@frappe.whitelist(allow_guest=True)
def get_transaction_orders(client=None, agent=None, status=None):
    f = {}
    if client: f["client"] = client
    if agent: f["agent"] = agent
    if status: f["status"] = status
    return frappe.db.get_all("Transaction Order", filters=f,
        fields=["name","transaction_type","client","scheme","amount","status","payment_status","order_date","allotted_units","allotted_nav","payment_link","agent"], order_by="creation desc")

@frappe.whitelist(allow_guest=True)
def save_client(**kwargs): return _save("MF Client", **kwargs)
@frappe.whitelist(allow_guest=True)
def save_folio(**kwargs): return _save("Folio", **kwargs)
@frappe.whitelist(allow_guest=True)
def save_sip(**kwargs): return _save("SIP", **kwargs)

@frappe.whitelist(allow_guest=True)
def save_transaction_order(**kwargs):
    data = {k:v for k,v in kwargs.items() if not k.startswith("cmd")}
    name = data.pop("name", None)
    if name and frappe.db.exists("Transaction Order", name):
        doc = frappe.get_doc("Transaction Order", name); doc.update(data); doc.save(ignore_permissions=True)
    else:
        doc = frappe.new_doc("Transaction Order"); doc.update(data); doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return doc.name

# ── PAYMENT ─────────────────────────────────────────────────
@frappe.whitelist(allow_guest=True)
def create_payment_link(order_name, amount):
    link = "https://pay.bizaxl.in/link/{}".format(order_name)
    if frappe.db.exists("Transaction Order", order_name):
        frappe.db.set_value("Transaction Order", order_name, "payment_link", link)
        cn = frappe.db.get_value("Transaction Order", order_name, "client")
        sn = frappe.db.get_value("Transaction Order", order_name, "scheme")
        c = frappe.db.get_value("MF Client", cn, ["full_name","mobile"], as_dict=True) if cn else None
        s = frappe.db.get_value("Scheme Master", sn, "scheme_name") if sn else "Scheme"
        if c: _wa(c.mobile, "💳 Pay ₹{} for {}: {} | Order: {} — Bizaxl MF".format(flt(amount,0), s, link, order_name))
        frappe.db.commit()
    return link

# ── WHATSAPP ────────────────────────────────────────────────
@frappe.whitelist(allow_guest=True)
def send_whatsapp(mobile, message_type, data=None):
    import json as _j
    d = _j.loads(data) if isinstance(data, str) else (data or {})
    msgs = {
        "sip_reminder": "📅 SIP Reminder: ₹{amount} for {scheme} due {date}. Bizaxl MF".format(**d),
        "kyc_verified": "✅ KYC Verified for {name}. Start investing now. Bizaxl MF".format(**d),
        "order_confirmed": "✅ Order {type} ₹{amount} in {scheme}. Ref: {ref}. Bizaxl MF".format(**d),
        "portfolio_update": "📊 Portfolio: ₹{current_value} | Gain: {gain}%. Bizaxl MF".format(**d),
        "payment_link": "💳 Pay ₹{amount} for {scheme}: {link}. Bizaxl MF".format(**d),
        "lead_followup": "👋 Hi {name}, following up on your investment inquiry. {agent_name}, Bizaxl MF".format(**d),
    }
    msg = msgs.get(message_type, "Message from Bizaxl MF")
    url = _wa(mobile, msg)
    return {"wa_url": url, "message": msg}

# ── REPORTS ─────────────────────────────────────────────────
@frappe.whitelist(allow_guest=True)
def get_aum_summary(distributor=None, agent=None, date=None):
    rows = frappe.db.get_all("Folio", filters={"status":"Active"}, fields=["scheme","invested_amount","current_value"])
    by_scheme = {}
    for r in rows:
        k = r["scheme"]
        if k not in by_scheme: by_scheme[k] = {"scheme":k,"invested":0,"current":0,"folios":0}
        by_scheme[k]["invested"] += flt(r["invested_amount"]); by_scheme[k]["current"] += flt(r["current_value"]); by_scheme[k]["folios"] += 1
    result = list(by_scheme.values())
    for r in result: r["gain"]=round(r["current"]-r["invested"],2); r["gain_pct"]=round((r["gain"]/r["invested"]*100) if r["invested"] else 0,2)
    return sorted(result, key=lambda x: -x["current"])

@frappe.whitelist(allow_guest=True)
def get_sip_book(agent=None, status=None):
    f = {}
    if status: f["status"] = status
    return frappe.db.get_all("SIP", filters=f, fields=["name","client","scheme","sip_amount","frequency","next_sip_date","mandate_status","status","total_invested"])

@frappe.whitelist(allow_guest=True)
def get_commission_report(distributor=None, period=None):
    f = {}
    if distributor: f["distributor"] = distributor
    if period: f["period"] = period
    return frappe.db.get_all("Commission Settlement", filters=f,
        fields=["name","period","amc","distributor","calculated_amount","received_amount","variance","tds_deducted","status"], order_by="period desc")

@frappe.whitelist(allow_guest=True)
def get_onboarding_funnel(agent=None):
    result = []
    for s in ["New","Contacted","Qualified","KYC","Order Placed","Active","Lost"]:
        f = {"status":s}
        if agent: f["assigned_agent"] = agent
        result.append({"status":s,"count":frappe.db.count("Lead",f)})
    return result

@frappe.whitelist(allow_guest=True)
def get_kyc_pending_tracker():
    return frappe.db.get_all("MF Client", filters={"kyc_status":["in",["Pending","Rejected"]]},
        fields=["name","full_name","mobile","pan","kyc_status","agent","creation"])

@frappe.whitelist(allow_guest=True)
def get_capital_gains(client, financial_year):
    rows = frappe.db.get_all("Capital Gains Statement", filters={"client":client,"financial_year":financial_year},
        fields=["name","financial_year","total_stcg","total_ltcg","total_redemptions","status"])
    return rows[0] if rows else {"client":client,"financial_year":financial_year,"total_stcg":0,"total_ltcg":0,"total_redemptions":0}

@frappe.whitelist(allow_guest=True)
def get_sip_reminder_schedule(agent="", days_ahead=3):
    today = datetime.date.today()
    cutoff = today + datetime.timedelta(days=int(days_ahead))
    return frappe.db.get_all("SIP", filters={"status":"Active","next_sip_date":["between",[str(today),str(cutoff)]]},
        fields=["name","client","scheme","sip_amount","next_sip_date","folio"])

@frappe.whitelist(allow_guest=True)
def get_agent_target_report(period=None):
    f = {}
    if period: f["period"] = period
    return frappe.db.get_all("Agent Target", filters=f,
        fields=["name","agent","period","aum_target","aum_achieved","sip_count_target","sip_count_achieved","new_client_target","new_clients_achieved","achievement_pct"])

# ── AGENT DASHBOARD SPECIFIC ────────────────────────────────
@frappe.whitelist(allow_guest=True)
def get_agent_dashboard(agent_euin):
    agent = frappe.db.get_value("MF Agent", {"euin":agent_euin}, ["name","agent_name","territory","aum_target","sip_count_target"], as_dict=True)
    if not agent: return {"error":"Agent not found"}
    an = agent["name"]
    my_leads = frappe.db.count("Lead", {"assigned_agent":an})
    my_clients = frappe.db.count("MF Client", {"agent":an})
    active_sips = frappe.db.sql("SELECT COUNT(*) FROM `tabSIP` s JOIN `tabMF Client` c ON s.client=c.name WHERE c.agent=%s AND s.status='Active'", [an])[0][0] or 0
    pending_kyc = frappe.db.count("MF Client", {"agent":an,"kyc_status":"Pending"})
    today_followups = frappe.db.count("Lead", {"assigned_agent":an,"follow_up_date":nowdate()})
    due_sips = frappe.db.sql("SELECT COUNT(*) FROM `tabSIP` s JOIN `tabMF Client` c ON s.client=c.name WHERE c.agent=%s AND s.status='Active' AND s.next_sip_date BETWEEN %s AND %s",[an,nowdate(),add_days(nowdate(),3)])[0][0] or 0
    total_aum = frappe.db.sql("SELECT COALESCE(SUM(p.current_value),0) FROM `tabPortfolio` p JOIN `tabMF Client` c ON p.client=c.name WHERE c.agent=%s",[an])[0][0] or 0
    recent_orders = frappe.db.get_all("Transaction Order", filters={"agent":an},
        fields=["name","transaction_type","client","scheme","amount","status","order_date"], order_by="creation desc", limit=5)
    return {"agent":agent,"stats":{"my_leads":my_leads,"my_clients":my_clients,"active_sips":active_sips,"pending_kyc":pending_kyc,"today_followups":today_followups,"due_sips":due_sips,"total_aum":flt(total_aum,2)},"recent_orders":recent_orders}

# ── SETTINGS ────────────────────────────────────────────────
@frappe.whitelist(allow_guest=True)
def get_settings():
    try: return frappe.db.get_singles_dict("MF Settings")
    except: return {}

@frappe.whitelist(allow_guest=True)
def save_settings(**kwargs):
    data = {k:v for k,v in kwargs.items() if not k.startswith("cmd")}
    try:
        doc = frappe.get_single("MF Settings"); doc.update(data); doc.save(ignore_permissions=True); frappe.db.commit(); return "Saved"
    except Exception as e: return str(e)

# ── INVESTOR PORTAL ─────────────────────────────────────────
@frappe.whitelist(allow_guest=True)
def investor_login(mobile, otp):
    client = frappe.db.get_value("MF Client", {"mobile":mobile,"kyc_status":"Verified"}, "name")
    if not client: return {"success":False,"message":"Mobile not found or KYC not verified"}
    stored = frappe.db.get_value("MF Client", client, "portal_password_hash")
    if otp == mobile[-4:] or otp == (stored or ""):
        fn = frappe.db.get_value("MF Client", client, "full_name")
        return {"success":True,"client":client,"full_name":fn}
    return {"success":False,"message":"Invalid OTP. Use last 4 digits of your mobile number."}

@frappe.whitelist(allow_guest=True)
def raise_service_request(**kwargs):
    data = {k:v for k,v in kwargs.items() if not k.startswith("cmd")}
    doc = frappe.new_doc("Service Request"); doc.update(data); doc.raised_date=nowdate(); doc.status="Open"; doc.insert(ignore_permissions=True); frappe.db.commit()
    return doc.name
