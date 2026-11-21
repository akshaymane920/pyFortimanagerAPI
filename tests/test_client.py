import pytest

import pyFortiManagerAPI
from pyFortiManagerAPI import FortiManager
from conftest import SESSION_ID, FakeSession


# ---------------------------------------------------------------- construction / login

def test_defaults():
    f = FortiManager(host="h")
    assert f.base_url == "https://h/jsonrpc"
    assert f.verify is True
    assert f.adom == "root"


def test_http_forces_verify_false():
    f = FortiManager(host="h", protocol="http", verify=True)
    assert f.verify is False
    assert f.base_url == "http://h/jsonrpc"


def test_login_sends_credentials_and_stores_session(fmg, fake_session):
    fmg.login()
    s = fake_session[0]
    login = s.calls[0]["json"]
    assert login["params"][0] == {"data": {"passwd": "p", "user": "u"}, "url": "sys/login/user"}
    assert fmg.sessionid == SESSION_ID


def test_login_reuses_session(fmg, fake_session):
    fmg.login()
    fmg.login()
    assert len(fake_session) == 1
    assert len(fake_session[0].calls) == 1


def test_proxies_false_disables_env(fake_session):
    f = FortiManager(host="h", proxies=False)
    f.login()
    assert fake_session[0].trust_env is False


def test_explicit_proxies_applied(fake_session):
    proxies = {"https": "http://proxy:3128"}
    FortiManager(host="h", proxies=proxies).login()
    assert fake_session[0].proxies == proxies


def test_failed_login_raises_clear_error(monkeypatch):
    def responder(payload):
        return {"result": [{"status": {"code": -22, "message": "Login fail"}, "url": "sys/login/user"}]}

    monkeypatch.setattr(pyFortiManagerAPI.requests, "session", lambda: FakeSession(responder))
    f = FortiManager(host="h")
    with pytest.raises(pyFortiManagerAPI.FortiManagerLoginError, match="Login fail"):
        f.get_adoms()


def test_logout_uses_same_session_and_resets_state(fmg, fake_session):
    fmg.login()
    fmg.logout()
    assert len(fake_session) == 1, "logout must reuse the logged-in session (proxies, cookies)"
    assert fake_session[0].calls[-1]["json"]["params"][0]["url"] == "sys/logout"
    assert fmg.sessionid is None and fmg.session is None
    fmg.login()
    assert len(fake_session) == 2, "login after logout must create a fresh session"


def test_every_request_carries_session_id(fmg, session):
    fmg.get_adoms()
    fmg.get_devices()
    fmg.custom_api({"method": "get", "params": [{"url": "x"}]})
    assert all(p["session"] == SESSION_ID for p in session.api_calls)


# ---------------------------------------------------------------- URL / payload smoke tests

