from app.crawler.health import LinkHealthAnalyzer


def test_link_health_analyzer_redirects():
    analyzer = LinkHealthAnalyzer(max_redirect_chain=2)
    
    # Normal redirect
    analyzer.record_visit("http://a.com", status_code=301, redirect_target="http://b.com")
    analyzer.record_visit("http://b.com", status_code=200)
    
    # Excessive chain (A -> B -> C -> D)
    analyzer.record_visit("http://c.com", status_code=301, redirect_target="http://d.com")
    analyzer.record_visit("http://d.com", status_code=301, redirect_target="http://e.com")
    analyzer.record_visit("http://e.com", status_code=301, redirect_target="http://f.com")
    
    # Loop (X -> Y -> X)
    analyzer.record_visit("http://x.com", status_code=301, redirect_target="http://y.com")
    analyzer.record_visit("http://y.com", status_code=301, redirect_target="http://x.com")
    
    issues = analyzer.analyze()
    
    loop_issues = [i for i in issues if i.issue_type == "redirect_loop"]
    assert len(loop_issues) == 2  # one for X, one for Y since both are in the loop
    
    chain_issues = [i for i in issues if i.issue_type == "redirect_chain"]
    assert len(chain_issues) == 1
    assert chain_issues[0].url == "http://c.com"

def test_link_health_analyzer_broken_links():
    analyzer = LinkHealthAnalyzer()
    
    # A links to B and C
    analyzer.record_links("http://a.com", {"http://b.com", "http://c.com", "http://d.com"})
    
    # B is good
    analyzer.record_visit("http://b.com", status_code=200)
    
    # C is 404
    analyzer.record_visit("http://c.com", status_code=404)
    
    # D redirects to E which is timeout
    analyzer.record_visit("http://d.com", status_code=301, redirect_target="http://e.com")
    analyzer.record_visit("http://e.com", error_type="Timeout")
    
    issues = analyzer.analyze()
    
    broken = [i for i in issues if i.issue_type == "broken_link"]
    assert len(broken) == 1
    assert broken[0].url == "http://c.com"
    
    conn_errors = [i for i in issues if i.issue_type == "connection_error"]
    assert len(conn_errors) == 1
    assert conn_errors[0].url == "http://d.com" # D is the linked URL, even though E timed out
