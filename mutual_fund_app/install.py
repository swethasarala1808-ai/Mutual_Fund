import frappe
from frappe.utils import nowdate, add_days
import random, datetime

def after_install():
    try:
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(str(e), "MF Install")

def load_sample_data():
    create_settings()
    create_amcs()
    create_schemes()
    create_nav_history()
    create_distributor()
    create_agents()
    create_commission_rules()
    create_leads()
    create_clients()
    create_folios()
    create_sips()
    create_transaction_orders()
    create_portfolios()
    frappe.db.commit()
    print("✅ Sample data loaded!")

def create_settings():
    if not frappe.db.table_exists("MF Settings"): return
    try:
        s = frappe.get_single("MF Settings")
        if not s.company_name:
            s.company_name = "Bizaxl Mutual Fund Services"
            s.sebi_registration = "INZ000XXXXXX"
            s.distributor_arn = "ARN-98765"
            s.ops_email = "ops@bizaxl.in"
            s.ops_mobile = "9999000000"
            s.whatsapp_number = "9999000000"
            s.tds_rate = 10
            s.sip_reminder_days_before = 3
            s.nav_sync_time = "18:30"
            s.save(ignore_permissions=True)
    except: pass

def create_amcs():
    if not frappe.db.table_exists("AMC Master"): return
    for d in [
        {"amc_name":"HDFC AMC","sebi_registration_no":"SEBI/IMD/DF/001/2003","cin":"L65991MH1999PLC123456","website":"https://www.hdfcfund.com","contact_email":"info@hdfcfund.com","contact_phone":"18002002267","rta_name":"CAMS","is_active":1},
        {"amc_name":"SBI Mutual Fund","sebi_registration_no":"SEBI/IMD/DF/009/2007","cin":"U65910MH1992PLC065289","website":"https://www.sbimf.com","contact_email":"care@sbimf.com","contact_phone":"18002093333","rta_name":"CAMS","is_active":1},
        {"amc_name":"Axis Mutual Fund","sebi_registration_no":"SEBI/IMD/DF/003/2009","cin":"U65100MH2009PLC190810","website":"https://www.axismf.com","contact_email":"investor@axismf.com","contact_phone":"18002107000","rta_name":"KFintech","is_active":1},
    ]:
        if not frappe.db.exists("AMC Master",{"amc_name":d["amc_name"]}):
            doc=frappe.new_doc("AMC Master"); doc.update(d); doc.insert(ignore_permissions=True)
    frappe.db.commit()

def create_schemes():
    if not frappe.db.table_exists("Scheme Master"): return
    for d in [
        {"scheme_name":"HDFC Mid Cap Opportunities Fund","amc":"HDFC AMC","isin":"INF179K01BB2","scheme_code":"HDFC001","category":"Equity","plan_type":"Regular","option_type":"Growth","expense_ratio":1.75,"min_investment":5000,"min_sip_amount":500,"risk_level":"High","fund_manager":"Chirag Setalvad","aum_cr":42500,"is_active":1},
        {"scheme_name":"HDFC Liquid Fund","amc":"HDFC AMC","isin":"INF179K01BC0","scheme_code":"HDFC002","category":"Liquid","plan_type":"Regular","option_type":"Growth","expense_ratio":0.25,"min_investment":5000,"min_sip_amount":1000,"risk_level":"Low","fund_manager":"Anil Bamboli","aum_cr":62000,"is_active":1},
        {"scheme_name":"SBI Bluechip Fund","amc":"SBI Mutual Fund","isin":"INF200K01338","scheme_code":"SBI001","category":"Equity","plan_type":"Regular","option_type":"Growth","expense_ratio":1.55,"min_investment":5000,"min_sip_amount":500,"risk_level":"High","fund_manager":"Sohini Andani","aum_cr":38200,"is_active":1},
        {"scheme_name":"SBI Short Term Debt Fund","amc":"SBI Mutual Fund","isin":"INF200K01239","scheme_code":"SBI002","category":"Debt","plan_type":"Regular","option_type":"Growth","expense_ratio":0.65,"min_investment":5000,"min_sip_amount":1000,"risk_level":"Low","fund_manager":"Rajeev Radhakrishnan","aum_cr":15400,"is_active":1},
        {"scheme_name":"Axis ELSS Tax Saver Fund","amc":"Axis Mutual Fund","isin":"INF846K01DP8","scheme_code":"AXIS001","category":"ELSS","plan_type":"Regular","option_type":"Growth","expense_ratio":1.65,"min_investment":500,"min_sip_amount":500,"risk_level":"High","fund_manager":"Shreyash Devalkar","aum_cr":31600,"is_active":1},
        {"scheme_name":"Axis Flexi Cap Fund","amc":"Axis Mutual Fund","isin":"INF846K01EW1","scheme_code":"AXIS002","category":"Equity","plan_type":"Regular","option_type":"Growth","expense_ratio":1.72,"min_investment":5000,"min_sip_amount":500,"risk_level":"Very High","fund_manager":"Jinesh Gopani","aum_cr":16800,"is_active":1},
    ]:
        if not frappe.db.exists("Scheme Master",{"isin":d["isin"]}):
            doc=frappe.new_doc("Scheme Master"); doc.update(d); doc.insert(ignore_permissions=True)
    frappe.db.commit()

