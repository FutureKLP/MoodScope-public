from scripts.build_backend_runtime import exclude_test_assets


def test_runtime_pruning_preserves_runtime_helpers_and_application_resources(tmp_path):
    removed=['_internal/torch/bin/test_jit','_internal/torch/bin/FileStoreTest',
             '_internal/torch/bin/test_interpreter_async.pt','_internal/torch/bin/script_module_v4.ptl',
             '_internal/library/tests/reference.wav']
    retained=['_internal/torch/bin/torch_shm_manager','_internal/torch/bin/protoc',
              '_internal/backend/test_policy.json','licenses/library/LICENSE']
    for name in removed+retained:
        path=tmp_path/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b'authored fixture')
    exclude_test_assets(tmp_path)
    assert all(not (tmp_path/name).exists() for name in removed)
    assert all((tmp_path/name).read_bytes()==b'authored fixture' for name in retained)