CASES = [
    # (callable, expected method, expected url)
    (lambda f: f.get_adoms(), "get", "dvmdb/adom"),
    (lambda f: f.get_adoms(name="x"), "get", "dvmdb/adom/x"),
    (lambda f: f.lock_adom(), "exec", "dvmdb/adom/lab/workspace/lock"),
    (lambda f: f.unlock_adom("other"), "exec", "dvmdb/adom/other/workspace/unlock"),
    (lambda f: f.get_devices(), "get", "/dvmdb/adom/lab/device/"),
    (lambda f: f.get_device("fw1"), "get", "/dvmdb/adom/lab/device/fw1"),
    (lambda f: f.add_device("1.1.1.1", "a", "b", "fw1"), "exec", "dvm/cmd/add/device"),
    (lambda f: f.add_model_device("fw1", "SN"), "exec", "dvm/cmd/add/device"),
    (lambda f: f.get_policy_packages(), "get", "pm/pkg/adom/lab/"),
    (lambda f: f.add_policy_package("pkg"), "set", "pm/pkg/adom/lab/"),
    (lambda f: f.add_install_target("fw1", "pkg"), "add", "pm/pkg/adom/lab/pkg/scope member"),
    (lambda f: f.get_meta_data(), "get", "/dvmdb/_meta_fields/device"),
    (lambda f: f.add_meta_data("m"), "add", "/dvmdb/_meta_fields/device"),
    (lambda f: f.assign_meta_to_device("fw1", "m", "v"), "update", "/dvmdb/adom/lab/device/fw1"),
    (lambda f: f.assign_meta_to_device_vdom("fw1", "v1", "m", "v"), "update", "/dvmdb/adom/lab/device/fw1/vdom/v1"),
    (lambda f: f.get_firewall_address_objects(), "get", "pm/config/adom/lab/obj/firewall/address"),
    (lambda f: f.get_firewall_address_v6_objects("a"), "get", "pm/config/adom/lab/obj/firewall/address6/a"),
    (lambda f: f.add_firewall_address_v6_object("a", "::1/128"), "add", "pm/config/adom/lab/obj/firewall/address6"),
    (lambda f: f.update_firewall_address_object("a", comment="c"), "update", "pm/config/adom/lab/obj/firewall/address/a"),
    (lambda f: f.delete_firewall_address_object("a"), "delete", "pm/config/adom/lab/obj/firewall/address/a"),
    (lambda f: f.delete_firewall_address_v6_object("a"), "delete", "pm/config/adom/lab/obj/firewall/address6/a"),
    (lambda f: f.get_address_groups(), "get", "pm/config/adom/lab/obj/firewall/addrgrp"),
    (lambda f: f.get_address_v6_groups(), "get", "pm/config/adom/lab/obj/firewall/addrgrp6"),
    (lambda f: f.add_address_group("g", ["a"]), "add", "pm/config/adom/lab/obj/firewall/addrgrp"),
    (lambda f: f.add_address_v6_group("g"), "add", "pm/config/adom/lab/obj/firewall/addrgrp6"),
    (lambda f: f.delete_address_group("g"), "delete", "pm/config/adom/lab/obj/firewall/addrgrp/g"),
    (lambda f: f.delete_address_v6_group("g"), "delete", "pm/config/adom/lab/obj/firewall/addrgrp6/g"),
    (lambda f: f.add_dynamic_group("g", "fw1", "root", ["a"]), "add",
     "pm/config/adom/lab/obj/firewall/addrgrp/g/dynamic_mapping"),
    (lambda f: f.get_firewall_vip_objects(), "get", "pm/config/adom/lab/obj/firewall/vip"),
    (lambda f: f.get_global_header_policies("pkg"), "get", "pm/config/global/pkg/pkg/global/header/policy"),
    (lambda f: f.get_global_header_policies("pkg", 5), "get", "pm/config/global/pkg/pkg/global/header/policy/5"),
    (lambda f: f.get_firewall_header_policies(policyid=5), "get", "pm/config/adom/lab/obj/global/header/policy/5"),
    (lambda f: f.get_global_footer_policies("pkg", 5), "get", "pm/config/global/pkg/pkg/global/footer/policy/5"),
    (lambda f: f.get_firewall_footer_policies(policyid=5), "get", "pm/config/adom/lab/obj/global/footer/policy/5"),
    (lambda f: f.policy_lookup("fw1", "port1", "1.1.1.1", "2.2.2.2", 6, 443), "exec", "sys/proxy/json"),
    (lambda f: f.get_interfaces("fw1"), "get", "pm/config/device/fw1/global/system/interface"),
    (lambda f: f.get_interface("fw1", "port1"), "get", "pm/config/device/fw1/global/system/interface/port1"),
    (lambda f: f.get_services(), "get", "pm/config/adom/lab/obj/firewall/service/custom"),
    (lambda f: f.get_service("HTTPS"), "get", "pm/config/adom/lab/obj/firewall/service/custom/HTTPS"),
    (lambda f: f.get_firewall_policies("pkg"), "get", "pm/config/adom/lab/pkg/pkg/firewall/policy/"),
    (lambda f: f.get_firewall_policies("pkg", 3), "get", "pm/config/adom/lab/pkg/pkg/firewall/policy/3"),
    (lambda f: f.get_dhcp("fw1"), "exec", "sys/proxy/json"),
    (lambda f: f.add_firewall_policy("pkg", "n", "p1", "a", "p2", "b", "ALL"), "add",
     "pm/config/adom/lab/pkg/pkg/firewall/policy/"),
    (lambda f: f.add_firewall_policy_with_v6("pkg", "n", "p1", "a", "a6", "p2", "b", "b6", "ALL"), "add",
     "pm/config/adom/lab/pkg/pkg/firewall/policy/"),
    (lambda f: f.update_firewall_policy("pkg", 3, status=0), "update", "pm/config/adom/lab/pkg/pkg/firewall/policy/3"),
    (lambda f: f.delete_firewall_policy("pkg", 3), "delete", "pm/config/adom/lab/pkg/pkg/firewall/policy/3"),
    (lambda f: f.move_firewall_policy("pkg", 3, policyid=1), "move", "pm/config/adom/lab/pkg/pkg/firewall/policy/3"),
    (lambda f: f.install_policy_package("pkg"), "exec", "securityconsole/install/package"),
    (lambda f: f.install_policy_package_to_device("pkg", "fw1", "root"), "exec", "securityconsole/install/package"),
    (lambda f: f.create_script("s", "show"), "add", "/dvmdb/adom/lab/script/"),
    (lambda f: f.get_all_scripts(), "get", "/dvmdb/adom/lab/script/"),
    (lambda f: f.update_script(1, "s", "show"), "update", "/dvmdb/adom/lab/script/"),
    (lambda f: f.delete_script("s"), "delete", "/dvmdb/adom/lab/script/"),
    (lambda f: f.run_script_on_multiple_devices("s", [{"name": "fw1", "vdom": "root"}]), "exec",
     "/dvmdb/adom/lab/script/execute"),
    (lambda f: f.run_script_on_single_device("s", "fw1", "root"), "exec", "/dvmdb/adom/lab/script/execute"),
    (lambda f: f.get_script_output("fw1", "root"), "get", "/dvmdb/adom/lab/script/log/list/device/fw1"),
    (lambda f: f.quick_db_install("fw1", "root"), "exec", "/securityconsole/install/device"),
    (lambda f: f.track_quick_db_install(7), "get", "/task/task/7"),
    (lambda f: f.create_interface("fw1", "v10", "port1", 0, "root", 10, "1.1.1.1", "255.255.255.0", "a"), "add",
     "pm/config/device/fw1/global/system/interface"),
    (lambda f: f.create_zone("fw1", "z", "root"), "add", "pm/config/device/fw1/vdom/root/system/zone"),
    (lambda f: f.get_zones("fw1", "root"), "get", "pm/config/device/fw1/vdom/root/system/zone"),
    (lambda f: f.get_zone("fw1", "z", "root"), "get", "pm/config/device/fw1/vdom/root/system/zone/z"),
    (lambda f: f.assign_interfaces_to_zone("fw1", "z", ["port1"], "root"), "set",
     "pm/config/device/fw1/vdom/root/system/zone"),
    (lambda f: f.create_device_group("g"), "add", "/dvmdb/adom/lab/group/g"),
    (lambda f: f.add_device_to_group("g", "fw1", "root"), "add", "/dvmdb/adom/lab/group/g/object member"),
    (lambda f: f.delete_device_to_group("g", "fw1", "root"), "delete", "/dvmdb/adom/lab/group/g/object member"),
    (lambda f: f.create_script_group("sg"), "add", "/dvmdb/adom/lab/script/"),
    (lambda f: f.get_dhcp_servers("fw1", "root"), "get", "pm/config/device/fw1/vdom/root/system/dhcp/server"),
]


