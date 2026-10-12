"""测试多账号并发调度器与隔离能力。"""
import os
import sys
import threading
import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

# 确保导入当前目录下的 muse2api
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

import app
from config import Config
from store import Store


def test_concurrency_lock():
    lock = app.ConcurrencyLock(limit=2)
    assert not lock.locked()

    # 第一个槽位
    assert lock.acquire(timeout=0.1)
    assert lock.locked()

    # 第二个槽位（并发 = 2）
    assert lock.acquire(timeout=0.1)
    assert lock.locked()

    # 第三个槽位应超时
    assert not lock.acquire(blocking=True, timeout=0.05)

    # 释放一个槽位
    lock.release()
    assert lock.locked()

    # 现在第三个可以获取了
    assert lock.acquire(timeout=0.1)

    lock.release()
    lock.release()
    assert not lock.locked()
    print("PASS: test_concurrency_lock")


def test_account_pool_manager():
    dummy_accounts = [
        {"id": "acc-1", "label": "A1", "enabled": True, "cookies": {"k": "v1"}},
        {"id": "acc-2", "label": "A2", "enabled": True, "cookies": {"k": "v2"}},
    ]
    dummy_store = SimpleNamespace(
        accounts=dummy_accounts,
        get_account=lambda aid: next((a for a in dummy_accounts if a["id"] == aid), None),
        pick_account=lambda preferred_id=None, rotate=True, force_rotate=False, exclude_ids=None: next(
            (a for a in dummy_accounts if a["id"] not in (exclude_ids or set())), None
        )
    )

    pool = app.AccountPoolManager(dummy_store)

    # 线程 1 占用 acc-1
    a1 = pool.acquire(timeout=0.5)
    assert a1["id"] == "acc-1"
    assert "acc-1" in pool.busy_accounts

    # 线程 2 并发占用 acc-2（自动避开忙碌的 acc-1）
    a2 = pool.acquire(timeout=0.5)
    assert a2["id"] == "acc-2"
    assert "acc-2" in pool.busy_accounts

    # 此时两个账号都忙，线程 3 应等待并超时
    t0 = time.monotonic()
    try:
        pool.acquire(timeout=0.1)
        raise AssertionError("应抛出超时")
    except app.MuseGenerationError:
        pass
    assert time.monotonic() - t0 >= 0.08

    # 释放 acc-1 后，线程 3 能够立刻拿到 acc-1
    pool.release(a1["id"])
    assert "acc-1" not in pool.busy_accounts

    a3 = pool.acquire(timeout=0.5)
    assert a3["id"] == "acc-1"

    # 清理释放
    pool.release(a2["id"])
    pool.release(a3["id"])
    assert len(pool.busy_accounts) == 0
    print("PASS: test_account_pool_manager")


def test_parallel_generation_simulation():
    """模拟两个请求使用不同账号并发执行生成。"""
    dummy_accounts = [
        {"id": "acc-1", "label": "A1", "enabled": True, "cookies": {"c": "1"}},
        {"id": "acc-2", "label": "A2", "enabled": True, "cookies": {"c": "2"}},
    ]
    orig_accounts = list(app.store.accounts)
    running_threads = set()
    active_accounts = []
    concurrency_observed = False
    lock = threading.Lock()

    def fake_generate(cookies, prompt, expect, timeout, expires=None, account_id=None, on_progress=None, reference_image=None):
        nonlocal concurrency_observed
        t_name = threading.current_thread().name
        with lock:
            running_threads.add(t_name)
            active_accounts.append(account_id)
            if len(running_threads) >= 2:
                concurrency_observed = True
        time.sleep(0.15)
        with lock:
            running_threads.discard(t_name)
        return {"filename": f"{account_id}.png", "size": 1234, "kind": expect}

    try:
        with patch("store._write", lambda *a, **k: None), \
             patch.object(app.store, "mark", lambda *a, **k: None), \
             patch.object(app.engine, "start", return_value=None), \
             patch.object(app.engine, "generate", side_effect=fake_generate), \
             patch.object(app, "_renew_and_persist", return_value=None), \
             patch.object(app, "_sync_cookies", return_value=None):

            app.store.accounts = dummy_accounts
            results = []
            def run_task(p):
                res = app._run_generation(p, "image", timeout=5)
                results.append(res)

            t1 = threading.Thread(target=run_task, args=("task 1",), name="Worker-1")
            t2 = threading.Thread(target=run_task, args=("task 2",), name="Worker-2")

            t1.start()
            t2.start()
            t1.join()
            t2.join()

            assert len(results) == 2
            assert concurrency_observed, "两个任务应在独立的线程中同时并发执行！"
            assert set(r[1] for r in results) == {"acc-1", "acc-2"}, "两个任务应分别调度在两个独立账号上！"
            assert len(app.ACCOUNT_POOL.busy_accounts) == 0, "任务结束后所有账号应彻底归还！"
    finally:
        app.store.accounts = orig_accounts
    print("PASS: test_parallel_generation_simulation")


if __name__ == "__main__":
    test_concurrency_lock()
    test_account_pool_manager()
    test_parallel_generation_simulation()
    print("ALL CONCURRENCY TESTS PASSED!")
