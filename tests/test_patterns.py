from reflow.patterns import database_kind, find_urls, is_connection_string, mask_secrets


def test_mask_secrets_keeps_keys():
    assert mask_secrets("Server=x;Pwd=abc;Token: xyz") == "Server=x;Pwd=***;Token: ***"


def test_mask_secrets_in_url_userinfo():
    assert mask_secrets("postgresql://user:secret@host/db") == "postgresql://user:***@host/db"


def test_find_urls_masks_query_secrets():
    assert find_urls("ver https://api.x/v1?token=abc ok") == ["https://api.x/v1?token=***"]


def test_connection_strings():
    assert is_connection_string("Data Source=ORCL;User Id=x")
    assert is_connection_string("mssql+pyodbc://host/db")
    assert not is_connection_string("SELECT * FROM notas")
    assert database_kind("mssql+pyodbc://host/db") == "sqlserver"
    assert database_kind("sqlite:///x.db") == "sqlite"