@pytest.mark.parametrize("call,method,url", CASES, ids=[c[2] + ":" + c[1] for c in CASES])
def test_request_shape(fmg, session, call, method, url):
    call(fmg)
    payload = session.last
    assert payload["method"] == method
    assert payload["params"][0]["url"] == url
    assert payload["session"] == SESSION_ID


# ---------------------------------------------------------------- regression tests for specific bugs

def test_get_policies_assigned_to_device_logs_in_and_uses_adom(fmg, fake_session):
    # Previously used self.session without logging in -> AttributeError on None
    fmg.get_policies_assigned_to_device("fw1", "root")
    payload = fake_session[0].last
    assert payload["params"][0]["data"]["target"] == ["adom/lab/device/fw1"]


def test_dynamic_object_respects_adom_and_vdom(fmg, session):
    fmg.add_dynamic_object("obj", "fw1", ["10.0.0.0", "255.0.0.0"], vdom="v1")
    p = session.last["params"][0]
    assert p["url"] == "pm/config/adom/lab/obj/firewall/address/obj/dynamic_mapping"
    assert p["data"][0]["_scope"] == [{"name": "fw1", "vdom": "v1"}]
    assert "comment" not in p["data"][0], "comment=None must not be sent as the string 'None'"


def test_update_dynamic_object_respects_adom(fmg, session):
    fmg.update_dynamic_object("obj", "fw1", ["10.0.0.0", "255.0.0.0"], do="remove")
    p = session.last
    assert p["method"] == "delete"
    assert p["params"][0]["url"] == "pm/config/adom/lab/obj/firewall/address/obj/dynamic_mapping"