def create_nav_history():
    if not frappe.db.table_exists("NAV History"): return
    base_navs={"INF179K01BB2":92.45,"INF179K01BC0":3845.22,"INF200K01338":71.33,"INF200K01239":28.87,"INF846K01DP8":84.12,"INF846K01EW1":63.55}
    today=datetime.date.today()
    for isin,base in base_navs.items():
        sn=frappe.db.get_value("Scheme Master",{"isin":isin},"name")
        if not sn: continue
        nav=base
        for i in range(30,-1,-1):
            d=today-datetime.timedelta(days=i)
            if d.weekday()>=5: continue
            nav=round(nav*(1+random.uniform(-0.008,0.012)),4)
            if not frappe.db.exists("NAV History",{"scheme":sn,"nav_date":str(d)}):
                doc=frappe.new_doc("NAV History"); doc.scheme=sn; doc.nav_date=str(d); doc.nav_value=nav; doc.source="AMFI"; doc.insert(ignore_permissions=True)
    frappe.db.commit()

def create_distributor():
    if not frappe.db.table_exists("Distributor"): return
    if not frappe.db.exists("Distributor",{"arn_number":"ARN-98765"}):
        doc=frappe.new_doc("Distributor"); doc.company_name="Bizaxl Securities Pvt Ltd"; doc.arn_number="ARN-98765"; doc.kyd_date="2024-01-15"; doc.kyd_status="Compliant"; doc.sebi_category="Corporate"; doc.gstin="27AAAAA0000A1Z5"; doc.pan="AAAAA0000A"; doc.bank_name="HDFC Bank"; doc.account_number="50200012345678"; doc.ifsc="HDFC0001234"; doc.contact_person="Ravi Menon"; doc.email="ravi@bizaxl.in"; doc.mobile="9876543210"; doc.is_active=1; doc.insert(ignore_permissions=True)
    frappe.db.commit()

def create_agents():
    if not frappe.db.table_exists("MF Agent"): return
    dist=frappe.db.get_value("Distributor",{"arn_number":"ARN-98765"},"name") or ""
    for d in [
        {"agent_name":"Priya Sharma","euin":"E123456","distributor":dist,"mobile":"9876500001","email":"priya@bizaxl.in","joining_date":"2023-04-01","aum_target":5000000,"sip_count_target":50,"territory":"Bengaluru South","status":"Active"},
        {"agent_name":"Rahul Kumar","euin":"E789012","distributor":dist,"mobile":"9876500002","email":"rahul@bizaxl.in","joining_date":"2023-07-01","aum_target":3000000,"sip_count_target":30,"territory":"Bengaluru North","status":"Active"},
    ]:
        if not frappe.db.exists("MF Agent",{"euin":d["euin"]}):
            doc=frappe.new_doc("MF Agent"); doc.update(d); doc.insert(ignore_permissions=True)
    frappe.db.commit()

def create_commission_rules():
    if not frappe.db.table_exists("Commission Rule"): return
    dist=frappe.db.get_value("Distributor",{"arn_number":"ARN-98765"},"name")
    for amc_name,trail in [("HDFC AMC",0.65),("SBI Mutual Fund",0.60),("Axis Mutual Fund",0.70)]:
        amc=frappe.db.get_value("AMC Master",{"amc_name":amc_name},"name")
        if amc and dist and not frappe.db.exists("Commission Rule",{"amc":amc,"distributor":dist}):
            doc=frappe.new_doc("Commission Rule"); doc.amc=amc; doc.distributor=dist; doc.trail_percent=trail; doc.upfront_percent=0; doc.effective_from="2024-01-01"; doc.insert(ignore_permissions=True)
    frappe.db.commit()

