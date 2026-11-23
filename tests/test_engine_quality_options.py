"""Focused quality controls and motion helpers, without graphics, media or assets."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))

import shaders
from quality import QualityOptions
from p3d.api import CameraState
from p3d import bodymath as bm
from p3d.camera import Rig, hold
from p3d.motion import Motions, Pose, blend
from p3d.attachments import final_hand_frame
from p3d.actor import Actor
from p3d import actor as actor_module


def load_engine(name, path, song):
    """Load engine code with import-only stand-ins, never a graphics context."""
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    gl = ModuleType("moderngl")
    gl.BLEND, gl.ONE = 1, 1
    gl.TRIANGLE_STRIP, gl.ONE_MINUS_SRC_ALPHA = 5, 2
    with patch.dict(sys.modules, song=song, moderngl=gl, text=ModuleType("text")):
        spec.loader.exec_module(module)
    return module


class QualityTests(unittest.TestCase):
    def setUp(self):
        self.cam = CameraState(pos=np.array([0., 1., 10.]),
                               target=np.array([0., 1., 0.]), focus=80., aperture=.04)

    def test_legacy_shader_is_exact_and_grain_disable_is_local(self):
        original = shaders.COMP_FS
        for blocks in ((), ("CAMERA_BG", "HUE_KEEP")):
            head, body = original.split("\n", 1)
            expected = head + "\n" + "".join(f"#define {b} 1\n" for b in blocks) + body
            self.assertEqual(shaders.comp_fs(blocks), expected)
            no_grain = shaders.comp_fs(blocks, grain=False)
            self.assertEqual(no_grain, expected.replace(
                "col += (n1+n2-1.0)*(1.15/255.0);", "// No added delivery grain."))
        self.assertEqual(shaders.COMP_FS, original)
        with self.assertRaises(ValueError):
            shaders.comp_fs((), grain="off")
        with patch.object(shaders, "COMP_FS", original.replace(
                "col += (n1+n2-1.0)*(1.15/255.0);", "// Existing film patch.")), \
                self.assertRaises(ValueError):
            shaders.comp_fs((), grain=False)

    def test_defaults_leave_camera_world_params_and_shutter_untouched(self):
        quality = QualityOptions()
        world = dict(sun_int=.8, rays=.3, sun_glow=.5)
        params = dict(sun_int=.8)
        self.assertIs(quality.world(3, world), world)
        self.assertIs(quality.parameters(3, params), params)
        self.assertEqual(params, dict(sun_int=.8))
        self.assertIs(quality.camera(3, self.cam), self.cam)
        self.assertEqual(quality.shutter_at(3, 60, .4, (3,)), .4)
        self.assertIsNone(quality.temporal_samples)
        self.assertIsNone(quality.shutter)

    def test_clarity_matches_stage_and_conductor_treatment(self):
        quality = QualityOptions.clarity(
            subject_focus=lambda t: (0., 1., 0.) if t < 2 else None,
            grade_when=lambda t: t >= 2)
        source = dict(sun_int=2., rays=.8, sun_glow=.6, exposure=1.2)
        self.assertIs(quality.world(1, source), source)
        graded = quality.world(2, source)
        self.assertEqual(graded, dict(sun_int=1.3, rays=.8*.65,
                                      sun_glow=.6*.75, exposure=1.2))
        self.assertEqual(source["sun_int"], 2.)
        params = dict(bloom_gain=.64)
        self.assertEqual(quality.parameters(2, params)["bloom_gain"], .64*.75)
        hero = quality.camera(1, self.cam)
        stage = quality.camera(2, self.cam)
        self.assertEqual((hero.focus, hero.aperture), (10., .012))
        self.assertEqual((stage.focus, stage.aperture), (80., .008))
        np.testing.assert_array_equal(hero.pos, self.cam.pos)
        np.testing.assert_array_equal(hero.target, self.cam.target)
        self.assertEqual((self.cam.focus, self.cam.aperture), (80., .04))
        self.assertEqual((quality.grain, quality.temporal_samples, quality.shutter,
                          quality.cut_safe), (False, 2, .35, True))

    def test_focus_uses_view_depth_not_radial_distance_and_checks_dynamic_points(self):
        quality = QualityOptions(subject_focus=(20., 1., 0.))
        self.assertEqual(quality.camera(0, self.cam).focus, 10.)
        self.assertEqual(QualityOptions(subject_focus=(0., 1., 11.)).camera(0, self.cam).focus, .02)
        self.cam.aperture = .002
        self.assertIs(QualityOptions(aperture_cap=.008).camera(0, self.cam), self.cam)
        with self.assertRaises(ValueError):
            QualityOptions(subject_focus=lambda t: (float("nan"), 0, 0)).camera(0, self.cam)

    def test_cut_safety_at_exact_cut_subframe_and_outside_shutter(self):
        quality = QualityOptions(cut_safe=True, cuts=(2.,))
        for fps in (30, 60):
            dt = .35 / fps
            for cut in (1., 2.):
                self.assertEqual(quality.shutter_at(cut-1e-6, fps, .35, (1.,)), .35)
                self.assertEqual(quality.shutter_at(cut, fps, .35, (1.,)), 0.)
                self.assertEqual(quality.shutter_at(cut+dt*.5, fps, .35, (1.,)), 0.)
                self.assertEqual(quality.shutter_at(cut+dt+1e-9, fps, .35, (1.,)), .35)
        self.assertEqual(quality.shutter_at(1, 60, 0, (1.,)), 0)

    def test_invalid_options_fail_explicitly(self):
        cases = (dict(grain=0), dict(cut_safe=1), dict(bloom_scale=-.1), dict(bloom_scale=None),
                 dict(sun_scale=float("nan")), dict(rays_scale=float("inf")),
                 dict(sun_glow_scale=-1), dict(shutter=-.1), dict(aperture_cap=-1),
                 dict(subject_aperture=-1), dict(temporal_samples=0),
                 dict(temporal_samples=True), dict(temporal_samples=1.5),
                 dict(subject_focus=(1, 2)), dict(grade_when=True),
                 dict(cuts=(float("inf"),)))
        for values in cases:
            with self.subTest(values=values), self.assertRaises(ValueError):
                QualityOptions(**values)

    def test_renderer_constructor_passes_quality_to_shader_without_rendering(self):
        song = SimpleNamespace(W=1920, H=1080, Song=lambda: object())
        module = load_engine("quality_test_renderer", "engine/render.py", song)
        module.comp_blocks = lambda: ()

        class StopAtComposite(Exception):
            pass

        for quality in (None, QualityOptions.clarity()):
            captured = []
            ctx = Mock()

            def program(**kwargs):
                captured.append(kwargs["fragment_shader"])
                if len(captured) == 6:
                    raise StopAtComposite
                return Mock()

            ctx.program.side_effect = program
            renderer = module.Renderer.__new__(module.Renderer)
            with self.assertRaises(StopAtComposite):
                renderer.__init__(ctx=ctx, quality=quality)
            expected = shaders.comp_fs((), grain=True if quality is None else quality.grain)
            self.assertEqual(captured[-1], expected)
            self.assertEqual(renderer.quality, quality or QualityOptions())


class LayerQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.song = SimpleNamespace(FPS=60, ASPECT=16/9, P3D={})
        cls.module = load_engine("p3d.quality_test_layer", "engine/p3d/layer.py", cls.song)

    def layer(self, quality):
        layer = self.module.Layer.__new__(self.module.Layer)
        layer.quality = quality
        layer.shutter = .35
        layer.samples = 2
        layer.rig = Rig([hold((0, 1, 10), (0, 1, 0), 0, 1, blend=0),
                         hold((1, 1, 10), (0, 1, 0), 1, 3, blend=0)], blend=0, aperture=.03)
        state = dict(sun_int=.8, rays=.5, sun_glow=.4, exposure=1., sun_el=10.)
        layer.world = SimpleNamespace(state=lambda t: dict(state), react=None)
        layer.audio = None
        layer._frame = None
        return layer

    def test_layer_constructor_inherits_or_overrides_motion_controls(self):
        class StopBeforeScene(Exception):
            pass
        for quality in (QualityOptions(), QualityOptions.clarity()):
            renderer = SimpleNamespace(ctx=object(), w=1920, h=1080, quality=quality)
            layer = self.module.Layer.__new__(self.module.Layer)
            rig = SimpleNamespace(shutter=.4)
            samples = lambda t: 3
            with patch.dict(sys.modules, draft=SimpleNamespace(DRAFT=False)), \
                    patch.object(self.module.S, "P3D", dict(motion_samples=samples)), \
                    patch.object(self.module.C, "make", return_value=rig), \
                    patch.object(self.module.Wd, "World"), \
                    patch.object(self.module.api, "Scene", side_effect=StopBeforeScene), \
                    self.assertRaises(StopBeforeScene):
                layer.__init__(renderer)
            self.assertEqual(layer.shutter, .4 if quality.shutter is None else .35)
            if quality.temporal_samples is None:
                self.assertIs(layer.samples, samples)
            else:
                self.assertEqual(layer.samples, 2)

    def test_layer_state_is_cut_safe_random_access_and_nonmutating(self):
        layer = self.layer(QualityOptions.clarity(subject_focus=(0., 1., 0.)))
        for t in (1., .9, 1.001, 1.1, 1.):
            layer._frame = None
            cam, prev, world = layer.state(t)
            self.assertEqual(world["sun_int"], .8*.65)
            self.assertEqual(layer.world.state(t)["sun_int"], .8)
            self.assertEqual(cam.aperture, .012)
            if 1 <= t < 1+.35/60:
                self.assertIs(cam, prev)
                self.assertEqual(layer._shutter_at(t), 0.)
            else:
                self.assertEqual(layer._shutter_at(t), .35)
            self.assertEqual(layer.shutter, .35)
        legacy = self.layer(QualityOptions())
        cam, prev, world = legacy.state(.9)
        np.testing.assert_array_equal(cam.pos, legacy.rig.state(.9, 16/9).pos)
        self.assertEqual(world["sun_int"], .8)
        self.assertEqual(cam.aperture, .03)

    def test_temporal_draw_uses_same_shot_samples_and_disables_all_cut_blur(self):
        layer = self.layer(QualityOptions.clarity(subject_focus=(0., 1., 0.)))
        layer.ctx = Mock()
        layer.R = SimpleNamespace(f_L=Mock())
        layer.scene = SimpleNamespace(entries=lambda: [])
        layer._mask_pass = Mock(return_value=None)
        layer._uniforms = lambda t, cam, prev, w: dict(
            uShutterDt=layer._shutter_at(t)/60, uAperture=cam.aperture)
        layer._draw_sets = Mock()
        for t, count in ((.9, 2), (1., 1), (1.001, 1), (1.1, 2)):
            layer._frame = None
            layer._draw_sets.reset_mock()
            layer.draw(t, {})
            calls = layer._draw_sets.call_args_list
            self.assertEqual(len(calls), count)
            self.assertEqual(sum(c.args[4] for c in calls), 1.)
            for call in calls:
                self.assertEqual(call.args[2].aperture, .012)
                self.assertEqual(call.args[1]["uShutterDt"], .35/60/2 if count == 2 else 0.)


class MotionQualityTests(unittest.TestCase):
    def test_actor_automatic_breathing_is_default_on_and_can_skip_second_pass(self):
        class StopAtFK(Exception):
            pass

        for automatic in (True, False):
            rig = SimpleNamespace(neutral_pos=np.zeros((1, 3)),
                                  fk=Mock(side_effect=StopAtFK))
            motions = Mock()
            options = {} if automatic else dict(auto_breathe=False)
            with patch.object(actor_module.assets, "load", return_value={}), \
                    patch.object(actor_module.mo, "Motions", return_value=motions):
                actor = Actor(rig=rig, life=False, **options)
            actor.base_pose = lambda t: Pose(1)
            actor.travel = lambda t: (0., np.zeros(3), 0.)
            with self.assertRaises(StopAtFK):
                actor.frame(1.)
            self.assertEqual(motions.breathe.call_count, int(automatic))
        with self.assertRaises(ValueError):
            Actor(auto_breathe="off")

    def test_gesture_solves_full_endpoint_once_and_blends_complete_poses(self):
        motions = Motions.__new__(Motions)
        source = Pose(2)
        source.contact = np.array([1., 0.])
        original = source.copy()
        calls = []

        def gesture(name, pose, weight, t, age, **kwargs):
            calls.append(weight)
            pose.q[0] = bm.qx(1.2)
            pose.rot = bm.qy(.3)
            pose.pos[:] = [1, 2, 3]
            pose.ground = 0.
            pose.contact = np.array([0., 1.])

        motions.gesture = gesture
        endpoint = source.copy()
        gesture("test", endpoint, 1, 0, 0)
        calls.clear()
        for weight in (0., .001, .4, .999, 1.):
            result = motions.blend_gesture("test", source, weight, 0)
            expected = blend(source, endpoint, weight)
            for key in ("q", "rot", "pos", "contact"):
                np.testing.assert_array_equal(getattr(result, key), getattr(expected, key))
            self.assertEqual(result.ground, expected.ground)
        self.assertEqual(calls, [1., 1., 1., 1.])
        np.testing.assert_array_equal(source.q, original.q)
        np.testing.assert_array_equal(source.pos, original.pos)
        with self.assertRaises(ValueError):
            motions.blend_gesture("test", source, float("nan"), 0)

    def test_feet_solve_after_breathing_without_later_ground_or_contact_shift(self):
        motions = Motions.__new__(Motions)
        source = Pose(2)
        source.contact = np.ones(2)
        events = []
        motions.breathe = lambda p, t, seed, depth: events.append("breathe")
        motions.leg_to = lambda p, s, target, **kw: events.append(
            (s, tuple(target), tuple(kw["foot"]), tuple(kw["knee"])))
        targets = {"L": np.array([.1, .05, .2]), "R": np.array([-.1, .05, .2])}
        rotations = {"L": bm.qy(.2), "R": bm.qy(-.2)}
        knees = {"L": np.array([.1, 0, 1]), "R": np.array([-.1, 0, 1])}
        frozen = deepcopy(targets)

        def solve(p):
            events.append("hands")
            motions.pin_feet(p, targets, rotations=rotations, knees=knees)

        result = motions.breathe_before_contacts(source, 1., solve)
        self.assertIs(result, source)
        self.assertEqual(events[:2], ["breathe", "hands"])
        self.assertEqual([row[0] for row in events[2:]], ["L", "R"])
        self.assertEqual((result.ground, result.contact), (0., None))
        for side in targets:
            np.testing.assert_array_equal(targets[side], frozen[side])
        for targets in ({}, {"X": (0, 0, 0)}, {"L": (float("nan"), 0, 0)}):
            with self.assertRaises(ValueError):
                motions.pin_feet(source, targets)

    def test_final_prop_grip_samples_solved_palm_and_transform_not_cue(self):
        p = np.array([3., 2., 1.])
        body = SimpleNamespace(where=Mock(return_value=(p, np.array([0., 0., 1.]))),
                               actor=SimpleNamespace(palm=Mock(return_value=(None, None, np.array([1., 0., 0.])))),
                               _wdir=Mock(return_value=np.array([0., 1., 0.])))
        pivot, across, outward, normal = final_hand_frame(body, .9)
        np.testing.assert_array_equal(pivot, p + np.array([0., .018, .006]))
        np.testing.assert_array_equal(across, [1, 0, 0])
        np.testing.assert_array_equal(outward, [0, 1, 0])
        np.testing.assert_array_equal(normal, [0, 0, 1])
        body.where.assert_called_once_with(.9, "palm.R", normal=True)
        body.actor.palm.assert_called_once_with(.9, "R")
        tilted = final_hand_frame(body, .9, roll=.3, tilt=.2)
        np.testing.assert_array_equal(tilted[0], pivot)
        axes = np.stack(tilted[1:])
        np.testing.assert_allclose(axes @ axes.T, np.eye(3), atol=1e-15)
        with self.assertRaises(ValueError):
            final_hand_frame(body, .9, side="X")


if __name__ == "__main__":
    unittest.main()