def test_update_dynamic_object_rejects_bad_do(fmg, session):
    with pytest.raises(ValueError):
        fmg.update_dynamic_object("obj", "fw1", [], do="bogus")


def test_add_device_without_description_sends_empty_string(fmg, session):
    fmg.add_device("1.1.1.1", "a", "b", "fw1")
    assert session.last["params"][0]["data"]["device"]["desc"] == ""


def test_run_script_on_single_device_scope_is_list(fmg, session):
    fmg.run_script_on_single_device("s", "fw1", "root")
    assert session.last["params"][0]["data"]["scope"] == [{"name": "fw1", "vdom": "root"}]


def test_update_address_v6_object_maps_subnet_to_ip6(fmg, session):
    fmg.update_firewall_address_v6_object("a", subnet="2001:db8::/64", comment="c")
    assert session.last["params"][0]["data"] == {"ip6": "2001:db8::/64", "comment": "c"}


def test_set_adom_requires_value(fmg):
    with pytest.raises(TypeError):
        fmg.set_adom()
    fmg.set_adom("x")
    assert fmg.adom == "x"


def test_update_address_group_add_and_remove(monkeypatch, fmg):
    def responder(payload):
        url = payload["params"][0]["url"]
        if url == "sys/login/user":
            return {"result": [{"status": {"code": 0, "message": "OK"}}], "session": SESSION_ID}
        return {"result": [{"status": {"code": 0}, "data": {"member": ["a", "b"]}}]}

    s = FakeSession(responder)
    monkeypatch.setattr(pyFortiManagerAPI.requests, "session", lambda: s)
    fmg.update_address_group("g", "c", do="add")
    assert s.last["params"][0]["data"]["member"] == ["a", "b", "c"]
    fmg.update_address_group("g", "a", do="remove")
    assert s.last["params"][0]["data"]["member"] == ["b"]
    with pytest.raises(ValueError):
        fmg.update_address_group("g", "a", do="bogus")


# ---------------------------------------------------------------- address object / make_data

def test_add_address_ipmask(fmg, session):
    fmg.add_firewall_address_object("n", subnet=["1.1.1.1", "255.255.255.255"])
    data = session.last["params"][0]["data"]
    assert data["type"] == 0 and data["subnet"] == ["1.1.1.1", "255.255.255.255"]


def test_add_address_fqdn(fmg, session):
    fmg.add_firewall_address_object("n", fqdn="example.com")
    data = session.last["params"][0]["data"]
    assert data["type"] == "fqdn" and "allow-routing" not in data


@pytest.mark.parametrize("kwargs", [{}, {"subnet": ["1.1.1.1", "255.255.255.255"], "fqdn": "x"}])
def test_add_address_validation(fmg, kwargs):
    with pytest.raises(ValueError):
        fmg.add_firewall_address_object("n", **kwargs)


def test_move_policy_requires_target(fmg):
    with pytest.raises(TypeError):
        fmg.move_firewall_policy("pkg", 3)


def test_make_data_policy_mapping():
    assert FortiManager.make_data(source_interface="p1", comment="c") == {"srcintf": "p1", "comments": "c"}


def test_make_data_object_mapping():
    assert FortiManager.make_data(_for="object", associated_interface="any") == {"associated-interface": "any"}


def test_make_data_unknown_key():
    with pytest.raises(KeyError):
        FortiManager.make_data(bogus=1)


def test_make_data_bad_for():
    with pytest.raises(ValueError):
        FortiManager.make_data(_for="nope", name="x")


def test_custom_api_does_not_mutate_input(fmg, session):
    payload = {"method": "get", "params": [{"url": "x"}]}
    fmg.custom_api(payload)
    assert "session" not in payload


def test_backup_config_builds_cli_command(fmg, session):
    fmg.backup_config_of_fortiGate_to_tftp("10.0.0.1", "backups", "bk", "fw1.conf", "fw1")
    create = session.api_calls[0]["params"][0]["data"]
    assert create["content"] == "execute backup config tftp backups/fw1.conf 10.0.0.1"
    assert create["target"] == 1
