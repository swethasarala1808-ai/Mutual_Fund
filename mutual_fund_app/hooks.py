app_name = "mutual_fund_app"
app_title = "BizAxl Mutual Fund"
app_publisher = "Swetha Sarala"
app_description = "Mutual Fund Distribution Platform"
app_email = "swethasarala1808@gmail.com"
app_license = "MIT"
app_version = "1.0.0"

after_install = "mutual_fund_app.install.after_install"

scheduler_events = {
    "cron": {
        "30 18 * * 1-5": ["mutual_fund_app.tasks.sync_nav"],
        "0 9 * * 1-5":   ["mutual_fund_app.tasks.send_sip_reminders"],
        "0 8 * * 1":      ["mutual_fund_app.tasks.create_review_tasks"],
    }
}

website_route_rules = [
    {"from_route": "/mf",              "to_route": "mf"},
    {"from_route": "/mf-dashboard",    "to_route": "mf-dashboard"},
    {"from_route": "/agent-dashboard", "to_route": "agent-dashboard"},
    {"from_route": "/investor-portal", "to_route": "investor-portal"},
]
