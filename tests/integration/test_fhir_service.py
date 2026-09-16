import json
import sqlite3

import pytest

from v43.fhir.compiler import FHIRCompileResult
from v43.fhir.contracts import contract_for_criterion
from v43.fhir.service_replay import official_875_sql, replay_service
from v43.fhir.validator import validate_fhir
from tests.unit.test_fhir_boundary import _store, _trace
from v43.fhir.compiler import compile_fhir


@pytest.mark.parametrize("criterion", ["185", "675", "745", "875"])
def test_service_replay_has_positive_hit_and_structurally_valid_query_miss(criterion):
    contract = contract_for_criterion(criterion)
    valid = validate_fhir(compile_fhir(_trace(criterion), _store(criterion), contract, "Patient/p1"), contract)
    assert replay_service(valid.resources, contract.service, "fixture://fhir", {"p1": "doc-1"}).status == "SERVICE_HIT"

    wrong_identity = replay_service(valid.resources, contract.service, "fixture://fhir", {"other": "doc-2"})
    assert valid.structural_status == "VALID"
    assert wrong_identity.status == "SERVICE_MISS"


def test_875_official_style_json1_query_uses_valid_json_each_and_extract():
    contract = contract_for_criterion("875")
    valid = validate_fhir(compile_fhir(_trace("875"), _store("875"), contract, "Patient/p1"), contract)
    resource = valid.resources[0]
    conn = sqlite3.connect(":memory:")
    conn.execute("create table observation(resource text not null)")
    conn.execute("insert into observation values (?)", (json.dumps(resource),))
    assert conn.execute("select json_valid(resource) from observation").fetchone()[0] == 1
    assert conn.execute(official_875_sql(), (contract.service.profiles[0], contract.service.value_system, "present")).fetchone()[0] == 1


def test_875_malformed_json_fails_instead_of_being_silently_accepted():
    conn = sqlite3.connect(":memory:")
    conn.execute("create table observation(resource text not null)")
    conn.execute("insert into observation values ('{malformed')")
    with pytest.raises(sqlite3.OperationalError, match="malformed JSON"):
        conn.execute(official_875_sql(), ("profile", "system", "present")).fetchall()