def create_leads():
    if not frappe.db.table_exists("Lead"): return
    agent=frappe.db.get_value("MF Agent",{"euin":"E123456"},"name") or ""
    for d in [
        {"full_name":"Amit Joshi","mobile":"9000000001","email":"amit@gmail.com","source":"Referral","assigned_agent":agent,"status":"New","city":"Bengaluru","estimated_investment":100000},
        {"full_name":"Sunita Rao","mobile":"9000000002","email":"sunita@gmail.com","source":"WhatsApp","assigned_agent":agent,"status":"Contacted","city":"Bengaluru","estimated_investment":50000},
        {"full_name":"Karan Mehta","mobile":"9000000003","email":"karan@gmail.com","source":"Event","assigned_agent":agent,"status":"Qualified","city":"Mysuru","estimated_investment":200000},
        {"full_name":"Deepa Nair","mobile":"9000000004","email":"deepa@gmail.com","source":"LinkedIn","assigned_agent":agent,"status":"KYC","city":"Bengaluru","estimated_investment":150000},
        {"full_name":"Vikram Patel","mobile":"9000000005","email":"vikram@gmail.com","source":"Cold Call","assigned_agent":agent,"status":"Order Placed","city":"Hubballi","estimated_investment":75000},
    ]:
        if not frappe.db.exists("Lead",{"mobile":d["mobile"]}):
            doc=frappe.new_doc("Lead"); doc.update(d); doc.insert(ignore_permissions=True)
    frappe.db.commit()

def create_clients():
    if not frappe.db.table_exists("MF Client"): return
    agent=frappe.db.get_value("MF Agent",{"euin":"E123456"},"name") or ""
    dist=frappe.db.get_value("Distributor",{"arn_number":"ARN-98765"},"name") or ""
    for d in [
        {"full_name":"Neha Verma","pan":"ABCPV1234D","date_of_birth":"1988-05-15","mobile":"9800000001","email":"neha@gmail.com","address":"12, MG Road, Bengaluru","pincode":"560001","bank_name":"ICICI Bank","account_number":"123456789012","ifsc":"ICIC0001234","nominee_name":"Raj Verma","nominee_relation":"Spouse","kyc_status":"Verified","agent":agent,"distributor":dist,"portal_password_hash":"0001"},
        {"full_name":"Suresh Iyer","pan":"DEFPI5678G","date_of_birth":"1975-11-22","mobile":"9800000002","email":"suresh@gmail.com","address":"45, Koramangala, Bengaluru","pincode":"560034","bank_name":"SBI","account_number":"987654321098","ifsc":"SBIN0001234","nominee_name":"Latha Iyer","nominee_relation":"Spouse","kyc_status":"Verified","agent":agent,"distributor":dist,"portal_password_hash":"0002"},
        {"full_name":"Preethi Das","pan":"GHIPD9012J","date_of_birth":"1992-03-08","mobile":"9800000003","email":"preethi@gmail.com","address":"78, Whitefield, Bengaluru","pincode":"560066","bank_name":"Axis Bank","account_number":"456789012345","ifsc":"UTIB0001234","nominee_name":"Ravi Das","nominee_relation":"Father","kyc_status":"Verified","agent":agent,"distributor":dist,"portal_password_hash":"0003"},
    ]:
        if not frappe.db.exists("MF Client",{"pan":d["pan"]}):
            doc=frappe.new_doc("MF Client"); doc.update(d); doc.insert(ignore_permissions=True)
    frappe.db.commit()

def create_folios():
    if not frappe.db.table_exists("Folio"): return
    clients=frappe.db.get_all("MF Client",fields=["name"],limit=3)
    schemes=frappe.db.get_all("Scheme Master",fields=["name"],limit=6)
    if not clients or not schemes: return
    for d in [
        {"folio_number":"FOLI123456","client":clients[0]["name"],"scheme":schemes[0]["name"],"units_held":1245.678,"average_nav":78.45,"invested_amount":97700,"current_value":115134.56,"xirr":14.5,"open_date":"2022-06-01","status":"Active"},
        {"folio_number":"FOLI234567","client":clients[0]["name"],"scheme":schemes[2]["name"],"units_held":876.543,"average_nav":65.20,"invested_amount":57150,"current_value":62422.61,"xirr":10.2,"open_date":"2023-01-15","status":"Active"},
        {"folio_number":"FOLI345678","client":clients[1]["name"],"scheme":schemes[0]["name"],"units_held":2150.00,"average_nav":80.00,"invested_amount":172000,"current_value":198570.30,"xirr":16.8,"open_date":"2021-09-01","status":"Active"},
        {"folio_number":"FOLI456789","client":clients[2]["name"],"scheme":schemes[4]["name"] if len(schemes)>4 else schemes[0]["name"],"units_held":590.00,"average_nav":72.30,"invested_amount":42657,"current_value":49659.80,"xirr":11.9,"open_date":"2023-06-01","status":"Active"},
    ]:
        if not frappe.db.exists("Folio",{"folio_number":d["folio_number"]}):
            doc=frappe.new_doc("Folio"); doc.update(d); doc.insert(ignore_permissions=True)
    frappe.db.commit()

