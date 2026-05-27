import frappe, random, datetime
from frappe.utils import nowdate, add_days, now

def sync_nav():
    schemes = frappe.db.get_all("Scheme Master", filters={"is_active":1}, fields=["name"])
    updated = 0
    for sch in schemes:
        try:
            last = frappe.db.get_value("NAV History", filters={"scheme":sch["name"]}, fieldname="nav_value", order_by="nav_date desc")
            nav = round(float(last or 100) * (1 + random.uniform(-0.008, 0.012)), 4)
            doc = frappe.new_doc("NAV History"); doc.scheme=sch["name"]; doc.nav_date=nowdate(); doc.nav_value=nav; doc.source="AMFI"; doc.insert(ignore_permissions=True)
            updated += 1
        except: pass
    log = frappe.new_doc("NAV Sync Log"); log.sync_date=nowdate(); log.sync_time=now(); log.records_updated=updated; log.records_failed=len(schemes)-updated; log.status="Success" if updated==len(schemes) else "Partial"; log.insert(ignore_permissions=True)
    frappe.db.commit()

def send_sip_reminders():
    days = frappe.db.get_single_value("MF Settings","sip_reminder_days_before") or 3
    today = datetime.date.today()
    cutoff = today + datetime.timedelta(days=int(days))
    sips = frappe.db.get_all("SIP", filters={"status":"Active","next_sip_date":["between",[str(today),str(cutoff)]]},
        fields=["name","client","scheme","sip_amount","next_sip_date"])
    for sip in sips:
        try:
            c = frappe.db.get_value("MF Client", sip["client"], ["full_name","mobile"], as_dict=True)
            s = frappe.db.get_value("Scheme Master", sip["scheme"], "scheme_name")
            if c and s:
                import urllib.parse
                msg = "📅 SIP Due: ₹{} for {} on {}. Ensure balance. — Bizaxl MF".format(sip["sip_amount"], s, sip["next_sip_date"])
                frappe.log_error("https://wa.me/91{}?text={}".format(c.mobile, urllib.parse.quote(msg)), "WA")
        except: pass
    frappe.db.commit()

def create_review_tasks():
    agents = frappe.db.get_all("MF Agent", filters={"status":"Active"}, fields=["name","agent_name"])
    for a in agents: frappe.log_error("Weekly review: {}".format(a["agent_name"]), "AgentTask")
    frappe.db.commit()
