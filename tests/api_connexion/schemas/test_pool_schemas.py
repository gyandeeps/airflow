# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import annotations

import pytest

from airflow.api_connexion.schemas.pool_schema import PoolCollection, pool_collection_schema, pool_schema
from airflow.models.pool import Pool
from airflow.utils.session import provide_session

from tests_common.test_utils.db import clear_db_pools

pytestmark = pytest.mark.db_test


class TestPoolSchema:
    def setup_method(self) -> None:
        clear_db_pools()

    def teardown_method(self) -> None:
        clear_db_pools()

    @provide_session
    def test_serialize(self, session):
        pool_model = Pool(pool="test_pool", slots=2, include_deferred=False)
        session.add(pool_model)
        session.commit()
        pool_instance = session.query(Pool).filter(Pool.pool == pool_model.pool).first()
        serialized_pool = pool_schema.dump(pool_instance)
        assert serialized_pool == {
            "name": "test_pool",
            "slots": 2,
            "occupied_slots": 0,
            "running_slots": 0,
            "queued_slots": 0,
            "scheduled_slots": 0,
            "deferred_slots": 0,
            "open_slots": 2,
            "description": None,
            "include_deferred": False,
        }

    @provide_session
    def test_deserialize(self, session):
        pool_dict = {"name": "test_pool", "slots": 3, "include_deferred": True}
        deserialized_pool = pool_schema.load(pool_dict, session=session)
        assert not isinstance(deserialized_pool, Pool)  # Checks if load_instance is set to True


class TestPoolCollectionSchema:
    def setup_method(self) -> None:
        clear_db_pools()

    def teardown_method(self) -> None:
        clear_db_pools()

    def test_serialize(self):
        pool_model_a = Pool(pool="test_pool_a", slots=3, include_deferred=False)
        pool_model_b = Pool(pool="test_pool_b", slots=3, include_deferred=True)
        instance = PoolCollection(pools=[pool_model_a, pool_model_b], total_entries=2)
        assert pool_collection_schema.dump(instance) == {
            "pools": [
                {
                    "name": "test_pool_a",
                    "slots": 3,
                    "occupied_slots": 0,
                    "running_slots": 0,
                    "queued_slots": 0,
                    "scheduled_slots": 0,
                    "deferred_slots": 0,
                    "open_slots": 3,
                    "description": None,
                    "include_deferred": False,
                },
                {
                    "name": "test_pool_b",
                    "slots": 3,
                    "occupied_slots": 0,
                    "running_slots": 0,
                    "queued_slots": 0,
                    "scheduled_slots": 0,
                    "deferred_slots": 0,
                    "open_slots": 3,
                    "description": None,
                    "include_deferred": True,
                },
            ],
            "total_entries": 2,
        }
