from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding='utf-8')


def test_waypoints_config_targets_patrol_node():
    text = _read('config/waypoints.yaml')
    assert 'cyclic_patrol_node:' in text
    assert 'autonomous_patrol_system:' not in text


def test_cyclic_patrol_declares_configurable_parameters():
    text = _read('autonomous_patrol_system/cyclic_patrol_node.py')
    assert "declare_parameter('total_cycles'" in text
    assert "'waypoints'," in text
    assert "declare_parameter('waypoint_timeout'" in text


def test_mission_controller_has_initial_state_parameter():
    text = _read('autonomous_patrol_system/mission_controller_node.py')
    assert "declare_parameter('initial_state', 'PATROLLING')" in text


def test_full_system_launch_contains_all_core_nodes():
    text = _read('launch/full_system.launch.py')
    for executable in [
        "executable='cyclic_patrol'",
        "executable='environment_monitor'",
        "executable='evidence_capture'",
        "executable='alert_dispatcher'",
        "executable='cli_feedback'",
        "executable='mission_controller'",
    ]:
        assert executable in text