def create_sips():
    if not frappe.db.table_exists("SIP"): return
    clients=frappe.db.get_all("MF Client",fields=["name"],limit=3)
    schemes=frappe.db.get_all("Scheme Master",fields=["name"],limit=3)
    if not clients or not schemes: return
    today=datetime.date.today()
    for d in [
        {"client":clients[0]["name"],"scheme":schemes[0]["name"],"sip_amount":5000,"frequency":"Monthly","sip_date":5,"start_date":"2022-06-05","next_sip_date":str(today+datetime.timedelta(days=2)),"mandate_status":"Registered","status":"Active","total_invested":120000},
        {"client":clients[1]["name"],"scheme":schemes[1]["name"],"sip_amount":10000,"frequency":"Monthly","sip_date":10,"start_date":"2021-09-10","next_sip_date":str(today+datetime.timedelta(days=5)),"mandate_status":"Registered","status":"Active","total_invested":290000},
        {"client":clients[2]["name"],"scheme":schemes[2]["name"] if len(schemes)>2 else schemes[0]["name"],"sip_amount":3000,"frequency":"Monthly","sip_date":15,"start_date":"2023-06-15","next_sip_date":str(today+datetime.timedelta(days=1)),"mandate_status":"Registered","status":"Active","total_invested":39000},
    ]:
        doc=frappe.new_doc("SIP"); doc.update(d); doc.insert(ignore_permissions=True)
    frappe.db.commit()

def create_transaction_orders():
    if not frappe.db.table_exists("Transaction Order"): return
    clients=frappe.db.get_all("MF Client",fields=["name"],limit=3)
    schemes=frappe.db.get_all("Scheme Master",fields=["name"],limit=3)
    agent=frappe.db.get_value("MF Agent",{"euin":"E123456"},"name") or ""
    if not clients or not schemes: return
    for d in [
        {"transaction_type":"Purchase","client":clients[0]["name"],"scheme":schemes[0]["name"],"amount":50000,"payment_mode":"Net Banking","arn":"ARN-98765","euin":"E123456","agent":agent,"order_date":add_days(nowdate(),-20),"status":"Confirmed","allotted_units":638.45,"allotted_nav":78.32,"payment_status":"Paid"},
        {"transaction_type":"SIP","client":clients[1]["name"],"scheme":schemes[1]["name"],"amount":10000,"payment_mode":"NACH","arn":"ARN-98765","euin":"E123456","agent":agent,"order_date":add_days(nowdate(),-10),"status":"Confirmed","allotted_units":152.78,"allotted_nav":65.45,"payment_status":"Paid"},
        {"transaction_type":"Purchase","client":clients[2]["name"],"scheme":schemes[2]["name"] if len(schemes)>2 else schemes[0]["name"],"amount":25000,"payment_mode":"UPI","arn":"ARN-98765","euin":"E123456","agent":agent,"order_date":add_days(nowdate(),-5),"status":"Routed","payment_status":"Paid"},
    ]:
        doc=frappe.new_doc("Transaction Order"); doc.update(d); doc.insert(ignore_permissions=True)
    frappe.db.commit()

def create_portfolios():
    if not frappe.db.table_exists("Portfolio"): return
    clients=frappe.db.get_all("MF Client",fields=["name"],limit=3)
    for i,client in enumerate(clients):
        data=[{"total_invested":154850,"current_value":177556.17,"absolute_gain":22706.17,"absolute_gain_pct":14.66,"xirr":14.5},{"total_invested":229150,"current_value":260992.91,"absolute_gain":31842.91,"absolute_gain_pct":13.89,"xirr":13.2},{"total_invested":81657,"current_value":88659.80,"absolute_gain":7002.80,"absolute_gain_pct":8.57,"xirr":11.9}]
        doc=frappe.new_doc("Portfolio"); doc.client=client["name"]; doc.as_of_date=nowdate(); doc.update(data[i]); doc.insert(ignore_permissions=True)
    frappe.db.commit()
    print("All sample data created!")
